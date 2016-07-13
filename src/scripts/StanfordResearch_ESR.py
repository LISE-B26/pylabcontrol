from src.core.scripts import Script

# import standard libraries
import numpy as np
import scipy.optimize as opt
from src.core import Parameter
from src.instruments import MicrowaveGenerator, DAQ
from collections import deque

from src.plotting.plots_1d import plot_esr


class StanfordResearch_ESR(Script):

    _DEFAULT_SETTINGS = [
        Parameter('power_out', -45.0, float, 'output power (dBm)'),
        Parameter('esr_avg', 50, int, 'number of esr averages'),
        Parameter('freq_start', 2.82e9, float, 'start frequency of scan'),
        Parameter('freq_stop', 2.92e9, float, 'end frequency of scan'),
        Parameter('freq_points', 100, int, 'number of frequencies in scan'),
        Parameter('integration_time', 0.01, float, 'measurement time of fluorescent counts'),
        Parameter('settle_time', .0002, float, 'time to allow system to equilibrate after changing microwave powers')
    ]

    _INSTRUMENTS = {
        'microwave_generator': MicrowaveGenerator,
        'daq': DAQ
    }

    _SCRIPTS = {}

    def __init__(self, instruments, scripts = None, name=None, settings=None, log_function=None, data_path = None):
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments, log_function=log_function, data_path = data_path)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        self.lines = []
        freq_values = np.linspace(self.settings['freq_start'], self.settings['freq_stop'], self.settings['freq_points'])
        freq_range = max(freq_values) - min(freq_values)
        num_freq_sections = int(freq_range) / int(self.instruments['microwave_generator']['instance'].settings['dev_width']*2) + 1
        clock_adjust = int((self.settings['integration_time'] + self.settings['settle_time']) / self.settings['settle_time'])
        freq_array = np.repeat(freq_values, clock_adjust)
        self.instruments['microwave_generator']['instance'].update({'amplitude': self.settings['power_out']})
        self.instruments['microwave_generator']['instance'].update({'modulation_type': 'FM'})

        sample_rate = float(1) / self.settings['settle_time']
        self.instruments['daq']['instance'].settings['analog_output']['ao2']['sample_rate'] = sample_rate
        self.instruments['daq']['instance'].settings['digital_input']['ctr0']['sample_rate'] = sample_rate

        # move to NV point if given
        # if not (nv_x is None):
        #     move_to_NV((nv_x, nv_y))

        esr_data = np.zeros((self.settings['esr_avg'], len(freq_values)))
        self.data = deque()
        self.fit_params_list = deque()

        # run sweeps
        for scan_num in xrange(0, self.settings['esr_avg']):
            if self._abort:
                break
            esr_data_pos = 0
            self.instruments['microwave_generator']['instance'].update({'enable_output': True})
            for sec_num in xrange(0, num_freq_sections):
                # initialize APD thread

                # calculate the minimum ad and max frequency of current section
                sec_min = min(freq_values) + self.instruments['microwave_generator']['instance'].settings['dev_width']*2 * sec_num
                sec_max = sec_min + self.instruments['microwave_generator']['instance'].settings['dev_width']*2

                # make freq. array for current section
                freq_section_array = freq_array[np.where(np.logical_and(freq_array >= sec_min,
                                                                        freq_array < sec_max))]
                # if section is empty skip
                if len(freq_section_array) == 0:
                    continue
                center_freq = (sec_max + sec_min) / 2.0
                freq_voltage_array = ((
                                      freq_section_array - sec_min) / (self.instruments['microwave_generator']['instance'].settings['dev_width']*2)) * 2 - 1  # normalize voltages to +-1 range

                self.instruments['microwave_generator']['instance'].update({'frequency': float(center_freq)})

                self.instruments['daq']['instance'].DI_init("ctr0",  len(freq_voltage_array) + 1)
                self.instruments['daq']['instance'].AO_init(["ao2"], freq_voltage_array)

                # start counter and scanning sequence
                self.instruments['daq']['instance'].DI_run()
                self.instruments['daq']['instance'].AO_run()
                self.instruments['daq']['instance'].AO_waitToFinish()
                self.instruments['daq']['instance'].AO_stop()

                raw_data, _ = self.instruments['daq']['instance'].DI_read()

                # raw_data = sweep_mw_and_count_APD(freq_voltage_array, dt)
                # counter counts continiously so we take the difference to get the counts per time interval
                diff_data = np.diff(raw_data)
                summed_data = np.zeros(len(freq_voltage_array) / clock_adjust)
                for i in range(0, int((len(freq_voltage_array) / clock_adjust))):
                    summed_data[i] = np.sum(diff_data[(i * clock_adjust + 1):(i * clock_adjust + clock_adjust - 1)])
                # also normalizing to kcounts/sec
                esr_data[scan_num, esr_data_pos:(esr_data_pos + len(summed_data))] = summed_data * (.001 / self.settings['integration_time'])
                esr_data_pos += len(summed_data)

                # clean up APD tasks
                self.instruments['daq']['instance'].DI_stop()

            esr_avg = np.mean(esr_data[0:(scan_num + 1)], axis=0)
            fit_params, _ = self.fit_esr(freq_values, esr_avg)
            self.data.append({'frequency': freq_values, 'data': esr_avg, 'fit_params': fit_params})

            progress = self._calc_progress(scan_num)
            self.updateProgress.emit(progress)

        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()

            self.save_image_to_disk()
            # # create and save images
            # filename = self.filename('-esr.jpg')
            # fig = Figure()
            # canvas = FigureCanvas(fig)
            # ax = fig.add_subplot(1, 1, 1)
            # plotting.plot_esr(self.data[-1]['fit_params'], self.data[-1]['frequency'], self.data[-1]['data'], ax)
            # fig.savefig(filename)

    def _calc_progress(self, scan_num):

        progress = float(scan_num) / self.settings['esr_avg'] * 100.
        self.progress = progress
        return int(progress)

    def _plot(self, axes_list):
        plot_esr(axes_list[0], self.data[-1]['frequency'], self.data[-1]['data'], self.data[-1]['fit_params'])

    def _update_plot(self, axes_list):
        plot_esr(axes_list[0], self.data[-1]['frequency'], self.data[-1]['data'], self.data[-1]['fit_params'])

    def get_axes_layout(self, figure_list):
        """
        returns the axes objects the script needs to plot its data
        the default creates a single axes object on each figure
        This can/should be overwritten in a child script if more axes objects are needed
        Args:
            figure_list: a list of figure objects
        Returns:
            axes_list: a list of axes objects

        """
        new_figure_list = [figure_list[1]]
        return super(StanfordResearch_ESR, self).get_axes_layout(new_figure_list)

    # fit ESR curve to lorentzian and return fit parameters. If initial guess known, put in fit_start_params, otherwise
    # guesses reasonable initial values.
    def fit_esr(self, freq_values, esr_data, fit_start_params=None):
        if (fit_start_params is None):
            offset = np.mean(esr_data)
            amplitude = np.max(esr_data) - np.min(esr_data)
            center = freq_values[esr_data.argmin()]
            width = 10000000  # 10 MHz arbitrarily chosen as reasonable
            fit_start_params = [amplitude, width, center, offset]
        try:
            return opt.curve_fit(self.lorentzian, freq_values, esr_data, fit_start_params)
        except RuntimeError:
            self.log('Lorentzian fit failed')
            return [-1, -1, -1, -1], 'Ignore'

    # defines a lorentzian with some amplitude, width, center, and offset to use with opt.curve_fit
    def lorentzian(self, x, amplitude, width, center, offset):
        return (-(amplitude*(.5*width)**2)/((x-center)**2+(.5*width)**2))+offset

if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'StanfordResearch_ESR': 'StanfordResearch_ESR'}, script, instr)

    print(script)
    print(failed)
    print(instr)