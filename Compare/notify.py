#program notifys when any changes to ogea_db happens
#this is one of the best named scripts ever because it rhymes

import datetime as dt
import csv
import argparse
import hashlib

import email_config as config
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

def readFile(filename):
    flat_data = {}
    with open(filename, 'rU') as f:
        dr = csv.DictReader(f, delimiter='|')
        for row in dr:
            flat_data[row['a_id']] = (
                row['state'], row['topic'], row['subtopic'], 
                row['question'], row['answer'], row['sources'], 
                row['date_aq'], row['conf_date'], row['ques_id'],
                )
    return flat_data

def writeChanges(file, changes):
    with open(file, 'w') as c:
        w = csv.writer(c)
        for k,v in changes.iteritems():
            w.writerow([k,v])

def checkData(old_data, new_data):
    changes = {}
    for k,v in old_data.iteritems():
        try:
            equal = hashCompare(v, new_data[k])
        except KeyError:
            changes[k] = {}
            changes[k]['old'] = v
            changes[k]['new'] = ('Fact has been deleted',)
        if equal == False:
            changes[k] = {}
            changes[k]['old'] = v
            changes[k]['new'] = new_data[k]
    return changes

def hashCompare(old_tupe, new_tupe):
    old = hashlib.md5()
    new = hashlib.md5()
    old.update(str(hash(old_tupe)))
    new.update(str(hash(new_tupe)))
    if old.digest() == new.digest():
        return True
    return False

def emailFlatFile(SUBJECT, FROM, TO, files):
    report = MIMEMultipart()
    report['Subject'] = SUBJECT
    report['From'] = FROM
    report['To'] = TO

    for f in files:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(f, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(f))
        report.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(config.FROM, config.PW)
    server.sendmail(FROM, TO, report.as_string())
    server.quit()

def printDict(d):
    for k,v in d.iteritems():
        print '{}: {}'.format(k,v)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Take in 2 filenames to compare')
    parser.add_argument('o', help='name of the old file, eg. old_data.csv')
    parser.add_argument('n', help='name of new file, eg. new_data.csv')
    args = parser.parse_args()

    old_file_data = readFile(args.o)
    new_file_data = readFile(args.n)
    changes = checkData(old_file_data, new_file_data)

    if len(changes) > 0:
        change_file = 'changes-{}.csv'.format(str(dt.date.today()))
        writeChanges(change_file, changes)
        emailFlatFile(config.SUBJECT, config.FROM, config.TO, [args.n, change_file])
        #store this new file as current file
