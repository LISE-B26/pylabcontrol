from src.core import Instrument, Parameter
from src.labview_fpga_lib.labview_fpga_error_codes import LabviewFPGAException
import time
def volt_2_bit(volt):
    """
    converts a voltage value into a bit value
    Args:
        volt:

    Returns:

    """
    if isinstance(volt, (int, float)):
        bit = int(volt / 10. * 32768.)
    else:
        # convert to numpy array in case we received a list
        bit = [int(x / 10. * 32768.) for x in volt]
    return bit

def seconds_to_ticks(seconds, clock_speed = 40e6):
    """
    convert seconds to ticks
    Args:
        seconds: time in seconds
        clock_speed: clock speed in Hz
    Returns:
        time in ticks
    """

    if isinstance(seconds, (int, float)):
        ticks = int(clock_speed * seconds)
    else:
        # convert to numpy array in case we received a list
        ticks = [int(clock_speed * x) for x in seconds]

    return ticks

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
        self.fpga.start()
        self.update(self.settings)
        print('NI7845RPidSimpleLoop initialized')

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
        print('NI7845RReadFifo initialized')

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
        Parameter('time_per_pt', 0.25, [ 0.25, 0.5, 1.0, 2.0, 5.0, 10.0], 'time (ms) to measure at each point'),
        Parameter('settle_time', 0.1, [ 0.1, 0.2, 0.5, 1.0, 2.0], 'wait time (ms) between points to allow galvo to settle'),
        Parameter('fifo_size', int(2**12), int, 'size of fifo for data acquisition'),
        Parameter('scanmode_x', 'forward', ['forward', 'backward', 'forward-backward'], 'scan mode (x) onedirectional or bidirectional'),
        Parameter('scanmode_y', 'forward', ['forward', 'backward'], 'direction of scan (y)'),
        Parameter('detector_mode', 'DC', ['DC', 'RMS'], 'return mean (DC) or rms of detector signal')
    ])

    _PROBES = {
        # 'Detector Signal': 'detector signal (AI4)',
        'elements_written_to_dma' : 'elements written to DMA',
        'DMATimeOut': 'DMATimeOut',
        'ix': 'ix',
        'iy':'iy',
        'detector_signal':'detector_signal',
        'acquire':'acquire',
        'running':'running',
        'Nx': 'Nx',
        'Ny': 'Ny',
        'loop_time':'loop_time',
        'DMA_elem_to_write':'DMA_elem_to_write',
        'meas_per_pt':'meas_per_pt',
        'settle_time':'settle_time',
        'failed':'failed'
    }
    def __init__(self, name = None, settings = None):
        super(NI7845RGalvoScan, self).__init__(name, settings)

        # start fpga
        self.fpga = self.FPGAlib.NI7845R()
        self.fpga.start()
        self.update(self.settings)
        print('NI7845RGalvoScan initialized')

    def __del__(self):
        print('stopping fpga {:s}'.format(self.name))
        #define NiFpga_GalvoScan_Bitfile "C:\\Users\\Experiment\\PycharmProjects\\PythonLab\\src\\labview_fpga_lib\\galvo_scan\\NiFpga_GalvoScan.lvbitx" stop()

    def read_probes(self, key):
        assert key in self._PROBES.keys(), "key assertion failed %s" % str(key)
        if key == 'ElementsWritten':
            key = 'elements_written_to_dma'
        value = getattr(self.FPGAlib, 'read_{:s}'.format(key))(self.fpga.session, self.fpga.status)
        return value

    @staticmethod
    def pts_to_extent(pta, ptb, roi_mode):
        """

        Args:
            pta: point a
            ptb: point b
            roi_mode:   mode how to calculate region of interest
                        corner: pta and ptb are diagonal corners of rectangle.
                        center: pta is center and ptb is extend or rectangle

        Returns: extend of region of interest [xVmin, xVmax, yVmax, yVmin]

        """
        if roi_mode == 'corner':
            xVmin = min(pta['x'], ptb['x'])
            xVmax = max(pta['x'], ptb['x'])
            yVmin = min(pta['y'], ptb['y'])
            yVmax = max(pta['y'], ptb['y'])
        elif roi_mode == 'center':
            xVmin = pta['x'] - float(ptb['x']) / 2.
            xVmax = pta['x'] + float(ptb['x']) / 2.
            yVmin = pta['y'] - float(ptb['y']) / 2.
            yVmax = pta['y'] + float(ptb['y']) / 2.
        return [xVmin, xVmax, yVmax, yVmin]

    def update(self, settings):
        super(NI7845RGalvoScan, self).update(settings)

        for key, value in settings.iteritems():
            if key in ['point_a', 'point_b', 'RoI_mode', 'num_points']:
                [xVmin, xVmax, yVmax, yVmin] = self.pts_to_extent(self.settings['point_a'],
                                                                  self.settings['point_b'],
                                                                  self.settings['RoI_mode'])
                # convert volt to I16 values
                [xVmin, xVmax, yVmax, yVmin] = volt_2_bit([xVmin, xVmax, yVmax, yVmin])

                Nx, Ny = self.settings['num_points']['x'], self.settings['num_points']['y']

                dVmin_x = int((xVmax- xVmin) / Nx)
                dVmin_y = int((yVmax - yVmin) / Ny)

                getattr(self.FPGAlib, 'set_Vmin_x')(xVmin, self.fpga.session, self.fpga.status)
                getattr(self.FPGAlib, 'set_Vmin_y')(yVmin, self.fpga.session, self.fpga.status)
                getattr(self.FPGAlib, 'set_Nx')(Nx, self.fpga.session, self.fpga.status)
                getattr(self.FPGAlib, 'set_Ny')(Ny, self.fpga.session, self.fpga.status)
                getattr(self.FPGAlib, 'set_dVmin_x')(dVmin_x, self.fpga.session, self.fpga.status)
                getattr(self.FPGAlib, 'set_dVmin_y')(dVmin_y, self.fpga.session, self.fpga.status)

            elif key in ['scanmode_x', 'scanmode_y', 'detector_mode']:
                index = [i for i, x in enumerate(self._DEFAULT_SETTINGS.valid_values[key]) if x == value][0]
                getattr(self.FPGAlib, 'set_{:s}'.format(key))(index, self.fpga.session, self.fpga.status)
            elif key in ['settle_time']:
                settle_time = int(value*1e3)
                getattr(self.FPGAlib, 'set_settle_time')(settle_time, self.fpga.session, self.fpga.status)
            elif key in ['time_per_pt']:
                measurements_per_pt = int(value/0.25)
                getattr(self.FPGAlib, 'set_meas_per_pt')(measurements_per_pt, self.fpga.session, self.fpga.status)
            elif key in ['fifo_size']:
                actual_fifo_size = self.FPGAlib.configure_FIFO(value, self.fpga.session, self.fpga.status)
                # print('requested ', value )
                # print('actual_fifo_size ', actual_fifo_size)

    def start_fifo(self):
        self.FPGAlib.start_FIFO(self.fpga.session, self.fpga.status)

    def stop_fifo(self):
        self.FPGAlib.stop_FIFO(self.fpga.session, self.fpga.status)

    def start_acquire(self):
        """
        acquire a galvo scan with the parameters defined in self.settings
        Returns:
            data of galvo scan as numpy array with dimensions Nx Ny
        """

        self.stop_fifo()
        # start fifo
        self.start_fifo()

        max_attempts = 20
        # start scan
        i = 0
        while self.running == False:
            getattr(self.FPGAlib, 'set_acquire')(True, self.fpga.session, self.fpga.status)
            # print('XXX', self.running)
            i +=1
            # wait a little before trying again
            time.sleep(0.1)
            if i> max_attempts:
                print('starting FPGA failed!!!')
                break

    def abort_acquire(self):
        getattr(self.FPGAlib, 'set_abort')(True, self.fpga.session, self.fpga.status)

    def read_fifo(self, block_size):
        '''
        read a block of data from the FIFO
        :return: data from channels AI1 and AI2 and the elements remaining in the FIFO
        '''
        fifo_data = self.FPGAlib.read_FIFO(block_size, self.fpga.session, self.fpga.status)
        if str(self.fpga.status.value) != '0':
            raise LabviewFPGAException(self.fpga.status)
        # print('fifo data', fifo_data)
        return fifo_data




if __name__ == '__main__':
    import time
    import numpy as np
    from copy import deepcopy

    fpga = NI7845RGalvoScan()



    fpga.fpga.start()

    print(fpga.FPGAlib.setter_functions)
    print(fpga.settings)
    fpga.fpga.stop()


