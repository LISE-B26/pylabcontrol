


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

    @property
    def dict(self):
        return self._data
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
    def __init__(self, parameter_list = []):

        assert isinstance(parameter_list, list), 'parameter_list has to be a list'

        if parameter_list == []:
            self._parameter_list = self.parameter_list_default


    def __str__(self):
        output_string = 'class type {:s}\n'.format(self.__class__.__name__)
        for parameter in self.parameter_list:
            output_string += '{:s}:\t {:s}\n'.format(parameter.name, str(parameter.value))
        return output_string

    @property

    @property
    def config(self):
        '''
        returns the configuration of the instrument as a dictionary
        :return: dictionary with entries name and value
        '''
        # build dictionary
        config = {}
        for p in self._parameter_list:
            config.update({p['name'] : p['value']})

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
                self._parameter_list[index[0]].update(parameter)



class ZI_Sweeper(Instrument):
    def __init__(self):
        super(ZI_Sweeper, self).__init__()
    @property
    def parameter_list_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''
        parameter_list_default = []
        return parameter_list_default


class Instrument_Dummy(Instrument):
        '''
        dummy instrument class, just to see how the creation of a new instrument works
        '''
        def __init__(self):
            super(Instrument_Dummy, self).__init__()
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



    inst = Instrument_Dummy()
    p_new = Parameter('parameter 1', 1)
    inst.update_parameter_list([p_new])


    print("instrument test passed")
if __name__ == '__main__':

    # test_parameter()
    # test_intrument()
    inst = Instrument_Dummy()
    p_new = Parameter('parameter 1', 1)
    inst.update_parameter_list([p_new])
    print(inst)