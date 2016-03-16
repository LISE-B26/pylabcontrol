import numpy as np
import ctypes

class PulseBlaster:

    CLOCK_FREQUENCY = ctypes.c_float(400.0)
    PULSE_PROGRAM = 0
    ON_FLAG = 0xE00000
    COMMAND2INT = {
        'CONTINUE': 0,
        'STOP': 1,
        'LOOP': 2,
        'END_LOOP': 3,
        'JSR': 4,
        'RTS': 5,
        'BRANCH': 6,
        'LONG_DELAY': 7,
        'WAIT': 8
    }
    IN_PROGRAMMING_MODE = False

    def __init__(self):
        self.pulse_blaster = ctypes.WinDLL('C:\Windows\System32\spinapi64.dll')

        status = self.pulse_blaster.pb_init()

        if status != 0:
            message = 'Error initializing the board: ' + str(self.pulse_blaster.pb_get_error())
            raise RuntimeError(message)

        self.pulse_blaster.close()

    def check_in_programming_mode(self):
        if not self.IN_PROGRAMMING_MODE:
            message = 'Attempted to program pulse blaster when not in programming mode.'
            raise RuntimeError(message)

    def program_command(self, pb_channel_code, command_type, command_argument, length_of_time):

        self.check_in_programming_mode()

        self.pulse_blaster.pb_core_clock(self.CLOCK_FREQUENCY)

        command_number = self.pulse_blaster.pb_inst_pbonly(pb_channel_code, self.COMMAND2INT[command_type],
                                                           command_argument, ctypes.c_double(length_of_time))

        return command_number

    def channels_to_pb_argument(self, channels):
        self.check_channels_are_valid(channels)
        binary_channel_code = int(np.sum([2**i for i in channels]))
        pb_channel_code = self.ON_FLAG | binary_channel_code
        return pb_channel_code

    def set_high_channels(self, channels):

        self.pulse_blaster.pb_init()
        self.pulse_blaster.pb_core_clock(self.CLOCK_FREQUENCY)
        pb_channel_code = self.channels_to_pb_argument(channels)

        self.start_programming_pb()
        instruction_number = self.program_command(pb_channel_code, 'BRANCH', 0, 100.0E-3)
        check_instruction_number(instruction_number)
        #self.pulse_blaster.pb_inst_pbonly(pb_channel_code, self.COMMAND2INT['BRANCH'], 0, ctypes.c_double(100.0E-3))
        self.end_programming_pb()
        self.pulse_blaster.pb_start()

    @staticmethod
    def check_instruction_number(inst_num):
        if inst_num == -99:
            message = 'An invalid parameter was send in a pulse blaster instruction.'
            raise ValueError(message)
        elif inst_num < 0:
            message = 'The pulseblaster returned an error upon sending an instruction to it.'
            raise RuntimeError(message)

    @staticmethod
    def check_channels_are_valid(channels):
        for channel_number in channels:
            if channel_number > 24 or channel_number < 0 or not isinstance(channel_number, (int, long)):
                message = 'Passed invalid channel number: ' + str(channel_number)
                raise ValueError(message)

    def turn_off_all_channels(self):
        self.set_high_channels([])

    def start_programming_pb(self):
        self.pulse_blaster.pb_start_programming(ctypes.c_int(self.PULSE_PROGRAM))
        self.IN_PROGRAMMING_MODE = True

    def end_programming_pb(self):
        self.pulse_blaster.pb_stop_programming()
        self.IN_PROGRAMMING_MODE = False

if __name__ == '__main__':
    pulse_blaster = PulseBlaster()
    #pulse_blaster.set_high_channels([0])