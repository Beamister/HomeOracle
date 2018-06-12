import os.path

dataDirectory = "Data"
defaultDataFile = "housing.csv"
dataDirectoryPath = os.path.join(os.path.split(__file__)[0], '..', dataDirectory)
defaultDataPath = os.path.join(dataDirectoryPath, defaultDataFile)
defaultDataFile = "housing.csv"
defaultDataHeaders = ["Crime", "Residential", "Industrial", "River Boundary", "Nitric Oxide",
                      "Rooms", "Pre 1940", "Employment distance", "Accessibility", "Tax",
                      "Education", "Black Population", "Lower Status", "Median Value"]

default3DCamera =  {'up': {'x': 0, 'y': 0, 'z': 1},
                    'center': {'x': 0, 'y': 0, 'z': 0},
                    'eye': {'x': 1, 'y': -2, 'z': 0.25}}

blue = '#0074D9'
orange = '#FF851B'