from constants import *

from model_trainer import ModelTrainer
from tables import Dependency, ModelEntry, TargetEntry, Session
from model import Model
import os
import pickle


class ModelManager:

    # Dictionary of model names to model objects
    models = {}
    max_inputs = 0

    def __init__(self, database_engine):
        self.database_engine = database_engine
        session = Session()
        for model_name in self.get_model_names():
            self.load_model(model_name)
        # Find largest model input count after all models loaded
        for model_name in self.get_trained_model_names():
            model_input_count = len(self.get_model_inputs(model_name))
            if model_input_count > self.max_inputs:
                self.max_inputs = model_input_count
        # Check for models that were in training when last shut down
        for model_record in session.query(ModelEntry).filter(ModelEntry.state == 'training'):
            self.train_model(model_record.name)
        session.close()

    def get_model_names(self, dataset_name=None):
        session = Session()
        model_names = []
        if dataset_name is None:
            model_records = session.query(ModelEntry).all()
        else:
            model_records = session.query(ModelEntry).filter(ModelEntry.dataset == dataset_name)
        if model_records is not None:
            for model in model_records:
                model_names.append(model.name)
        session.close()
        return model_names

    def get_trained_model_names(self, dataset_name=None):
        model_names = []
        session = Session()
        if dataset_name is None:
            model_records = session.query(ModelEntry.name).filter(ModelEntry.state == 'trained')
        else:
            model_records = session.query(ModelEntry.name).filter(ModelEntry.dataset == dataset_name,
                                                                  ModelEntry.state == 'trained')
        for model in model_records:
            model_names.append(model.name)
        session.close()
        return model_names

    def get_model_table(self):
        session = Session()
        models_entries = session.query(ModelEntry)
        table = []
        for model_entry in models_entries:
            dependencies = ", ".join(self.get_model_dependencies(model_entry.name))
            table.append({'Name': model_entry.name, 'Type': model_entry.type, 'Dataset': model_entry.dataset,
                          'State': model_entry.state, 'Dependencies': dependencies})
        session.close()
        return table

    def add_new_model(self, settings):
        new_model_name = settings['name']
        new_model = Model(settings)
        self.models[new_model_name] = new_model
        self.save_model(new_model_name)
        new_model_record = ModelEntry(name=settings['name'], type=settings['type'],
                                      dataset=settings['dataset'], state='untrained')
        session = Session()
        session.add(new_model_record)
        session.commit()
        session.close()

    def train_model(self, model_name):
        model_trainer_thread = ModelTrainer(self, model_name, self.database_engine)
        model_trainer_thread.start()

    def update_max_inputs(self, model_input_count):
        if model_input_count > self.max_inputs:
            self.max_inputs = model_input_count

    def delete_model(self, model_name):
        session = Session()
        model_record = session.query(ModelEntry).filter(ModelEntry.name == model_name)
        model_record.delete()
        session.commit()
        del self.models[model_name]
        os.remove(model_name)
        # Update max inputs value
        self.max_inputs = 0
        for model_name in self.get_trained_model_names():
            model_input_count = len(self.get_model_inputs(model_name))
            if model_input_count > self.max_inputs:
                self.max_inputs = model_input_count
        session.close()

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
        prediction = self.get_recursive_prediction(model_name, start_price,
                                                   start_input_dictionary, end_input_dictionary)['final']
        return round(prediction, 2)

    # returns the list of input parameters, including those from input models, without duplicates
    def get_model_inputs(self, model_name):
        if model_name == '':
            return []
        model = self.models[model_name]
        inputs = []
        for parent_model in model.input_models:
            inputs += self.get_model_inputs(parent_model)
        inputs += model.input_parameters
        return list(set(inputs))

    def load_model(self, model_name):
        with open(model_name, 'rb') as model_file:
            self.models[model_name] = pickle.load(model_file)

    def save_model(self, model_name):
        with open(model_name, 'wb') as model_file:
            pickle.dump(self.models[model_name], model_file)

    def get_available_inputs(self, dataset_name):
        if dataset_name == 'boston_housing':
            result = DEFAULT_DATA_HEADERS.copy()
            result.remove(DEFAULT_TARGET_HEADER)
            return result
        core_data_table_headers = TargetEntry.__table__.columns.keys()
        return [column_header for column_header in core_data_table_headers
                if column_header not in CORE_METADATA_HEADERS]

    def get_max_model_inputs(self):
        return self.max_inputs

    def get_model_dependencies(self, model_name):
        dependencies_list = []
        for parent_model in self.models[model_name].input_models:
            dependencies_list.append(parent_model)
            dependencies_list += self.get_model_dependencies(parent_model)
        return list(set(dependencies_list))
