from src.core import Instrument,Parameter
# =============== ZURCIH INSTRUMENTS =======================
# ==========================================================
class ZIHF2(Instrument):

    try:
        import zhinst.utils as utils
        _status = True
    except ImportError:
        # make a fake ZI instrument
        _status = False
    except:
        raise

    '''
    instrument class to talk to Zurich instrument HF2 lock in ampifier
    '''
    def __init__(self, name = None, parameter_list = []):

        if self._status:
            self.daq = self.utils.autoConnect(8005,1) # connect to ZI, 8005 is the port number
            self.device = self.utils.autoDetect(self.daq)
            self.options = self.daq.getByte('/%s/features/options' % self.device)
        else:
            self.daq = None
            self.device = None
            self.options = None

        super(ZIHF2, self).__init__(name, parameter_list)

    @property
    def _parameters_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''

        parameter_list_default = [
            Parameter('freq', 1e6, (int, float), 'frequency of output channel'),
            Parameter('sigins',
                      [
                          Parameter('channel', 0, [0,1], 'signal input channel'),
                          Parameter('imp50', 1, [0,1], '50Ohm impedance on (1) or off (0)'),
                          Parameter('ac', False, bool, 'ac coupling on (1) or off (0)'),
                          Parameter('range', 10, [0.01, 0.1, 1, 10], 'range of signal input'),
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
                          Parameter('phaseshift', 0, (int, float), 'phaseshift of demodulation'),
                          Parameter('oscselect', 0, [0,1], 'oscillator for demodulation'),
                          Parameter('adcselect', 0, int, 'adcselect')
                       ]
                      ),
            Parameter('aux',
                      [
                          Parameter('channel', 0, [0,1], 'auxilary channel'),
                          Parameter('offset', 1, (int, float), 'offset in volts')
                       ]
                      )
        ]

        return parameter_list_default




        return self.harware_detected
    # Poll the value of input 1 for polltime seconds and return the magnitude of the average data. Timeout is in milisecond.
    def poll(self,  pollTime, variable = 'R', timeout = 500):
        '''
        :param variable: string or list of string, which varibale to poll ('R', 'x', 'y')
        :param pollTime:
        :param timeout:
        :return:
        '''

        valid_variables = ['R','X','Y']

        if self.is_connected:
            path = '/%s/demods/%d/sample' % (self.device, self.demod_c)
            self.daq.subscribe(path)
            flat_dictionary_key = True
            data_poll = self.daq.poll(pollTime,timeout,1,flat_dictionary_key)
            data = {}
            for var in ['X','Y']:
                data.update({var: data_poll[path][var.lower()]})
            data.update({'R': np.sqrt(np.square(data['x'])+np.square(data['y']))})

            if isinstance(variable,str):
                variable = [variable]
            return_variable = {k: data[k] for k in variable}
        else:
            return_variable = None

        return return_variable

    def dict_to_settings(self, dictionary):
        '''
        converts dictionary to list of  setting, which can then be passed to the zi controler
        :param dictionary = dictionary that contains the settings
        :return: settings = list of settings, which can then be passed to the zi controler
        '''
        # create list that is passed to the ZI controler


        settings = []



        for key, element in sorted(dictionary.iteritems()):
            if isinstance(element, dict) and key in ['sigins', 'sigouts', 'demods']:
                # channel = element['channel']
                channel = get_elemet('sigouts', self.parameters).as_dict()['sigouts']['channel']
                for sub_key, val in sorted(element.iteritems()):
                    if not sub_key == 'channel':
                        settings.append(['/%s/%s/%d/%s'%(self.device, key, channel, sub_key), val])
            elif isinstance(element, dict) and key in ['aux']:
                channel = get_elemet('aux', self.parameters).as_dict()['aux']['channel']
                settings.append(['/%s/AUXOUTS/%d/OFFSET'% (self.device, channel), element['offset']])
            elif key in ['freq']:
                channel = get_elemet('sigouts', self.parameters).as_dict()['sigouts']['channel']
                settings.append(['/%s/oscs/%d/freq' % (self.device, channel), dictionary['freq']])
                # settings.append(['/%s/oscs/%d/freq' % (self.device, dictionary['sigouts']['channel']), dictionary['freq']])
            elif isinstance(element, dict) == False:
                settings.append([key, element])


        return settings

    def update_parameters(self, parameters_new):
        # call the update_parameter_list to update the parameter list
        parameters_new = super(ZIHF2, self).update_parameters(parameters_new)
        # now we actually apply these newsettings to the hardware

        commands = self.dict_to_settings(parameters_new)
        if self.is_connected:
            self.daq.set(commands)