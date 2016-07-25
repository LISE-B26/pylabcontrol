from src.core.scripts import Script
from src.core import Parameter
from src.instruments import DAQ
from collections import deque

from src.plotting.plots_1d import plot_counts
import numpy as np
import time


class Daq_Read_Counter(Script):
    _DEFAULT_SETTINGS = [
        Parameter('integration_time', .25, float, 'Time per data point'),
        Parameter('counter_channel', 'ctr0', ['ctr0', 'ctr1'], 'Daq channel used for counter')
    ]

    _INSTRUMENTS = {'daq': DAQ}

    _SCRIPTS = {

    }

    def __init__(self, instruments, scripts=None, name=None, settings=None, log_function=None, data_path=None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments,
                        log_function=log_function, data_path=data_path)

        self.data = {'counts': deque()}


    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        sample_rate = float(1) / self.settings['integration_time']
        normalization = self.settings['integration_time']/.001
        self.instruments['daq']['instance'].settings['digital_input'][self.settings['counter_channel']]['sample_rate'] = sample_rate

        self.data = {'counts': deque()}

        self.last_value = 0

        sample_num = 2

        self.instruments['daq']['instance'].DI_init("ctr0", sample_num, continuous_acquisition=True)

        # start counter and scanning sequence
        self.instruments['daq']['instance'].DI_run()

        while True:
            if self._abort:
                break

            # TODO: this is currently a nonblocking read so we add a time.sleep at the end so it doesn't read faster
            # than it acquires, this should be replaced with a blocking read in the future
            raw_data, _ = self.instruments['daq']['instance'].DI_read()

            for value in raw_data:
                self.data['counts'].append(((float(value) - self.last_value) / normalization))
                self.last_value = value
            self.progress = 50.
            self.updateProgress.emit(int(self.progress))

            time.sleep(2.0 / sample_rate)

        # clean up APD tasks
        self.instruments['daq']['instance'].DI_stop()

    def plot(self, figure_list):
        # COMMENT_ME
        super(Daq_Read_Counter, self).plot([figure_list[1]])

    def _plot(self, axes_list):
        # COMMENT_ME
        data = self.data['counts']
        if data:
            plot_counts(axes_list[0], self.data['counts'])

if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'Daq_Read_Cntr': 'Daq_Read_Cntr'}, script, instr)

    print(script)
    print(failed)
    print(instr)