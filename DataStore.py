############# Third Year Project ###############
#
#   Author: Luke Beamish
#   Date Created: 27/3/17
#   Last modified: 27/3/17
#
#   This class loads and stores the raw data
#   from the given sources
#
################################################

from numpy import *

class DataStore:

    def __init__(self, sources):
        self.data = {}
        for key in sources:
            self.loadDataSet(key, sources[key][0])
        self.sources = sources

    def loadDataSet(self, sourceName, sourceFile):
        dataSet = []
        with open(sourceFile, "r", encoding = "utf8") as file:
            for line in file:
                line.strip()
                currentRow = line.split(" ")
                currentRow = [float(i) for i in currentRow if i != ""]
                list(map(float, currentRow))
                dataSet.append(currentRow)
        self.data[sourceName] = array(dataSet)

    def getSourceNames(self):
        names = []
        for name in self.sources:
            names.append(name)
        return names

    def getVariableNames(self, source):
        variables = []
        #The list of column names is the 4th set attribute
        columns = self.sources[source][3]
        ignoredColumns = self.sources[source][2]
        targetColumn = self.sources[source][1]
        for i in range(len(columns)):
            if not(i in ignoredColumns or i in targetColumn):
                variables.append(columns[i])
        return variables

    #Returns an array of shape[n samples][n values]
    def getTrainingOutputs(self, source):
        dataSet = self.data[source]
        targetColumns = self.sources[source][1]
        return dataSet[:, targetColumns]

    def getTrainingInputs(self, source):
        ignoredColumns = self.sources[source][2]
        targetColumns = self.sources[source][1]
        columnCount = len(self.data[source][0])
        desiredColumns = [i for i in range(columnCount)
                          if not(i in ignoredColumns or i in targetColumns)]
        dataSet = self.data[source]
        return dataSet[:, desiredColumns]


    #Returns the data associated with the given source
    def __getitem__(self, item):
        return self.data[item]

    #Returns the number of data sources
    def __len__(self):
        return len(self.sources)