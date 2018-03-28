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

import numpy

class DataSet:

    def __init__(self, sources):
        self.data = {}
        for key in sources:
            self.loadDataSet(key, sources[key][0])
        self.sources = sources

    def loadDataSet(self, sourceName, sourceFile):
        dataSet = []
        rowNumber = 0
        with open(sourceFile, "r", encoding = "utf8") as file:
            for line in file:
                line.strip()
                currentRow = line.split(" ")
                currentRow = [i for i in currentRow if i != ""]
                list(map(float, currentRow))
                dataSet.append(currentRow)
        self.data[sourceName] = dataSet

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
            if not(i in ignoredColumns or i == targetColumn):
                variables.append(columns[i])
        return variables

    def getTrainingOutputs(self, source):
        dataSet = numpy.array(self.data[source]).transpose().tolist()
        trainingOutputs = []
        for outputColumn in self.sources[source][1]:
            trainingOutputs.append(dataSet[outputColumn])
        return trainingOutputs

    def getTrainingInputs(self, source):
        ignoredColumns = self.sources[source][2]
        targetColumn = self.sources[source][1]
        columnCount = len(self.data[source][0])
        desiredColumns = [i for i in range(columnCount)
                          if not(i in ignoredColumns or i == targetColumn)]
        trainingInputs = []
        #Get data and transpose it
        dataSet = numpy.array(self.data[source]).transpose().tolist()
        for i in desiredColumns:
            trainingInputs.append(dataSet[i])
        return trainingInputs


    #Returns the data associated with the given source
    def __getitem__(self, item):
        return self.data[item]

    #Returns the number of data sources
    def __len__(self):
        return len(self.sources)