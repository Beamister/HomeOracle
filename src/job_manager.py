import datetime
import threading
import time

import boto3
from sqlalchemy.orm import sessionmaker
from tables import Job, Base

from constants import *


def interpret_date_toke(date_token):
    return date_token


# Takes a set of URL tokens and evaluates them based on the current date, then returns the URL to pull and the date to
# store the date under in the Dynamodb
def parse_url_tokens(tokens):
    result = tokens[0]
    current_token_index = 1
    while current_token_index < len(tokens):
        current_token = tokens[current_token_index]
        if current_token == '-d':
            result += interpret_date_toke(tokens[current_token_index + 1])
            current_token_index += 2
        elif current_token == '-s':
            result += tokens[current_token_index + 1]
            current_token_index += 2
    return result


# TODO
# Returns a dictionary of indicator names to locations to values
def pull_data(url, indicator_columns, location_column_index):
    return {}


def pull_indicator(job):
    source_name = str(job.details)
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
    sources_table = dynamodb.Table('Sources')
    indicators_table = dynamodb.Table('Indicators')
    sourc_details = sources_table.get_item(Key={'SourceName': source_name})['Item']
    url_to_pull, date = parse_url_tokens(sourc_details['sourceTokens'])
    location_column_index = sourc_details['locationColumn']
    indicator_columns = sourc_details['indicators']
    indicator_data = pull_data(url_to_pull, indicator_columns, location_column_index)
    for indicator in indicator_data:
        indicators_table.update_item(key={'IndicatorName': indicator},
                                     updateExpression="SET #dates.#date = :data",
                                     ExpressionUpdateName={'#dates': 'dates',
                                                           '#date': date
                                                           },
                                     ExpressionAttributeValues={':data': indicator_data[indicator]})


def complete_job(job):
    if job.job_type == PULL_INDICATOR_JOB:
        pass
    elif job.job_type == PULL_LAND_REGISTRY_JOB:
        pass
    elif job.job_type == UPDATE_DATA_SET_JOB:
        pass


class JobManager(threading.Thread):

    def __init__(self, thread_id, thread_name, counter, database_engine):
        threading.Thread.__init__(self)
        self.database_engine = database_engine
        self.thread_id = thread_id
        self.thread_name = thread_name
        self.counter = counter
        Base.metadata.create_all(self.database_engine)
        Base.metadata.bind = self.database_engine
        session = sessionmaker(bind=self.database_engine)
        self.session = session()

    def run(self):
        running = True
        while running:
            current_job = self.session.query(Job).order_by(Job.timestamp_when_valid).first()
            if current_job is None or datetime.strptime(current_job.timestamp_when_valid,
                                                        TIMESTAMP_FORMAT) < datetime.datetime.now():
                time.sleep(SECONDS_PER_HOUR)
            else:
                complete_job(current_job)
                self.session.delete(current_job)
                self.session.commit()

    # Date/time parameters specify when the job can be carried out
    def add_job(self, year, month, day, hour, minute, second, job_type, details):
        timestamp = TIMESTAMP_FORMATTER.format(year, month, day, hour, minute, second)
        new_job = Job(timestamp_when_valid=timestamp, job_type=job_type, details=details)
        self.session.add(new_job)
        self.session.commit()
