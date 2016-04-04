
class Parameter(dict):
    def __init__(self, name, value = None, valid_values = None, info = None):
        """

        Parameter(name, value, valid_values, info)
        Parameter(name, value, valid_values)
        Parameter(name, value)
        Parameter({name: value})

        Future updates:
        Parameter({name1: value1, name2: value2})
        Parameter([p1, p2]), where p1 and p2 are parameter objects

        Args:
            name: name of parameter
            value: value of parameter can be any basic type or a list
            valid_values: defines which values are accepted for value can be a type or a list if not provided => type(value)
            info: description of parameter, if not provided => empty string

        """


        if isinstance(name, str):

            if valid_values is None:
                valid_values = type(value)

            assert isinstance(valid_values, (type,list))

            if info is None:
                info = ''
            assert isinstance(info, str)

            assert self.is_valid(value, valid_values)

            if isinstance(value, list) and isinstance(value[0], Parameter):
                #todo: check if folloing statement is correct: this should create a Parameter object and not a dict!
                self._valid_values = {name: {k: v for d in value for k, v in d.valid_values.iteritems()}}
                self.update({name: {k: v for d in value for k, v in d.iteritems()}})
                self._info = {name: {k: v for d in value for k, v in d.info.iteritems()}}

            else:
                self._valid_values = {name: valid_values}
                self.update({name: value})
                self._info = {name: info}

        elif isinstance(name, (list, dict)) and value is None:

            self._valid_values = {}
            self._info = {}
            if isinstance(name, dict):
                for k, v in name.iteritems():
                    # convert to Parameter if value is a dict
                    if isinstance(v, dict):
                        v = Parameter(v)
                    self._valid_values.update({k: type(v)})
                    self.update({k: v})
                    self._info.update({k: ''})
            elif isinstance(name, list) and isinstance(name[0], Parameter):
                for p in name:
                    c= 0
                    for k, v in p.iteritems():
                        c+=1
                        self._valid_values.update({k: p.valid_values[k]})
                        self.update(Parameter({k: v}))
                        self._info.update({k: p.info[k]})
            else:
                raise TypeError('unknown input: ', name)


    def __setitem__(self, key, value):
        assert self.is_valid(value, self.valid_values[key]), "{:s}(type {:s}) is not in {:s}".format(str(value), type(value), str(self.valid_values[key]))

        if isinstance(value, dict) and len(self)>0 and len(self) == len(self.valid_values):
            for k, v in value.iteritems():
                    self[key].update({k:v})
        else:
            super(Parameter, self).__setitem__(key, value)

    def update(self, *args):
        for d in args:
            for key, value in d.iteritems():
                self.__setitem__(key, value)

    @property
    def valid_values(self):
        return self._valid_values

    @property
    def info(self):
        return self._info

    @staticmethod
    def is_valid(value, valid_values):
        valid = False

        if isinstance(valid_values, type) and type(value) is valid_values:
            valid = True
        elif isinstance(valid_values, type) and valid_values == float and type(value) == int:
            #special case to allow ints as float inputs
            valid = True
        elif isinstance(value, dict) and isinstance(valid_values, dict):
            # check that all values actually exist in valid_values
            # assert value.keys() & valid_values.keys() == value.keys() # python 3 syntax
            assert set(value.keys()) & set(valid_values.keys()) == set(value.keys()) # python 2
            valid = True
            for k ,v in value.items():
                if type(v) is not valid_values[k]:
                    valid = True
        elif isinstance(valid_values, list) and value in valid_values:
            valid = True
        return valid