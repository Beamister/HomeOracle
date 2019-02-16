import datetime
from dateutil.relativedelta import relativedelta
import threading
from time import sleep
from urllib import request
import boto3
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from tables import Job, StagedEntry, TargetEntry, IndicatorValue
import pandas
from io import StringIO
from constants import *
from location_engine import LocationEngine


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
    entry_date = datetime.datetime.strptime(pull_timestamp, TIMESTAMP_FORMAT).date()
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
                    entry_date += relativedelta(years=modifier)
                    year_modified = True
                token_string_value = str(entry_date.year)
                if type_count == 2:
                    token_string_value = token_string_value[-2:]
            elif token_type == 'm':
                if not month_modified:
                    entry_date += relativedelta(months=modifier)
                    month_modified = True
                token_string_value = str(entry_date.month)
                while len(token_string_value) < type_count:
                    token_string_value = '0' + token_string_value
            elif token_type == 'd':
                if not day_modified:
                    entry_date += relativedelta(days=modifier)
                    day_modified = True
                token_string_value = str(entry_date.day)
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
    return url_string, entry_date


# Returns a dictionary of indicator names to locations to values, presumes pulled data is in csv format
# indicators is dictionary of for {"indicator name" : column_index,}
def pull_source_data(url, indicator_columns, location_column_index):
    data = request.urlopen(url).read()
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

# Called to update data entries when the land registry returns update records
def update_entry_from_land_registry(update_entry, existing_entry):
    existing_entry.date = update_entry.date
    existing_entry.value = update_entry.value
    existing_entry.PDD_type = update_entry.PDD_type
    existing_entry.postcode = update_entry.postcode
    existing_entry.new_property_flag = update_entry.new_property_flag
    existing_entry.property_type = update_entry.property_type
    existing_entry.tenure_type = update_entry.tenure_type


def get_days_to_next_pull(source):
    last_pull_date = datetime.strptime(source['lastPull'])
    days_since_last_pull = (last_pull_date - datetime.datetime.now).days
    days_between_pulls = FREQUENCY_DAY_COUNTS[source['frequency']]
    return days_between_pulls - days_since_last_pull


class JobManager(threading.Thread):

    indicators_metadata = {}

    def __init__(self, thread_id, thread_name, counter, database_engine):
        threading.Thread.__init__(self)
        self.database_engine = database_engine
        self.thread_id = thread_id
        self.thread_name = thread_name
        self.counter = counter
        session = sessionmaker(bind=self.database_engine)
        self.session = session()
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        self.sources_table = dynamodb.Table('Sources')
        self.update_indicators_metadata()
        self.location_engine = LocationEngine(database_engine)

    # Called when staging entries to work out when they should be committed
    def calculate_commit_datetime(self):
        current_datetime = datetime.datetime.now()
        sources = self.sources_table.scan(ProjectionExpression='SourceName, frequency, lastPull')['Items']
        sources.sort(key=get_days_to_next_pull, reverse=True)
        for source in sources:
            current_frequency_length = FREQUENCY_DAY_COUNTS[source['frequency']]
            comparison_datetime = current_datetime + relativedelta(days=current_frequency_length / 2)
            if current_datetime > comparison_datetime:
                return datetime.strptime(source['lastPull'], TIMESTAMP_FORMAT) \
                       + relativedelta(days=current_frequency_length + COMMIT_DELAY)
        return datetime.datetime.now()

    def update_entries_from_source(self, source_entry_date, frequency, indicators, area_resolution):
        frequency_radius_delta = relativedelta(FREQUENCY_DAY_COUNTS[frequency] / 2)
        lower_threshold_date = source_entry_date - frequency_radius_delta
        upper_threshold_date = source_entry_date + frequency_radius_delta
        # noinspection PyComparisonWithNone
        entries_to_update = self.session.query(TargetEntry).filter(getattr(TargetEntry, indicators[0]) == None,
                                                                   TargetEntry.date >= lower_threshold_date,
                                                                   TargetEntry.date <= upper_threshold_date)
        for entry in entries_to_update:
            location = self.location_engine.convert_postcode(entry.postcode, area_resolution)
            for indicator in indicators:
                value = self.session.query(IndicatorValue).filter(IndicatorValue == source_entry_date,
                                                                  IndicatorValue.location == location)
                setattr(entry, indicator, value)
        self.session.commit()

    def pull_source(self, job):
        source_name = str(job.details)
        source_details = self.sources_table.get_item(Key={'SourceName': source_name})['Item']
        url_to_pull, entry_date = parse_url_tokens(source_details['sourceTokens'], job.timestamp_when_valid)
        location_column_index = source_details['locationColumn']
        indicator_columns = source_details['indicators']
        indicators_data = pull_source_data(url_to_pull, indicator_columns, location_column_index)
        date_column = pandas.DataFrame(len(indicators_data) * [entry_date], columns=['date'])
        indicators_data = pandas.concat((date_column, indicators_data), axis='columns')
        indicators_data.to_sql('indicator_values', conn=self.database_engine, if_exists='append', index=False)
        # Update the timestamp of the last pull for the source
        self.sources_table.update_item(key={'SourceName': source_name},
                                       UpdateExpression='SET lastPull = :date',
                                       ExpressionAttributeValues={':date': job.timestamp_when_valid})
        next_pull_datetime = datetime.datetime.strptime(job.timestamp_when_valid, TIMESTAMP_FORMAT)
        if source_details['frequency'] == 'daily':
            next_pull_datetime += relativedelta(days=1)
        elif source_details['frequency'] == 'weekly':
            next_pull_datetime += relativedelta(days=7)
        elif source_details['frequency'] == 'monthly':
            next_pull_datetime += relativedelta(months=1)
        elif source_details['frequency'] == 'yearly':
            next_pull_datetime += relativedelta(years=1)
        return next_pull_datetime

    def pull_land_registry(self):
        data = request.urlopen(LAND_REGISTRY_URL).read()
        data = str(data, 'utf-8')
        data_frame = pandas.read_csv(StringIO(data), header=None, names=LAND_REGISTRY_DATA_HEADERS)
        # Only include entries with PPD type A
        # data_frame = [data_frame.PDD_type == 'A']
        # Convert date strings to date objects
        data_frame['date'] = pandas.to_datetime(data_frame['date'], format=LAND_REGISTRY_TIMESTAMP_FORMAT)
        # Reorder columns
        data_frame = data_frame[STAGED_ENTRY_HEADERS]
        # Convert old or new character value to boolean
        data_frame['new_property_flag'] = data_frame['new_property_flag'].map(dict(Y=True, N=False))
        current_highest_id = -1
        latest_entry = self.session.query(StagedEntry).order_by(desc(StagedEntry.entry_id)).first()
        if latest_entry is not None:
            current_highest_id = latest_entry.id
        batch_start_id = current_highest_id + 1
        batch_end_id = batch_start_id + len(data_frame)
        # Add id column
        data_frame.insert(0, 'entry_id', range(batch_start_id, batch_end_id))
        data_frame.to_sql('staged_entries', conn=self.database_engine, if_exists='append', index=False)
        # Process deletion entries
        deletion_entries = self.session.query(StagedEntry).filter(StagedEntry.record_type == 'D')
        for deletion_entry in deletion_entries:
            self.session.query(TargetEntry).filter(TargetEntry.sale_id == deletion_entry.sale_id).delete()
            deletion_entry.delete()
        # Get update entries
        update_entries = self.session.query(StagedEntry).filter(StagedEntry.record_type == 'C')
        for update_entry in update_entries:
            existing_entry = self.session.query(TargetEntry).filter(TargetEntry.sale_id == update_entry.sale_id).one()
            if existing_entry is not None:
                update_entry_from_land_registry(update_entry, existing_entry)
            update_entry.delete()
            self.session.commit()
        return str(batch_end_id)

    def run(self):
        running = True
        while running:
            current_job = self.session.query(Job).order_by(Job.timestamp_when_valid).first()
            if current_job is None or current_job.timestamp_when_valid > datetime.datetime.now():
                sleep(JOB_MANAGER_POLL_DELAY)
            else:
                self.complete_job(current_job)
                current_job.delete()

    def complete_job(self, job):
        if job.job_type == PULL_SOURCE_JOB:
            next_pull_datetime = self.pull_source(job)
            self.add_job(next_pull_datetime, PULL_SOURCE_JOB, job.details)
        elif job.job_type == PULL_LAND_REGISTRY_JOB:
            update_job_details = self.pull_land_registry()
            commit_job_datetime = self.calculate_commit_datetime()
            next_pull_datetime = datetime.datetime.strptime(job.timestamp_when_valid, TIMESTAMP_FORMAT) \
                + relativedelta(months=1)
            self.add_job(next_pull_datetime, PULL_LAND_REGISTRY_JOB, '')
            self.add_job(commit_job_datetime, COMMIT_JOB, update_job_details)
        elif job.job_type == COMMIT_JOB:
            self.commit_entries(int(job.details))

    def update_indicators_metadata(self):
        sources_data = self.sources_table.scan()['Items']
        for source in sources_data:
            resolution = source['resolution']
            frequency = source['frequency']
            for indicator in source['indicators']:
                self.indicators_metadata[indicator] = {}
                self.indicators_metadata[indicator]['resolution'] = resolution
                self.indicators_metadata[indicator]['frequency'] = frequency

    # Called when a new source is added, checks if commit jobs need to be pushed back to account for new source
    def update_commit_schedule(self, first_pull_date, frequency):
        # Calculate when the next pull is that cannot take place immediately
        next_scheduled_pull = first_pull_date
        while next_scheduled_pull < datetime.datetime.now():
            if frequency == 'yearly':
                next_scheduled_pull += relativedelta(years=1)
            elif frequency == 'monthly':
                next_scheduled_pull += relativedelta(months=1)
            else:
                next_scheduled_pull += relativedelta(days=FREQUENCY_DAY_COUNTS[frequency])
        threshold_date = next_scheduled_pull - relativedelta(days=FREQUENCY_DAY_COUNTS[frequency] / 2)
        commits_before_threshold = self.session.query(Job).filter(Job.job_type == COMMIT_JOB,
                                                                  Job.timestamp_when_valid < threshold_date)
        for commit in commits_before_threshold:
            commit.timestamp_when_valid = next_scheduled_pull

    # Date/time parameters specify when the job can be carried out
    def add_job(self, valid_datetime, job_type, details):
        new_job = Job(timestamp_when_valid=valid_datetime, job_type=job_type, details=details)
        self.session.add(new_job)
        self.session.commit()

    def commit_entries(self, end_batch_id):
        current_staged_entry = self.session.query(StagedEntry).order_by(StagedEntry.entry_id)\
            .filter(StagedEntry.entry_id <= end_batch_id)
        while current_staged_entry is not None:
            self.commit_entry(current_staged_entry)

    def commit_entry(self, staged_entry):
        indicator_values = {}
        for indicator in self.indicators_metadata:
            value_location = self.location_engine.convert_postcode(staged_entry.postcode,
                                                                   self.indicators_metadata[indicator]['resolution'])
            previous_value_entry = self.session.query(IndicatorValue)\
                .filter(IndicatorValue.indicator == indicator,
                        IndicatorValue.location == value_location,
                        IndicatorValue.date < staged_entry.date)\
                .order_by(IndicatorValue.date.desc())\
                .first()
            following_value_entry = self.session.query(IndicatorValue)\
                .filter(IndicatorValue.indicator == indicator,
                        IndicatorValue.location == value_location,
                        IndicatorValue.date > staged_entry.date)\
                .order_by(IndicatorValue.date)\
                .first()
            if previous_value_entry is None and following_value_entry is None:
                value = None
                indicator_date = None
            elif following_value_entry is None \
                    or abs((previous_value_entry.date - staged_entry.date).days) \
                    < abs((following_value_entry.date - staged_entry.date).days):
                value = previous_value_entry.value
                indicator_date = previous_value_entry.date
            else:
                value = following_value_entry.value
                indicator_date = following_value_entry.date
            # Check if value falls within frequency range
            if indicator_date is not None and (abs(staged_entry.date - indicator_date)).days\
                    > (FREQUENCY_DAY_COUNTS[self.indicators_metadata[indicator]['frequency']] / 2):
                value = None
            indicator_values[indicator] = value
        new_entry = TargetEntry(entry_id=staged_entry.entry_id, sale_id=staged_entry.sale_id,
                                date=staged_entry.date, value=staged_entry.value, PDD_type=staged_entry.PDD_type,
                                postcode=staged_entry.postcode, town_or_city=staged_entry.town_or_city,
                                district=staged_entry.district, county=staged_entry.county,
                                new_property_flag=staged_entry.new_property_flag,
                                property_type=staged_entry.property_type, tenure_type=staged_entry.tenure_type)
        for indicator in indicator_values:
            setattr(new_entry, indicator, indicator_values[indicator])
        self.session.add(new_entry)
        self.session.commit()
