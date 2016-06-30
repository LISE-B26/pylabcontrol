from src.core.scripts import Script
from src.core import Parameter
from src.instruments import DAQ, B26PulseBlaster
import itertools

from PySide.QtCore import Signal, QThread
from src.plotting.plots_1d import plot_delay_counts, plot_pulses, update_pulse_plot, update_delay_counts
import numpy as np

MAX_AVERAGES_PER_SCAN = 1000000  # 1E6


class ExecutePulseBlasterSequence(Script, QThread):
    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter(None)

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster}

    _SCRIPTS = {}
    updateProgress = Signal(int)

    def __init__(self, instruments, scripts=None, name=None, settings=None, log_function=None, data_path=None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments,
                        log_function=log_function, data_path=data_path)
        QThread.__init__(self)

        self.num_daq_reads = 0
        self.num_averages = 0

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        normalization = 1

        self.pulse_sequences, self.num_loops, tau_list = self._create_pulse_sequences()

        self.data['tau_list': tau_list, 'counts': np.zeros(len(self.pulse_sequences))]
        count_data = np.zeros(len(self.pulse_sequences))

        num_daq_reads = 0
        for pulse in self.pulse_sequences[0]:
            if pulse.channel_id == 'apd_readout':
                num_daq_reads += 1

        (num_1E6_avg_pb_programs, remainder) = divmod(self.num_averages, MAX_AVERAGES_PER_SCAN)

        for average_loop in range(int(num_1E6_avg_pb_programs)):
            if self._abort:
                break
            print('loop ' + str(average_loop))
            num_loops_sweep = MAX_AVERAGES_PER_SCAN

            for index, sequence in enumerate(self.pulse_sequences):
                if self._abort:
                    break
                result = self._process_results(
                    self._single_sequence(sequence, num_loops_sweep, num_daq_reads))  # keep entire array
                count_data[index] = count_data[index] + result
                self.data['counts'][index] = count_data[index] * normalization  # make function
                self.sequence_index = index
                # self.updateProgress.emit(int(99 * (index + 1.0) / len(self.pulse_sequences) / num_1E6_avg_pb_programs + (99 * (average_loop / num_1E6_avg_pb_programs))))
                self.updateProgress.emit(self._calc_progress())

        if remainder != 0:
            num_loops_sweep = remainder
            for index, sequence in enumerate(self.pulse_sequences):
                if self._abort:
                    break
                result = self._process_results(self._single_sequence(sequence, num_loops_sweep, num_daq_reads))
                count_data[index] = count_data[index] + result
                self.data['counts'][index] = count_data[index] * normalization
                self.sequence_index = index
                self.updateProgress.emit(self._calc_progress())

        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()
            self.save_image_to_disk()

        self.updateProgress.emit(100)

    def _plot(self, axes_list):
        counts = self.data['counts']
        x_data = self.data['tau_list']
        axis1 = axes_list[0]
        if not counts == []:
            plot_delay_counts(axis1, x_data, counts)
        axis2 = axes_list[1]
        plot_pulses(axis2, self.pulse_sequences[self.sequence_index])

    def _update_plot(self, axes_list):
        counts = self.data['counts']
        x_data = self.data['tau_list']
        axis1 = axes_list[0]
        if not counts == []:
            update_delay_counts(axis1, x_data, counts)
        axis2 = axes_list[1]
        update_pulse_plot(axis2, self.pulse_sequences[self.sequence_index])

    def _single_sequence(self, pulse_sequence, num_loops, num_daq_reads):
        self.instruments['PB']['instance'].program_pb(pulse_sequence,
                                                      num_loops=num_loops)
        if self.num_daq_reads != 0:
            self.instruments['daq']['instance'].gated_DI_init('ctr0', int(self.num_loops * num_daq_reads))
            self.instruments['daq']['instance'].gated_DI_run()
        self.instruments['PB']['instance'].start_pulse_seq()
        if self.num_daq_reads != 0:
            result_array, _ = self.instruments['daq']['instance'].gated_DI_read(
                timeout=5)  # thread waits on DAQ getting the right number of gates
            for i in range(self.num_daq_reads):
                result = sum(itertools.islice(result_array, i, None, self.num_daq_reads))
        # clean up APD tasks
        if self.num_daq_reads != 0:
            self.instruments['daq']['instance'].gated_DI_stop()

        return result

    # MUST BE IMPLEMENTED IN INHERITING SCRIPT
    def _create_pulse_sequences(self):
        raise NotImplementedError

    def _calc_progress(self):
        self.updateProgress.emit(50)

    def _normalize_to_baseline(self, signal, baseline_max=0, baseline_min=0):
        if baseline_max == 0:
            return signal
        else:
            return ((signal - baseline_min) / (baseline_max - baseline_min))


if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'ExecutePulseBlasterSequence': 'ExecutePulseBlasterSequence'},
                                                   script, instr)

    print(script)
    print(failed)
    print(instr)
