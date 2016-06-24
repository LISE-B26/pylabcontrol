from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
import numpy as np
import scipy as sp

from src.instruments import PiezoController
from src.scripts import GalvoScan


class Focusing(Script, QThread):
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', '', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', False, bool, 'check to automatically save data'),
        Parameter('point_a', (0.0, 0.0), tuple, 'top left corner point of scan region'),
        Parameter('point_b', (0.1, -0.1), tuple, 'bottom right corner point of scan region'),
        Parameter('num_points_xy', (30, 30), tuple, 'number of points to scan in x,y'),
        Parameter('wait_time', .001, float, 'time to wait after moving objective to allow system to stabilize'),
        Parameter('axis', 'x', ['x', 'y', 'z'], 'axis of piezo to use for autofocusing'),
        Parameter('min_z', 40, float, 'starting height of z sweep in volts'),
        Parameter('max_z', 60, float, 'ending height of z sweep in volts'),
        Parameter('num_points_z', 20, int, 'number of points to look at in z'),
        Parameter('optimization_type', 'stddev', ['stddev, mean'], 'method to optimize focus')
    ])

    _INSTRUMENTS = {'piezo_controller': PiezoController}

    _SCRIPTS = {'galvo_scan': GalvoScan}

    updateProgress = Signal(int)

    def __init__(self, instruments, scripts, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        assert (self.settings['min_z'] >= 1 and self.settings['max_z'] <= 99)

        Script.__init__(self, name, settings = settings, scripts =scripts, instruments = instruments, log_function= log_function, data_path = data_path)

        volt_range = np.linspace(self.settings['min_z'], self.settings['max_z'], self.settings['num_points_z'])

        self.data = {
            'voltages': volt_range,
            'FoM': np.array()
        }

        QThread.__init__(self)

    def _function(self):
        piezo = self.instruments['piezo_controller']
        for voltage in self.data['voltages']:
            piezo.update{'voltage': voltage}
            time.sleep(waitTime)
            print(xMin)
            print(xMax)
            print(xPts)
            if (APD):
                scanner = GalvoScanAPD.ScanNV(xMin, xMax, xPts, yMin, yMax, yPts, timePerPt)
            else:
                scanner = GalvoScanPD.ScanNV(xMin, xMax, xPts, yMin, yMax, yPts, timePerPt)
            image = scanner.scan(queue=None)
            xdata.append(voltage)
            if std == True:
                ydata.append(sp.ndimage.measurements.standard_deviation(image))
            else:
                ydata.append(sp.ndimage.measurements.mean(image))
            if plotting:
                cls.plotData(datline, xdata, ydata, canvas, axes)

                cls.plotImg(image, canvas, axes_img)

                if ydata[-1] == max(ydata): image_best = image

                cls.plotImg(image_best, canvas, axes_img_best)

        cls.setDaqPt(xInit, yInit)
        (a, mean, sigma, c), _ = cls.fit(voltRange, ydata)
        if plotting:
            cls.plotFit(fitline, a, mean, sigma, c, minV, maxV, canvas)
        # checks if computed mean is outside of scan range and, if so, sets piezo to center of scan range to prevent a
        # poor fit from trying to move the piezo by a large amount and breaking the stripline
        if (mean > np.min(voltRange) and mean < np.max(voltRange) and a > 0):
            piezo.setVoltage(mean)
            print(mean)
        else:
            piezo.setVoltage(np.mean(voltRange))
        if canvas is None and plotting and blocking:
            plt.show()
        elif canvas is None and plotting:
            plt.close()

        if return_data:
            return mean, voltRange, ydata
        elif return_data == False:
            return mean

            # Fits the data to a gaussian given by the cls.gaussian method, and returns the fit parameters. If the fit fails,
            # returns (-1,-1,-1) as the parameters
    @classmethod
    def fit(cls, x, y):
        # x: x input data
        # y: y input data
        try:
            n = len(x)
            # compute mean and standard deviation initial guesses
            # mean = numpy.sum(x*y)/numpy.sum(y)
            mean = x[np.argmax(y)]

            sigma = np.sqrt(abs(sum((x - mean) ** 2 * y) / sum(y)))

            c = min(y)

            print('initial guess for mean and std: {:0.3f} +- {:0.3f}'.format(mean, sigma))

            return sp.optimize.curve_fit(cls.gaussian, x, y, p0=[1, mean, sigma, c])
        except RuntimeError:
            print('Gaussian fit failed. Setting piezo to mean of input range')
            return (-1, -1, -1, -1), 'Ignore'

    # defines a gaussian for use in the fitting routine
    @staticmethod
    # x: variable
    # a: gaussian amplitude
    # x0: gaussian center
    # sigma: standard deviation
    # c: offset
    def gaussian(x, a, x0, sigma, c):
        return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2)) + c

raise NotImplementedError