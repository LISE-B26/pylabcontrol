


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

class Instrument(object):
    '''
    generic instrument class
    '''
    def __init__(self, config = None):

        if config ==None:
            config = self.config_default

        for key, val in config:
            self.set_parameter(key, val)


    @property
    def config(self):
        '''
        returns the configuration of the instrument as a dictionary
        :return:
        '''
        return self._config


    @property
    def config_default(self):
        '''
        returns the default configuration of the instrument as a dictionary
        :return:
        '''

        return self._config_default

    def set_parameter(self, parameter):
        if parameter in self._parameter_list:
            self._config


def test_parameter():
    passed =True

    try:
        p = Parameter('param', 0.0)
        p = Parameter('param', 0, int, 'test int')
        p = Parameter('param', 0.0, (int, float), 'test tupple')
        p = Parameter('param', 0.0, [0.0, 0.1], 'test list')
    except:
        passed =False

    return passed

if __name__ == '__main__':
    # print(test_parameter())
    p1 = Parameter('param1', 0.0, (int, float), 'test tupple')
    p2 = Parameter('param1', 'X', str, 'test X')
    parameter_list = [p1,p2]

    for p in parameter_list:
        print(p.name)