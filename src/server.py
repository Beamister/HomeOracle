import dash
from sqlalchemy import create_engine

from job_manager import JobManager
from commit_manager import CommitManager

class ServerState():
    commit_index = -1

server_state = ServerState()

external_stylesheets = ['']

database_password_file = open('databasePassword.txt', 'r')
database_password = database_password_file.readline().strip()
database_password_file.close()
database_engine = create_engine(
                    "mysql://luke:" +
                    database_password +
                    "@third-year-project.cz8muheslaeo.eu-west-2.rds.amazonaws.com:3306/third_year_project")


job_manager = JobManager(1, 'JobsManagerthread', 1, database_engine, server_state)
commit_manager = CommitManager(2, 'CommitMangerThread', 2, database_engine, server_state)
job_manager.start()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.config.suppress_callback_exceptions = True
