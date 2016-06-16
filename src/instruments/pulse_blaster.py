from src.core import Instrument, Parameter, Pulse
from collections import namedtuple
import numpy as np
import itertools

class PulseBlaster(Instrument):

    _PROBES = {}

    _DEFAULT_SETTINGS = Parameter([
        Parameter('output_0', [
            Parameter('channel', 0, int, 'channel to which laser is connected'),
            Parameter('status', False, bool, 'True if voltage is high to the laser, false otherwise'),
            Parameter('delay_time', 0.2, float, 'delay time between pulse sending time and laser switch on [ns]')
        ]),
        Parameter('output_1', [
            Parameter('channel', 1, int, 'channel to which the daq is connected to'),
            Parameter('status', False, bool, 'True if voltage is high to the daq, false otherwise'),
            Parameter('delay_time', 0.2, float, 'delay time between pulse sending time and daq acknowledgement [ns]')
        ]),
        Parameter('output_2', [
            Parameter('channel', 2, int, 'channel to which the the microwave p trigger is connected to'),
            Parameter('status', False, bool, 'True if voltage is high to the microwave p trigger, false otherwise'),
            Parameter('delay_time', 0.2, float, 'delay time between pulse sending time and microwave p trigger [ns]')
        ]),
        Parameter('output_3', [
            Parameter('channel', 3, int, 'channel to which the the microwave q trigger is connected to'),
            Parameter('status', False, bool, 'True if voltage is high to the microwave q trigger, false otherwise'),
            Parameter('delay_time', 0.2, float, 'delay time between pulse sending time and microwave q trigger [ns]')
        ]),
        Parameter('output_4', [
            Parameter('channel', 4, int, 'channel to which the microwave switch is connected to'),
            Parameter('status', False, bool, 'True if voltage is high to the microwave switch, false otherwise'),
            Parameter('delay_time', 0.2, float, 'delay time between pulse sending time and microwave switch [ns]')
        ])
    ])

    def __init__(self, name = None, settings = None):
        super(PulseBlaster, self).__init__(name, settings)
        self.Pulse = namedtuple('Pulse', ('channel_id', 'start_time', 'duration'))
        self.PBStateChange = namedtuple('PBStateChange', ('channel_bits', 'time'))


    def update(self, settings):
        # call the update_parameter_list to update the parameter list
        super(PulseBlaster, self).update(settings)

    def get_delay(self, channel_name_or_int):
        if isinstance(channel_name_or_int, str):
            channel_name = channel_name_or_int
            return self.settings[channel_name][delay_time]

        elif isinstance(channel_name_or_int, int):
            channel_num = channel_name_or_int
            for key, value in self.settings:
                if isinstance(value, dict) and 'channel' in value.keys() and value['channel'] == channel_num:
                    return self.settings[key][delay_time]

        raise AttributeError('Could not find delay of channel name or number: {s}'.format(str(channel_name_or_int)))

    @staticmethod
    def find_overlapping_pulses(pulse_collection):
        pulse_dict = {}
        for pulse in pulse_collection:
            pulse_dict.setdefault(pulse.channel_id, []).append((pulse.start_time,
                                                                pulse.start_time + pulse.duration))

        overlapping_pulses = []
        for pulse_id, time_interval_list in pulse_dict.iteritems():
            for time_interval_pair in itertools.combinations(time_interval_list, 2):
                if time_interval_pair[0][0] < time_interval_pair[1][1] and time_interval_pair[1][0] < \
                        time_interval_pair[0][1]:
                    overlapping_pulse_1 = Pulse(pulse_id, time_interval_pair[0][0],
                                                time_interval_pair[0][1] - time_interval_pair[0][0])
                    overlapping_pulse_2 = Pulse(pulse_id, time_interval_pair[1][0],
                                                time_interval_pair[1][1] - time_interval_pair[1][0])

                    if overlapping_pulse_1.start_time < overlapping_pulse_2.start_time:
                        overlapping_pulses.append((overlapping_pulse_1, overlapping_pulse_2))
                    else:
                        overlapping_pulses.append((overlapping_pulse_2, overlapping_pulse_1))

        return overlapping_pulses


    def create_physical_pulse_seq(self, pulse_collection):
        """

        Args:
            pulse_collection: A collection of pulses, named tuples with (name, start_time, pulse_duration)

        Returns:

        """

        overlapping_pulses = B26PulseBlaster.find_overlapping_pulses(pulse_collection)
        assert len(overlapping_pulses) == 0, "Could not proceed, found overlapping pulses: {0}".format(str(overlapping_pulses))

        delayed_pulse_collection = [self.Pulse(pulse.channel_id,
                                               pulse.start_time - self.get_delay(pulse.channel_id),
                                               pulse.duration)
                                    for pulse in pulse_collection]

        # make sure the pulses start at 0 time
        min_pulse_time = min(map(lambda pulse: pulse.start_time, delayed_pulse_collection))

        if min_pulse_time < 0:
            delayed_pulse_collection = [self.Pulse(pulse.channel_id,
                                                   pulse.start_time - min_pulse_time,
                                                   pulse.duration)
                                        for pulse in delayed_pulse_collection]

        # return the sorted list of pulses, sorted by when they start
        return delayed_pulse_collection

    def generate_pb_sequence(self, pulse_collection):

        pb_command_dict = {}
        for pulse in pulse_collection:
            pb_command_dict.setdefault(pulse.start_time, []).append(1 << self.settings[pulse.name]['channel'])
            pulse_end_time = pulse.start_time + pulse.duration
            pb_command_dict.setdefault(pulse.end_time,  []).append(1 << self.settings[pulse.name]['channel'])

        pb_command_list = []
        for time, bit_strings  in pb_command_dict:
            channel_bits = np.bitwise_or.reduce(bit_strings)
            pb_command_list.append(self.PBStateChange(channel_bits, time))

        pb_command_list.sort(key=lambda x: x.time)

        def change_to_propogating_signal(self, state_change_collection):

            for i in range(1, len(state_change_collection)):
                new_channel_bits = state_change_collection[i - 1] ^ state_change_collection[i]
                state_change_collection[i] = self.StateChange(state_change_collection[i].time, new_channel_bits)

            return state_change_collection


        pb_command_list = change_to_propogating_signal(pb_command_list)

        return pb_command_list


class B26PulseBlaster(PulseBlaster):
    _DEFAULT_SETTINGS = Parameter([
        Parameter('laser', [
            Parameter('channel', 0, int, 'channel to which laser is connected'),
            Parameter('status', False, bool, 'True if voltage is high to the laser, false otherwise'),
            Parameter('delay_time', 0.2, float, 'delay time between pulse sending time and laser switch on [ns]')
        ]),
        Parameter('apd_readout', [
            Parameter('channel', 1, int, 'channel to which the daq is connected to'),
            Parameter('status', False, bool, 'True if voltage is high to the daq, false otherwise'),
            Parameter('delay_time', 0.2, float, 'delay time between pulse sending time and daq acknowledgement [ns]')
        ]),
        Parameter('microwave_p', [
            Parameter('channel', 2, int, 'channel to which the the microwave p trigger is connected to'),
            Parameter('status', False, bool, 'True if voltage is high to the microwave p trigger, false otherwise'),
            Parameter('delay_time', 0.2, float, 'delay time between pulse sending time and microwave p trigger [ns]')
        ]),
        Parameter('microwave_q', [
            Parameter('channel', 3, int, 'channel to which the the microwave q trigger is connected to'),
            Parameter('status', False, bool, 'True if voltage is high to the microwave q trigger, false otherwise'),
            Parameter('delay_time', 0.2, float, 'delay time between pulse sending time and microwave q trigger [ns]')
        ]),
        Parameter('microwave_switch', [
            Parameter('channel', 4, int, 'channel to which the microwave switch is connected to'),
            Parameter('status', False, bool, 'True if voltage is high to the microwave switch, false otherwise'),
            Parameter('delay_time', 0.2, float, 'delay time between pulse sending time and microwave switch [ns]')
        ])
    ])

    _PROBES = {}

    def __init__(self, name=None, settings=None):
        super(B26PulseBlaster, self).__init__(name, settings)


    def update(self, settings):
        # call the update_parameter_list to update the parameter list
        # oh god this is confusing
        super(B26PulseBlaster, self).update(settings)

    def read_probes(self):
        pass


    def include_delays(self, pulse_collection):
        pass

    def run_program(self):
        pass

    # def create_physical_pulse_seq(self, pulse_collection):
    #
    #     return self.channel2name(super(B26PulseBlaster, self).create_physical_pulse_seq(pulse_collection))

    def get_name(self, channel):
        for key, value in self.settings:
            if 'channel' in value.keys() and value['channel'] == channel:
                return key

        raise AttributeError('Could not find instrument name attached to channel {s}'.format(channel))

    def get_channel(self, channel_id):
        if channel_id in self.settings.keys():
            return self.settings[channel_id]['channel']

        else:
            raise AttributeError('Could not find channel for instrument {s}'.format(channel_id))

    def get_delay(self, channel_id):
        if isinstance(channel_id, str):
            return self.settings[channel_id]['delay_time']
        else:
            for key, value in self.settings:
                if 'channel' in value.keys() and value['channel'] == channel_id:
                    return self.settings[channel_id]['delay_time']

if __name__=='__main__':

    pb = B26PulseBlaster()