

class Model:

    # Does not include parameters input to parent models
    input_parameters = []
    input_models = []
    name = ''
    dataset = ''
    training_entry_count = 0

    # TODO
    def __init__(self, settings):
        self.input_parameters = settings['input_parameters']
        self.input_models = settings['input_models']

    # TODO - Passes each row in the dataframe through the base model and returns a series of the results
    def process(self, input_values):
        return 1

    # TODO - Returns a dictionary of final_price, start_predict and end_predict values
    def predict(self, start_price, end_price, start_inputs, end_inputs, parent_predictions):
        return 100

    # TODO - Takes in dataframe to train the base model
    def train(self, input_values):
        pass
