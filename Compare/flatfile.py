import psycopg2
import psycopg2.extras
from db_info import DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD

import datetime as dt
import csv

con = psycopg2.connect(host = DB_HOST, database = DB_NAME, user = DB_USERNAME, password = DB_PASSWORD)
cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

def process_query(data):
    keys = [c[0] for c in cur.description]
    end_data = []
    for row in data:
        dict_row = dict.fromkeys(keys)
        citations = []
        for r, k in zip(row, keys):
            if k == 'a_id':
                cur.execute("select schema_citation.url from schema_answer join schema_answer_citations on schema_answer.id = schema_answer_citations.answer_id join schema_citation on schema_citation.id = schema_answer_citations.citation_id where schema_answer.id = (%s);", (r,))
                cites = cur.fetchall()
                count = 1
                for c in cites:
                    citations.append(c[0])
                    count += 1
                dict_row['sources'] = citations
            dict_row[k] = r
        end_data.append(dict_row)
    print len(end_data)
    return end_data

def dump_data():
    cur.execute("select schema_state.name as state, schema_topic.name as topic, schema_subtopic.name as subtopic, schema_question.text as question, schema_question.id as ques_id, schema_answer.id as a_id, schema_answer.text as answer, schema_answer.confirmed_on as conf_date, schema_answer.date_aquired as date_aq from schema_state inner join schema_answer on schema_state.id = schema_answer.state_id inner join schema_question on schema_answer.question_id = schema_question.id inner join schema_subtopic on schema_question.subtopic_id = schema_subtopic.id inner join schema_topic on schema_subtopic.topic_id = schema_topic.id;")
    return process_query(cur.fetchall())

def write_flat(filename, data):
    cols = ['state', 'topic', 'subtopic', 'ques_id', 'question', 'answer', 'sources', 'date_aq', 'conf_date', 'a_id']
    with open(filename, 'w') as flat:
        dw = csv.DictWriter(flat, cols, delimiter = '|')
        dw.writeheader()        
        for row in data:
            dw.writerow(row)

if __name__ == '__main__':
    end_data = dump_data()
    write_flat('ogea_data_{}.csv'.format(str(dt.date.today())), end_data)



