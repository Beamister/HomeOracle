############# Third Year Project ###############
#
#   Author: Luke Beamish
#   Date Created: 27/3/17
#   Last modified: 27/3/17
#
#   This class generates and runs the GUI
#   that users interact with
#
################################################

from tkinter import *
from tkinter import messagebox

class GUI:

    def __init__(self, master, models, dataSet):
        self. master = master
        self.models = models
        self.dataSet = dataSet
        self.trained = False
        self.currentSourceVar = StringVar(self.master)
        self.currentSourceVar.set("None")
        self.currentSource = "None"
        self.currentModelVar = StringVar(self.master)
        self.currentModelVar.set("None")
        self.currentModel = "None"
        self.modelList = list(models.keys())
        self.sourceList = dataSet.getSourceNames()
        self.frame = Frame(self.master)
        self.frame.pack()
        self.title = Label(self.frame, text = "Predict how your house price will change")
        self.title.grid(row = 0, column = 0, columnspan = 2)
        self.sourceSelect = OptionMenu(self.frame, self.currentSourceVar, self.sourceList, command = self.sourceSelect)
        self.sourceSelect.grid(row = 1, column = 0)
        self.modelSelect = OptionMenu(self.frame, self.currentModelVar, self.modelList, command = self.modelSelect)
        self.modelSelect.grid(row = 1, column = 1)
        self.trainButton = Button(self.frame, text = "Train", command = self.trainModel)
        self.trainButton.grid(row = 3, column = 0)
        self.predictButton = Button(self.frame, text = "Predict", command = self.queryModel)
        self.predictButton.grid(row = 3, column = 1)
        self.priceInputLabel = Label(self.frame, text="Input Price:")
        self.priceInputLabel.grid(row=4, column=0)
        self.priceOutputLabel = Label(self.frame, text = "Output Price:")
        self.priceOutputLabel.grid(row = 4, column = 1)
        self.priceInput = Entry(self.frame)
        self.priceInput.grid(row = 5, column =0)
        self.priceOutput = Entry(self.frame)
        self.priceOutput.grid(row=5, column=1)

    def modelSelect(self, selection):
        self.trained = False
        self.currentModel = selection[0]

    def trainModel(self):
        if(self.currentModel == "None"):
            messagebox.showerror("Error", "You have not yet selected the model")
        elif(self.currentSource == "None"):
            messagebox.showerror("Error", "You have not yet selected a data set")
        else:
            self.models[self.currentModel].trainModel(self.dataSet.getTrainingInputs(self.currentSource),
                                                      self.dataSet.getTrainingOutputs(self.currentSource))
            self.trained = True


    def queryModel(self):
        if(self.trained == True):
            inputValues = []
            for input in self.inputs:
                inputValues.append(input.get())
            inputValues.append(self.priceInput.get())
            result = self.models[self.currentModel].queryModel(inputValues)
            self.priceOutput.delete(0, 'end')
            self.priceOutput.insert(0, result)
        elif(self.currentModel == "None"):
            messagebox.showerror("Error", "You have not yet selected a model")
        elif(self.currentSource == "None"):
            messagebox.showerror("Error", "You have not yet selected a data set")
        else:
            messagebox.showerror("Error", "You have not yet trained the model")

    def sourceSelect(self, selection):
        self.currentSource = selection[0]
        if(hasattr(self, "variablesFrame")):
            self.variablesFrame.destroy()
        self.generateVariableFields(selection[0])

    def generateVariableFields(self, sourceName):
        self.variablesFrame = Frame(self.frame)
        self.variablesFrame.grid(row = 2, column = 0, columnspan = 2)
        variables = self.dataSet.getVariableNames(sourceName)
        self.inputs = []
        currentRow = 0
        for variable in variables:
            startVariableLabel = Label(self.variablesFrame, text = "Starting " + variable + " value")
            startVariableLabel.grid(row = currentRow, column = 0)
            startVariableInput = Entry(self.variablesFrame)
            startVariableInput.grid(row = currentRow, column = 1)
            endVariableLabel = Label(self.variablesFrame, text="Finishing " + variable + " value")
            endVariableLabel.grid(row=currentRow, column = 2)
            endVariableInput = Entry(self.variablesFrame)
            endVariableInput.grid(row = currentRow, column = 3)
            self.inputs.append(startVariableInput)
            self.inputs.append(endVariableInput)
            currentRow += 1