import threading
from time import sleep
from sqlalchemy import desc, Table
from sqlalchemy.orm import sessionmaker
from tables import Job, Base, StagedEntry, TargetEntry, IndicatorValue
from constants import *
import boto3

#TODO
def convert_location(postcode, area_resolution):
    pass

class CommitManager(threading.Thread):

    indicator_resolutions = {}

    def __init__(self, thread_id, thread_name, counter, database_engine, server_state):
        self.database_engine = database_engine
        self.thread_id = thread_id
        self.thread_name = thread_name
        self.counter = counter
        self.server_state = server_state
        session = sessionmaker(bind=self.database_engine)
        self.session = session()
        self.update_indicator_resolutions()

    def update_indicator_resolutions(self):
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
        sources_table = dynamodb.Table('Sources')
        sources_data = sources_table.scan()['Items']
        for source in sources_data:
            resolution = sources_data[source]['resolution']
            for indicator in sources_data[source]['indicators']:
                self.indicator_resolutions[indicator] = sources_data[source]['indicators'][indicator]

    def commit_entries(self, id):
            current_staged_entry = self.session.query(StagedEntry).order_by(StagedEntry.entry_id)\
                .filter(StagedEntry.entry_id <= self.server_state.commit_index)
            if current_staged_entry is not None:
                self.commit_entry(current_staged_entry)
            else:
                sleep(COMMIT_MANAGER_POLL_DELAY)


    def commit_entry(self, staged_entry: StagedEntry):
        indicator_values = {}
        for indicator in self.indicator_resolutions:
            value_location = convert_location(staged_entry.postcode, self.indicator_resolutions[indicator])
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
            elif following_value_entry is None \
                    or abs((previous_value_entry.date - staged_entry.date).days) \
                    < abs((following_value_entry.date - staged_entry.date).days):
                value = previous_value_entry.value
            else:
                value = following_value_entry.value
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