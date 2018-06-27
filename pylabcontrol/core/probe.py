
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


from pylabcontrol.core.instrument import Instrument
from collections import deque
from pylabcontrol.core.read_write_functions import save_b26_file

class Probe(object):


    def __init__(self, instrument, probe_name, name = None, info = None, buffer_length = 100):
        """
        creates a probe...
        Args:
            name (optinal):  name of probe, if not provided take name of function
            settings (optinal): a Parameter object that contains all the information needed in the script
        """


        assert isinstance(instrument, Instrument)
        assert isinstance(probe_name, str)
        assert probe_name in instrument._PROBES


        if name is None:
            name = probe_name
        assert isinstance(name, str)

        if info is None:
            info = ''
        assert isinstance(info, str)

        self.name = name
        self.info = info
        self.instrument = instrument
        self.probe_name = probe_name

        self.buffer = deque(maxlen = buffer_length)


    @property
    def value(self):
        """
        reads the value from the instrument
        """

        value = getattr(self.instrument, self.probe_name)
        self.buffer.append(value)

        return value

    def __str__(self):
        output_string = '{:s} (class type: {:s})\n'.format(self.name, self.__class__.__name__)
        return output_string
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        assert isinstance(value, str)
        self._name = value

    def plot(self, axes):
        axes.plot(self.buffer)
        axes.hold(False)

    def to_dict(self):
        """

        Returns: itself as a dictionary

        """

        # dictator = {self.name: {'probe_name': self.probe_name, 'instrument_name': self.instrument.name}}
        dictator = {self.instrument.name: self.probe_name}

        return dictator

    def save(self, filename):
        """
        save the instrument to path as a .b26 file

        Args:
            filename: path of file
        """
        save_b26_file( filename, probes=self.to_dict())


    @staticmethod
    def load_and_append(probe_dict, probes, instruments={}):
        """
        load probes from probe_dict and append to probes, if additional instruments are required create them and add them to instruments

        Args:
            probe_dict: dictionary of form

                probe_dict = {
                    instrument1_name : probe1_of_instrument1, probe2_of_instrument1, ...
                    instrument2_name : probe1_of_instrument2, probe2_of_instrument2, ...
                }

            where probe1_of_instrument1 is a valid name of a probe in instrument of class instrument1_name

            # optional arguments (as key value pairs):
            #     probe_name
            #     instrument_name
            #     probe_info
            #     buffer_length
            #
            #
            # or
            #     probe_dict = {
            #     name_of_probe_1 : instrument_class_1
            #     name_of_probe_2 : instrument_class_2
            #     ...
            #     }


            probes: dictionary of form
                probe_dict = {
                    instrument1_name:
                        {name_of_probe_1_of_instrument1 : probe_1_instance,
                         name_of_probe_2_instrument1 : probe_2_instance
                         }
                         , ...}

            instruments: dictionary of form

                instruments = {
                name_of_instrument_1 : instance_of_instrument_1,
                name_of_instrument_2 : instance_of_instrument_2,
                ...
                }
    Returns:
                updated_probes = { name_of_probe_1 : probe_1_instance, name_of_probe_2 : probe_2_instance, ...}
                loaded_failed = {name_of_probe_1: exception_1, name_of_probe_2: exception_2, ....}
                updated_instruments
        """


        loaded_failed = {}
        updated_probes = {}
        updated_probes.update(probes)
        updated_instruments = {}
        updated_instruments.update(instruments)

        # =====  load new instruments =======
        new_instruments = list(set(probe_dict.keys())-set(probes.keys()))
        if new_instruments != []:
            updated_instruments, failed = Instrument.load_and_append({instrument_name: instrument_name for instrument_name in new_instruments}, instruments)


            if failed != []:
                # if loading an instrument fails all the probes that depend on that instrument also fail
                # ignore the failed instrument that did exist already because they failed because they did exist
                for failed_instrument in set(failed) - set(instruments.keys()):
                    for probe_name in probe_dict[failed_instrument]:
                        loaded_failed[probe_name] = ValueError('failed to load instrument {:s} already exists. Did not load!'.format(failed_instrument))
                    del probe_dict[failed_instrument]

        # =====  now we are sure that all the instruments that we need for the probes already exist


        for instrument_name, probe_names in probe_dict.items():
            if not instrument_name in updated_probes:
                updated_probes.update({instrument_name:{}})

            for probe_name in probe_names.split(','):
                if probe_name in updated_probes[instrument_name]:
                    loaded_failed[probe_name] = ValueError('failed to load probe {:s} already exists. Did not load!'.format(probe_name))
                else:
                    probe_instance = Probe(updated_instruments[instrument_name], probe_name)
                    updated_probes[instrument_name].update({probe_name: probe_instance})

        return updated_probes, loaded_failed, updated_instruments








if __name__ == '__main__':
    probe_dict = {'DummyInstrument': 'internal,value1'}
    instruments, __ = Instrument.load_and_append({'DummyInstrument': 'DummyInstrument'})

    probes_obj, failed, instruments = Probe.load_and_append(
        probe_dict=probe_dict,
        probes={},
        instruments=instruments)
    print(('fffff', probes_obj))
    # Probe.load_and_append(
    #     probe_dict={name: probes[name] for name in added_probes},
    #     probes=self.probes,
    #     instruments=self.instruments)
    # # from pylabcontrol.core import instantiate_instruments
    # instruments = {'inst_dummy': 'DummyInstrument'}
    #
    # instrument = instantiate_instruments(instruments)['inst_dummy']
    #
    # p = Probe(instrument, 'value1', 'random')
    #
    # print(instruments['inst_dummy'])
    #
    # print(p.name)
    # print(p.value)
    # print(p.value)



