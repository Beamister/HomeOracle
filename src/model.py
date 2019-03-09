from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from constants import *
import pandas


class Model:
    # Does not include parameters input to parent models
    input_parameters = []
    input_models = []
    name = ''
    dataset = ''
    training_entry_count = MAX_TRAINING_ENTRIES
    type = ''
    target_column_name = ''

    def __init__(self, settings):
        print(settings)
        self.name = settings['name']
        self.input_parameters = settings['input_parameters']
        self.input_models = settings['input_models']
        self.dataset = settings['dataset']
        self.type = settings['type']
        self.training_entry_count = settings['max_training_examples']
        if self.dataset == 'boston_housing':
            self.target_column_name = DEFAULT_TARGET_HEADER
        else:
            self.target_column_name = CORE_TARGET_HEADER
        if self.type == 'decision_tree':
            estimator_count = settings['estimator_count']
            max_tree_depth = settings['max_tree_depth']
            self.model = RandomForestRegressor(n_estimators=estimator_count, max_depth=max_tree_depth)
        elif self.type == 'svm':
            self.scaler = StandardScaler()
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
        column_names = self.input_models + self.input_parameters
        model_values = input_values[column_names]
        # If using SVM then add scale DataFrame before making prediction
        if self.type == 'svm':
            # Set model output column to dummy zero value so DataFrame fits scaling
            model_values['output_column'] = 0
            model_values = self.scaler.transform(model_values)
            model_values = pandas.DataFrame(model_values, columns=column_names + ['output_column'])
        outputs = self.model.predict(model_values[self.input_models + self.input_parameters])
        outputs = pandas.Series(outputs)
        # If using SVM then inverse scaling
        if self.type == 'svm':
            model_values['output_column'] = outputs
            model_values = self.scaler.inverse_transform(model_values)
            model_values = pandas.DataFrame(model_values, columns=column_names + ['output_column'])
            outputs = model_values['output_column']
        return outputs

    # Returns a dictionary of final_price, start_predict and end_predict values
    def predict(self, start_price, start_inputs, end_inputs, parent_predictions):
        start_parent_inputs = []
        end_parent_inputs = []
        for parent in self.input_models:
            start_parent_inputs.append(parent_predictions[parent]['start'])
            end_parent_inputs.append(parent_predictions[parent]['end'])
        start_inputs = [start_inputs[parameter_name] for parameter_name in self.input_parameters]
        end_inputs = [end_inputs[parameter_name] for parameter_name in self.input_parameters]
        start_values = start_parent_inputs + start_inputs
        end_values = end_parent_inputs + end_inputs
        if self.type == 'svm':
            # Add dummy zero column to fit data to scaler
            scaled_values = self.scaler.transform([start_values + [0], end_values + [0]])
            start_values = scaled_values[0][:-1]
            end_values = scaled_values[1][:-1]
        start_prediction = self.model.predict([start_values])[0]
        end_prediction = self.model.predict([end_values])[0]
        if self.type == 'svm':
            # Add dummy zero column to fit data to scaler
            scaled_values = self.scaler.inverse_transform([start_values + [start_prediction],
                                                           end_values + [end_prediction]])
            start_prediction = scaled_values[0][-1]
            end_prediction = scaled_values[1][-1]
        final_price_prediction = start_price * (end_prediction / start_prediction)
        return {
            'start': start_prediction,
            'end': end_prediction,
            'final': final_price_prediction
        }

    # Takes in dataframe to train the base model
    def train(self, training_values):
        if self.type == 'svm':
            column_names = self.input_models + self.input_parameters + [self.target_column_name]
            training_values = self.scaler.fit_transform(training_values[column_names])
            training_values = pandas.DataFrame(training_values, columns=column_names)
        self.model.fit(training_values[self.input_models + self.input_parameters],
                       training_values[self.target_column_name])
