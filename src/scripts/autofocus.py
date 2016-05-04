from src.core import Parameter, Script
from PySide.QtCore import Signal, QThread
from src.instruments import PiezoController
from src.scripts import GalvoScan
import numpy as np
import scipy as sp

class AutoFocus(Script, QThread):
    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/----data_tmp_default----', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off'),
        Parameter('piezo_min_voltage', 30.0, float, 'lower bound of piezo voltage sweep'),
        Parameter('piezo_max_voltage', 70.0, float, 'upper bound of piezo voltage sweep'),
        Parameter('num_sweep_points', 10, int, 'number of values to sweep between min and max voltage'),
        Parameter('mode', 'mean', ['mean', 'std_dev'], 'optimization function for focusing'),
        Parameter('wait_time', 0.1, float)
    ])

    _INSTRUMENTS = {
        'z_piezo': PiezoController
    }
    _SCRIPTS = {
        'take_image': GalvoScan
    }

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = Signal(float)
    def __init__(self, instruments, scripts, name = None, settings = None, log_output = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings, instruments, scripts, log_output = log_output)
        # QtCore.QThread.__init__(self)
        QThread.__init__(self)


    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        z_piezo = self.instruments.z_piezo['instance']
        z_piezo.update(self.instruments.z_piezo['settings'])
        sweep_voltages = np.linspace(self.settings.piezo_min_voltage,
                                     self.settings.piezo_max_voltage,
                                     self.settings.num_sweep_points)
        self.data['sweep_voltages'] = sweep_voltages
        self.data['focus_function_result'] = []
        self.data['images'] = []

        for voltage in sweep_voltages:
            # set the voltage on the piezo
            z_piezo.voltage = float(voltage)
            self.log('Voltage set to {:d}'.format(voltage))

            # take a galvo scan
            self.scripts.take_image['instance'].run()
            self.data['images'].append(self.scripts.take_image.data)
            self.log('Took image.')

            # calculate focusing function for this sweep
            if self.settings.mode == 'mean':
                self.data['focus_function_result'].append(float(np.mean(self.data['images'])))
            elif self.settings.mode == 'std_dev':
                self.data['focus_function_result'].append(float(np.std(self.data['images'])))

            # update progress bar
            progress = 100.0 * np.where(sweep_voltages == voltage) / float(self.settings.num_sweep_points)
            self.updateProgress.emit(progress)

        # fit the data and set piezo to focus spot

        #gaussian = lambda x, params: params[0] + params[1] * np.exp(((x-params[2])/params[3])**2)
        #error_function = lambda params, x, y: gaussian(params, x) - y
        #reasonable_params = [2.0, 10.0, 50.0, 10.0]

        #p2, success = sp.optimize.curve_fit(gaussian, self.data['sweep_voltages'],
        #                                    self.data['focus_function_result'], reasonable_params)


        # check to see if data should be saved and save it
        if self.settings.save:
            self.save()
            self.save_data()
            self.save_log()


    def plot(self, axes):
        axes.plot(self.data['sweep_voltages'][0:len(self.data['focus_function_result'])],
                  self.data['focus_function_result'])
        axes.set_xlim([self.data['sweep_voltages'][0], self.data['sweep_voltages'][-1]])
        axes.set_xlabel('Piezo Voltage [V]')
        axes.set_ylabel('Focusing Function')
        axes.set_title('Autofocusing Routine')

    def stop(self):
        self._abort = True


if __name__ == '__main__':
    # from src.core import Instrument
    # from src.scripts import GalvoScan
    # # instruments, loaded_failed = Instrument.load_and_append({'daq': 'DAQ'})
    # # print(instruments)
    # # gs = GalvoScan(instruments)
    #
    # scripts, loaded_failed, instruments = Script.load_and_append({"take_image": 'GalvoScan'})
    # print(scripts, instruments)
    # if loaded_failed != []:
    #     print('FAILED')
    #
    # instruments, loaded_failed = Instrument.load_and_append({'z_piezo':'PiezoController'},instruments)
    # print('DD', scripts, instruments)
    # if loaded_failed != []:
    #     print('FAILED')
    #
    # #
    # af = AutoFocus(name = 'aff', instruments=instruments, scripts=scripts)
    # print(af)
    scripts, loaded_failed, instruments = Script.load_and_append({"af": 'AutoFocus'})
    print(scripts, loaded_failed, instruments)