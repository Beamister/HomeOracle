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
from tkinter import messagebox

from DataSet import DataSet
from GUI import GUI
from LRModel import LRModel
from tkinter import *

#Dictionary of data sources, key is user name, value is a list of attributes,
#attributes - filename, target column index, columns to ignore, column names
dataSources = {"Boston":["Filename", 13, [11],
                         ["Crime", "Residential", "Industrial", "River Boundary", "Nitric Oxide",
                          "Rooms", "Pre 1940", "Employment distance", "Accessibility", "Tax",
                          "Education", "Blacks", "Lower Status", "Median Value"]]}
dataSet = DataSet(dataSources)
linearRegressionModel = LRModel()
models = {"LRModel" : linearRegressionModel}
root = Tk()
root.wm_title("House Price Impact Calculator")
gui = GUI(root, models, dataSet)
root.mainloop()