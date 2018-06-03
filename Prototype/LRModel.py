############# Third Year Project ###############
#
#   Author: Luke Beamish
#   Date Created: 26/3/17
#   Last modified: 27/3/17
#
#   This class generates and runs the linear
#   regression model for predicting changes
#
################################################

from sklearn import linear_model
from numpy import *

class LRModel:

    def __init__(self):
        self.model = linear_model.LinearRegression()


    def trainModel(self, trainingInputs, trainingOutputs):
        self.model.fit(array(trainingInputs), array(trainingOutputs))

    def queryModel(self, inputData):
        startInput = array(inputData[0:-1:2], ndmin = 2)
        endInput = array(inputData[1:-1:2], ndmin = 2)
        startPrice = inputData[-1]
        startPredict = float(self.model.predict(startInput)[0][0])
        endPredict = float(self.model.predict(endInput)[0][0])
        return startPrice * (endPredict / startPredict)
