


class Parameter(object):
    def __init__(self, name, value, valid_values = None, info = None):
        '''

        :param name:
        :param value:
        :param valid_values: either a list of valid values, a type or a tuple of types
        :param info:
        :return:
        '''

        def assert_valid_value(valid_value):
            '''
            check if valid value is a valid input
            :param valid_value:
            :return: True or False
            '''
            valid = False
            if isinstance(valid_value, list):
                valid = True
            elif isinstance(valid_value, tuple):
                valid = True
                for element in valid_value:
                    if not isinstance(element, type):
                        valid = False
            elif isinstance(valid_value, type):
                valid = True
            elif valid_value == None:
                valid = True
            return valid


        if valid_values is None:
            valid_values = type(value)

        if info is None:
            info = 'N/A'

        assert assert_valid_value(valid_values), "valid_type has to be a type, tupple of type or list"
        assert isinstance(info, str), 'info has to be a string'

        self._data = {
            'name' : name,
            'value': value,
            'valid_values': valid_values,
            'info':info
            }

        assert self.isvalid(value), "value is not if valid type"

    def __repr__(self):
        return str(self.dict)

    def dict_to_str(self, dictonary):
        '''
        casts dict into a (nested) string name : value
        :return:
        '''
        # todo: correct indentation
        return_str = ''

        for key, val in dictonary.iteritems():
            if isinstance(val, dict):
                return_str += '{:s}:\n{:s}\n'.format(key, self.dict_to_str(val))
            else:
                return_str += '{:s}:\t {:s}\n'.format(key, str(val))

        return return_str.replace('\n','\n\t')
    @property
    def dict(self):
        def parameter_to_dict(parameter):
            '''
            casts parameter into a (nested) dictonary {name : value}
            :return:
            '''
            return_dict = {}
            # if value is a list of parameters
            if isinstance(parameter.value, list) and isinstance(parameter.value[0],Parameter):
                sub_dict = {}
                for element in parameter.value:
                    sub_dict.update(parameter_to_dict(element))
                return_dict.update({parameter.name : sub_dict})
            elif isinstance(parameter.value, Parameter):
                return_dict.update({parameter.name : parameter_to_dict(parameter.value)})
            elif isinstance(parameter, Parameter):
                return_dict.update({parameter.name : parameter.value})

            return return_dict

        return parameter_to_dict(self)
    @property
    def name(self):
        return self._data['name']

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self._data.update({'name' : value})
        else:
            raise TypeError('Wrong type! \
                             name should be a string')
    @property
    def value(self):
        return self._data['value']

    @value.setter
    def value(self, value):
        if self.isvalid(value):
            self._data.update({'value':value})
        else:
            raise TypeError('Wrong type! \
                             Type should be .. improve msg here')
    @property
    def info(self):
        return self._data['info']
    @info.setter
    def info(self, value):
        if isinstance(value, str):
            self._data.update({'info' : value})
        else:
            raise TypeError('Wrong type! \
                             info should be a string')

    def isvalid(self, value):
        '''
        checks if value is a valid parameter value
        :param value:
        :return: True or False depending if value is valid
        '''
        valid = False
        if isinstance(self._data['valid_values'], list):
            if value in self._data['valid_values']:
                valid = True
        elif isinstance(self._data['valid_values'], tuple):
            if type(value) in self._data['valid_values']:
                valid = True
        elif isinstance(self._data['valid_values'], type):
            if type(value) is self._data['valid_values']:
                valid = True

        return valid

    @property
    def valid_values(self):
        return self._data['valid_values']

    def __eq__(self, other):
        '''
        checks if two parameters have the same valid_values and name
        :param other:
        :return:
        '''

        is_equal = True
        if self.name != other.name:
            is_equal = False
        if self.valid_values != other.valid_values:
            is_equal = False
        return is_equal

    def update(self, other):
        if self == other:
            self.value = other.value
            self.info = other.info
        else:
            raise TypeError('Parameters are not of the same type! \
                             They should have the same name and same valid values')

class Instrument(object):
    '''
    generic instrument class
    '''
    def __init__(self, name = None):


        self._parameter_list = self.parameter_list_default

        if name is None:
            name = self.__class__.__name__
        self.name = name


    def __str__(self):

        def parameter_to_string(parameter):
            # print('parameter', parameter)
            return_string = ''
            # if value is a list of parameters
            if isinstance(parameter.value, list) and isinstance(parameter.value[0],Parameter):
                return_string += '{:s}\n'.format(parameter.name)
                for element in parameter.value:
                    return_string += parameter_to_string(element)
            elif isinstance(parameter, Parameter):
                return_string += '\t{:s}:\t {:s}\n'.format(parameter.name, str(parameter.value))

            return return_string

        output_string = '{:s} (class type: {:s})\n'.format(self.name, self.__class__.__name__)

        for parameter in self.parameter_list:
            # output_string += parameter_to_string(parameter)
            output_string += str(parameter)+'\n'
        return output_string

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self._name = value
        else:
            raise TypeError('Name has to be a string')
    @property
    def dict(self):
        '''
        returns the configuration of the instrument as a dictionary
        :return: nested dictionary with entries name and value
        '''
        # build dictionary

        config = {}
        for p in self._parameter_list:
            config.update(p.dict)

        return config


    @property
    def parameter_list_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''
        parameter_list_default = []
        return parameter_list_default

    @property
    def parameter_list(self):
        return self._parameter_list

    def update_parameter_list(self, parameter_list_new):
        '''
        updates the parameters if they exist
        :param parameter_list_new:
        :return:
        '''
        for parameter in parameter_list_new:
            # get index of parameter in default list
            index = [i for i, p in enumerate(self.parameter_list_default) if p == parameter]
            if len(index)>1:
                raise TypeError('Error: Dublicate parameter in default list')
            elif len(index)==1:
                self.parameter_list[index[0]].update(parameter)



class Instrument_Dummy(Instrument):
        '''
        dummy instrument class, just to see how the creation of a new instrument works
        '''
        def __init__(self, name = None, parameter_list = []):
            super(Instrument_Dummy, self).__init__(name)
            self.update_parameter_list(parameter_list)

        @property
        def parameter_list_default(self):
            '''
            returns the default parameter_list of the instrument
            :return:
            '''
            parameter_list_default = [
                Parameter('parameter 1', 0),
                Parameter('parameter 2', 2.0)
            ]
            return parameter_list_default


class ZIHF2(Instrument):
    import zhinst.utils as utils
    '''
    instrument class to talk to Zurich instrument HF2 lock in ampifier
    '''
    def __init__(self, name = None, parameter_list = []):


        self.daq = self.utils.autoConnect(8005,1) # connect to ZI, 8005 is the port number
        self.device = self.utils.autoDetect(self.daq)
        self.options = self.daq.getByte('/%s/features/options' % self.device)

        super(ZIHF2, self).__init__(name)
        self.update_parameter_list(self.parameter_list_default)

    @property
    def parameter_list_default(self):
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
                          Parameter('ac', 0, [0,1], 'ac coupling on (1) or off (0)'),
                          Parameter('range', 10, [0.01, 0.1, 1, 10], 'range of signal input'),
                          Parameter('diff', 0, [0,1], 'differential signal on (1) or off (0)')
                       ]
                      ),
            Parameter('sigouts',
                      [
                          Parameter('channel', 0, [0,1], 'signal output channel'),
                          Parameter('on', 1, [0,1], 'output on (1) or off (0)'),
                          Parameter('add', 0, [0,1], 'add aux signal on (1) or off (0)'),
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

    # Poll the value of input 1 for polltime seconds and return the magnitude of the average data. Timeout is in milisecond.
    def poll(self, pollTime, timeout = 500):
        path = '/%s/demods/%d/sample' % (self.device, self.demod_c)
        self.daq.subscribe(path)
        flat_dictionary_key = True
        data = self.daq.poll(pollTime,timeout,1,flat_dictionary_key)
        R = numpy.sqrt(numpy.square(data[path]['x'])+numpy.square(data[path]['y']))
        return(numpy.mean(R))

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
                channel = element['channel']
                for sub_key, val in sorted(element.iteritems()):
                    if not sub_key == 'channel':
                        settings.append(['/%s/%s/%d/%s'%(self.device, key, channel, sub_key), val])
            elif isinstance(element, dict) and key in ['aux']:
                settings.append(['/%s/AUXOUTS/%d/OFFSET'% (self.device, element['channel']), element['offset']])
            elif key in ['freq']:
                settings.append(['/%s/oscs/%d/freq' % (self.device, self.dict['sigouts']['channel']), dictionary['freq']])
                # settings.append(['/%s/oscs/%d/freq' % (self.device, dictionary['sigouts']['channel']), dictionary['freq']])
            elif isinstance(element, dict) == False:
                settings.append([key, element])


        return settings

    def update_parameter_list(self, parameter_list_new):
        # call the update_parameter_list to update the parameter list
        super(ZIHF2, self).update_parameter_list(parameter_list_new)
        # now we actually apply these newsettings to the hardware
        dictonary = {}
        for parameter in parameter_list_new:
            dictonary.update(parameter.dict)

        commands = self.dict_to_settings(dictonary)
        self.daq.set(commands)

class ZI_Sweeper(Instrument):

    def __init__(self, zihf2, name = None, parameter_list = []):
        '''

        :param zihf2: ZIHF2 instrument object
        :param name:
        :param parameter_list:
        :return:
        '''
        self.zihf2 = zihf2

        super(ZI_Sweeper, self).__init__(name)
        self.update_parameter_list(self.parameter_list_default)

    @property
    def parameter_list_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''

        parameter_list_default = [
            Parameter('start', 1.8e6, (float, int), 'start value of sweep'),
            Parameter('stop', 1.9e6, (float, int), 'end value of sweep'),
            Parameter('samplecount', 101, int, 'number of data points'),
            Parameter('gridnode', 'oscs/0/freq', ['oscs/0/freq', 'oscs/1/freq'], 'start value of sweep'),
            Parameter('xmapping', 0, [0, 1], 'mapping 0 = linear, 1 = logarithmic'),
            Parameter('bandwidthcontrol', 2, [2], '2 = automatic bandwidth control'),
            Parameter('scan', 0, [0, 1, 2], 'scan direction 0 = sequential, 1 = binary (non-sequential, each point once), 2 = bidirecctional (forward then reverse)'),
            Parameter('loopcount', 1, int, 'number of times it sweeps'),
            Parameter('averaging/sample', 1, int, 'number of samples to average over')

        ]
        return parameter_list_default


def test_parameter():
    passed =True

    try:

        p1 = Parameter('param', 0.0)
        p2 = Parameter('param', 0, int, 'test int')
        p3 = Parameter('param', 0.0, (int, float), 'test tupple')
        p4 = Parameter('param', 0.0, [0.0, 0.1], 'test list')
        print('passed single parameter test')

        p_nested = Parameter('param nested', p1, None, 'test list')
        p_nested = Parameter('param nested', p4, [p1,p4], 'test list')
        print('passed nested parameter test')
    except:
        passed =False

    return passed

def test_intrument():


    try:
        inst = Instrument_Dummy('my dummny')
        p_new = Parameter('parameter 1', 1)
        inst.update_parameter_list([p_new])

        inst = Instrument_Dummy('my dummny', [p_new])


        print("instrument class test passed")
    except:
        print("instrument test failed")

    try:
        zi = ZIHF2('my zi instrument')
        # test updating parameter
        zi.update_parameter_list([Parameter('freq', 2e6)])


        print("ZIHF2 instrument class test passed")
    except:
        print("ZIHF2 instrument test failed")


if __name__ == '__main__':

    # test_parameter()
    # test_intrument()

    zi = ZIHF2('my zi instrument')
    zi_sweep = ZI_Sweeper(zi, 'my zi sweeper')

    print(zi_sweep)
    print(zi_sweep.zihf2.device)
    #
    # zi = ZIHF2('my zi instrument')
    #
    # zi.update_parameter_list([Parameter('freq', 2e6)])
    # print(zi)
    # print('====')
    # print(zi.dict)
    # p1 = Parameter('param 1', 0.0)
    # p2 = Parameter('param 2', 0, int, 'test int')
    # p3 = Parameter('param 3', 0.0, (int, float), 'test tupple')
    # p4 = Parameter('param 4', 0.4, [0.4, 0.1], 'test list')
    # print('passed single parameter test')
    #
    # p_nested_1 = Parameter('param nested', [p1,p2], None, 'test list')
    # p_nested = Parameter('param nested 2', [p4, p3, p_nested_1], None, 'test list')
    # print('passed nested parameter test')
    #
    # print('======')
    # print(p_nested.dict_to_str(p_nested.dict))
    # print('======')
    # print(p_nested.dict)
