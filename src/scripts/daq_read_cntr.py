from src.core.scripts import Script
from src.core import Parameter
from src.instruments import DAQ
from collections import deque

from PyQt4.QtCore import pyqtSignal, QThread

from src.plotting.plots_1d import plot_counts


class Daq_Read_Cntr(Script, QThread):
    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('integration_time', .25, float, 'Time per data point')
    ])

    _INSTRUMENTS = {'daq': DAQ}

    _SCRIPTS = {

    }
    updateProgress = pyqtSignal(int)

    def __init__(self, instruments, scripts=None, name=None, settings=None, log_function=None, data_path=None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        self._abort = False
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments,
                        log_function=log_function, data_path=data_path)
        QThread.__init__(self)
        self._plot_type = 'aux'

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        self._abort = False

        sample_rate = 1/self.settings['integration_time']
        normalization = self.settings['integration_time']/.001
        self.instruments['daq']['instance'].settings['digital_input']['ctr0']['sample_rate'] = sample_rate

        self.data = {'counts': deque()}

        sample_num = 1

        self.instruments['daq']['instance'].DI_init("ctr0", sample_num, continuous_acquisition=True)

        # start counter and scanning sequence
        self.instruments['daq']['instance'].DI_run()

        while True:
            if self._abort:
                break

            raw_data, _ = self.instruments['daq']['instance'].DI_read()

            self.data['counts'].append((raw_data/normalization))

            self.updateProgress.emit(50)

        # clean up APD tasks
        self.instruments['daq']['instance'].DI_stop()

        # send 100 to signal that script is finished
        self.updateProgress.emit(100)

    def plot(self, figure):
        data = self.data['counts']
        if data:
            axes = self.get_axes_layout(figure)
            plot_counts(self.data[-1]['fit_params'], self.data[-1]['frequency'], self.data[-1]['data'], axes)

    def stop(self):
        self._abort = True

if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'Daq_Read_Cntr': 'Daq_Read_Cntr'}, script, instr)

    print(script)
    print(failed)
    print(instr)