############# Third Year Project ###############
#
#   Author: Luke Beamish
#   Date Created: 26/3/17
#   Last modified: 26/3/17
#
#   This is the main file for running my third
#   year project, aiming to predict how house
#   prices change in response to changes in
#   their local area.
#
################################################

from prototype.dataStore import DataStore
from prototype.GUI import GUI
from prototype.LRModel import LRModel
from tkinter import *

#Dictionary of data sources, key is user name, value is a list of attributes,
#attributes - filename, output column indices, columns to ignore, column names
dataSources = {"Boston":["../Data/housing.csv", [13], [11],
                         ["Crime", "Residential", "Industrial", "River Boundary", "Nitric Oxide",
                          "Rooms", "Pre 1940", "Employment distance", "Accessibility", "Tax",
                          "Education", "Black Population", "Lower Status", "Median Value"]]}
dataStore = DataStore(dataSources)
linearRegressionModel = LRModel()
models = {"LRModel" : linearRegressionModel}
root = Tk()
root.wm_title("House Price Impact Calculator")
gui = GUI(root, models, dataStore)
root.mainloop()
