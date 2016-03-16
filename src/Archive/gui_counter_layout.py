__author__ = 'Experiment'
from PyQt4 import QtGui




def add_counter_layout(self):
    self.counterPlot = MyMplCanvas(self.main_widget, width=5, height=4, dpi=100)
    self.buttonStartCounter = QtGui.QPushButton('Start Counter',self.main_widget)
    self.buttonStartCounter.clicked.connect(self.StartCounterBtnClicked)
    self.buttonStopCounter = QtGui.QPushButton('Stop Counter',self.main_widget)
    self.buttonStopCounter.clicked.connect(self.StopCounterBtnClicked)
    self.counterLayout = QtGui.QGridLayout()
    self.counterLayout.addWidget(self.buttonStartCounter,1,1)
    self.counterLayout.addWidget(self.buttonStopCounter,1,2)
    self.vbox.addLayout(self.counterLayout)
    self.plotBox.addWidget(self.counterPlot)
    self.counterQueue = Queue.Queue()
