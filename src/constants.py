import os.path

dataDirectory = "Data"
defaultDataFile = "housing.csv"
dataDirectoryPath = os.path.join(os.path.split(__file__)[0], '..', dataDirectory)
defaultDataPath = os.path.join(dataDirectoryPath, defaultDataFile)
defaultDataFile = "housing.csv"
defaultDataHeaders = ["Crime", "Residential", "Industrial", "River Boundary", "Nitric Oxide",
                      "Rooms", "Pre 1940", "Employment distance", "Accessibility", "Tax",
                      "Education", "Black Population", "Lower Status", "Median Value"]

blue = '#0074D9'
orange = '#FF851B'