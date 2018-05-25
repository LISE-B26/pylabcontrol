
# This file is part of pylabcontrol, software for laboratory equipment control for scientific experiments.
# Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell
#
#
# pylabcontrol is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pylabcontrol is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pylabcontrol.  If not, see <http://www.gnu.org/licenses/>.


class Parameter(dict):
    def __init__(self, name, value=None, valid_values=None, info=None, visible=False):
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
            visible: boolean if true always show parameter if false hide it
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
                self._valid_values = {name: {k: v for d in value for k, v in d.valid_values.items()}}
                self.update({name: {k: v for d in value for k, v in d.items()}})
                self._info = {name: {k: v for d in value for k, v in d.info.items()}}
                self._visible = {name: {k: v for d in value for k, v in d.visible.items()}}

            else:
                self._valid_values = {name: valid_values}
                self.update({name: value})
                self._info = {name: info}
                self._visible = {name: visible}

        elif isinstance(name, (list, dict)) and value is None:

            self._valid_values = {}
            self._info = {}
            self._visible = {}
            if isinstance(name, dict):
                for k, v in name.items():
                    # convert to Parameter if value is a dict
                    if isinstance(v, dict):
                        v = Parameter(v)
                    self._valid_values.update({k: type(v)})
                    self.update({k: v})
                    self._info.update({k: ''})
                    self._visible.update({k: visible})
            elif isinstance(name, list) and isinstance(name[0], Parameter):
                for p in name:
                    for k, v in p.items():
                        self._valid_values.update({k: p.valid_values[k]})
                        self.update({k: v})
                        self._info.update({k: p.info[k]})
                        self._visible.update({k: p.visible[k]})
            else:
                raise TypeError('unknown input: ', name)

    def __setitem__(self, key, value):
        """
        overwrites the standard dictionary and checks if value is valid
        Args:
            key: dictionary key
            value: dictionary value

        """

        # print('AHHAHAH', self.valid_values)
        message = "{0} (of type {1}) is not in {2}".format(str(value), type(value), str(self.valid_values[key]))
        assert self.is_valid(value, self.valid_values[key]), message

        if isinstance(value, dict) and len(self)>0 and len(self) == len(self.valid_values):
            for k, v in value.items():
                    self[key].update({k:v})
        else:
            super(Parameter, self).__setitem__(key, value)

    def update(self, *args):
        """
        updates the values of the parameter, just as a regular dictionary
        """
        for d in args:
            for (key, value) in d.items():
                self.__setitem__(key, value)

    @property
    def visible(self):
        """

        Returns: if parameter should be shown (False) or hidden (True) in the GUI

        """
        return self._visible


    @property
    def valid_values(self):
        """
        Returns: valid value of the paramerer (a type like int, float or a list)
        """
        return self._valid_values

    @property
    def info(self):
        """

        Returns: a text describing the paramter

        """
        return self._info

    @staticmethod
    def is_valid(value, valid_values):
        """
        check is the value is valid
        Args:
            value: value to be tested
            valid_values: allowed valid values (type or list of values)

        Returns:

        """

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
            # valid = True
            for k ,v in value.items():
                valid = Parameter.is_valid(v, valid_values[k])
                if valid ==False:
                    break

        elif isinstance(value, dict) and valid_values == Parameter:
            valid = True

        elif isinstance(valid_values, list) and value in valid_values:
            valid = True

        return valid


if __name__ == '__main__':
    p = Parameter([
        Parameter('x', 1),
        Parameter('filter wheel', [
            Parameter('channel', 1, int, 'channel to which motor is connected'),
            Parameter('settle_time', 0.8, float, 'settling time'),
            Parameter('ND2.0', 4 * 2700, int, 'position corresponding to position 1'),
            Parameter('ND1.0', 4 * 1700, int, 'position corresponding to position 2'),
            Parameter('Red', 4 * 750, int, 'position corresponding to position 3'),
            Parameter('current_position', 'ND1.0', ['ND1.0', 'ND2.0', 'Red'],
                      'current position of filter wheel')
        ])
    ])
    print('asdad')
    print((p['filter wheel'], type(p['filter wheel'])))


    print('======')
    # print(p['filter wheel'].valid_values)
    print((p.valid_values['filter wheel']))
    #
    # p = Parameter({'a':1})
    # print(p)
    # p = Parameter('a', 1)
    # print(p)