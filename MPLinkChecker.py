#!/usr/bin/python

"""Finds links, checks each for validity, and sends email report of broken links"""

from bs4 import BeautifulSoup
#from itertools import *
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
from multiprocessing import Pool
import multiprocessing
import requests
import smtplib
import datetime
import csv

def makeSoup(url):
    r = requests.get(url, auth=('user', 'pass'))
    return BeautifulSoup(r.content)
    
def addStates():
    s = []
    for option in ogea_soup.find_all('option'):
        abbrv = option.get('id')
        if  abbrv != None:
            s.append(abbrv[-2:])
    return s

def addIDs(soup, a_tags):
    id_list = []
    for a in a_tags:
        try:
            citeID = a.findParent().get('class')[2]
            index = citeID.find('_')
            citeID = citeID[-index-1:]
            id_list.append(citeID)
        except:           
            try:
                citeID = a.findParent().findParent().span.get('id')
                if citeID == 'showall': citeID = 'check state main page widget'
                index = citeID.find('_')
                citeID = citeID[-index-1:]
                id_list.append(citeID)
            except:
                id_list.append(None)
    return id_list

def checkState(s):
    name = multiprocessing.current_process().name
    print '{} process is starting on {}'.format(name, s)
    fails = []
    state_soup = makeSoup(root_url + s)
    a_tags = state_soup.find_all('a')
    id_list = addIDs(state_soup, a_tags)
    id_count = 0
    bad_count = 0
    for a in a_tags:
        link = a.attrs['href']
        try:
            source = requests.get(link, auth=('user', 'pass'), stream = True)
            if source.status_code != 200 and source.status_code != 400 and source.status_code != 401:
                bad_count += 1  
                fails.append([s, id_list[id_count], link, source.status_code])
        except:
            pass
        finally:
            id_count += 1
    print '{} process is exiting on {} and found {} broken links'.format(name, s, bad_count)
    return fails

def addFail(result):
    if len(result) > 0:
        broken_links.append(result)

def writeFails(broken_links):
    with open('BrokenLinks.csv', 'w') as broken:
        writer = csv.writer(broken, delimiter=',')
        writer.writerow(['State', 'Fact_ID', 'Link', 'Error Code'])
        for state in broken_links:
            for link in state:
                writer.writerow(link)
                
def emailReport(SUBJECT, FROM, TO, file_name):
    report = MIMEMultipart()
    report['Subject'] = SUBJECT
    report['From'] = FROM
    report['To'] = TO

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(file_name, 'rb').read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(file_name))
    report.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('email@sample.com', 'password') #add email/password where the report will be sent from
    server.sendmail(FROM, TO, report.as_string())
    server.quit()

root_url = 'http://elections.neworganizing.com/en/guide/'
ogea_soup = makeSoup(root_url)
states = addStates()
broken_links = []

if __name__ == '__main__':
    start = datetime.datetime.now()
    pool = Pool()
    for s in states:
        pool.apply_async(checkState, args = (s, ), callback = addFail)
    pool.close()
    pool.join()
    
    writeFails(broken_links)
    SUBJECT = 'OGEA Broken Links Update {}'.format(datetime.datetime.now())
    FROM = 'email@sample.com' #edit to match emailReport()
    TO = 'admin@sample.com' #edit to whoever should receive the report
    emailReport(SUBJECT, FROM, TO, 'BrokenLinks.csv')
    end = datetime.datetime.now()
    total = end-start
    print 'Runtime: {} seconds, {} microseconds.'.format(total.seconds, total.microseconds)
    
