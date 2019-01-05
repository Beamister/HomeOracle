import datetime
from dateutil.relativedelta import relativedelta
import threading
import time
import urllib
import boto3
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from tables import Job, Base, StagedEntry, TargetEntry
import pandas
from io import StringIO
from constants import *
from operator import itemgetter


def get_modifier(date_token):
    if '+' in date_token:
        return int(date_token.split('+')[-1])
    elif '-' in date_token:
        return int(date_token.split('-')[-1]) * -1
    else:
        return 0


# Takes a set of URL tokens and evaluates them based on the current date, then returns the URL to pull and the date to
# store the date under in the Dynamodb
def parse_url_tokens(tokens, pull_timestamp):
    pull_datetime = datetime.datetime.strptime(pull_timestamp, TIMESTAMP_FORMAT)
    url_string = tokens[0]
    year_modified = False
    month_modified = False
    day_modified = False
    # Loop finds date tokens and replaces them with static tokens
    for token_type in ['y', 'm', 'd']:
        while ('-' + token_type) in tokens:
            specifier_index = tokens.index('-' + token_type)
            type_count = tokens[specifier_index + 1].count(token_type)
            modifier = get_modifier(tokens[specifier_index + 1])
            token_string_value = ''
            if token_type == 'y':
                if not year_modified:
                    pull_datetime += relativedelta(years=modifier)
                    year_modified = True
                token_string_value = str(pull_datetime.year)
                if type_count == 2:
                    token_string_value = token_string_value[-2:]
            elif token_type == 'm':
                if not month_modified:
                    pull_datetime += relativedelta(months=modifier)
                    month_modified = True
                token_string_value = str(pull_datetime.month)
                while len(token_string_value) < type_count:
                    token_string_value = '0' + token_string_value
            elif token_type == 'd':
                if not day_modified:
                    pull_datetime += relativedelta(days=modifier)
                    day_modified = True
                token_string_value = str(pull_datetime.day)
                while len(token_string_value) < type_count:
                    token_string_value = '0' + token_string_value
            tokens[specifier_index] = '-s'
            tokens[specifier_index + 1] = token_string_value
    current_token_index = 1
    while current_token_index < len(tokens):
        current_token = tokens[current_token_index]
        if current_token == '-s':
            url_string += tokens[current_token_index + 1]
            current_token_index += 2
    data_date_string = pull_datetime.strftime(TIMESTAMP_FORMAT)
    return url_string, data_date_string


# Returns a dictionary of indicator names to locations to values, presumes pulled data is in csv format
# indicators is dictionary of for {"indicator name" : column_index,}
def pull_source_data(url, indicator_columns, location_column_index):
    data = urllib.request.urlopen(url).read()
    data = str(data, 'utf-8')
    data_frame = pandas.read_csv(StringIO(data))
    entries_count = len(data_frame)
    result = pandas.DataFrame(columns=['indicator', 'location', 'value'])
    for indicator_name in indicator_columns:
        indicator_column_index = indicator_columns[indicator_name]
        name_column = pandas.DataFrame(entries_count * [indicator_name])
        new_frame = pandas.concat((name_column,
                                   data_frame[:][location_column_index],
                                   data_frame[:][indicator_column_index]), axis='columns')
        result.append(new_frame)
    return result


def pull_source(job, database_engine):
    source_name = str(job.details)
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
    sources_table = dynamodb.Table('Sources')
    indicators_table = dynamodb.Table('Indicators')
    source_details = sources_table.get_item(Key={'SourceName': source_name})['Item']
    url_to_pull, date = parse_url_tokens(source_details['sourceTokens'], job.timestamp_when_valid)
    location_column_index = source_details['locationColumn']
    indicator_columns = source_details['indicators']
    indicators_data = pull_source_data(url_to_pull, indicator_columns, location_column_index)
    date_column = pandas.DataFrame(len(indicators_data) * [date], columns=['date'])
    indicators_data = pandas.concat((date_column, indicators_data), axis='columns')
    indicators_data.to_sql('indicator_values', conn=database_engine, if_exists='append', index=False)
    # Update the timestamp of the last pull for the source
    dynamodb.Table('Sources').update_item(key={'SourceName': source_name},
                                          UpdateExpression='SET lastPull = :date',
                                          ExpressionAttributeValues={':date': job.timestamp_when_valid})
    next_pull_datetime = datetime.datetime.strptime(job.timestamp_when_valid)
    if source_details['frequency'] == 'daily':
        next_pull_datetime += relativedelta(days=1)
    elif source_details['frequency'] == 'weekly':
        next_pull_datetime += relativedelta(days=7)
    elif source_details['frequency'] == 'monthly':
        next_pull_datetime += relativedelta(months=1)
    elif source_details['frequency'] == 'yearly':
        next_pull_datetime += relativedelta(years=1)
    return next_pull_datetime

# Called to update data entries when the land registry returns update records
def update_entry_from_land_registry(update_entry, existing_entry):
    existing_entry.date = update_entry.date
    existing_entry.value = update_entry.value
    existing_entry.PDD_type = update_entry.PDD_type
    existing_entry.postcode = update_entry.postcode
    existing_entry.town_or_city = update_entry.town_or_city
    existing_entry.district = update_entry.district
    existing_entry.county = update_entry.county
    existing_entry.new_property_flag = update_entry.new_property_flag
    existing_entry.property_type = update_entry.property_type
    existing_entry.tenure_type = update_entry.tenure_type

def get_days_to_next_pull(source):
    last_pull_date = datetime.strptime(source['lastPull'])
    days_since_last_pull = (last_pull_date - datetime.datetime.now).days
    days_between_pulls = FREQUENCY_DAY_COUNTS[source['frequency']]
    return days_between_pulls - days_since_last_pull

# Called when staging entries to work out when they should be committed
def calculate_commit_datetime():
    current_datetime = datetime.datetime.now()
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
    sources_table = dynamodb.Table('Sources')
    sources = sources_table.scan(ProjectionExpression='SourceName, frequency, lastPull')['Items']
    sources.sort(key=get_days_to_next_pull, reverse=True)
    for source in sources:
        current_frequency_length = FREQUENCY_DAY_COUNTS[source['frequency']]
        comparison_datetime = current_datetime + relativedelta(days=current_frequency_length / 2)
        if current_datetime > comparison_datetime:
            return datetime.strptime(source['lastPull'], TIMESTAMP_FORMAT)\
                   + relativedelta(days=current_frequency_length + COMMIT_DELAY)
    return datetime.datetime.now()

def pull_land_registry(database_engine, session):
    data = urllib.request.urlopen(LAND_REGISTRY_URL).read()
    data = str(data, 'utf-8')
    data_frame = pandas.read_csv(StringIO(data), header=None, names=LAND_REGISTRY_DATA_HEADERS)
    # Only include entries with PPD type A
    data_frame = [data_frame.PDD_type == 'A']
    # Reorder columns
    data_frame = [[STAGED_ENTRY_HEADERS]]
    # Convert old or new character value to boolean
    data_frame['old_or_new'] = data_frame['old_or_new'].map({'Y' : True, 'N' : False})
    current_highest_id = -1
    latest_entry = session.query(StagedEntry).order_by(desc(StagedEntry.id)).first()
    if latest_entry is not None:
        current_highest_id = latest_entry.id
    batch_start_id = current_highest_id + 1
    batch_end_id = batch_start_id + len(data_frame)
    # Add id column
    data_frame.insert(0, 'entry_id', range(batch_start_id, batch_end_id))
    data_frame.to_sql('staged_entries', conn=database_engine, if_exists='append', index=False)
    # Process deletion entries
    deletion_entries = session.query(StagedEntry).filter(StagedEntry.record_type == 'D')
    for deletion_entry in deletion_entries:
        session.query(TargetEntry).filter(TargetEntry.sale_id == deletion_entry.sale_id).delete()
        deletion_entry.delete()
    # Get update entries
    update_entries = session.query(StagedEntry).filter(StagedEntry.record_type == 'C')
    for update_entry in update_entries:
        existing_entry = session.query(TargetEntry).filter(TargetEntry.sale_id == update_entry.sale_id).one()
        if existing_entry is not None:
            update_entry_from_land_registry(update_entry, existing_entry)
        update_entry.delete()
    return str(batch_end_id)


class JobManager(threading.Thread):

    def __init__(self, thread_id, thread_name, counter, database_engine, server_state):
        threading.Thread.__init__(self)
        self.database_engine = database_engine
        self.thread_id = thread_id
        self.thread_name = thread_name
        self.counter = counter
        self.server_state = server_state
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
                self.complete_job(current_job)
                current_job.delete()

    def complete_job(self, job):
        if job.job_type == PULL_SOURCE_JOB:
            next_pull_datetime = pull_source(job)
            self.add_job(next_pull_datetime, PULL_SOURCE_JOB, job.details)
        elif job.job_type == PULL_LAND_REGISTRY_JOB:
            update_job_details = pull_land_registry(self.database_engine, self.session)
            commit_job_datetime = calculate_commit_datetime()
            next_pull_datetime = datetime.datetime.strptime(job.timestamp_when_valid, TIMESTAMP_FORMAT) \
                                 + relativedelta(months=1)
            self.add_job(next_pull_datetime, PULL_LAND_REGISTRY_JOB, '')
            self.add_job(commit_job_datetime, COMMIT_JOB, update_job_details)
        elif job.job_type == COMMIT_JOB:
            self.server_state.commit_index = int(job.details)

    # TODO
    # Called when a new source is added, checks if commit jobs need to be pushed back to account for new source
    def update_commit_schedule(self):
        pass

    # Date/time parameters specify when the job can be carried out
    def add_job(self, datetime, job_type, details):
        timestamp = TIMESTAMP_FORMATTER.format(datetime.year, datetime.month, datetime.day, datetime.hour,
                                               datetime.minute, datetime.second)
        new_job = Job(timestamp_when_valid=timestamp, job_type=job_type, details=details)
        self.session.add(new_job)
        self.session.commit()
