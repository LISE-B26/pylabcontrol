from src.core.scripts import Script
from PySide.QtCore import Signal, QThread
from src.core import Parameter
from src.instruments import NI7845RReadWrite
import time
import numpy as np
import pandas as pd

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

    def __init__(self, instruments, scripts = None, name=None, settings=None, log_function=None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        self._abort = False
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments, log_function=log_function, data_path = data_path)
        QThread.__init__(self)

        self._plot_type = 'two'

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
            self.save_b26()
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
the script scans the voltage of all three channels from 0 to 5 volt and records the detector response
this gives a three dimensional dataset
    """

    updateProgress = Signal(int)
    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'C:\\Users\\Experiment\\Desktop\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', True, bool, 'check to automatically save data'),
        Parameter('WP_1', [
            Parameter('channel', 5, range(8), 'analog channel that controls waveplate 1'),
            Parameter('V_min', 0.0, float, 'minimum voltage of scan'),
            Parameter('V_max', 5.0, float, 'maximum voltage of scan'),
            Parameter('dV', 0.2, float, 'voltage step of scan')
        ]),
        Parameter('WP_2', [
            Parameter('channel', 6, range(8), 'analog channel that controls waveplate 1'),
            Parameter('V_min', 0.0, float, 'minimum voltage of scan'),
            Parameter('V_max', 5.0, float, 'maximum voltage of scan'),
            Parameter('dV', 0.2, float, 'voltage step of scan')
        ]),
        Parameter('WP_3', [
            Parameter('channel', 7, range(8), 'analog channel that controls waveplate 1'),
            Parameter('V_min', 0.0, float, 'minimum voltage of scan'),
            Parameter('V_max', 5.0, float, 'maximum voltage of scan'),
            Parameter('dV', 0.2, float, 'voltage step of scan')
        ]),
        # Parameter('channel_WP_1', 5, range(8), 'analog channel that controls waveplate 1'),
        # Parameter('channel_WP_2', 6, range(8), 'analog channel that controls waveplate 2'),
        # Parameter('channel_WP_3', 7, range(8), 'analog channel that controls waveplate 3'),
        Parameter('channel_OnOff', 4, [4,5,6,7], 'digital channel that turns polarization controller on/off'),
        Parameter('channel_detector', 0, range(4), 'analog input channel of the detector signal')
    ])

    _INSTRUMENTS = {
        'FPGA_IO': NI7845RReadWrite
    }

    _SCRIPTS = {

    }

    def __init__(self, instruments, scripts = None, name=None, settings=None, log_function=None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        self._abort = False
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments, log_function=log_function, data_path = data_path)
        QThread.__init__(self)

        self._plot_type = 'main'

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """


        def calc_progress(v1, v3, volt_range_1, volt_range_3):
            dV = np.mean(np.diff(volt_range_1))
            progress_v3 = (v3 - min(volt_range_3)) / (max(volt_range_3) - min(volt_range_3))
            progress_v1 = (v1 - min(volt_range_1)) / (max(volt_range_1) - min(volt_range_1))
            progress = progress_v1 + progress_v3 * dV / (max(volt_range_1) - min(volt_range_1))
            return int(100*progress)

        self.data = {}
        fpga_io = self.instruments['FPGA_IO']['instance']
        # fpga_io.update(self.instruments['FPGA_IO']['settings'])

        # turn controller on
        control_channel = 'DIO{:d}'.format(self.settings['channel_OnOff'])
        instrument_settings = {control_channel: True}
        fpga_io.update(instrument_settings)

        # channel_out_1 = 'AO{:d}'.format(self.settings['channel_WP_{:d}'.format(1)])
        # channel_out_2 = 'AO{:d}'.format(self.settings['channel_WP_{:d}'.format(2)])
        # channel_out_3 = 'AO{:d}'.format(self.settings['channel_WP_{:d}'.format(3)])
        channel_out_1 = 'AO{:d}'.format(self.settings['WP_1']['channel'])
        channel_out_2 = 'AO{:d}'.format(self.settings['WP_2']['channel'])
        channel_out_3 = 'AO{:d}'.format(self.settings['WP_3']['channel'])
        channel_in = 'AI{:d}'.format(self.settings['channel_detector'])

        # set the voltages
        volt_range_1 = np.arange(self.settings['WP_1']['V_min'], self.settings['WP_1']['V_max'], self.settings['WP_1']['dV'])
        volt_range_2 = np.arange(self.settings['WP_2']['V_min'], self.settings['WP_2']['V_max'], self.settings['WP_2']['dV'])
        volt_range_3 = np.arange(self.settings['WP_3']['V_min'], self.settings['WP_3']['V_max'], self.settings['WP_3']['dV'])
        for v1 in volt_range_1:
            signal_1 = float(v1)
            for v3 in volt_range_3:
                signal_3 = float(v3)
                self.log('WP1 = {:0.2f}V, WP3 = {:0.2f}V: wait 3 seconds to settle down'.format(signal_1, signal_3))
                fpga_io.update({channel_out_1: signal_1, channel_out_2: 0, channel_out_3: signal_3})
                time.sleep(3)
                data = []
                for v2 in volt_range_2:
                    signal_2 = float(v2)
                    fpga_io.update({channel_out_2: signal_2})
                    time.sleep(1)
                    detector_value = getattr(fpga_io, channel_in)
                    data.append(detector_value)
                self.data.update({'WP1 = {:0.2f}V, WP3 = {:0.2f}V'.format(signal_1, signal_3) : data})
                progress = calc_progress(v1, v3, volt_range_1, volt_range_3)
                self.updateProgress.emit(progress)

        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()

        self.updateProgress.emit(100)


    @staticmethod
    def data_to_pandas_panel(data):
        """
        casts the data in dictionary form into a pandas panel (3D dataset)
        Args:
            data: dictionary produced by the script

        Returns: pandas panel (3D dataset)

        """

        def get_voltages_from_tag(s):
            v1 = float(s.split(',')[0].split('WP1 = ')[1].split('V')[0])
            v3 = float(s.split(',')[1].split(' WP3 = ')[1].split('V')[0])
            return v1, v3

        v1_array = sorted(list(set([get_voltages_from_tag(k)[0] for k, value in data.iteritems()])))
        v3_array = sorted(list(set([get_voltages_from_tag(k)[1] for k, value in data.iteritems()])))
        v2_array = sorted(list(set([get_voltages_from_tag(k)[1] for k, value in data.iteritems()])))

        def get_img_df(v3):
            df = pd.DataFrame(
                [data['WP1 = {:0.2f}V, WP3 = {:0.2f}V'.format(v1, v3)][0:len(v2_array)] for v1 in v1_array],
                index=['{:0.2f}V'.format(v1) for v1 in v1_array],
                columns=['{:0.2f}V'.format(v2) for v2 in v2_array])
            return df

        panel = pd.Panel.from_dict({'{:0.2f}V'.format(v3): get_img_df(v3) for v3 in v3_array})
        return panel.transpose(1, 2, 0)

    @staticmethod
    def plot_pol_map(value, axis, data_panel, plot_axes = None):
        """
        plots the polarization map
        Args:
            value: value of voltage for which to plot 2D map
            axis: axis along which to slice data (1,2,3)
            data_panel: pandas data panel as obtained from data_to_pandas_panel()
            plot_axes: axes on which to plot data
        Returns:

        """
        if isinstance(value, float):
            value = '{:0.2f}V'.format(value)

        v1_array, v2_array, v3_array = data_panel.axes

        if axis == 1:
            data = data_panel[value]
            #         extent=[0, len(v2_array),len(v3_array),0]
            xlabel = 'waveplate 2 (V)'
            ylabel = 'waveplate 3 (V)'
            title = 'waveplate 1 = {:s}'.format(value)
            extent = [float(min(v2_array).split('V')[0]), float(max(v2_array).split('V')[0]),
                      float(max(v3_array).split('V')[0]), float(min(v3_array).split('V')[0])]
        elif axis == 2:
            data = data_panel.major_xs(value)
            #         extent=[0, len(v1_array),len(v3_array),0]
            extent = [float(min(v1_array).split('V')[0]), float(max(v1_array).split('V')[0]),
                      float(max(v3_array).split('V')[0]), float(min(v3_array).split('V')[0])]
            xlabel = 'waveplate 1 (V)'
            ylabel = 'waveplate 3 (V)'
            title = 'waveplate 2 = {:s}'.format(value)
        elif axis == 3:
            data = data_panel.minor_xs(value)
            #         extent=[0, len(v1_array),len(v2_array),0]
            extent = [float(min(v1_array).split('V')[0]), float(max(v1_array).split('V')[0]),
                      float(max(v2_array).split('V')[0]), float(min(v2_array).split('V')[0])]
            xlabel = 'waveplate 1 (V)'
            ylabel = 'waveplate 2 (V)'
            title = 'waveplate 3 = {:s}'.format(value)

        if plot_axes is None:
            import matplotlib.pyplot as plt
            plt.figure()
            im = plt.imshow(data, extent=extent)
            cb = plt.colorbar(im)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.title(title)
        else:
            im = plot_axes.imshow(data, extent=extent)
            # cb = plt.colorbar(im)
            plot_axes.set_xlabel(xlabel)
            plot_axes.set_ylabel(ylabel)
            plot_axes.set_title(title)
        # return data

    @staticmethod
    def plot_scan(data_panel, v1=None, v2=None, v3=None, plot_axes = None):
        """
        plots the detector signal as a function of the axis for which the value is None
        Args:
            data_panel: data set in form of a pandas data panel
            v1: float or text of form {:0.2f} or None
            v2: float or text of form {:0.2f} or None
            v3: float or text of form {:0.2f} or None

        Returns:

        """
        #     need to get two values
        assert np.sum([x == None for x in [v1, v2, v3]]) == 1, 'function requires exactly two not None values'

        if v1 == None:
            perm = [1, 0, 2]
            value1, value2 = v2, v3
            xlabel = 'waveplate 1 (V)'
            title = 'WP2 = {:0.2f}V, WP3 = {:0.2f}V'.format(v2, v3)
        elif v2 == None:
            perm = [0, 1, 2]
            value1, value2 = v1, v3
            xlabel = 'waveplate 2 (V)'
            title = 'WP1 = {:0.2f}V, WP3 = {:0.2f}V'.format(v1, v3)
        elif v3 == None:
            perm = [0, 2, 1]
            value1, value2 = v1, v2
            xlabel = 'waveplate 3 (V)'
            title = 'WP1 = {:0.2f}V, WP2 = {:0.2f}V'.format(v1, v2)

        if isinstance(value1, float):
            value1 = '{:0.2f}V'.format(value1)
        if isinstance(value2, float):
            value2 = '{:0.2f}V'.format(value2)

        print('p', perm, value1, value2)

        scan_data = data_panel.transpose(perm[0], perm[1], perm[2])[value1][value2]

        if plot_axes is None:
            import matplotlib.pyplot as plt
            plt.figure()
            plt.plot([float(x.split('V')[0]) for x in scan_data.index], scan_data.values)
            plt.xlabel(xlabel)
            plt.ylabel('detector signal')
            plt.title(title)
        else:
            plot_axes.plot([float(x.split('V')[0]) for x in scan_data.index], scan_data.values)
            plot_axes.set_xlabel(xlabel)
            plot_axes.set_ylabel('detector signal')
            plot_axes.set_title(title)

    def plot(self, axes1):

        last_key = sorted(self.data.keys())[-1]
        print('last_key', last_key)
        volt_range = np.arange(0, 5, 0.2)
        axes1.plot(volt_range, self.data[last_key], '-o')

    def stop(self):
        self._abort = True

class FPGA_PolarizationSignalScan(Script, QThread):
    """
script to map out detector response as a function of polarization controller voltage WP2
the script scans the voltage of  channel 2 from 0 to 5 volt and records the detector response
this gives a one dimensional dataset
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
        Parameter('channel_detector', 0, range(4), 'analog input channel of the detector signal'),
        Parameter('V_1', 2.4, float, 'voltage applied to waveplate 1'),
        Parameter('V_3', 2.4, float, 'voltage applied to waveplate 3')
    ])

    _INSTRUMENTS = {
        'FPGA_IO': NI7845RReadWrite
    }

    _SCRIPTS = {

    }

    def __init__(self, instruments, scripts = None, name=None, settings=None, log_function=None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        self._abort = False
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments, log_function=log_function, data_path = data_path)
        QThread.__init__(self)

        self._plot_type = 'main'

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """


        def calc_progress(v2, volt_range):
            dV = np.mean(np.diff(volt_range))
            progress = (v2 - min(volt_range)) / (max(volt_range) - min(volt_range))
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

        signal_1 = float(self.settings['V_1'])
        signal_3 = float(self.settings['V_3'])

        volt_range = np.arange(0, 5, 0.2)
        data = []
        for v2 in volt_range:
            signal_2 = float(v2)
            fpga_io.update({channel_out_2: signal_2})
            time.sleep(1)
            detector_value = getattr(fpga_io, channel_in)
            data.append(detector_value)
            progress = calc_progress(v2, volt_range)
            self.data.update({'WP1 = {:0.2f}V, WP3 = {:0.2f}V'.format(signal_1, signal_3): data})
            self.updateProgress.emit(progress)

        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()

        self.updateProgress.emit(100)

    def plot(self, figure):
        axes1 = self.get_axes_layout(figure)
        last_key = sorted(self.data.keys())[-1]
        volt_range = np.arange(0, 5, 0.2)
        axes1.plot(volt_range[0:len(self.data[last_key])], self.data[last_key], '-o')

    def stop(self):
        self._abort = True
if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'pol_control': 'FPGA_PolarizationController'}, script, instr)

    print(script)
    print(failed)
    print(instr)