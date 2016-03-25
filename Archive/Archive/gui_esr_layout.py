__author__ = 'Experiment'
from PyQt4 import QtGui

from src.gui_old import gui_custom_widgets as gui_cw


def add_esr_layout(self):
    self.esrPlot = gui_cw.MyMplCanvas(self.main_widget, width=5, height=4, dpi=100)
    self.rfPower = QtGui.QLineEdit(self.main_widget)
    self.rfPowerL = QtGui.QLabel(self.main_widget)
    self.rfPowerL.setText("Rf Power (dBm):")
    self.freqMin = QtGui.QLineEdit(self.main_widget)
    self.freqMinL = QtGui.QLabel(self.main_widget)
    self.freqMinL.setText("Minimum Frequency (Hz)")
    self.freqMax = QtGui.QLineEdit(self.main_widget)
    self.freqMaxL = QtGui.QLabel(self.main_widget)
    self.freqMaxL.setText("Maximum Frequency (Hz)")
    self.numPtsESR = QtGui.QLineEdit(self.main_widget)
    self.numPtsESRL = QtGui.QLabel(self.main_widget)
    self.numPtsESRL.setText("Num Points")
    self.buttonStartESR = QtGui.QPushButton('Start ESR',self.main_widget)
    self.buttonStartESR.clicked.connect(self.StartESRBtnClicked)
    self.buttonStopESR = QtGui.QPushButton('Stop ESR',self.main_widget)
    self.buttonStopESR.clicked.connect(self.StopESRBtnClicked)

    self.esrLayout = QtGui.QGridLayout()
    self.esrLayout.addWidget(self.rfPower,1,1)
    self.esrLayout.addWidget(self.rfPowerL,1,2)
    self.esrLayout.addWidget(self.freqMin,2,1)
    self.esrLayout.addWidget(self.freqMinL,2,2)
    self.esrLayout.addWidget(self.freqMax,3,1)
    self.esrLayout.addWidget(self.freqMaxL,3,2)
    self.esrLayout.addWidget(self.numPtsESR,4,1)
    self.esrLayout.addWidget(self.numPtsESRL,4,2)
    self.esrLayout.addWidget(self.buttonStartESR,5,1)
    self.esrLayout.addWidget(self.buttonStopCounter,5,2)
    self.vbox.addLayout(self.esrLayout)
    self.plotBox.addWidget(self.esrPlot)
    self.esrQueue = Queue.Queue()