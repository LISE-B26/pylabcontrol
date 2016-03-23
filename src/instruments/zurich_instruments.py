from src.core import Instrument,Parameter
import numpy as np


# =============== ZURCIH INSTRUMENTS =======================
# ==========================================================
class ZIHF2(Instrument):

    try:
        import zhinst.utils as utils
        _is_connected = True
    except ImportError:
        # make a fake ZI instrument
        _is_connected = False
    except:
        raise

    '''
    instrument class to talk to Zurich instrument HF2 lock in ampifier
    '''
    def __init__(self, name = None, parameters = None):

        if self._is_connected:
            self.daq = self.utils.autoConnect(8005,1) # connect to ZI, 8005 is the port number
            self.device = self.utils.autoDetect(self.daq)
            self.options = self.daq.getByte('/%s/features/options' % self.device)
        else:
            self.daq = None
            self.device = None
            self.options = None

        super(ZIHF2, self).__init__(name, parameters)
        # apply all settings to instrument
        self.update(self.parameters)

    def _commands_from_parameters(self, parameters):
        '''
        converts dictionary to list of  setting, which can then be passed to the zi controler
        :param parameters = dictionary that contains the settings
        :return: settings = list of settings, which can then be passed to the zi controler
        '''
        # create list that is passed to the ZI controler


        settings = []

        for key, element in sorted(parameters.iteritems()):
            if isinstance(element, dict) and key in ['sigins', 'sigouts', 'demods']:
                # channel = self.parameters['sigouts']['channel']
                channel = element['channel']
                # print('verify channel (sigins, sigouts, demods)', channel)
                for sub_key, val in sorted(element.iteritems()):
                    if not sub_key == 'channel':
                        settings.append(['/%s/%s/%d/%s'%(self.device, key, channel, sub_key), val])
            elif isinstance(element, dict) and key in ['aux']:
                # channel = get_elemet('aux', self.parameters).as_dict()['aux']['channel']
                channel = element['channel']
                # print('verify channel (aux)', channel)
                settings.append(['/%s/AUXOUTS/%d/OFFSET'% (self.device, channel), element['offset']])
            elif key in ['freq']:
                # channel = get_elemet('sigouts', self.parameters).as_dict()['sigouts']['channel']
                channel = self.parameters['sigouts']['channel']
                # print('verify channel (freq)', channel)
                settings.append(['/%s/oscs/%d/freq' % (self.device, channel), parameters['freq']])
                # settings.append(['/%s/oscs/%d/freq' % (self.device, dictionary['sigouts']['channel']), dictionary['freq']])
            elif isinstance(element, dict) == False:
                settings.append([key, element])

        return settings

    # ========================================================================================
    # ======= overwrite functions from instrument superclass =================================
    # ========================================================================================
    @property
    def _parameters_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''

        parameters_default = Parameter([
            Parameter('freq', 1e6, float, 'frequency of output channel'),
            Parameter('sigins',
                      [
                          Parameter('channel', 0, [0,1], 'signal input channel'),
                          Parameter('imp50', 1, [0,1], '50Ohm impedance on (1) or off (0)'),
                          Parameter('ac', False, bool, 'ac coupling on (1) or off (0)'),
                          Parameter('range', 10.0, [0.01, 0.1, 1.0, 10.0], 'range of signal input'),
                          Parameter('diff',  False, bool, 'differential signal on (1) or off (0)')
                       ]
                      ),
            Parameter('sigouts',
                      [
                          Parameter('channel', 0, [0,1], 'signal output channel'),
                          Parameter('on',  False, bool, 'output on (1) or off (0)'),
                          Parameter('add',  False, bool, 'add aux signal on (1) or off (0)'),
                          Parameter('range', 10, [0.01, 0.1, 1, 10], 'range of signal output')
                       ]
                      ),
            Parameter('demods',
                      [
                          Parameter('channel', 0, [0,1], 'demodulation channel'),
                          Parameter('order', 4, int, 'filter order'),
                          Parameter('rate', 10e3, [10e3], 'rate'),
                          Parameter('harmonic', 1, int, 'harmonic at which to demodulate'),
                          Parameter('phaseshift', 0.0, float, 'phaseshift of demodulation'),
                          Parameter('oscselect', 0, [0,1], 'oscillator for demodulation'),
                          Parameter('adcselect', 0, int, 'adcselect')
                       ]
                      ),
            Parameter('aux',
                      [
                          Parameter('channel', 0, [0,1], 'auxilary channel'),
                          Parameter('offset', 1.0, float, 'offset in volts')
                       ]
                      )
        ])

        return parameters_default

    def update(self, parameters):
        """
        updates the internal dictionary and sends changed values to instrument
        Args:
            parameters: parameters to be set
        """
        # call the update_parameter_list to update the parameter list
        super(ZIHF2, self).update(parameters)

        # now we actually apply these newsettings to the hardware
        commands = self._commands_from_parameters(parameters)
        if self.is_connected:
            self.daq.set(commands)
        else:
            print('hardware is not connected, the command to be send is:')
            print(commands)


    @property
    def _probes(self):
        '''

        Returns: a dictionary that contains the values that can be read from the instrument
        the key is the name of the value and the value of the dictionary is an info

        '''
        return {
            'input1': 'this is the input from channel 1',
            'R': 'the amplitude of the demodulation signal',
            'X': 'the X-quadrature of the demodulation signal',
            'Y': 'the Y-quadrature of the demodulation signal',
            'freq': 'the frequency of the output channel'
        }

    def read_probes(self, key):
        '''

        requests value from the instrument and returns it
        Args:
            key: name of requested value

        Returns: reads values from instrument

        '''
        assert key in self._probes.keys()

        if key.upper() in ['X', 'Y', 'R']:
            # these values we actually request from the instrument
            data = self.poll(key)
            data = data[key]
        elif key in ['freq']:
            # these values just look up in the parameter settings
            data = self.parameters['freq']

        return data

    @property
    def is_connected(self):
        '''
        check if instrument is active and connected and return True in that case
        :return: bool
        '''
        return self._is_connected


    # Poll the value of input 1 for polltime seconds and return the magnitude of the average data. Timeout is in milisecond.
    def poll(self,  variable = 'R', pollTime = 0.1, timeout = 500):
        '''
        :param variable: string or list of strings, which varibale to poll ('R', 'x', 'y')
        :param pollTime: set to
        :param timeout: 0.1s could be varibale in the future
        :return:
        '''

        print('warning! polling from ZI, pollTime and timeout still hardcoded')
        valid_variables = ['R','X','Y']

        if self.is_connected:
            path = '/%s/demods/%d/sample' % (self.device, self.demod_c)
            self.daq.subscribe(path)
            flat_dictionary_key = True
            data_poll = self.daq.poll(pollTime,timeout,1,flat_dictionary_key)
            data = {}
            for var in ['X','Y']:
                data.update({var: data_poll[path][var.lower()]})
            data.update({'R': np.sqrt(np.square(data['X'])+np.square(data['Y']))})

            if isinstance(variable,str):
                variable = [variable]
            return_variable = {k: data[k.upper()] for k in variable}
        else:
            return_variable = None

        return return_variable
