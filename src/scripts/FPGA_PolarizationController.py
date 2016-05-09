from src.core.scripts import Script
from PySide.QtCore import Signal, QThread
from src.core import Parameter
from src.instruments import NI7845RReadWrite
import time
import numpy as np
class FPGA_PolarizationController(Script):
    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('channel_WP_1', 5, range(8), 'analog channel that controls waveplate 1'),
        Parameter('channel_WP_2', 6, range(8), 'analog channel that controls waveplate 2'),
        Parameter('channel_WP_3', 7, range(8), 'analog channel that controls waveplate 3'),
        Parameter('V_1', 2.0, float, 'voltage applied to waveplate 1'),
        Parameter('V_2', 1.0, float, 'voltage applied to waveplate 2'),
        Parameter('V_3', 2.0, float, 'voltage applied to waveplate 3'),
        Parameter('channel_OnOff', 4, [4,5,6,7], 'digital channel that turns polarization controller on/off'),
        Parameter('channel_detector', 0, range(4), 'analog input channel of the detector signal')
    ])

    _INSTRUMENTS = {
        'FPGA_IO': NI7845RReadWrite
    }

    _SCRIPTS = {

    }
    # updateProgress = Signal(int)

    def __init__(self, instruments, scripts = None, name=None, settings=None, log_output=None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        self._abort = False
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments, log_output=log_output)
        # QThread.__init__(self)

        self._plot_type = 1

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        self.data = {'WP1_volt': [], 'det_signal': []}
        fpga_io = self.instruments['FPGA_IO']['instance']
        # fpga_io.update(self.instruments['FPGA_IO']['settings'])

        # turn controller on
        control_channel = 'DIO{:d}'.format(self.settings['channel_OnOff'])
        instrument_settings = {control_channel: True}

        # set the voltages

        for c in [1,2,3]:
            channel_out = 'AO{:d}'.format(self.settings['channel_WP_{:d}'.format(c)])
            signal = float(self.settings['V_{:d}'.format(c)])
            instrument_settings.update({channel_out:signal})
        fpga_io.update(instrument_settings)


        c = 1
        channel_out = 'AO{:d}'.format(self.settings['channel_WP_{:d}'.format(c)])
        channel_in = 'AI{:d}'.format(self.settings['channel_detector'])
        volt_range = np.arange(-0.5,0.5, 0.1)
        volt_o = self.settings['V_{:d}'.format(c)]

        self.data = {'WP1_volt':[], 'det_signal':[]}
        for dV in volt_range:
            # print(dV)
            signal = float(volt_o+dV)
            fpga_io.update({channel_out:signal})
            detector_value = getattr(fpga_io, channel_in)
            print(dV, detector_value)
            self.data['WP1_volt'].append(volt_o+dV)
            self.data['det_signal'].append(detector_value)
            time.sleep(0.2)





    def plot(self, axes):
        axes.plot(self.data['WP1_volt'], self.data['det_signal'])

    def stop(self):
        self._abort = True


if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'pol_control': 'FPGA_PolarizationController'}, script, instr)

    print(script)
    print(failed)
    print(instr)