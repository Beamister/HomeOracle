import dash
from sqlalchemy import create_engine, Table

from model_manager import ModelManager
from tables import Base, database_engine
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


# Called on first run of the server to initialise first pull job
def init():
    # Commented out for front end deployment to AWS
    job_manager.add_job(datetime.datetime.now(), PULL_LAND_REGISTRY_JOB, '')


Base.metadata.create_all(database_engine)
job_manager = JobManager(1, 'JobsManagerThread', 1, database_engine)

if '-i' in sys.argv:
    init()

server_state = ServerState()

external_stylesheets = ['']

# Reflect the dataset table from the database
Table('core_dataset', Base.metadata, autoload=True, autoload_with=database_engine, keep_existing=False, extend_existing=True)

# switch to enable the job manager
if '-j' in sys.argv:
    job_manager.start()

model_manager = ModelManager(database_engine)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.config.suppress_callback_exceptions = True
