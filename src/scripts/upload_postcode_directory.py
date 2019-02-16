import pandas
from sqlalchemy import create_engine

directory_file = open('Data/Postcode_Directory_Documents/Data/Postcode_Directory_Single.csv')
columns = ['pcds', 'cty', 'ced', 'laua', 'ward', 'ctry', 'rgn', 'pcon', 'eer', 'nuts', 'pct', 'hlthau', 'ccg', 'lsoa11',
           'msoa11', 'pfa']

data_frame = pandas.read_csv(directory_file, usecols=columns)[columns]

database_password_file = open('databasePassword.txt', 'r')
database_password = database_password_file.readline().strip()
database_password_file.close()
database_engine = create_engine(
                    "mysql://luke:" +
                    database_password +
                    "@third-year-project.cz8muheslaeo.eu-west-2.rds.amazonaws.com:3306/third_year_project")

print("Uploading data")
data_frame.to_sql('postcode_lookup', database_engine, if_exists='replace', index=False)