from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Float, Date, Table, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import boto3
import server
from constants import *

Base = declarative_base()


def get_indicators():
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    sources_table = dynamodb.Table('Sources')
    indicators = []
    for source_indicators in sources_table.scan(ProjectionExpression='indicators')['Items']:
        indicators += list(source_indicators.keys())


def add_column(column_name, tablename='dataset', column_type='float'):
    session_maker = scoped_session(sessionmaker(bind=server.database_engine))
    session = session_maker()
    statement = f'ALTER TABLE {tablename} ADD {column_name} {column_type}'
    session.execute(statement)
    session.commit()
    session.close()
    # Refresh the table details held in metadata by reflecting from database
    Table(tablename, Base.metadata, autoload=True, autoload_with=server.database_engine, keep_existing=False)


class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    # timestamp of point after which job can be carried out
    timestamp_when_valid = Column(DateTime)
    # job type specifies what action the job should carry out
    # PULL_SOURCE_JOB = 'pull_source' - download a set of indicators from a source
    # PULL_LAND_REGISTRY_JOB = 'pull_land_registry' - download the last months property sales from the land registry
    #   into the staging table
    # COMMIT_JOB = 'update_data_set' - commits staged entries, merging them with indicator values
    job_type = Column(String(32))
    # Details value contains instructions that vary depending on job type:
    # - pull_source - name of the indicator to pull
    # - pull_land_registry_- empty
    # - update_data_set - list of staged entry ids to commit
    details = Column(String(128))


class StagedEntry(Base):
    __tablename__ = 'staged_entries'
    entry_id = Column(BigInteger, primary_key=True)
    sale_id = Column(String(48))
    date = Column(Date)
    value = Column(Integer)
    PDD_type = Column(String(1))
    postcode = Column(String(16))
    town_or_city = Column(String(128))
    district = Column(String(128))
    county = Column(String(128))
    new_property_flag = Column(Boolean)
    property_type = Column(String(1))
    tenure_type = Column(String(1))
    record_type = Column(String(1))


class TargetEntry(Base):
    __tablename__ = 'dataset'
    entry_id = Column(BigInteger, primary_key=True)
    sale_id = Column(String(48))
    date = Column(Date)
    value = Column(Integer)
    PDD_type = Column(String(1))
    postcode = Column(String(16))
    town_or_city = Column(String(128))
    district = Column(String(128))
    county = Column(String(128))
    new_property_flag = Column(Boolean)
    property_type = Column(String(1))
    tenure_type = Column(String(1))


class IndicatorValue(Base):
    __tablename__ = 'indicator_values'
    date = Column(Date, primary_key=True)
    indicator = Column(String(64), primary_key=True)
    location = Column(String(64), primary_key=True)


class Locations(Base):
    __tablename__ = 'postcode_lookup'
    postcode = Column(String(10), primary_key=True)  # column name - pcds
    county = Column(String(9))  # counties.json, column name - cty
    county_electoral_division = Column(String(9))  # ceds.json, column name - ced
    district = Column(String(9))  # districts.json, column name - laua
    ward = Column(String(9))  # wards.json, column name - ward
    country = Column(String(9))  # countries.json, column name - ctry
    region = Column(String(9))  # regions.json, column name - rgn
    parliamentry_constituency = Column(String(9))  # constituencies.json, column name - pcon
    european_electoral_region = Column(String(9))  # european_registers.json, column name - eer
    lau2_or_nut_area = Column(String(9))  # nuts.json, column name - nuts
    # parish = Column(String(9))  # parishes.json, column name - NOT IN LOOKUP DIRECTORY
    primary_care_trust = Column(String(9))  # pcts.json, column name - pct
    strategic_health_authority = Column(String(9))  # nhsHa.json, column name - hlthau
    clinical_commisionaing_group = Column(String(9))  # ccgs.json, column name - ccg
    lower_layer_super_output_area = Column(String(9))  # lsoa.json, column name - lsoa11
    middle_layer_super_output_area = Column(String(9))  # msoa.json, column name - msoa11
    police_force = Column(String(9))  # police_force.csv, column name - pfa
