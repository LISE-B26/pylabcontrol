from src.core.scripts import Script
from PySide.QtCore import Signal, QThread
from src.core import Parameter
from src.instruments import NI7845RReadWrite
import time
import numpy as np

class FPGA_PolarizationController(Script, QThread):
    """
script to balance photodetector to zero by adjusting polarization controller voltages
    """
    updateProgress = Signal(int)
    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'C:\\Users\\Experiment\\Desktop\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', True, bool, 'check to automatically save data'),
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

    def __init__(self, instruments, scripts = None, name=None, settings=None, log_output=None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        self._abort = False
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments, log_output=log_output)
        QThread.__init__(self)

        self._plot_type = 2

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """


        def calc_progress(current_voltage, voltage_range):

            progress = ( current_voltage - min(voltage_range) ) / ( max(voltage_range) - min(voltage_range) )

            return int(100*progress)

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
        self.log('wait 2 seconds to settle down')
        time.sleep(2)


        c = 2
        channel_out = 'AO{:d}'.format(self.settings['channel_WP_{:d}'.format(c)])
        channel_in = 'AI{:d}'.format(self.settings['channel_detector'])
        # volt_range = np.arange(-0.5,0.5, 0.1)
        # volt_o = self.settings['V_{:d}'.format(c)]

        dV = 0.1
        self.data = {'WP1_volt':[], 'det_signal':[]}


        signal = float(self.settings['V_{:d}'.format(c)])
        searching = True
        while searching:
            if self._abort:
                break
            # print(dV)
            signal += dV
            fpga_io.update({channel_out:signal})
            detector_value = getattr(fpga_io, channel_in)
            print(channel_out, signal, detector_value)
            self.data['WP1_volt'].append(signal)
            self.data['det_signal'].append(detector_value)



            time.sleep(0.2)
            # progress = calc_progress(dV, volt_range)
            progress = 10
            self.updateProgress.emit(progress)

            if signal>5:
                searching = False

        self.updateProgress.emit(90)

        if self.settings['save']:
            self.save()
            self.save_data()
            self.save_log()

        self.updateProgress.emit(100)





    def plot(self, axes1, axes2):
        axes1.plot(self.data['WP1_volt'], self.data['det_signal'], '-o')

        axes2.plot(self.data['WP1_volt'][0:-1], np.diff(self.data['det_signal']), '-o')

    def stop(self):
        self._abort = True


class FPGA_PolarizationSignalMap(Script, QThread):
    """
script to map out detector response as a function of polarization controller voltages
    """

    updateProgress = Signal(int)
    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'C:\\Users\\Experiment\\Desktop\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', True, bool, 'check to automatically save data'),
        Parameter('channel_WP_1', 5, range(8), 'analog channel that controls waveplate 1'),
        Parameter('channel_WP_2', 6, range(8), 'analog channel that controls waveplate 2'),
        Parameter('channel_WP_3', 7, range(8), 'analog channel that controls waveplate 3'),
        Parameter('channel_OnOff', 4, [4,5,6,7], 'digital channel that turns polarization controller on/off'),
        Parameter('channel_detector', 0, range(4), 'analog input channel of the detector signal')
    ])

    _INSTRUMENTS = {
        'FPGA_IO': NI7845RReadWrite
    }

    _SCRIPTS = {

    }

    def __init__(self, instruments, scripts = None, name=None, settings=None, log_output=None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        self._abort = False
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments, log_output=log_output)
        QThread.__init__(self)

        self._plot_type = 1

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """


        def calc_progress(v1, v3, volt_range):
            dV = np.mean(np.diff(volt_range))
            progress_v3 = (v3 - min(volt_range)) / (max(volt_range) - min(volt_range))
            progress_v1 = (v1 - min(volt_range)) / (max(volt_range) - min(volt_range))
            progress = progress_v1 + progress_v3 * dV / (max(volt_range) - min(volt_range))
            return int(100*progress)

        self.data = {}
        fpga_io = self.instruments['FPGA_IO']['instance']
        # fpga_io.update(self.instruments['FPGA_IO']['settings'])

        # turn controller on
        control_channel = 'DIO{:d}'.format(self.settings['channel_OnOff'])
        instrument_settings = {control_channel: True}
        fpga_io.update(instrument_settings)

        channel_out_1 = 'AO{:d}'.format(self.settings['channel_WP_{:d}'.format(1)])
        channel_out_2 = 'AO{:d}'.format(self.settings['channel_WP_{:d}'.format(2)])
        channel_out_3 = 'AO{:d}'.format(self.settings['channel_WP_{:d}'.format(3)])
        channel_in = 'AI{:d}'.format(self.settings['channel_detector'])

        # set the voltages
        volt_range = np.arange(0, 5, 0.2)
        for v1 in volt_range:
            signal_1 = float(v1)
            for v3 in volt_range:
                signal_3 = float(v3)
                self.log('WP1 = {:0.2f}V, WP3 = {:0.2f}V: wait 3 seconds to settle down'.format(signal_1, signal_3))
                fpga_io.update({channel_out_1: signal_1, channel_out_2: 0, channel_out_3: signal_3})
                time.sleep(3)
                data = []
                for v2 in volt_range:
                    signal_2 = float(v2)
                    fpga_io.update({channel_out_2: signal_2})
                    time.sleep(1)
                    detector_value = getattr(fpga_io, channel_in)
                    data.append(detector_value)
                self.data.update({'WP1 = {:0.2f}V, WP3 = {:0.2f}V'.format(signal_1, signal_3) : data})
                progress = calc_progress(v1, v3, volt_range)
                self.updateProgress.emit(progress)

        if self.settings['save']:
            self.save()
            self.save_data()
            self.save_log()

        self.updateProgress.emit(100)





    def plot(self, axes1):

        last_key = sorted(self.data.keys())[-1]
        print('last_key', last_key)
        volt_range = np.arange(0, 5, 0.2)
        axes1.plot(volt_range, self.data[last_key], '-o')

    def stop(self):
        self._abort = True

if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'pol_control': 'FPGA_PolarizationController'}, script, instr)

    print(script)
    print(failed)
    print(instr)