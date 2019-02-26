

class ModelManager:

    # Dictionary of model names to model objects
    models = {}

    def __init__(self):
        pass

    # TODO - choosing a dataset returns only models using that dataset
    def get_model_names(self, dataset_name=None):
        return ['test1', 'test2', 'test3']

    # TODO
    def get_model_table(self):
        return [{'test header 1': 'test value 1', 'test header 2': 'test value 2', 'test header 3': 'test value 3', }]

    # TODO
    def add_new_model(self, settings):
        pass

    # TODO
    def train_model(self, model_name):
        pass

    # TODO
    def delete_model(self, model_name):
        pass

    # TODO -
    def get_prediction(self, model_name, start_price, start_inputs, end_inputs):
        print(model_name, start_price, start_inputs, end_inputs)
        return 100

    # TODO
    def get_model_inputs(self, model_name):
        if model_name == 'test1':
            return ['test input 1', 'test input 2', 'test input 3']
        elif model_name == 'test2':
            return ['test input 4', 'test input 5', 'test input 6', 'test input 7']
        else:
            return ['test input 2', 'test input 3', 'test input 6', 'test input 8']

    # TODO
    def load_model(self, model_name):
        pass

    # TODO
    def save_model(self):
        pass

    # TODO
    def get_available_inputs(self, dataset_name):
        return ['test1', 'test2', 'test3']

    # TODO
    def get_max_model_inputs(self):
        return 10