import dash
from sqlalchemy import create_engine, Table
from tables import Base
from job_manager import JobManager
from constants import *
from json import load, dump
import sys
import datetime


class ServerState:

    def __init__(self):
        try:
            state_file = open(SERVER_STATE_FILE, 'r')
            state = load(state_file)
            state_file.close()
            for state_variable in state:
                # noinspection PyCallByClass
                # ensures that attributes are set without calling class set attribute which intercepts changes
                super.__setattr__(self, state_variable, state[state_variable])
        except FileNotFoundError:
            # Set default values
            pass

    # Intercepts changes to server state and records them to file
    def __setattr__(self, key, value):
        # noinspection PyCallByClass
        # used to ensure that attribute gets set as normal
        super.__setattr__(self, key, value)
        state_variables = {key: value for key, value in self.__dict__.items()
                           if not key.startswith('__') and not callable(key)}
        state_file = open(SERVER_STATE_FILE, 'w')
        dump(state_variables, state_file, skipkeys=True)
        state_file.close()


# Called on first run of the server to set up tables and such
def init():
    Base.metadata.create_all(database_engine)
    job_manager.add_job(datetime.datetime.now(), PULL_LAND_REGISTRY_JOB, '')


server_state = ServerState()

external_stylesheets = ['']

database_password_file = open('databasePassword.txt', 'r')
database_password = database_password_file.readline().strip()
database_password_file.close()
database_engine = create_engine(
                    "mysql://luke:" +
                    database_password +
                    "@third-year-project.cz8muheslaeo.eu-west-2.rds.amazonaws.com:3306/third_year_project")
Base.metadata.bind = database_engine
# Reflect the dataset table from the database
Table('dataset', Base.metadata, autoload=True, autoload_with=database_engine, keep_existing=False)

job_manager = JobManager(1, 'JobsManagerThread', 1, database_engine)
job_manager.start()

if '-i' in sys.argv:
    init()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.config.suppress_callback_exceptions = True
