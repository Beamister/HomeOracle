from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    timestamp_when_valid = Column(String(64))
    job_type = Column(String(32))
    details = Column(String(128))
