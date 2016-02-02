"""
Created on Feb 2 2016

@author: Jan Gieseler

# this file creates the gui
# gui is designed with QT Designer that creates a .ui file (e.g. mainwindow.ui)
# use the batch (pyside-uic.bat) file that contains C:\Anaconda\python.exe C:\Anaconda\Lib\site-packages\PySide\scripts\uic.py %*
# to convert .ui file into .py file (e.g. mainwindow.py) by executing pyside-uic mainwindow.ui -o mainwindow.py
# import the .py file (e.g.  mainwindow.py)
"""

from qt_creator_gui.mainwindow import Ui_MainWindow
import sys
from PySide import QtCore, QtGui
import hardware_modules.maestro as maestro




# ============= GENERAL SETTING ====================================
# ==================================================================
settings = {
    "serial_port_maestro" : "COM5",
    "channel_beam_block_IR" : 4
}


# ============= CLASS FOR THE MAIN GUI =============================
# ==================================================================
class ControlMainWindow(QtGui.QMainWindow):
    def __init__(self, settings, parent=None):
        super(ControlMainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # link buttons to functions
        self.ui.buttonRecordData.clicked.connect(lambda: self.record_data())

        # link checkboxes to functions
        self.ui.checkIRon.stateChanged.connect(lambda: self.switch_IR())
        self.ui.checkPIActive.stateChanged.connect(lambda: self.switch_PI_loop())

        self.settings = settings
        self._servo = maestro.Controller(self.settings['serial_port_maestro'])
        self.beam_block_IR = maestro.BeamBlock(self._servo, self.settings['channel_beam_block_IR'])


    def record_data(self):
        '''
        Changes script to be executed based on current text in box
        :param ApplicationWindow:
        '''
        self.ui.statusbar.showMessage("Record Data",1000)

    def switch_IR(self):
        '''
        Changes script to be executed based on current text in box
        :param ApplicationWindow:
        '''


        status_IR = self.ui.checkIRon.isChecked()

        if status_IR:
            self.beam_block_IR.open()
        else:
            self.beam_block_IR.block()

        self.ui.statusbar.showMessage("IR laser {:s}".format(str(status_IR)),1000)

    def switch_PI_loop(self):
        '''
        Changes script to be executed based on current text in box
        :param ApplicationWindow:
        '''

        status_PI_loop =self.ui.checkPIActive.isChecked()
        print(status_PI_loop)
        self.ui.statusbar.showMessage("IR laser  {:s}".format(str(status_PI_loop)),1000)


# ============= RUN GUI ============================================
# ==================================================================
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mySW = ControlMainWindow(settings)
    mySW.show()
    sys.exit(app.exec_())
