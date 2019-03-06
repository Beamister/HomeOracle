from constants import *
from sqlalchemy.orm import sessionmaker

from model_trainer import ModelTrainer
from tables import Dependency, Model, TargetEntry
from model import Model
import os
import pickle

class ModelManager:

    # Dictionary of model names to model objects
    models = {}
    max_inputs = 0

    def __init__(self, database_engine):
        self.database_engine = database_engine
        session = sessionmaker(bind=self.database_engine)
        self.session = session()
        for model_name in self.get_model_names():
            self.load_model(model_name)
        # Find largest model input count after all models loaded
        for model_name in self.get_model_names():
            model_input_count = len(self.get_model_inputs(model_name))
            if model_input_count > self.max_inputs:
                self.max_inputs = model_input_count

    def get_model_names(self, dataset_name=None):
        if dataset_name is None:
            model_names = self.session.query(Model.name)
        else:
            model_names = self.session.query(Model.name).filter(Model.dataset == dataset_name)
        return list(model_names)

    def get_model_table(self):
        models_entries = self.session.query(Model)
        table = []
        for model_entry in models_entries:
            dependencies = ", ".join(self.get_model_dependencies(model_entry.name))
            table.append({'Name': model_entry.name, 'Type': model_entry.type, 'Dataset': model_entry.dataset,
                          'State': model_entry.state, 'Dependencies': dependencies})
        return table

    def add_new_model(self, settings):
        new_model_name = settings['name']
        new_model = Model(settings)
        self.models[new_model_name] = new_model
        self.save_model(new_model_name)
        new_model_record = Model(name=settings['name'], type=settings['type'],
                                 dataset=settings['dataset'], state='untrained')
        self.session.add(new_model_record)
        self.session.commit()
        model_input_count = len(self.get_model_inputs(new_model_name))
        if model_input_count > self.max_inputs:
            self.max_inputs = model_input_count

    def train_model(self, model_name):
        model_trainer_thread = ModelTrainer(self, model_name, self.database_engine)
        model_trainer_thread.start()

    def delete_model(self, model_name):
        self.session.query(Model).filter(Model.name == model_name).delete()
        del self.models[model_name]
        os.remove(model_name)

    def get_recursive_prediction(self, model_name, start_price, start_inputs, end_inputs):
        model = self.models[model_name]
        parent_predictions = {}
        for parent_model in model.input_models:
            parent_predictions[parent_model] = self.get_recursive_prediction(parent_model, start_price,
                                                                             start_inputs, end_inputs)
        prediction = model.predict(start_price, start_inputs, end_inputs, parent_predictions)
        return prediction

    def get_prediction(self, model_name, start_price, start_inputs, end_inputs):
        input_parameter_names = self.get_model_inputs(model_name)
        start_input_dictionary = dict(zip(input_parameter_names, start_inputs))
        end_input_dictionary = dict(zip(input_parameter_names, end_inputs))
        return self.get_recursive_prediction(model_name, start_price,
                                             start_input_dictionary, end_input_dictionary)['final']

    # returns the list of input parameters, including those from input models, without duplicates
    def get_model_inputs(self, model_name):
        model = self.models[model_name]
        inputs = []
        for parent_model in model.input_models:
            inputs += self.get_model_inputs(parent_model)
        inputs += model.input_parameters
        return list(set(inputs))

    def load_model(self, model_name):
        with open(model_name, '') as model_file:
            self.models[model_name] = pickle.load(model_file)

    def save_model(self, model_name):
        with open(model_name, '') as model_file:
            pickle.dump(self.models[model_name], model_file)

    def get_available_inputs(self, dataset_name):
        if dataset_name == 'boston_housing':
            return DEFAULT_DATA_HEADERS
        core_data_table_headers = TargetEntry.__table__.columns.keys()
        return [column_header for column_header in core_data_table_headers
                if column_header not in CORE_METADATA_HEADERS]

    def get_max_model_inputs(self):
        return self.max_inputs

    def get_model_dependencies(self, model_name):
        dependencies_list = []
        dependency_entries = self.session.query(Dependency).filter(Dependency.child == model_name)
        for dependency_entry in dependency_entries:
            dependencies_list.append(dependency_entry.parent)
        return dependencies_list
