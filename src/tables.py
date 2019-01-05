from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    # timestamp of point after which job can be carried out
    timestamp_when_valid = Column(String(64))
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
    date = Column(String(32))
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
    date = Column(String(32))
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
    date = Column(String(32), primary_key=True)
    indicator = Column(String(64), primary_key=True)
    location = Column(String(64), primary_key=True)
    value = Float

