from src.core.instruments import Instrument
from collections import deque
from src.core.read_write_functions import save_b26_file

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
                name_of_probe_1 :
                    {'instrument_class': value_inst_class, optional aguments..}
                name_of_probe_2 :
                    {'instrument_class': value_inst_class, optional aguments..}
                ...
                }
            where name_of_probe_1 is a valid name of a probe in instrument of class value_inst_class

            optional arguments (as key value pairs):
                probe_name
                instrument_name
                probe_info
                buffer_length


            or
                probe_dict = {
                name_of_probe_1 : instrument_class_1
                name_of_probe_2 : instrument_class_2
                ...
                }



            probes: dictionary of form
                probe_dict = { name_of_probe_1 : probe_1_instance, name_of_probe_2 : probe_2_instance, ...}

            instruments: dictionary of form

                instruments = {
                name_of_instrument_1 : instance_of_instrument_1,
                name_of_instrument_2 : instance_of_instrument_2,
                ...
                }
     Returns:
                probe_dict = { name_of_probe_1 : probe_1_instance, name_of_probe_2 : probe_2_instance, ...}
                loaded_failed = {name_of_probe_1: exception_1, name_of_probe_2: exception_2, ....}
                updated_instruments
        """


        def get_instrument(instrument_class, instruments):
            """

            Args:
                instrument_class: name of instrument (str)
                instruments: dictionary of instruments where key is name of instrument and value is instance

            Returns:

            """


            instrument = {}

            for k, v in instruments.iteritems():
                if v.__class__ == instrument_class:
                    instrument[k] = v

            return instrument


        loaded_failed = {}
        updated_probes = {}
        updated_probes.update(probes)
        updated_instruments = {}
        updated_instruments.update(instruments)

        for key, value in probe_dict.iteritems():

            if isinstance(value, str):
                instrument_class = value
                probe_name = key
                instrument_name = instrument_class
                probe_info = None
                buffer_length = None
            elif issubclass(value, Instrument):
                instrument_class = value.__class__.name
                probe_name = key
                instrument_name = instrument_class
                probe_info = None
                buffer_length = None
            elif isinstance(value, dict):
                instrument_class  = value['instrument_class']

                if 'probe_name' in value:
                    probe_name = value['probe_name']
                else:
                    probe_name = key
                if 'instrument_name' in value:
                    instrument_name = value['instrument_name']
                else:
                    instrument_name = instrument_class
                if 'probe_info' in value:
                    probe_info = value['probe_info']
                else:
                    probe_info = None
                if 'buffer_length' in value:
                    buffer_length = value['buffer_length']
                else:
                    buffer_length = None

            else:
                raise TypeError('wrong dictionary values ')


            # check if probe already exists
            if probe_name in probes.keys():
                print('WARNING: probe {:s} already exists. Did not load!'.format(probe_name))
                loaded_failed[probe_name] = ValueError('probe {:s} already exists. Did not load!'.format(probe_name))
            else:

                probe_instance = None

                # check if instrument already exists
                instrument = get_instrument(instrument_class, instruments)

                if instrument == {}:
                    instruments, __ = Instrument.load_and_append({instrument_name: instrument_class}, instruments)
                    instrument = {instrument_name: instruments[instrument_name]}

                #  ========= create probes =========

                try:

                    class_creation_string = ''
                    if probe_name !=  key:
                        class_creation_string += ', name = probe_name'
                    if buffer_length is not None:
                        class_creation_string += ', buffer_length = buffer_length'
                    if probe_info is not None:
                        class_creation_string += ', probe_info = probe_info'
                    if instrument_name != instrument_class:
                        class_creation_string += ', instrument_name = instrument_name'

                    class_creation_string = 'class_of_script(instrument=instrument[instrument_name], probe_name = key)'.format(class_creation_string)

                    probe_instance = eval(class_creation_string)
                    updated_probes.update({key: probe_instance})
                except Exception as inst:
                    loaded_failed[key] = inst


        return updated_probes, loaded_failed, updated_instruments








if __name__ == '__main__':
    probe_dict = {"DummyInstrument": {
        "deep_internal": "DummyInstrument",
        "internal": "DummyInstrument"}
    }



    # Probe.load_and_append(
    #     probe_dict={name: probes[name] for name in added_probes},
    #     probes=self.probes,
    #     instruments=self.instruments)
    # # from src.core import instantiate_instruments
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



