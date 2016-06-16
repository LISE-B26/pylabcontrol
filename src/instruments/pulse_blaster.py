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
        self.PBStateChange = namedtuple('PBStateChange', ('channel_bits', 'time'))


    def update(self, settings):
        # call the update_parameter_list to update the parameter list
        super(PulseBlaster, self).update(settings)

    def get_delay(self, channel_name_or_int):
        if isinstance(channel_name_or_int, str):
            channel_name = channel_name_or_int
            return self.settings[channel_name]['delay_time']

        elif isinstance(channel_name_or_int, int):
            channel_num = channel_name_or_int
            for key, value in self.settings:
                if isinstance(value, dict) and 'channel' in value.keys() and value['channel'] == channel_num:
                    return self.settings[key]['delay_time']

        raise AttributeError('Could not find delay of channel name or number: {s}'.format(str(channel_name_or_int)))

    @staticmethod
    def find_overlapping_pulses(pulse_collection):
        """
        Finds all overlapping pulses in a collection of pulses, and returns the clashing pulses. Note that only pulses
        with the same channel_id can be overlapping.

        Args:
            pulse_collection: An iterable collection of Pulse objects

        Returns:
            A list of length-2 tuples of overlapping pulses. Each pair of pulses has the earlier pulse in the first
            position

        """
        # put pulses into a dictionary, where key=channel_id and value = list of (start_time, end_time) for each pulse
        pulse_dict = {}
        for pulse in pulse_collection:
            pulse_dict.setdefault(pulse.channel_id, []).append((pulse.start_time,
                                                                pulse.start_time + pulse.duration))

        # for every channel_id, check every pair of pulses to see if they overlap
        overlapping_pulses = []
        for pulse_id, time_interval_list in pulse_dict.iteritems():
            for time_interval_pair in itertools.combinations(time_interval_list, 2):

                #this is the overlap condition for two pulses
                if time_interval_pair[0][0] < time_interval_pair[1][1] and time_interval_pair[1][0] < \
                        time_interval_pair[0][1]:
                    overlapping_pulse_1 = Pulse(pulse_id, time_interval_pair[0][0],
                                                time_interval_pair[0][1] - time_interval_pair[0][0])
                    overlapping_pulse_2 = Pulse(pulse_id, time_interval_pair[1][0],
                                                time_interval_pair[1][1] - time_interval_pair[1][0])

                    # if we find an overlap, add them to our list in ascending order of start_time
                    if overlapping_pulse_1.start_time < overlapping_pulse_2.start_time:
                        overlapping_pulses.append((overlapping_pulse_1, overlapping_pulse_2))
                    else:
                        overlapping_pulses.append((overlapping_pulse_2, overlapping_pulse_1))

        return overlapping_pulses


    def create_physical_pulse_seq(self, pulse_collection):
        """
        Creates the physical pulse sequence from a pulse_collection, adding delays to each pulse, and ensuring the first
        pulse starts at time = 0.

        Args:
            pulse_collection: An iterable collection of pulses, named tuples with (name, start_time, pulse_duration)

        Returns:
            A list of pulses.

        """

        # find the start time of the earliest pulse
        min_pulse_time = np.min([pulse.start_time for pulse in pulse_collection])

        assert min_pulse_time >= 0, 'pulse with negative start time detected, that is not a valid pulse'

        # add delays to each pulse
        delayed_pulse_collection = [Pulse(pulse.channel_id,
                                               pulse.start_time - self.get_delay(pulse.channel_id),
                                               pulse.duration)
                                    for pulse in pulse_collection]

        # make sure the pulses start at same time as min_pulse_time
        delayed_min_pulse_time = np.min([pulse.start_time for pulse in delayed_pulse_collection])
        if delayed_min_pulse_time < min_pulse_time:
            delayed_pulse_collection = [Pulse(pulse.channel_id,
                                                   pulse.start_time - delayed_min_pulse_time + min_pulse_time,
                                                   pulse.duration)
                                        for pulse in delayed_pulse_collection]

        # return the sorted list of pulses, sorted by when they start
        return delayed_pulse_collection

    def generate_pb_sequence(self, pulse_collection):
        """
        Creates a (ordered) list of PBStateChange objects for use with the pulseblaster API from a collection
        of Pulse's. Specifically, generate_pb_sequence generates a corresponding sequence of (bitstring, duration)
        objects that indicate the channels to keep on and for how long before the next instruction.

        Args:
            pulse_collection: An iterable collection of Pulse's

        Returns:
            A (ordered) list of PBStateChange objects that indicate what bitstrings to turn on at what times.

        """

        # Create a dictionary with key=time and val=list of channels to toggle at that time
        # Note: we do not specifically keep track of whether we toggle on or off at a given time (is not necessary)
        pb_command_dict = {}
        for pulse in pulse_collection:
            pb_command_dict.setdefault(pulse.start_time, []).append(1 << self.settings[pulse.channel_id]['channel'])
            pulse_end_time = pulse.start_time + pulse.duration
            pb_command_dict.setdefault(pulse_end_time, []).append(1 << self.settings[pulse.channel_id]['channel'])

        # Make sure we have a command at time=0, teh command to have nothing on.
        if 0 not in pb_command_dict.keys():
            pb_commend_dict[0] = 0

        # For each time, combine all of the channels we need to toggle into a single bit string, and add it to a
        # command list of PBStateChange objects
        pb_command_list = []
        for time, bit_strings  in pb_command_dict.iteritems():
            channel_bits = np.bitwise_or.reduce(bit_strings)
            pb_command_list.append(self.PBStateChange(channel_bits, time))

        # sort the list by the time a command needs to be placed
        pb_command_list.sort(key=lambda x: x.time)

        def change_to_propogating_signal(state_change_collection):

            propogating_state_changes = []
            for i in range(0, len(state_change_collection)-1):

                # for the first command, just take the bitstring of the first element
                if i == 0:
                    new_channel_bits = state_change_collection[0].channel_bits

                # otherwise, xor with the previous bitstring we computed (in propogating_state_changes)
                else:
                    new_channel_bits = propogating_state_changes[i-1].channel_bits ^ state_change_collection[i].channel_bits

                time_between_change = state_change_collection[i+1].time - state_change_collection[i].time
                propogating_state_changes.append(self.PBStateChange(new_channel_bits, time_between_change))

            return propogating_state_changes

        # change this list so that instead of absolute times, they are durations, and the bitstrings properly propogate
        # i.e., if we want to keep channel 0 on at t = 1000 but now want to turn on channel 4, our bitstring would be
        # 10001 = 17 for the command at this time.
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

    def get_name(self, channel):
        for key, value in self.settings:
            if 'channel' in value.keys() and value['channel'] == channel:
                return key

        raise AttributeError('Could not find instrument name attached to channel {s}'.format(channel))

if __name__=='__main__':

    pb = B26PulseBlaster()
