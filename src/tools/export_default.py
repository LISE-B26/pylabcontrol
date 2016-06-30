

def export_default_probes(path):
    """
    NOT IMPLEMENTED YET
    tries to instantiate all the instruments that are imported in /instruments/__init__.py
    and the probes of each instrument that could be instantiated into a .b26 file in the folder path
    Args:
        path: target path for .b26 files
    """
    import src.instruments as instruments
    from src.core import Probe
    import inspect
    import os
    for name, obj in inspect.getmembers(instruments):

        if inspect.isclass(obj):

            try:
                instrument = obj()
                print('--- created ', obj.__name__, ' -- ')
                for probe_name, probe_info in instrument._PROBES.iteritems():
                    probe = Probe(instrument, probe_name, info = probe_info)
                    filename = os.path.join(path, '{:s}.b26'.format(instrument.name))
                    probe.save(filename)
            except:
                print('failed to create probe file for: {:s}'.format(obj.__name__))


def export_default_instruments(path):
    """
    tries to instantiate all the instruments that are imported in /instruments/__init__.py
    and saves instruments that could be instantiate into a .b2 file in the folder path
    Args:
        path: target path for .b26 files
    """
    import src.instruments as instruments
    import inspect

    for name, obj in inspect.getmembers(instruments):

        if inspect.isclass(obj):

            try:
                instrument = obj()
                print('created ', name)
                filename = '{:s}{:s}.b26'.format(path, name)
                instrument.save_b26(filename)
                print('saved ', name)
            except:
                print('failed to create instrument file for: {:s}'.format(obj.__name__))

def export_default_scripts(path):
    """
    tries to instantiate all the scripts that are imported in /scripts/__init__.py
    saves each script that could be instantiated into a .b26 file in the folder path
    Args:
        path: target path for .b26 files
    """
    loaded_instruments = {}
    loaded_scripts = {}
    from src.core.scripts import Script
    import src.scripts as scripts
    import inspect

    scripts_to_load = {name:name for name, obj in inspect.getmembers(scripts) if inspect.isclass(obj)}
    print('attempt to load {:d} scripts: '.format(len(scripts_to_load)))
    loaded_scripts, failed, loaded_instruments = Script.load_and_append(scripts_to_load)

    for name, value in loaded_scripts.iteritems():
        filename = '{:s}{:s}.b26'.format(path, name)
        value.save_b26(filename)

    print('\n================================================')
    print('================================================')
    print('saved {:d} scripts, {:d} failed'.format(len(loaded_scripts), len(failed)))
    if failed != {}:
        for error_name, error in failed.iteritems():
            print('failed to create script: ', error_name, error)

            # raise error


if __name__ == '__main__':
    # export_default_instruments('C:\\Users\\Experiment\\PycharmProjects\\PythonLab\\b26_files\\instruments_auto_generated\\')
    export_default_scripts('C:\\Users\\Experiment\\PycharmProjects\\PythonLab\\b26_files\\scripts_auto_generated\\')

    # export_default_probes('C:\\Users\\Experiment\\PycharmProjects\\PythonLab\\b26_files\\probes_auto_generated\\')
