from src.core.scripts import Script
from src.core import Parameter
from src.instruments import NI7845RReadWrite
import time
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

class FPGA_PolarizationController(Script):
    """
script to balance photodetector to zero by adjusting polarization controller voltages
    """
    _DEFAULT_SETTINGS = [
        Parameter('channel_WP_1', 5, range(8), 'analog channel that controls waveplate 1'),
        Parameter('channel_WP_2', 6, range(8), 'analog channel that controls waveplate 2'),
        Parameter('channel_WP_3', 7, range(8), 'analog channel that controls waveplate 3'),
        Parameter('V_1', 2.0, float, 'voltage applied to waveplate 1'),
        Parameter('V_2', 1.0, float, 'voltage applied to waveplate 2'),
        Parameter('V_3', 2.0, float, 'voltage applied to waveplate 3'),
        Parameter('channel_OnOff', 4, [4,5,6,7], 'digital channel that turns polarization controller on/off'),
        Parameter('channel_detector', 0, range(4), 'analog input channel of the detector signal')
    ]

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
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments, log_function=log_function, data_path = data_path)
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
            signal += dV
            fpga_io.update({channel_out:signal})
            detector_value = getattr(fpga_io, channel_in)
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



    def _plot(self, axes_list):
        axes1, axes2 = axes_list
        axes1.plot(self.data['WP1_volt'], self.data['det_signal'], '-o')

        axes2.plot(self.data['WP1_volt'][0:-1], np.diff(self.data['det_signal']), '-o')

class FPGA_PolarizationSignalMap(Script):
    """
script to map out detector response as a function of polarization controller voltages
the script scans the voltage of all three channels from 0 to 5 volt and records the detector response
this gives a three dimensional dataset
    """

    _DEFAULT_SETTINGS = [
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
    ]

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
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments, log_function=log_function, data_path = data_path)

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

class FPGA_PolarizationSignalScan(Script):
    """
script to map out detector response as a function of polarization controller voltage WP2
the script scans the voltage of  channel 2 from 0 to 5 volt and records the detector response
this gives a one dimensional dataset
    """

    _DEFAULT_SETTINGS = [
        Parameter('channel_WP_1', 5, range(8), 'analog channel that controls waveplate 1'),
        Parameter('channel_WP_2', 6, range(8), 'analog channel that controls waveplate 2'),
        Parameter('channel_WP_3', 7, range(8), 'analog channel that controls waveplate 3'),
        Parameter('channel_OnOff', 4, [4,5,6,7], 'digital channel that turns polarization controller on/off'),
        Parameter('channel_detector', 0, range(4), 'analog input channel of the detector signal'),
        Parameter('V_1', 2.4, float, 'voltage applied to waveplate 1'),
        Parameter('V_3', 2.4, float, 'voltage applied to waveplate 3'),
        Parameter('V_2',
                  [Parameter('min', 0, float, 'min voltage applied to waveplate 2'),
                   Parameter('max', 5.0, float, 'max voltage applied to waveplate 2'),
                   Parameter('number', 10, int, 'number of voltage steps applied to waveplate 2')]
                  ),
        Parameter('settle_time', 1.0, float, 'settle time in seconds between voltage steps')
    ]

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
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments, log_function=log_function, data_path = data_path)


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

        signal_2_min = self.settings['V_2']['min']
        signal_2_max = self.settings['V_2']['max']
        signal_2_steps = self.settings['V_2']['number']
        volt_range = np.linspace(signal_2_min, signal_2_max, signal_2_steps)

        settle_time = 1e3* self.settings['settle_time']

        fpga_io.update({channel_out_1: signal_1, channel_out_2: signal_3})
        self.msleep(settle_time)

        data = np.zeros((len(volt_range), 4))
        for i, v2 in enumerate(volt_range):
            if self._abort:
                break
            signal_2 = float(v2)
            fpga_io.update({channel_out_2: signal_2})
            self.msleep(settle_time)
            detector_value = getattr(fpga_io, channel_in)
            data[i,:] = np.array([signal_1, signal_2, signal_3, detector_value])
            progress = calc_progress(v2, volt_range)



            self.data['WP1 (V)'] =  data[0:i,0]
            self.data['WP2 (V)'] = data[0:i, 1]
            self.data['WP3 (V)'] = data[0:i, 2]
            self.data['Det. Signal'] = data[0:i, 3]

            self.updateProgress.emit(progress)

        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()

    def _plot(self, axes_list):

        if self.data != {}:
            axes = axes_list[0]

            volt_range = self.data['WP2 (V)']
            signal = self.data['Det. Signal']

            def func(x, a, b):
                return a * x + b

            popt, pcov = curve_fit(func, volt_range, signal)


            axes.plot(volt_range, signal, '-o')

            axes.plot(volt_range, func(volt_range, popt[0], popt[1]), 'k-')
            axes.set_title('setpoint = {:0.2f}V'.format(-popt[1] / popt[0]))


class FPGA_BalancePolarization(Script):
    """
    script to bring the detector response to zero
    two channels are set to a fixed voltage while the signal of the third channel is varied until the detector response is zero
    """

    _DEFAULT_SETTINGS = [
        Parameter('channel_WP_1', 5, range(8), 'analog channel that controls waveplate 1'),
        Parameter('channel_WP_2', 6, range(8), 'analog channel that controls waveplate 2'),
        Parameter('channel_WP_3', 7, range(8), 'analog channel that controls waveplate 3'),
        Parameter('channel_OnOff', 4, [4,5,6,7], 'digital channel that turns polarization controller on/off'),
        Parameter('channel_detector', 0, range(4), 'analog input channel of the detector signal'),
        Parameter('V_1', 2.4, float, 'voltage applied to waveplate 1'),
        Parameter('V_3', 2.4, float, 'voltage applied to waveplate 3'),
        Parameter('V_2',
                  [Parameter('min', 0, float, 'starting min voltage applied to waveplate 2'),
                   Parameter('max', 5.0, float, 'max voltage applied to waveplate 2'),
                   Parameter('number', 10, int, 'NOT IN USE!! number of voltage steps applied to waveplate 2')]
                  ),
        Parameter('settle_time', 1.0, float, 'settle time in seconds between voltage steps'),
        Parameter('V_2_min', False, bool, 'if true set V2 to the min value and don\'t update')
    ]

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

        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments, log_function=log_function, data_path = data_path)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

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

        signal_2_min = self.settings['V_2']['min']
        signal_2_max = self.settings['V_2']['max']
        signal_2_steps = self.settings['V_2']['number']
        volt_range = np.linspace(signal_2_min, signal_2_max, signal_2_steps)

        settle_time = 1e3*self.settings['settle_time']

        fpga_io.update({channel_out_1: signal_1, channel_out_2: signal_3})
        self.msleep(settle_time)

        self.data['WP2 (V)'] = []
        self.data['Det. Signal'] = []
        reached_zero = False

        v2 = signal_2_min
        self.log('STARTING....')
        while reached_zero is False:
            if self._abort:
                break
            signal_2 = float(v2)
            fpga_io.update({channel_out_2: signal_2})
            self.msleep(settle_time)
            detector_value = getattr(fpga_io, channel_in)

            self.data['WP2 (V)'].append(v2)
            self.data['Det. Signal'].append(detector_value)

            v2 = self.calc_zero_pos()

            self.updateProgress.emit(50)

        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()

    def calc_zero_pos(self):
        """
        calculates the WP voltage for which the detector signal reaches zero
        Returns:

        """

        signal_2_min = self.settings['V_2']['min']
        signal_2_max = self.settings['V_2']['max']

        if self.settings['V_2_min']:
            return signal_2_min


        volt_range = self.data['WP2 (V)']
        signal = self.data['Det. Signal']
        if len(volt_range)<2:
            zero_pos = volt_range[-1]+0.1
        else:
            dx = volt_range[-1] - volt_range[-2]
            dy = signal[-1] - signal[-2]
            zero_pos =  signal[-1] / dy * dx + volt_range[-1]
            print('dx{:0.2f}\t,dy {:0.2f}'.format(dx,dy))

        # now check that zero_pos is a reasonable value

        if zero_pos< signal_2_min:
            zero_pos = signal_2_min

        if zero_pos > signal_2_max:
            zero_pos = signal_2_max

        print('old signal{:0.2f}\t, new signal {:0.2f}'.format(volt_range[-1], zero_pos))

        return zero_pos


    def _plot(self, axes_list):

        if self.data != {}:
            axes1, axes2 = axes_list

            volt_range = self.data['WP2 (V)']
            signal = self.data['Det. Signal']
            #
            # def func(x, a, b):
            #     return a * x + b
            #
            # popt, pcov = curve_fit(func, volt_range, signal)


            axes1.plot(signal, '-o')
            axes1.set_title('detector signal')
            axes2.plot(volt_range, '-o')
            axes2.set_title('WP2 voltage')
            # axes1.plot(volt_range, func(volt_range, popt[0], popt[1]), 'k-')
            # axes1.set_title('setpoint = {:0.2f}V'.format(-popt[1] / popt[0]))

if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'pol_control': 'FPGA_PolarizationController'}, script, instr)

    print(script)
    print(failed)
    print(instr)