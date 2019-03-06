from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from constants import *
import pandas


class Model:

    # Does not include parameters input to parent models
    input_parameters = []
    input_models = []
    name = ''
    dataset = ''
    training_entry_count = 0
    type = ''
    target_column_name = ''

    def __init__(self, settings):
        self.name = settings['name']
        self.input_parameters = settings['input_parameters']
        self.input_models = settings['input_models']
        self.dataset = settings['dataset']
        self.type = settings['type']
        if self.dataset == 'boston_housing':
            self.target_column_name = DEFAULT_TARGET_HEADER
        else:
            self.target_column_name = CORE_TARGET_HEADER
        if self.type == 'decision_tree':
            estimator_count = settings['estimator_count']
            max_tree_depth = settings['max_tree_depth']
            self.model = RandomForestRegressor(n_estimators=estimator_count, max_depth=max_tree_depth)
        elif self.type == 'svm':
            c_value = settings['c_value']
            epsilon_value = settings['epsilon_value']
            kernel = settings['kernel_type']
            if kernel == 'polynomial':
                degree = settings['polynomial_degree']
            else:
                degree = None
            self.model = SVR(kernel=kernel, C=c_value, epsilon=epsilon_value, degree=degree)
        else:
            raise Exception("Invalid model type")

    # Passes each row in the dataframe through the base model and returns a series of the results
    def process(self, input_values: pandas.DataFrame):
        outputs = self.model.predict(input_values[self.input_models + self.input_parameters])
        return pandas.Series(outputs)

    # Returns a dictionary of final_price, start_predict and end_predict values
    def predict(self, start_price, end_price, start_inputs, end_inputs, parent_predictions):
        start_parent_inputs = []
        end_parent_inputs = []
        for parent in self.input_models:
            start_parent_inputs.append(parent_predictions[parent]['start'])
            end_parent_inputs.append(parent_predictions[parent]['end'])
        start_prediction = self.model.predict(start_parent_inputs + start_inputs)
        end_prediction = self.model.predict(end_parent_inputs + end_inputs)
        final_price_predicition = start_price * (end_prediction / start_prediction)
        return {'start': start_prediction, 'end': end_prediction, 'final': final_price_predicition}

    # Takes in dataframe to train the base model
    def train(self, training_values):
        self.model.fit(training_values[self.input_models + self.input_parameters],
                       training_values[self.target_column_name])
