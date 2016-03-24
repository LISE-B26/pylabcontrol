

def load_instruments(instruments):
    """
    Creates instances of the instruments inputted; in the case of the Maestro Beam Block and other motors, makes sure
    to use the same controller for all of them by creating a single controller instance for each maestro motor to be
    initialized with.

    Args:
        instruments: instruments is a dictionary with (key,value) = (name of the instrument, instrument class name),
        for example instruments = {'Chamber Pressure Gauge': 'PressureGauge'}

    Returns:
        a dictionary with (key,value) = (name of instrument, instance of instrument class) for all of the instruments
        passed to the function that were successfully imported and initialized. Otherwise, instruments are omitted
        in the outputted list.

    Examples:
        In the following, instrument_1 loads correctly, but instrument_2 does not, so only an instance of instrument_1
        is outputted.

        >>> load_instruments({'instrument_1_name':'Instrument1Class', 'instrument_2_name':'Instrument2Class'})
        {'instrument_1_name':Instrument1Class()}

    """

    instrument_instances = {}
    controller_instance = None

    for instrument_name, instrument_class_name in instruments.iteritems():

        try:
            # try to import the instrument
            module = __import__('src.instruments', fromlist=[instrument_class_name])
            # this returns the name of the module that was imported.

            class_of_instrument = getattr(module, instrument_class_name)
            # this will take the module and look for the class of the instrument in it.
            # This has the same name as the name for the module, because of our __init__.py file in the instruments
            # folder. This raises an AttributeError if, in fact, we did not import the module

            #special case of the Maestro Beam Block initialization:
            if instrument_class_name is 'MaestroBeamBlock':
                if not controller_instance:
                    # Need to create a controller first, and use that instance for all Maestro Motors.

                    module = __import__('src.instruments', fromlist=[instrument_class_name])
                    class_of_controller = getattr(module, instrument_class_name)
                    controller_instance = class_of_controller()

                # create the instrument_instance
                instrument_instance = class_of_instrument(maestro = controller_instance, name = instrument_name)

            else:
                # this creates an instance of the class
                instrument_instance = class_of_instrument(name=instrument_name)

            # adds the instance to our output ditionary
            instrument_instances[instrument_name] = instrument_instance

        except AttributeError:
            # catches when we try to create an instrument of a class that doesn't exist!
            pass

    return instrument_instances


def load_scripts(scripts, instruments):
    """
    Creates instances of the scripts inputted;

    Args:
        scripts: scripts is a dictionary with (key,value) = (name of the script, script class name),
        for example script = {'dummy script': 'ScriptDummy'}

    Returns:
        a dictionary with (key,value) = (name of script, instance of script class) for all of the scripts
        passed to the function that were successfully imported and initialized. Otherwise, scripts are omitted
        in the outputted list.

    Examples:
        In the following, script_1 loads correctly, but script_2 does not, so only an instance of script_1
        is outputted.

        >>> load_scripts({'script_1_name':'Script1Class', 'script_2_name':'Script2Class'})
        {'script_1_name':Script1Class()}

    """


    scripts_instances = {}
    print('instruments', instruments)
    for script_name, value in scripts.iteritems():
        print('====', script_name)
        try:

            if isinstance(value, dict):
                assert 'script_class' in value
                assert 'instruments' in value

                script_class_name = value['script_class']
                script_instruments = value['instruments']

                script_instruments = {instrument_name: instruments[instrument_reference] for instrument_name, instrument_reference in script_instruments.iteritems()}

            elif isinstance(value, str):
                script_class_name = value
                script_instruments = None

            else:
                TypeError("values of input not recognized!")


            # try to import the script
            module = __import__('src.scripts', fromlist=[script_class_name])
            # this returns the name of the module that was imported.

            class_of_script = getattr(module, script_class_name)
            # this will take the module and look for the class of the script in it.
            # This has the same name as the name for the module, because of our __init__.py file in the scripts
            # folder. This raises an AttributeError if, in fact, we did not import the module

            print(class_of_script, script_name)
            # this creates an instance of the class
            if script_instruments is None:
                script_instance = class_of_script(name=script_name)
            else:
                script_instruments['name'] = script_name
                script_instance = class_of_script(**script_instruments)

            # adds the instance to our output dictionary
            scripts_instances[script_name] = script_instance
            print('script_name', script_name, scripts_instances)

        except AttributeError:
            # catches when we try to create a script of a class that doesn't exist!
            # pass
            raise

    return scripts_instances


def load_probes(probes, instruments):

    return probes
