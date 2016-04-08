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


class NI7845RReadAnalogIO(Instrument):

    import src.labview_fpga_lib.read_ai_ao.read_ai_ao as FPGAlib

    _DEFAULT_SETTINGS = Parameter([
        Parameter('AO0', 0.0, float, 'analog output channel 0'),
        Parameter('AO1', 0.0, float, 'analog output channel 1'),
        Parameter('AO2', 0.0, float, 'analog output channel 2'),
        Parameter('AO3', 0.0, float, 'analog output channel 3'),
        Parameter('AO4', 0.0, float, 'analog output channel 4'),
        Parameter('AO5', 0.0, float, 'analog output channel 5'),
        Parameter('AO6', 0.0, float, 'analog output channel 6'),
        Parameter('AO7', 0.0, float, 'analog output channel 7')
    ])

    _PROBES = {
        'AI0': 'analog input channel 0',
        'AI1': 'analog input channel 1',
        'AI2': 'analog input channel 2',
        'AI3': 'analog input channel 3',
        'AI4': 'analog input channel 4',
        'AI5': 'analog input channel 5',
        'AI6': 'analog input channel 6',
        'AI7': 'analog input channel 7'
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
        print('GG', settings)
        super(NI7845RReadAnalogIO, self).update(settings)

        for key, value in settings.iteritems():
            if key in ['AO0', 'AO1', 'AO2', 'AO3', 'AO4', 'AO5', 'AO6', 'AO7']:
                print('SGL_to_U32(value)', volt_2_bit(value))
                getattr(self.FPGAlib, 'set_{:s}'.format(key))(volt_2_bit(value), self.fpga.session, self.fpga.status)

if __name__ == '__main__':
    import time


    fpga = NI7845RReadAnalogIO()

    print(fpga.settings)

    print(fpga.AI0)
    print(fpga.AI1)
    print(fpga.AI2)
    print(fpga.AI3)



    print('a', fpga.AI7)
    fpga.update({'AO4':-2.0})
    time.sleep(0.3)
    print('b', fpga.AI7)
    fpga.update({'AO4': -1.0})
    time.sleep(0.3)
    print('c', fpga.AI7)


