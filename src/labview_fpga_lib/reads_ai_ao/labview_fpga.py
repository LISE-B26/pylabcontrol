from src.core import Instrument, Parameter
from ctypes import c_uint32, c_int32



class NI7845R(Instrument):
    import src.labview_fpga_lib.reads_ai_ao.reads_ai_ao as FPGAlib
    session = c_uint32()
    status = c_int32()

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
        super(NI7845R, self).__init__(name, settings)

        print(self.start())

        self.update(self.settings)

    def __del__(self):
        self.stop()

    def start(self):
        self.FPGAlib.start_fpga(self.session, self.status)
        return self.status

    def stop(self):
        self.FPGAlib.stop_fpga(self.session, self.status)



    def read_probes(self, key):
        assert key in self._PROBES.keys(), "key assertion failed %s" % str(key)
        print('self.is_connected', self.is_connected)
        # value = getattr(self.FPGAlib, 'read_{:s}'.format(key))(self.session, self.status)
        value = 0
        return value


    def update(self, settings):
        super(NI7845R, self).update(settings)

        # for key, value in settings.iteritems():
        #     if key in ['AO0', 'AO1', 'AO2', 'AO3', 'AO4', 'AO5', 'AO6', 'AO7']:
        #         getattr(self.FPGAlib, 'set_{:s}'.format(key))(value, self.session, self.status)

if __name__ == '__main__':

    fpga = NI7845R()

    print(fpga.settings)

