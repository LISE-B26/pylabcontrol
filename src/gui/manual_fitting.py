from PyQt4 import QtGui, QtCore
from PyQt4.uic import loadUiType
from PyLabControl.src.core import Parameter, Instrument, Script, ReadProbes, Probe, ScriptIterator
from PyLabControl.src.gui import B26QTreeItem, LoadDialog, LoadDialogProbes
from PyLabControl.src.scripts.select_points import SelectPoints
from PyLabControl.src.core.read_write_functions import load_b26_file

import os.path
import numpy as np
import json as json
from PyQt4.QtCore import QThread, pyqtSignal, QObject

from matplotlib.backends.backend_qt4agg import (NavigationToolbar2QT as NavigationToolbar)
from qt_b26_gui import MatplotlibWidget
import sys
import glob
import time
import Queue
import scipy.optimize
import pandas as pd

Ui_MainWindow, QMainWindow = loadUiType('manual_fitting_window.ui') # with this we don't have to convert the .ui file into a python file!

class FittingWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        def create_figures():
            self.matplotlibwidget = MatplotlibWidget(self.plot)
            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.matplotlibwidget.sizePolicy().hasHeightForWidth())
            self.matplotlibwidget.setSizePolicy(sizePolicy)
            self.matplotlibwidget.setMinimumSize(QtCore.QSize(200, 200))
            self.matplotlibwidget.setObjectName(QtCore.QString.fromUtf8("matplotlibwidget"))
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

    def plot_clicked(self, mouse_event):
        if type(self.peak_vals) is list:
            self.peak_vals.append([mouse_event.xdata, mouse_event.ydata])
            axes = self.matplotlibwidget.axes
            # can't use patches, as they use data coordinates for radius but this is a high aspect ratio plot so the
            # circle was extremely stretched
            axes.plot(mouse_event.xdata, mouse_event.ydata, 'ro', markersize = 5)

            # axes.text(mouse_event.xdata, mouse_event.ydata, '{:d}'.format(len(self.peak_vals[-1])),
            #                  horizontalalignment='center',
            #                  verticalalignment='center',
            #                  color='black'
            #                  )
            self.matplotlibwidget.draw()

    class do_fit(QObject):
        finished = pyqtSignal()  # signals the end of the script
        status = pyqtSignal(str) # sends messages to update the statusbar

        def __init__(self, filepath, plotwidget, queue, peak_vals, peak_locs):
            QObject.__init__(self)
            self.filepath = filepath
            self.plotwidget = plotwidget
            self.queue = queue
            self.peak_vals = peak_vals
            self.peak_locs = peak_locs

        def n_lorentzian(self, x, offset, *peak_params):
            value = 0
            width_array = peak_params[:len(peak_params)/3]
            amplitude_array = peak_params[len(peak_params)/3:2*len(peak_params)/3]
            center_array = peak_params[2*len(peak_params)/3:]
            for width, amplitude, center in zip(width_array, amplitude_array, center_array):
                value += amplitude * np.square(0.5 * width) / (np.square(x - center) + np.square(0.5 * width))
            value += offset
            return value

                # return np.sum((-1/ ((x - center_array[0]) ** 2 + (.5 * width) ** 2))) + offset
            # return np.sum((-(np.array(amplitude_array) * (.5 * width) ** 2) / ((x - np.array(center_array)) ** 2 + (.5 * width) ** 2))) + offset

        def fit_n_lorentzian(self, x, y, fit_start_params=None):
            popt, _ = scipy.optimize.curve_fit(self.n_lorentzian, x, y, fit_start_params)
            return popt

        def save(self):
            save_path = os.path.join(self.filepath, 'data-manual.csv')
            df = pd.DataFrame(self.fits)
            df.to_csv(save_path)

        def run(self):
            esr_folders = glob.glob(os.path.join(self.filepath, './data_subscripts/*esr*'))

            data_array = []
            self.status.emit('loading data')
            for esr_folder in esr_folders[:-1]:
                data = Script.load_data(esr_folder)
                data_array.append(data)

            self.fits = [[]] * len(data_array)

            self.status.emit('executing manual fitting')
            index = 0
            # for data in data_array:
            while index < len(data_array):
                data = data_array[index]
                #this must be after the draw command, otherwise plot doesn't display for some reason
                self.status.emit('executing manual fitting NV #' + str(index))
                self.plotwidget.axes.clear()
                self.plotwidget.axes.plot(data['frequency'], data['data'])
                self.plotwidget.draw()

                while(True):
                    if self.queue.empty():
                        time.sleep(.5)
                    else:
                        value = self.queue.get()
                        if value == 'next':
                            while not self.peak_vals == []:
                                self.peak_vals.pop(-1)
                            if len(self.single_fit) == 1:
                                self.fits[index] = self.single_fit
                            else:
                                self.fits[index] = [y for x in self.single_fit for y in x]
                            index += 1
                            self.status.emit('saving')
                            self.save()
                            break
                        elif value == 'clear':
                            self.plotwidget.axes.clear()
                            self.plotwidget.axes.plot(data['frequency'], data['data'])
                            self.plotwidget.draw()
                        elif value == 'fit':
                            if len(self.peak_vals) > 1:
                                centers, heights = zip(*self.peak_vals)
                                widths = 1e7 * np.ones(len(heights))
                            elif len(self.peak_vals) == 1:
                                centers, heights = self.peak_vals[0]
                                widths = 1e7
                            elif len(self.peak_vals) == 0:
                                self.single_fit = [np.mean(data['data'])]
                                self.peak_locs.setText('No Peak')
                                self.plotwidget.axes.plot(data['frequency'],np.repeat(np.mean(data['data']), len(data['frequency'])))
                                self.plotwidget.draw()
                                continue
                            offset = np.mean(data['data'])
                            amplitudes = offset-np.array(heights)
                            if len(self.peak_vals) > 1:
                                fit_start_params = [[offset], np.concatenate((widths, amplitudes, centers))]
                                fit_start_params = [y for x in fit_start_params for y in x]
                            elif len(self.peak_vals) == 1:
                                fit_start_params = [offset, widths, amplitudes, centers]
                            try:
                                popt = self.fit_n_lorentzian(data['frequency'], data['data'], fit_start_params = fit_start_params)
                            except RuntimeError:
                                print('fit failed, optimal parameters not found')
                                break
                            self.plotwidget.axes.plot(data['frequency'], self.n_lorentzian(data['frequency'], *popt))
                            self.plotwidget.draw()
                            params = popt[1:]
                            widths_array = params[:len(params)/3]
                            amplitude_array = params[len(params)/3: 2 * len(params) / 3]
                            center_array = params[2 * len(params) / 3:]
                            positions = zip(center_array, amplitude_array, widths_array)
                            self.single_fit = [[popt[0]], positions]
                            self.peak_locs.setText('Peak Positions: ' + str(center_array))
                        elif type(value) is int:
                            index = int(value)
                            break

            self.finished.emit()
            self.status.emit('saving finished')

    def update_status(self, str):
        self.statusbar.showMessage(str)

    def start_fitting(self):
        self.queue = Queue.Queue()
        self.peak_vals = []
        self.fit_thread = QThread() #must be assigned as an instance variable, not local, as otherwise thread is garbage
                                    #collected immediately at the end of the function before it runs
        self.fitobj = self.do_fit(str(self.data_filepath.text()), self.matplotlibwidget, self.queue, self.peak_vals, self.peak_locs)
        self.fitobj.moveToThread(self.fit_thread)
        self.fit_thread.started.connect(self.fitobj.run)
        self.fitobj.finished.connect(self.fit_thread.quit)  # clean up. quit thread after script is finished
        self.fitobj.status.connect(self.update_status)
        self.fit_thread.start()

    def open_file_dialog(self):
        """
        opens a file dialog to get the path to a file and
        """
        dialog = QtGui.QFileDialog
        filename = dialog.getExistingDirectory(self, 'Select a file:', self.data_filepath.text())
        if str(filename)!='':
            self.data_filepath.setText(filename)


app = QtGui.QApplication(sys.argv)
ex = FittingWindow()
ex.show()
ex.raise_()
sys.exit(app.exec_())
