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


class GUI:

    def __init__(self, master, models, dataSet):
        self. master = master
        self.frame = Frame(self.master)
        self.frame.pack()
        self.title = Label(self.frame, text = "Predict how your house price will change")
        self.title.grid(row = 0, column = 0)