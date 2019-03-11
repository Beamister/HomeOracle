import boto3
from sqlalchemy import create_engine, Table
from sqlalchemy.orm import sessionmaker, session
from sqlalchemy.ext.declarative import declarative_base

AWS_REGION = 'eu-west-2'
source_name = 'Crime database'


database_password_file = open('databasePassword.txt', 'r')
database_password = database_password_file.readline().strip()
database_password_file.close()
database_engine = create_engine(
                    "mysql://luke:" +
                    database_password +
                    "@third-year-project.cz8muheslaeo.eu-west-2.rds.amazonaws.com:3306/third_year_project")
base = declarative_base(bind=database_engine)

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
sources_table = dynamodb.Table('Sources')
source_data = sources_table.get_item(Key={'SourceName': source_name})['Item']
session_maker = sessionmaker(bind=database_engine)
session = session_maker()
Table('core_dataset', base.metadata, autoload=True, autoload_with=database_engine,
      keep_existing=False, extend_existing=True)
table_headers = base.metadata.tables['core_dataset'].columns.keys()
for indicator in source_data['indicators'].keys():
    print('Removing ' + indicator)
    if indicator in table_headers:
        database_engine.execute('ALTER TABLE core_dataset DROP COLUMN %s' % (indicator))
    else:
        print('Indicator not found in database')
sources_table.delete_item(Key={'SourceName': source_name})
session.close()
