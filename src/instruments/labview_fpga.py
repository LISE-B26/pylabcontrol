from src.core import Instrument, Parameter

def volt_2_bit(volt):
    """
    converts a voltage value into a bit value
    Args:
        volt:

    Returns:



    """

    bit = int(volt / 10. * 32768.)

    return bit

# ==================================================================================
# simple fpga program that reads analog inputs and outputs
# ==================================================================================
class NI7845RReadAnalogIO(Instrument):

    import src.labview_fpga_lib.read_ai_ao.read_ai_ao as FPGAlib

    _DEFAULT_SETTINGS = Parameter([
        Parameter('AO0', 0.0, float, 'analog output channel 0 in volt'),
        Parameter('AO1', 0.0, float, 'analog output channel 1 in volt'),
        Parameter('AO2', 0.0, float, 'analog output channel 2 in volt'),
        Parameter('AO3', 0.0, float, 'analog output channel 3 in volt'),
        Parameter('AO4', 0.0, float, 'analog output channel 4 in volt'),
        Parameter('AO5', 0.0, float, 'analog output channel 5 in volt'),
        Parameter('AO6', 0.0, float, 'analog output channel 6 in volt'),
        Parameter('AO7', 0.0, float, 'analog output channel 7 in volt')
    ])

    _PROBES = {
        'AI0': 'analog input channel 0 in bit',
        'AI1': 'analog input channel 1 in bit',
        'AI2': 'analog input channel 2 in bit',
        'AI3': 'analog input channel 3 in bit',
        'AI4': 'analog input channel 4 in bit',
        'AI5': 'analog input channel 5 in bit',
        'AI6': 'analog input channel 6 in bit',
        'AI7': 'analog input channel 7 in bit'
    }
    def __init__(self, name = None, settings = None):
        super(NI7845RReadAnalogIO, self).__init__(name, settings)

        # start fpga
        self.fpga = self.FPGAlib.NI7845R()
        self.fpga.start()
        self.update(self.settings)

    def __del__(self):
        self.fpga.stop()

    def read_probes(self, key):
        assert key in self._PROBES.keys(), "key assertion failed %s" % str(key)
        value = getattr(self.FPGAlib, 'read_{:s}'.format(key))(self.fpga.session, self.fpga.status)
        return value


    def update(self, settings):
        super(NI7845RReadAnalogIO, self).update(settings)

        for key, value in settings.iteritems():
            if key in ['AO0', 'AO1', 'AO2', 'AO3', 'AO4', 'AO5', 'AO6', 'AO7']:
                print('SGL_to_U32(value)', volt_2_bit(value))
                getattr(self.FPGAlib, 'set_{:s}'.format(key))(volt_2_bit(value), self.fpga.session, self.fpga.status)


# ==================================================================================
# simple fpga program that implements a PID loop and can read data quickly into a buffer
# ==================================================================================
class NI7845RPidSimpleLoop(Instrument):

    import src.labview_fpga_lib.pid_loop_simple.pid_loop_simple as FPGAlib

    _DEFAULT_SETTINGS = Parameter([
        Parameter('ElementsToWrite', 500, int, 'elements to write to buffer'),
        Parameter('PiezoOut', 0.0, float, 'piezo output in volt'),
        Parameter('Setpoint', 0.0, float, 'set point for PID loop in volt')
    ])

    _PROBES = {
        'AI1': 'analog input channel 1',
        'AI1_filtered': 'analog input channel 1',
        'AI2': 'analog input channel 2',
        'DeviceTemperature': 'device temperature of fpga'
    }
    def __init__(self, name = None, settings = None):
        super(NI7845RPidSimpleLoop, self).__init__(name, settings)

        # start fpga
        self.fpga = self.FPGAlib.NI7845R()
        self.fpga.start()
        self.update(self.settings)

    def __del__(self):
        self.fpga.stop()

    def read_probes(self, key):
        assert key in self._PROBES.keys(), "key assertion failed %s" % str(key)
        value = getattr(self.FPGAlib, 'read_{:s}'.format(key))(self.fpga.session, self.fpga.status)
        return value


    def update(self, settings):
        super(NI7845RPidSimpleLoop, self).update(settings)

        for key, value in settings.iteritems():
            if key in ['PiezoOut', 'Setpoint']:
                getattr(self.FPGAlib, 'set_{:s}'.format(key))(volt_2_bit(value), self.fpga.session, self.fpga.status)
            elif key in ['ElementsToWrite']:
                getattr(self.FPGAlib, 'set_{:s}'.format(key))(value, self.fpga.session, self.fpga.status)



if __name__ == '__main__':
    import time


    fpga = NI7845RPidSimpleLoop()

    print(fpga.settings)




