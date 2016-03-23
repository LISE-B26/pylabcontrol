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


if __name__ == '__main__':
    # test code
    example_instruments = {'ZIHF2': 'ZIHF2', 'Microwave Generator': 'MicrowaveGenerator'}
    instances = load_instruments(example_instruments)
    print(instances)