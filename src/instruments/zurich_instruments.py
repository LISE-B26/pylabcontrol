from src.core import Instrument,Parameter
import numpy as np


# =============== ZURCIH INSTRUMENTS =======================
# ==========================================================
class ZIHF2(Instrument):
    # COMMENT_ME

    try:
        import zhinst.utils as utils
        _is_connected = True
    except ImportError:
        # make a fake ZI instrument
        _is_connected = False
    except:
        raise

    _DEFAULT_SETTINGS = Parameter([
        Parameter('freq', 1e6, float, 'frequency of output channel'),
        Parameter('sigins',
                  [
                      Parameter('channel', 0, [0,1], 'signal input channel'),
                      Parameter('imp50',False, bool, '50Ohm impedance on (1) or off (0)'),
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
                      Parameter('range', 10.0, [0.01, 0.1, 1.0, 10.0], 'range of signal output')
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
                      Parameter('adcselect', 0, int, 'adcselect not sure what that is!?')
                   ]
                  ),
        Parameter('aux',
                  [
                      Parameter('channel', 0, [0,1], 'auxilary channel'),
                      Parameter('offset', 1.0, float, 'offset in volts')
                   ]
                  )
    ])

    _PROBES = {
            'input1': 'this is the input from channel 1',
            'R': 'the amplitude of the demodulation signal',
            'X': 'the X-quadrature of the demodulation signal',
            'Y': 'the Y-quadrature of the demodulation signal',
            'freq': 'the frequency of the output channel'
        }

    '''
    instrument class to talk to Zurich instrument HF2 lock in ampifier
    '''
    def __init__(self, name = None, settings = None):
        #COMMENT_ME

        self.daq = self.utils.autoConnect(8005,1) # connect to ZI, 8005 is the port number
        self.device = self.utils.autoDetect(self.daq)
        self.options = self.daq.getByte('/%s/features/options' % self.device)

        super(ZIHF2, self).__init__(name, settings)
        # apply all settings to instrument
        self.update(self.settings)


    # ========================================================================================
    # ======= overwrite old_functions from instrument superclass =================================
    # ========================================================================================

    def update(self, settings):
        '''
        updates the internal dictionary and sends changed values to instrument
        Args:
            commands: parameters to be set
        '''
        # call the update_parameter_list to update the parameter list
        super(ZIHF2, self).update(settings)


        def commands_from_settings(settings):
            '''
            converts dictionary to list of  setting, which can then be passed to the zi controler
            :param settings = dictionary that contains the commands
            :return: commands = list of commands, which can then be passed to the zi controler
            '''
            # create list that is passed to the ZI controler


            commands = []



            for key, element in sorted(settings.iteritems()):
                if isinstance(element, dict) and key in ['sigins', 'sigouts', 'demods']:
                    if 'channel' in element:
                        channel = element['channel']
                    else:
                        channel = self.settings[key]['channel']
                    for sub_key, val in sorted(element.iteritems()):
                        if not sub_key == 'channel':
                            commands.append(['/%s/%s/%d/%s'%(self.device, key, channel, sub_key), val])
                elif isinstance(element, dict) and key in ['aux']:
                    if 'channel' in element:
                        channel = element['channel']
                    else:
                        channel = self.settings['aux']['channel']
                    if 'offset' in element:
                        offset = element['offset']
                    else:
                        offset = self.settings['aux']['offset']
                        print('offset', offset)
                    commands.append(['/%s/AUXOUTS/%d/OFFSET'% (self.device, channel),offset ])
                elif key in ['freq']:
                    channel = self.settings['sigouts']['channel']
                    commands.append(['/%s/oscs/%d/freq' % (self.device, channel), settings['freq']])
                elif isinstance(element, dict) == False:
                    commands.append([key, element])


            return commands


        # now we actually apply these newsettings to the hardware
        commands = commands_from_settings(settings)
        if self.is_connected:
            try:
                self.daq.set(commands)
            except RuntimeError:
                print('runtime error. commands\n{:s}'.format(commands))
        else:
            print('hardware is not connected, the command to be send is:')
            print(commands)

    def read_probes(self, key):
        '''

        requests value from the instrument and returns it
        Args:
            key: name of requested value

        Returns: reads values from instrument

        '''
        assert key in self._PROBES.keys(), "key assertion failed {:s}".format(str(key))

        if key.upper() in ['X', 'Y', 'R']:
            # these values we actually request from the instrument
            data = self.poll(key)
            data = data[key]

        elif key in ['freq']:
            # these values just look up in the parameter settings
            data = self.settings['freq']

        return data

    @property
    def is_connected(self):
        '''
        check if instrument is active and connected and return True in that case
        :return: bool
        '''
        return self._is_connected


    # Poll the value of input 1 for polltime seconds and return the magnitude of the average data. Timeout is in milisecond.
    def poll(self,  variable = 'R', demod_c = 0, pollTime = 0.1, timeout = 500):
        """

        Args:
            variable: string or list of strings, which varibale to poll ('R', 'x', 'y')
            demod_c:
            pollTime: integration time
            timeout: 0.1s could be varibale in the future

        Returns: requested value from instrument as a dictionary {varible: array of values}

        """

        # print('warning! polling from ZI, pollTime and timeout still hardcoded')
        valid_variables = ['R','X','Y']

        if self.is_connected:
            path = '/%s/demods/%d/sample' % (self.device, demod_c)
            self.daq.subscribe(path)
            flat_dictionary_key = True
            data_poll = self.daq.poll(pollTime,timeout,1,flat_dictionary_key)
            data = {}
            for var in ['X','Y']:
                data.update({var: data_poll[path][var.lower()]})
            data.update({'R': np.sqrt(np.square(data['X'])+np.square(data['Y']))})

            if isinstance(variable,str):
                variable = [variable]

            # poll gives an array of values read from the instrument, here we are only instersted in the mean
            return_variable = {k: np.mean(data[k.upper()]) for k in variable}
        else:
            return_variable = None

        return return_variable
