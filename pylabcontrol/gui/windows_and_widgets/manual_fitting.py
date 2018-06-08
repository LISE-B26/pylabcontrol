from PyQt5 import QtGui, QtCore
from PyQt5.uic import loadUiType
from pylabcontrol.core import Script

import os.path
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QObject

from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from pylabcontrol.gui.windows_and_widgets import MatplotlibWidget
import sys
import glob
import time
import queue
import scipy.optimize
import pandas as pd

try:
    ui_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'ui_files', 'manual_fitting_window.ui'))
    Ui_MainWindow, QMainWindow = loadUiType(ui_file_path) # with this we don't have to convert the .ui file into a python file!
except (ImportError, IOError):
    from PyQt5.QtWidgets import QMainWindow
    from PyQt5.QtWidgets import QDialog
    print('Warning: on the fly conversion of load_dialog.ui file failed, loaded .py file instead!!\n')



class FittingWindow(QMainWindow, Ui_MainWindow):
    """
    Class defining main gui window for doing manual fitting

    QMainWindow: Qt object returned from loadUiType
    UI_MainWindow: Ui reference returned from loadUiType
    """
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        def create_figures():
            """
            Sets up figures in GUI
            """
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
            """
            Sets up all connections between buttons and plots in the gui, and their corresponding backend functions
            """
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
        """
        Adds the appropriate value to the queue used for communication with the fitting routine thread when a given
        button is clicked.
        """
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
        """
        When a click is registered on the plot, appends the click location to self.peak_vals and plots a red dot in the
        click location
        :param mouse_event: a mouse event object for the click
        """
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
        """
        This class does all of the work of the manual fitting, including loading and saving data, processing input, and
        displaying output to the plots. It is implemented as a separate class so that it can be easily moved to a second
        thread. If it is on the same thread as the gui, you can't both run this code and still interact with the gui.
        Thus, the second thread allows both to occur simultaneously.
        """
        finished = pyqtSignal()  # signals the end of the script
        status = pyqtSignal(str) # sends messages to update the statusbar

        def __init__(self, filepath, plotwidget, queue, peak_vals, peak_locs):
            """
            Initializes the fit class
            :param filepath: path to file containing the ESR data to fit
            :param plotwidget: reference to plotwidget passed from gui
            :param queue: thread-safe queue used for gui-class communication across threads
            :param peak_vals: peak locations manually selected in gui
            :param peak_locs: pointer to textbox that will contain locations of fit peaks
            """
            QObject.__init__(self)
            self.filepath = filepath
            self.plotwidget = plotwidget
            self.queue = queue
            self.peak_vals = peak_vals
            self.peak_locs = peak_locs

        def n_lorentzian(self, x, offset, *peak_params):
            """
            Defines a lorentzian with n peaks
            :param x: independent variable
            :param offset: offset of lorentzians
            :param peak_params: this is a flattened array of length 3n with the format [widths amplitudes centers], that
                                is the first n values are the n peak widths, the next n are the n amplitudes, and the
                                last n are the n centers
            :return: the output of the lorentzian for each input value x
            """
            value = 0
            width_array = peak_params[:len(peak_params)/3]
            amplitude_array = peak_params[len(peak_params)/3:2*len(peak_params)/3]
            center_array = peak_params[2*len(peak_params)/3:]
            for width, amplitude, center in zip(width_array, amplitude_array, center_array):
                value += amplitude * np.square(0.5 * width) / (np.square(x - center) + np.square(0.5 * width))
            value += offset
            return value

        def fit_n_lorentzian(self, x, y, fit_start_params=None):
            """
            uses scipy.optimize.curve_fit to fit an n-peak lorentzian to the data, where the number of peaks is
            determined by the number of peaks given as starting parameters for the fit
            :param x:
            :param y:
            :param fit_start_params: this is a flattened array of length 3n + 1 with the format
                                [offset widths amplitudes centers], that is the first value is hte offset, the next n
                                values are the n peak widths, the next n are the n amplitudes, and the last n are the n
                                centers
            :return: optimized fit values, in the same format as fit_start_params
            """
            popt, _ = scipy.optimize.curve_fit(self.n_lorentzian, x, y, fit_start_params)
            return popt

        def save(self):
            """
            Saves the fit data to the data filepath + 'data-manual.csv'. The saving format has one line corresponding to
            each peak, with the corresponding nv number, fit center, width, and amplitude, and manual center and
            amplitude included
            """
            save_path = os.path.join(self.filepath, 'data-manual.csv')
            self.fits.to_csv(save_path, index = False)

        def load_fitdata(self):
            """
            Tries to load and return the previous results of save, or if this file has not been previously analyzed,
            returns a DataFrame with the correct headers and no data
            :return: the loaded (or new) pandas DataFrame
            """
            load_path = os.path.join(self.filepath, 'data-manual.csv')
            if os.path.exists(load_path):
                fits = pd.read_csv(load_path)
            else:
                fits = pd.DataFrame({'nv_id': [], 'peak_id': [], 'offset': [], 'fit_center': [], 'fit_amplitude': [],
                        'fit_width': [], 'manual_center': [], 'manual_height': []})
            return fits

        def run(self):
            """
            Code to run fitting routine. Should be run in a separate thread from the gui.
            """
            esr_folders = glob.glob(os.path.join(self.filepath, './data_subscripts/*esr*'))

            data_array = []
            self.status.emit('loading data')
            for esr_folder in esr_folders[:-1]:
                data = Script.load_data(esr_folder)
                data_array.append(data)

            self.fits = self.load_fitdata()

            self.status.emit('executing manual fitting')
            index = 0
            self.last_good = []
            self.initial_fit = False
            # for data in data_array:
            while index < len(data_array):
                data = data_array[index]
                #this must be after the draw command, otherwise plot doesn't display for some reason
                self.status.emit('executing manual fitting NV #' + str(index))
                self.plotwidget.axes.clear()
                self.plotwidget.axes.plot(data['frequency'], data['data'])
                if index in self.fits['nv_id'].values:
                    fitdf = self.fits.loc[(self.fits['nv_id'] == index)]
                    offset = fitdf['offset'].as_matrix()[0]
                    centers = fitdf['fit_center'].as_matrix()
                    amplitudes = fitdf['fit_amplitude'].as_matrix()
                    widths = fitdf['fit_width'].as_matrix()
                    fit_params = np.concatenate((np.concatenate((widths, amplitudes)), centers))
                    self.plotwidget.axes.plot(data['frequency'], self.n_lorentzian(data['frequency'], *np.concatenate(([offset], fit_params))))
                self.plotwidget.draw()

                if not self.last_good == []:
                    self.initial_fit = True
                    self.queue.put('fit')

                while(True):
                    if self.queue.empty():
                        time.sleep(.5)
                    else:
                        value = self.queue.get()
                        if value == 'next':
                            while not self.peak_vals == []:
                                self.last_good.append(self.peak_vals.pop(-1))
                            if self.single_fit:
                                to_delete = np.where(self.fits['nv_id'].values == index)
                                # print(self.fits[to_delete])
                                self.fits = self.fits.drop(self.fits.index[to_delete])
                                # for val in to_delete[0][::-1]:
                                #     for key in self.fits.keys():
                                #         del self.fits[key][val]
                                for peak in self.single_fit:
                                    self.fits = self.fits.append(pd.DataFrame(peak))

                            index += 1
                            self.status.emit('saving')
                            self.save()
                            break
                        elif value == 'clear':
                            self.last_good = []
                            self.plotwidget.axes.clear()
                            self.plotwidget.axes.plot(data['frequency'], data['data'])
                            self.plotwidget.draw()
                        elif value == 'fit':
                            if self.initial_fit:
                                input = self.last_good
                            else:
                                input = self.peak_vals
                            if len(input) > 1:
                                centers, heights = list(zip(*input))
                                widths = 1e7 * np.ones(len(heights))
                            elif len(input) == 1:
                                centers, heights = input[0]
                                widths = 1e7
                            elif len(input) == 0:
                                self.single_fit = None
                                self.peak_locs.setText('No Peak')
                                self.plotwidget.axes.plot(data['frequency'],np.repeat(np.mean(data['data']), len(data['frequency'])))
                                self.plotwidget.draw()
                                continue
                            offset = np.mean(data['data'])
                            amplitudes = offset-np.array(heights)
                            if len(input) > 1:
                                fit_start_params = [[offset], np.concatenate((widths, amplitudes, centers))]
                                fit_start_params = [y for x in fit_start_params for y in x]
                            elif len(input) == 1:
                                fit_start_params = [offset, widths, amplitudes, centers]
                            try:
                                popt = self.fit_n_lorentzian(data['frequency'], data['data'], fit_start_params = fit_start_params)
                            except RuntimeError:
                                print('fit failed, optimal parameters not found')
                                break
                            self.plotwidget.axes.clear()
                            self.plotwidget.axes.plot(data['frequency'], data['data'])
                            self.plotwidget.axes.plot(data['frequency'], self.n_lorentzian(data['frequency'], *popt))
                            self.plotwidget.draw()
                            params = popt[1:]
                            widths_array = params[:len(params)/3]
                            amplitude_array = params[len(params)/3: 2 * len(params) / 3]
                            center_array = params[2 * len(params) / 3:]
                            positions = list(zip(center_array, amplitude_array, widths_array))
                            self.single_fit = []
                            peak_index = 0
                            for position in positions:
                                self.single_fit.append({'nv_id': [index], 'peak_id': [peak_index], 'offset': [popt[0]], 'fit_center': [position[0]], 'fit_amplitude': [position[1]], 'fit_width': [position[2]], 'manual_center': [input[peak_index][0]], 'manual_height': [input[peak_index][1]]})
                                peak_index += 1
                            self.peak_locs.setText('Peak Positions: ' + str(center_array))
                            self.initial_fit = False
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
            self.status.emit('dataset finished')

    def update_status(self, str):
        """
        Updates the gui statusbar with the given string
        :param str: string to set the statusbar
        """
        self.statusbar.showMessage(str)

    def start_fitting(self):
        """
        Launches the fitting routine on another thread
        """
        self.queue = queue.Queue()
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
        opens a file dialog to get the path to a file and sets the data_filepath entry area to that fliepath
        """
        dialog = QtGui.QFileDialog
        filename = dialog.getExistingDirectory(self, 'Select a file:', self.data_filepath.text())
        if str(filename)!='':
            self.data_filepath.setText(filename)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = FittingWindow()
    ex.show()
    ex.raise_()
    sys.exit(app.exec_())
