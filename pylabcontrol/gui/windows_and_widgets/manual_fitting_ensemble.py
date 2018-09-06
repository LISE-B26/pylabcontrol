from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.uic import loadUiType
from pylabcontrol.core import Script

import os.path
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QObject

from matplotlib.backends.backend_qt4agg import (NavigationToolbar2QT as NavigationToolbar)
from gui.windows_and_widgets.main_window import MatplotlibWidget
import sys
import glob
import time
import queue
import pandas as pd
from scipy.interpolate import UnivariateSpline

try:
    ui_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'ui_files', 'manual_fitting_window_ensemble.ui'))
    Ui_MainWindow, QMainWindow = loadUiType(ui_file_path) # with this we don't have to convert the .ui file into a python file!
except (ImportError, IOError):
    from PyQt5.QtWidgets import QMainWindow
    from PyQt5.QtWidgets import QDialog
    print('Warning: on the fly conversion of load_dialog.ui file failed, can not continue!!\n')

class FittingWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        def create_figures():
            self.matplotlibwidget = MatplotlibWidget(self.plot)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.matplotlibwidget.sizePolicy().hasHeightForWidth())
            self.matplotlibwidget.setSizePolicy(sizePolicy)
            self.matplotlibwidget.setMinimumSize(QtCore.QSize(200, 200))
            # self.matplotlibwidget.setObjectName(QtCore.QString.fromUtf8("matplotlibwidget"))
            self.horizontalLayout_3.addWidget(self.matplotlibwidget)
            self.mpl_toolbar = NavigationToolbar(self.matplotlibwidget.canvas, self.toolbar_space)
            self.horizontalLayout_2.addWidget(self.mpl_toolbar)
            self.peak_vals = None

        def setup_connections():
            self.btn_fit.clicked.connect(self.btn_clicked)
            self.btn_clear.clicked.connect(self.btn_clicked)
            self.btn_next.clicked.connect(self.btn_clicked)
            self.matplotlibwidget.mpl_connect('button_press_event', self.plot_clicked)
            self.btn_open.clicked.connect(self.open_file_dialog)
            self.btn_run.clicked.connect(self.btn_clicked)
            self.btn_goto.clicked.connect(self.btn_clicked)
            self.btn_prev.clicked.connect(self.btn_clicked)
            self.btn_skip.clicked.connect(self.btn_clicked)

        create_figures()
        setup_connections()

    def btn_clicked(self):
        sender = self.sender()
        if sender is self.btn_run:
            self.start_fitting()
        elif sender is self.btn_next:
            self.queue.put('next')
        elif sender is self.btn_fit:
            self.queue.put('fit')
        elif sender is self.btn_clear:
            while not self.peak_vals == []:
                self.peak_vals.pop(-1)
            self.queue.put('clear')
        elif sender is self.btn_goto:
            self.queue.put(int(self.input_next.text()))
        elif sender is self.btn_prev:
            self.queue.put('prev')
        elif sender is self.btn_skip:
            self.queue.put('skip')

    def plot_clicked(self, mouse_event):
        if type(self.peak_vals) is list:
            self.peak_vals.append([mouse_event.xdata, mouse_event.ydata])
            axes = self.matplotlibwidget.axes
            # can't use patches, as they use data coordinates for radius but this is a high aspect ratio plot so the
            # circle was extremely stretched
            axes.plot(mouse_event.xdata, mouse_event.ydata, 'ro', markersize = 5)
            self.matplotlibwidget.draw()

    class do_fit(QObject):
        finished = pyqtSignal()  # signals the end of the script
        status = pyqtSignal(str) # sends messages to update the statusbar
        NUM_ESR_LINES = 8

        def __init__(self, filepath, plotwidget, queue, peak_vals, interps):
            QObject.__init__(self)
            self.filepath = filepath
            self.plotwidget = plotwidget
            self.queue = queue
            self.peak_vals = peak_vals
            self.interps = interps


        def save(self):
            def freqs(index):
                return self.frequencies[0] + (self.frequencies[-1]-self.frequencies[0])/(len(self.frequencies)-1)*index
            save_path = os.path.join(self.filepath, 'line_data.csv')
            data = list()
            for i in range(0, self.NUM_ESR_LINES):
                data.append(list())
            for i in range(0, self.NUM_ESR_LINES):
                indices = self.interps[i](self.x_range)
                data[i] = [freqs(indices[j]) for j in range(0,len(self.x_range))]

            df = pd.DataFrame(data)
            df = df.transpose()
            df.to_csv(save_path)
            self.plotwidget.figure.savefig(self.filepath + './lines.jpg')

        def run(self):
            data_esr = []
            for f in sorted(glob.glob(os.path.join(self.filepath, './data_subscripts/*'))):
                data = Script.load_data(f)
                data_esr.append(data['data'])
            self.frequencies = data['frequency']

            data_esr_norm = []
            for d in data_esr:
                data_esr_norm.append(d / np.mean(d))

            self.x_range = list(range(0, len(data_esr_norm)))

            self.status.emit('executing manual fitting')
            index = 0
            # for data in data_array:
            while index < self.NUM_ESR_LINES:
                #this must be after the draw command, otherwise plot doesn't display for some reason
                self.status.emit('executing manual fitting NV #' + str(index))
                self.plotwidget.axes.clear()
                self.plotwidget.axes.imshow(data_esr_norm, aspect = 'auto', origin = 'lower')
                if self.interps:
                    for f in self.interps:
                        self.plotwidget.axes.plot(f(self.x_range), self.x_range)

                self.plotwidget.draw()

                while(True):
                    if self.queue.empty():
                        time.sleep(.5)
                    else:
                        value = self.queue.get()
                        if value == 'next':
                            while not self.peak_vals == []:
                                self.peak_vals.pop(-1)
                            # if len(self.single_fit) == 1:
                            #     self.fits[index] = self.single_fit
                            # else:
                            #     self.fits[index] = [y for x in self.single_fit for y in x]
                            index += 1
                            self.interps.append(f)
                            break
                        elif value == 'clear':
                            self.plotwidget.axes.clear()
                            self.plotwidget.axes.imshow(data_esr_norm, aspect='auto', origin = 'lower')
                            if self.interps:
                                for f in self.interps:
                                    self.plotwidget.axes.plot(f(self.x_range), self.x_range)
                            self.plotwidget.draw()
                        elif value == 'fit':
                            peak_vals = sorted(self.peak_vals, key = lambda tup: tup[1])
                            y,x = list(zip(*peak_vals))
                            f = UnivariateSpline(np.array(x),np.array(y))
                            x_range = list(range(0,len(data_esr_norm)))
                            self.plotwidget.axes.plot(f(x_range), x_range)
                            self.plotwidget.draw()
                        elif value == 'prev':
                            index -= 1
                            break
                        elif value == 'skip':
                            index += 1
                            break
                        elif type(value) is int:
                            index = int(value)
                            break

            self.finished.emit()
            self.status.emit('saving')
            self.plotwidget.axes.clear()
            self.plotwidget.axes.imshow(data_esr_norm, aspect='auto', origin = 'lower')
            if self.interps:
                for f in self.interps:
                    self.plotwidget.axes.plot(f(self.x_range), self.x_range)
            self.save()
            self.status.emit('saving finished')

    def update_status(self, str):
        self.statusbar.showMessage(str)

    def start_fitting(self):
        self.queue = queue.Queue()
        self.peak_vals = []
        self.interps = []
        self.fit_thread = QThread() #must be assigned as an instance variable, not local, as otherwise thread is garbage
                                    #collected immediately at the end of the function before it runs
        self.fitobj = self.do_fit(str(self.data_filepath.text()), self.matplotlibwidget, self.queue, self.peak_vals, self.interps)
        self.fitobj.moveToThread(self.fit_thread)
        self.fit_thread.started.connect(self.fitobj.run)
        self.fitobj.finished.connect(self.fit_thread.quit)  # clean up. quit thread after script is finished
        self.fitobj.status.connect(self.update_status)
        self.fit_thread.start()

    def open_file_dialog(self):
        """
        opens a file dialog to get the path to a file and
        """
        dialog = QtWidgets.QFileDialog
        filename = dialog.getExistingDirectory(self, 'Select a file:', self.data_filepath.text())
        if str(filename)!='':
            self.data_filepath.setText(filename)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = FittingWindow()
    ex.show()
    ex.raise_()
    sys.exit(app.exec_())