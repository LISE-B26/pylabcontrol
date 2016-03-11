
from PyQt4.uic import loadUiType
Ui_MainWindow, QMainWindow = loadUiType('zi_control.ui') # with this we don't have to convert the .ui file into a python file!
# from qt_creator_gui.zi_control import Ui_MainWindow

from hardware_modules.instruments import Instrument_Dummy, Maestro_Controller, ZIHF2, Maestro_BeamBlock
from scripts.scripts import Script_Dummy

from PyQt4 import QtCore, QtGui

from qt_creator_gui.qt_gui_widgets import QTreeInstrument, QTreeScript, QTreeParameter
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

class ControlMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(ControlMainWindow, self).__init__()
        self.setupUi(self)

        def create_figures():
            # fill the empty widgets with a figure
            fig_live = Figure()
            self.canvas_live = FigureCanvas(fig_live)
            self.plot_data_live.addWidget(self.canvas_live)
            self.axes_live = fig_live.add_subplot(111)

            # fig_psd = Figure()
            # self.canvas_psd = FigureCanvas(fig_psd)
            # self.plot_data_psd.addWidget(self.canvas_psd)
            # self.axes_psd = fig_psd.add_subplot(111)
            # self.axes_psd.set_xlabel('frequency (Hz)')
        maestro = Maestro_Controller('maestro 6 channels')
        my_instruments = [
            Instrument_Dummy('inst dummy 1'),
            ZIHF2('ZiHF2',{'freq', 10.0}),
            Maestro_BeamBlock(maestro,'IR beam block')
        ]


        for elem in my_instruments:
            item = QTreeInstrument( self.tree_scripts, elem )

        my_scripts = [
            Script_Dummy('script dummy 1')
        ]

        for elem in my_scripts:
            item = QTreeScript( self.tree_scripts, elem )

        self.tree_scripts.setColumnWidth(0,200)

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    ex = ControlMainWindow()
    ex.show()
    sys.exit(app.exec_())