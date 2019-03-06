from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Float, Date, Table, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import boto3
import server
from constants import *

Base = declarative_base()


def get_class_by_tablename(tablename):
    for c in Base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c


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
    pcds = Column(String(10), primary_key=True)  # postcode
    lat = Column(Float)  # latitude
    long = Column(Float)  # longitude
    cty = Column(String(9))  # counties.json, county
    ced = Column(String(9))  # ceds.json, county electoral division
    laua = Column(String(9))  # districts.json, district
    ward = Column(String(9))  # wards.json, ward
    ctry = Column(String(9))  # countries.json, country
    rgn = Column(String(9))  # regions.json, region
    pcon = Column(String(9))  # constituencies.json, parliamentary constituency
    eer = Column(String(9))  # european_registers.json, european electoral register
    nuts = Column(String(9))  # nuts.json, lau2 or nut area
    # parish = Column(String(9))  # parishes.json, NOT IN LOOKUP DIRECTORY
    pct = Column(String(9))  # pcts.json, primary care trust
    hlthau = Column(String(9))  # nhsHa.json, strategic health authority
    ccg = Column(String(9))  # ccgs.json, clinical commissioning group
    lsoa11 = Column(String(9))  # lsoa.json, lower layer super output area
    msoa11 = Column(String(9))  # msoa.json, middle layer super output area
    pfa = Column(String(9))  # police_force.csv, police force area


class Model(Base):
    __tablename__ = 'models'
    name = Column(String(64), primary_key=True)
    type = Column(String(32))
    dataset = Column(String(32))
    state = Column(String(32))


class Dependency(Base):
    __tablename__ = 'model_dependencies'
    parent = Column(String(64), primary_key=True)
    child = Column(String(64), primary_key=True)
