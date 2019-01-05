import threading
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from tables import Job, Base, StagedEntry, TargetEntry

class CommitManager(threading.Thread):

    def __init__(self, thread_id, thread_name, counter, database_engine, server_state):
        threading.Thread.__init__(self)
        self.database_engine = database_engine
        self.thread_id = thread_id
        self.thread_name = thread_name
        self.counter = counter
        self.server_state = server_state
        Base.metadata.create_all(self.database_engine)
        Base.metadata.bind = self.database_engine
        session = sessionmaker(bind=self.database_engine)
        self.session = session()

    def run(self):
        running = True
        while running:
            pass