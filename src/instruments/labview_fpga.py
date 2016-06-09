from src.core import Instrument, Parameter
from src.labview_fpga_lib.labview_fpga_error_codes import LabviewFPGAException

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
class NI7845RReadWrite(Instrument):

    import src.labview_fpga_lib.read_ai_ao.read_ai_ao as FPGAlib

    _DEFAULT_SETTINGS = Parameter([
        Parameter('AO0', 0.0, float, 'analog output channel 0 in volt'),
        Parameter('AO1', 0.0, float, 'analog output channel 1 in volt'),
        Parameter('AO2', 0.0, float, 'analog output channel 2 in volt'),
        Parameter('AO3', 0.0, float, 'analog output channel 3 in volt'),
        Parameter('AO4', 0.0, float, 'analog output channel 4 in volt'),
        Parameter('AO5', 0.0, float, 'analog output channel 5 in volt'),
        Parameter('AO6', 0.0, float, 'analog output channel 6 in volt'),
        Parameter('AO7', 0.0, float, 'analog output channel 7 in volt'),
        Parameter('DIO4', False, bool, 'digital output channel 4 on/off'),
        Parameter('DIO5', False, bool, 'digital output channel 5 on/off'),
        Parameter('DIO6', False, bool, 'digital output channel 6 on/off'),
        Parameter('DIO7', False, bool, 'digital output channel 7 on/off')
    ])

    _PROBES = {
        'AI0': 'analog input channel 0 in bit',
        'AI1': 'analog input channel 1 in bit',
        'AI2': 'analog input channel 2 in bit',
        'AI3': 'analog input channel 3 in bit',
        'AI4': 'analog input channel 4 in bit',
        'AI5': 'analog input channel 5 in bit',
        'AI6': 'analog input channel 6 in bit',
        'AI7': 'analog input channel 7 in bit',
        'DIO0': 'digital input channel 0',
        'DIO1': 'digital input channel 1',
        'DIO2': 'digital input channel 2',
        'DIO3': 'digital input channel 3'
    }
    def __init__(self, name = None, settings = None):
        super(NI7845RReadWrite, self).__init__(name, settings)

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
        super(NI7845RReadWrite, self).update(settings)

        for key, value in settings.iteritems():
            if key in ['AO0', 'AO1', 'AO2', 'AO3', 'AO4', 'AO5', 'AO6', 'AO7']:
                getattr(self.FPGAlib, 'set_{:s}'.format(key))(volt_2_bit(value), self.fpga.session, self.fpga.status)
            elif key in ['DIO4', 'DIO5', 'DIO6', 'DIO7']:
                getattr(self.FPGAlib, 'set_{:s}'.format(key))(value, self.fpga.session, self.fpga.status)

# ==================================================================================
# simple fpga program that implements a PID loop and can read data quickly into a buffer
# ==================================================================================
class NI7845RPidSimpleLoop(Instrument):
    # NOT WORKING!!!
    import src.labview_fpga_lib.pid_loop_simple.pid_loop_simple as FPGAlib

    _DEFAULT_SETTINGS = Parameter([
        Parameter('ElementsToWrite', 500, int, 'total elements to write to buffer'),
        Parameter('PiezoOut', 0.0, float, 'piezo output in volt'),
        Parameter('Setpoint', 0.0, float, 'set point for PID loop in volt'),
        Parameter('SamplePeriodsPID', int(4e5), int, 'sample period of PID loop in ticks (40 MHz)'),
        Parameter('SamplePeriodsAcq', 200, int, 'sample period of acquisition loop in ticks (40 MHz)'),
        Parameter('gains', [
            Parameter('proportional', 0, int, 'proportional gain of PID loop in ??'),
            Parameter('integral', 0, int, 'integral gain of PID loop in ??'),
        ]),
        Parameter('PI_on', False, bool, 'turn PID loop on/off'),
        Parameter('Acquire', False, bool, 'data acquisition on/off'),
        Parameter('fifo_size', int(2**12), int, 'size of fifo for data acquisition'),
        Parameter('TimeoutBuffer', 0, int, 'time after which buffer times out in clock ticks (40MHz)')
    ])

    _PROBES = {
        'AI1': 'analog input channel 1',
        'AI1_filtered': 'analog input channel 1',
        'AI2': 'analog input channel 2',
        'DeviceTemperature': 'device temperature of fpga',
        'ElementsWritten' : 'elements written to DMA'
    }
    def __init__(self, name = None, settings = None):
        super(NI7845RPidSimpleLoop, self).__init__(name, settings)

        # start fpga
        self.fpga = self.FPGAlib.NI7845R()
        print('===== start fpga =======')
        self.fpga.start()
        print('===== update fpga =======')
        print(self.settings)
        self.update(self.settings)

    def __del__(self):
        print('stopping fpga NI7845RPidSimpleLoop')
        self.fpga.stop()

    def read_probes(self, key):
        assert key in self._PROBES.keys(), "key assertion failed %s" % str(key)
        value = getattr(self.FPGAlib, 'read_{:s}'.format(key))(self.fpga.session, self.fpga.status)
        return value


    def update(self, settings):
        super(NI7845RPidSimpleLoop, self).update(settings)

        for key, value in settings.iteritems():
            if key in ['PiezoOut']:
                if self.settings['PI_on'] == True:
                    print('PI is active, manual piezo control not active!')
                else:
                    getattr(self.FPGAlib, 'set_{:s}'.format(key))(volt_2_bit(value), self.fpga.session, self.fpga.status)
            elif key in ['Setpoint']:
                getattr(self.FPGAlib, 'set_{:s}'.format(key))(volt_2_bit(value), self.fpga.session, self.fpga.status)
            elif key in ['PI_on']:
                getattr(self.FPGAlib, 'set_PIDActive')(value, self.fpga.session, self.fpga.status)
            elif key in ['Acquire']:
                getattr(self.FPGAlib, 'set_AcquireData')(value, self.fpga.session, self.fpga.status)
            elif key in ['gains']:
                if 'proportional' in value:
                    getattr(self.FPGAlib, 'set_PI_gain_prop')(value['proportional'], self.fpga.session, self.fpga.status)
                if 'integral' in value:
                    getattr(self.FPGAlib, 'set_PI_gain_int')(value['integral'], self.fpga.session, self.fpga.status)
            elif key in ['ElementsToWrite', 'sample_period_PI', 'SamplePeriodsAcq', 'PI_on']:
                getattr(self.FPGAlib, 'set_{:s}'.format(key))(value, self.fpga.session, self.fpga.status)
            elif key in ['fifo_size']:
                actual_fifo_size = self.FPGAlib.configure_FIFO_AI(value, self.fpga.session, self.fpga.status)
                print('requested ', value )
                print('actual_fifo_size ', actual_fifo_size)

    def start_fifo(self):
        self.FPGAlib.start_FIFO_AI(self.fpga.session, self.fpga.status)

    def stop_fifo(self):
        self.FPGAlib.stop_FIFO_AI(self.fpga.session, self.fpga.status)


    def read_fifo(self, block_size):
        '''
        read a block of data from the FIFO
        :return: data from channels AI1 and AI2 and the elements remaining in the FIFO
        '''

        fifo_data = self.FPGAlib.read_FIFO_AI(block_size, self.fpga.session, self.fpga.status)

        if str(self.fpga.status) != 0:
            raise LabviewFPGAException(self.fpga.status)

        return fifo_data



# ==================================================================================
# simple fpga program that reads data fromt the FPGA FIFO
# ==================================================================================
class NI7845RReadFifo(Instrument):

    import src.labview_fpga_lib.read_fifo.read_fifo as FPGAlib

    _DEFAULT_SETTINGS = Parameter([
        Parameter('ElementsToWrite', 500, int, 'total elements to write to buffer'),
        Parameter('SamplePeriodsAcq', 200, int, 'sample period of acquisition loop in ticks (40 MHz)'),        Parameter('PI_on', False, bool, 'turn PID loop on/off'),
        Parameter('Acquire', False, bool, 'data acquisition on/off'),
        Parameter('fifo_size', int(2**12), int, 'size of fifo for data acquisition')
    ])

    _PROBES = {
        'AI1': 'analog input channel 1',
        'AI2': 'analog input channel 2',
        'ElementsWritten' : 'elements written to DMA'
    }
    def __init__(self, name = None, settings = None):
        super(NI7845RReadFifo, self).__init__(name, settings)

        # start fpga
        self.fpga = self.FPGAlib.NI7845R()
        print('===== start fpga =======')
        self.fpga.start()
        print('===== update fpga =======')
        print(self.settings)
        self.update(self.settings)

    def __del__(self):
        print('stopping fpga {:s}'.format(self.name))
        self.fpga.stop()

    def read_probes(self, key):
        assert key in self._PROBES.keys(), "key assertion failed %s" % str(key)
        value = getattr(self.FPGAlib, 'read_{:s}'.format(key))(self.fpga.session, self.fpga.status)
        return value


    def update(self, settings):
        super(NI7845RReadFifo, self).update(settings)

        for key, value in settings.iteritems():
            if key in ['Acquire']:
                getattr(self.FPGAlib, 'set_AcquireData')(value, self.fpga.session, self.fpga.status)
            elif key in ['ElementsToWrite', 'SamplePeriodsAcq']:
                getattr(self.FPGAlib, 'set_{:s}'.format(key))(value, self.fpga.session, self.fpga.status)
            elif key in ['fifo_size']:
                actual_fifo_size = self.FPGAlib.configure_FIFO_AI(value, self.fpga.session, self.fpga.status)
                print('requested ', value )
                print('actual_fifo_size ', actual_fifo_size)

    def start_fifo(self):
        self.FPGAlib.start_FIFO_AI(self.fpga.session, self.fpga.status)

    def stop_fifo(self):
        self.FPGAlib.stop_FIFO_AI(self.fpga.session, self.fpga.status)


    def read_fifo(self, block_size):
        '''
        read a block of data from the FIFO
        :return: data from channels AI1 and AI2 and the elements remaining in the FIFO
        '''

        fifo_data = self.FPGAlib.read_FIFO_AI(block_size, self.fpga.session, self.fpga.status)
        if str(self.fpga.status.value) != '0':
            raise LabviewFPGAException(self.fpga.status)

        return fifo_data

# ==================================================================================
# fpga program that performs a galvo scan
# ==================================================================================
class NI7845RGalvoScan(Instrument):

    import src.labview_fpga_lib.galvo_scan.galvo_scan as FPGAlib

    _DEFAULT_SETTINGS = Parameter([
        Parameter('point_a',
                  [Parameter('x', -0.4, float, 'x-coordinate'),
                   Parameter('y', -0.4, float, 'y-coordinate')
                   ]),
        Parameter('point_b',
                  [Parameter('x', 0.4, float, 'x-coordinate'),
                   Parameter('y', 0.4, float, 'y-coordinate')
                   ]),
        Parameter('RoI_mode', 'corner', ['corner', 'center'], 'mode to calculate region of interest.\n \
                                                       corner: pta and ptb are diagonal corners of rectangle.\n \
                                                       center: pta is center and pta is extend or rectangle'),
        Parameter('num_points',
                  [Parameter('x', 120, int, 'number of x points to scan'),
                   Parameter('y', 120, int, 'number of y points to scan')
                   ]),
        Parameter('time_per_pt', .001, [.001, .002, .005, .01, .015, .02], 'time in s to measure at each point'),
        Parameter('settle_time', .0002, [.0002], 'wait time between points to allow galvo to settle'),
        Parameter('fifo_size', int(2**12), int, 'size of fifo for data acquisition'),
        Parameter('scan_mode_x', 'forward', ['forward', 'backward', 'forward-backward'], 'scan mode (x) onedirectional or bidirectional'),
        Parameter('scan_mode_y', 'forward', ['forward', 'backward'], 'direction of scan (y)'),
    ])

    _PROBES = {
        'Detector Signal': 'detector signal (AI4)',
        'ElementsWritten' : 'elements written to DMA'
    }
    def __init__(self, name = None, settings = None):
        super(NI7845RGalvoScan, self).__init__(name, settings)

        # start fpga
        self.fpga = self.FPGAlib.NI7845R()
        print('===== start fpga =======')
        self.fpga.start()
        print('===== update fpga =======')
        print(self.settings)
        self.update(self.settings)

    def __del__(self):
        print('stopping fpga {:s}'.format(self.name))
        self.fpga.stop()

    def read_probes(self, key):
        assert key in self._PROBES.keys(), "key assertion failed %s" % str(key)
        value = getattr(self.FPGAlib, 'read_{:s}'.format(key))(self.fpga.session, self.fpga.status)
        return value


    def update(self, settings):
        raise NotImplementedError
        super(NI7845RGalvoScan, self).update(settings)

        for key, value in settings.iteritems():
            if key in ['point_a', 'point_b', 'RoI_mode', 'num_points']:
                update_scan_parameters()
            elif key in []:
            # if key in ['Acquire']:
            #     getattr(self.FPGAlib, 'set_AcquireData')(value, self.fpga.session, self.fpga.status)
            # elif key in ['ElementsToWrite', 'SamplePeriodsAcq']:
            #     getattr(self.FPGAlib, 'set_{:s}'.format(key))(value, self.fpga.session, self.fpga.status)
            # elif key in ['fifo_size']:
            #     actual_fifo_size = self.FPGAlib.configure_FIFO_AI(value, self.fpga.session, self.fpga.status)
            #     print('requested ', value )
            #     print('actual_fifo_size ', actual_fifo_size)

    def start_fifo(self):
        self.FPGAlib.start_FIFO_AI(self.fpga.session, self.fpga.status)

    def stop_fifo(self):
        self.FPGAlib.stop_FIFO_AI(self.fpga.session, self.fpga.status)


    def read_fifo(self, block_size):
        '''
        read a block of data from the FIFO
        :return: data from channels AI1 and AI2 and the elements remaining in the FIFO
        '''
        raise NotImplementedError
        fifo_data = self.FPGAlib.read_FIFO_AI(block_size, self.fpga.session, self.fpga.status)
        if str(self.fpga.status.value) != '0':
            raise LabviewFPGAException(self.fpga.status)

        return fifo_data


if __name__ == '__main__':
    import time
    import numpy as np
    from copy import deepcopy

    fpga = NI7845RReadFifo()

    print(fpga.settings)

        # reset FIFO
    block_size = 2**8

    N= 2*block_size
    dt = 2000



    time.sleep(0.1)
    print('----stop-----')
    fpga.stop_fifo()
    print('----config-----')
    fpga.update({'fifo_size': block_size * 2})
    print('----start-----')
    fpga.start_fifo()
    time.sleep(0.1)
    number_of_reads = int(np.ceil(1.0 * N / block_size))
    print('number_of_reads', number_of_reads)
    N_actual = number_of_reads * block_size

    # apply settings to instrument
    instr_settings = {
        'SamplePeriodsAcq': dt,
        'ElementsToWrite': N

    }
    fpga.update(instr_settings)
    time.sleep(0.1)

    print('----------')
    print(fpga.settings)
    print('----------')

    print('ElementsWritten: ', fpga.ElementsWritten)
    fpga.update({'Acquire': True})

    # time.sleep(1)
    print(fpga.settings)




    ai1 = np.zeros(N_actual)
    ai2 = np.zeros(N_actual)
    i = 0
    while i < number_of_reads:
        elem_written = fpga.ElementsWritten
        if elem_written>=block_size:
            data = fpga.read_fifo(block_size)
            # print(i, 'AI1', data['AI1'])
            print(i, 'elements_remaining', data['elements_remaining'])
            ai1[i * block_size:(i + 1) * block_size] = deepcopy(data['AI1'])
            ai2[i * block_size:(i + 1) * block_size] = deepcopy(data['AI2'])
            i += 1

        print('-----', i, '------', 'elem_written', elem_written)

    print(ai1)
    print('------------------------------------------------')
    print(ai2)

