import threading
from sqlalchemy.orm import sessionmaker, query
from sqlalchemy.sql.expression import func
from tables import ModelEntry, TargetEntry, Base
import time
import pandas
from constants import *


class ModelTrainer(threading.Thread):

    def __init__(self, model_manager, model_name, database_engine):
        threading.Thread.__init__(self)
        self.database_engine = database_engine
        self.model_manager = model_manager
        self.bottom_model_name = model_name
        session = sessionmaker(bind=database_engine)
        self.session = session()

    # Recursively processes training data through parent models
    def recursive_process(self, model_name, dataframe):
        model = self.model_manager.models[model_name]
        for parent_model in model.input_models:
            self.recursive_process(parent_model, dataframe)
        model_output = model.process(dataframe)
        dataframe[model_name] = model_output

    def train_model(self, model_name):
        model_record = self.session.query(ModelEntry).filter(ModelEntry.name == model_name).one()
        model_record.state = 'training'
        self.session.commit()
        parent_models = self.model_manager.models[model_name].input_models
        for parent_model in parent_models:
            # Train any untrained parent models
            if self.session.query(ModelEntry).filter(ModelEntry.name == parent_model, ModelEntry.state == 'untrained')\
                    .exists().scalar():
                self.train_model(parent_model)
            # Wait for any parent models that are still in training, in cases where another process started the training
            while self.session.query(ModelEntry).filter(ModelEntry.name == parent_model, ModelEntry.state == 'training')\
                    .exists().scalar():
                time.sleep(30)
        model = self.model_manager.models[model_name]
        dataset_name = model.dataset
        entry_count = model.training_entry_count
        if dataset_name == 'core_dataset':
            dataframe = pandas.read_sql(self.session.query(Base.metadata.tables['core_dataset']).order_by(func.rand()).limit(entry_count).statement,
                                        self.database_engine)
        else:
            dataframe = pandas.read_csv(DEFAULT_DATA_PATH, sep='\s+', names=DEFAULT_DATA_HEADERS)
            if entry_count > len(dataframe):
                entry_count = len(dataframe)
            dataframe = dataframe.sample(entry_count)
        for parent_model in parent_models:
            self.recursive_process(parent_model, dataframe)
        model.train(dataframe)
        self.model_manager.save_model(model_name)
        model_record.state = 'trained'
        self.session.commit()
        # Update the model manager max input count - done here to happen at the end of training
        self.model_manager.update_max_inputs(len(self.model_manager.get_model_inputs(model_name)))

    def run(self):
        self.train_model(self.bottom_model_name)
        self.session.close()
