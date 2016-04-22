from src.core.probe import Probe

def instantiate_instruments(instruments):
    """
    Creates instances of the instruments inputted; in the case of the Maestro Beam Block and other motors, makes sure
    to use the same controller for all of them by creating a single controller instance for each maestro motor to be
    initialized with.

    Args:
        instruments:
        instruments is a dictionary with
        (key,value) = (name of the instrument, instrument class name),
        for example instruments = {'Chamber Pressure Gauge': 'PressureGauge'}

        or

        (key,value) = (name of the instrument, {'class' : instrument class name, "settings", dict with settings}),


    Returns:
        a dictionary with (key,value) = (name of instrument, instance of instrument class) for all of the instruments
        passed to the function that were successfully imported and initialized. Otherwise, instruments are omitted
        in the outputted list.

    Examples:
        In the following, instrument_1 loads correctly, but instrument_2 does not, so only an instance of instrument_1
        is outputted.

    """

    instrument_instances = {}
    controller_instance = None

    for instrument_name, instrument_class_name in instruments.iteritems():
        if isinstance(instrument_class_name, dict):
            instrument_settings = instrument_class_name['settings']
            instrument_class_name = str(instrument_class_name['class'])
        else:
            instrument_settings = None
        try:

            # try to import the instrument
            module = __import__('src.instruments', fromlist=[instrument_class_name])
            # this returns the name of the module that was imported.
            class_of_instrument = getattr(module, instrument_class_name)

            # this will take the module and look for the class of the instrument in it.
            # This has the same name as the name for the module, because of our __init__.py file in the instruments
            # folder. This raises an AttributeError if, in fact, we did not import the module

            #special case of the Maestro Beam Block initialization:
            if instrument_class_name in ['MaestroBeamBlock', 'MaestroFilterWheel']:
                if not controller_instance:
                    # Need to create a controller first, and use that instance for all Maestro Motors.
                    # module = __import__('src.instruments', fromlist=[instrument_class_name])
                    # class_of_controller = getattr(module, instrument_class_name)
                    # controller_instance = class_of_controller()
                    from src.instruments.maestro import MaestroController
                    controller_instance = MaestroController()
                # create the instrument_instance
                instrument_instance = class_of_instrument(maestro = controller_instance, name = instrument_name, settings = instrument_settings)

            else:
                if instrument_settings is None:
                    # this creates an instance of the class
                    instrument_instance = class_of_instrument(name=instrument_name)
                else:
                    instrument_instance = class_of_instrument(name=instrument_name, settings = instrument_settings)

            # adds the instance to our output ditionary
            instrument_instances[instrument_name] = instrument_instance

        except AttributeError as e:
            print('{:s} ({:s}) did not load'.format(instrument_name, class_of_instrument))
            print(e.message)
            # catches when we try to create an instrument of a class that doesn't exist!
            raise AttributeError

    return instrument_instances

def instantiate_scripts(scripts, instruments, log_function = None):
    """
    Creates instances of the scripts inputted;

    Args:
        scripts: scripts is a dictionary with
        (key,value) = (name of the script, script class name),
        for example script = {'dummy script': 'ScriptDummy'}

        or

        scripts is a dictionary with
        (key,value) = (name of the script, {"class": script class name, "settings": settings, "instruments": instrument, "subscripts": subscripts}),

        log_function (optional): log_function where script outputs text
    Returns:
        a dictionary with (key,value) = (name of script, instance of script class) for all of the scripts
        passed to the function that were successfully imported and initialized. Otherwise, scripts are omitted
        in the outputted list.

    Examples:
        In the following, script_1 loads correctly, but script_2 does not, so only an instance of script_1
        is outputted.

        load_scripts({'script_1_name':'Script1Class', 'script_2_name':'Script2Class'})
        {'script_1_name':Script1Class()}

    """

    def create_script_instance(script_name, value):
        script_instance = None
        script_instruments = {}
        script_scripts = {}
        script_settings =  {}
        if isinstance(value, dict):
            assert 'class' in value
            assert 'instruments' in value or 'scripts' in value or 'settings' in value

            script_class = str(value['class'])
            if 'instruments' in value:
                script_instruments = value['instruments']
                script_instruments = {
                    instrument_name: instruments[instrument_reference]
                    for instrument_name, instrument_reference in script_instruments.iteritems()
                    }

            if 'scripts' in value:
                script_scripts = value['scripts']
                script_scripts = {
                    script_name: create_script_instance(script_name, val)
                    for script_name, val in script_scripts.iteritems()
                    }
            if 'settings' in value:
                script_settings = value['settings']

        elif isinstance(value, str):
            script_class = value

        else:
            TypeError("values of input not recognized!")


        # try to import the script
        module = __import__('src.scripts', fromlist=[script_class])
        # this returns the name of the module that was imported.

        class_of_script = getattr(module, script_class)
        # this will take the module and look for the class of the script in it.
        # This has the same name as the name for the module, because of our __init__.py file in the scripts
        # folder. This raises an AttributeError if, in fact, we did not import the module


        # if there are instruments required be the script that have not been provided yet, need to load instruments
        missing_instruments = {}
        for instrument_name in class_of_script._INSTRUMENTS.keys():
            if instrument_name in script_instruments.keys() and isinstance(script_instruments[instrument_name], class_of_script._INSTRUMENTS[instrument_name]):
                pass
            else:
                missing_instruments.update({instrument_name: str(class_of_script._INSTRUMENTS[instrument_name].__name__)})
                # missing_instruments.update({instrument_name: str(class_of_script._INSTRUMENTS[instrument_name].__class__.__name__)})
        # for instrument_name in set(class_of_script._INSTRUMENTS.keys()).difference(set(script_instruments.keys())):
        #     missing_instruments.update({instrument_name: class_of_script._INSTRUMENTS['instrument_name']})

        new_instruments = instantiate_instruments(missing_instruments)
        script_instruments.update(new_instruments)
        instruments.update(new_instruments)
        # this creates an instance of the class
        try:

            class_creation_string = ''
            if script_instruments !={}:
                class_creation_string += ', instruments = script_instruments'
            if script_scripts !={}:
                class_creation_string += ', scripts = script_scripts'
            if script_settings !={}:
                class_creation_string += ', settings = script_settings'
            if log_function is not None:
                class_creation_string += ', log_output = log_function'
            class_creation_string = 'class_of_script(name=script_name{:s})'.format(class_creation_string)

            print('class_creation_string', class_creation_string)
            print('class_of_script', class_of_script)
            script_instance = eval(class_creation_string)

        except:
            raise

        if script_instance is None:
            raise AttributeError
        return script_instance

    scripts_instances = {}

    for script_name, value in scripts.iteritems():

            script = create_script_instance(script_name, value)

            if script is not None:
                scripts_instances[script_name] = script



    return scripts_instances

def instantiate_probes(probes, instruments):
    """
     Creates instances of the probes inputed;

     Args:
         probes: probes is a nested dictionary with
            (key, sub_dict ) = (name of the probe, {'probe_name': value_probe, 'instrument_name': value_inst}),
            where value_probe is a valid name of a probe in intrument with name value_inst
         for example script = {'detector signal': {'probe_name': "AI0", 'instrument_name': "my_DAQ"}}

     Returns:
         a dictionary with (key,sub_dict) = (name of probe, reference to probe) for all of the probes
         passed to the function that were successfully imported and initialized. Otherwise, probes are omitted
         in the outputted list.

     """

    probe_instances = {}
    for name, sub_dict in probes.iteritems():
        assert isinstance(sub_dict, dict)
        assert "probe_name" in sub_dict
        assert "instrument_name" in sub_dict

        probe_name = sub_dict['probe_name']
        instrument_name = sub_dict['instrument_name']

        if "probe_info" in sub_dict:
            probe_info = sub_dict['probe_info']
        else:
            probe_info = ''

        assert instrument_name in instruments, "{:s} not in {:s}".format(instrument_name, instruments.keys())
        assert probe_name in instruments[instrument_name]._PROBES

        probe_instances.update({name: Probe(instruments[instrument_name], probe_name, name, probe_info)})

    return probe_instances




if __name__ == '__main__':
    instruments = {
        # 'inst_dummy': 'DummyInstrument',
        'zihf2': 'ZIHF2',
        'pressure gauge': 'PressureGauge',
        'cryo station': 'CryoStation',
        'spectrum analyzer': 'SpectrumAnalyzer',
        'microwave generator': 'MicrowaveGenerator'
    }

    scripts = {

        'u-wave spectra': {
            'script_class': 'KeysightGetSpectrum',
            'instruments': {
                'spectrum_analyzer': 'spectrum analyzer'
            }
        },

        'u-wave spectra vs power': {
            'script_class': 'MWSpectraVsPower',
            'instruments': {
                'cryo_station': 'cryo station',
                'spectrum_analyzer': 'spectrum analyzer',
                'microwave_generator': 'microwave generator'
            }
        },

        # 'u-wave spectra vs power': {
        #     'script_class': 'MWSpectraVsPower',
        #     'instruments':{
        #     'microwave_generator' : 'microwave generator',
        #     'cryo_station' : 'cryo station',
        #     'spectrum_analyzer' : 'spectrum analyzer'
        #     }
        # },

        'ZI sweep': {
            'script_class': 'ZISweeper',
            'instruments': {'zihf2': 'zihf2'}
        },

        'High res scan': {
            'script_class': 'ZISweeperHighResolution',
            'scripts': {
                'zi sweep': {
                    'script_class': 'ZISweeper',
                    'instruments': {'zihf2': 'zihf2'}
                }
            }
        }

    }

    probes = {
        # 'random': {'probe_name': 'value1', 'instrument_name': 'inst_dummy'},
        # 'value2': {'probe_name': 'value2', 'instrument_name': 'inst_dummy'},
        'ZI (R)': {'probe_name': 'R', 'instrument_name': 'zihf2'},
        'ZI (X)': {'probe_name': 'X', 'instrument_name': 'zihf2'},
        'T (platform)': {'probe_name': 'platform_temp', 'instrument_name': 'cryo station'},
        'T (stage 1)': {'probe_name': 'stage_1_temp', 'instrument_name': 'cryo station'},
        'T (stage 2)': {'probe_name': 'stage_2_temp', 'instrument_name': 'cryo station'}
        # 'Chamber Pressure' : { 'probe_name': 'pressure', 'instrument_name': 'pressure gauge'}
    }





    filename = "Z:\Lab\Cantilever\Measurements\\__tmp\\a.b26"
    save_b26_file(filename, instruments, scripts, probes)

    # filename = 'C:\\Users\\Experiment\\gui_settings.b26gui'

    data = load_b26_file(filename)

    print(data['instruments'])

    #
    #
    # import yaml
    # in_file_name = "Z:\Lab\Cantilever\Measurements\\tmp_\\a"
    # with open(in_file_name, 'r') as infile:
    #     in_data = yaml.safe_load(infile)
    #
    # instruments = in_data['instruments']
    # scripts = in_data['scripts']
    # probes = in_data['probes']
    #
    #
    #
    # inst = load_instruments(instruments)
    #
    # sc = load_scripts(scripts, inst)
    #
    # pr = load_probes(probes, inst)



