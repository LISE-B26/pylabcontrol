from src.core.scripts import Script
import src.scripts as scripts
from src.core import Probe

import inspect

def export_default_probes(path):
    import src.instruments as instruments
    import inspect

    for name, obj in inspect.getmembers(instruments):
        if inspect.isclass(obj):
            try:
                instrument = obj()

                for probe_name, probe_info in instrument._PROBES.iteritems():
                    probe = Probe(instrument, probe_name, info = probe_info)
                    filename = '{:s}/{:s}/{:s}.b26'.format(path, instrument.name, probe_name)
                    probe.save(filename)
            except:
                print('failed to create probe file for: {:s}'.format(obj.__name__))


def export_default_instruments(path):
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

    loaded_instruments = {}
    loaded_scripts = {}

    scripts_to_load = {name:name for name, obj in inspect.getmembers(scripts) if inspect.isclass(obj)}

    loaded_scripts, failed, loaded_instruments = Script.load_and_append(scripts_to_load)

    for name, value in loaded_scripts.iteritems():
        filename = '{:s}{:s}.b26'.format(path, name)
        value.save_b26(filename)

    if failed != {}:
        for error_name, error in failed.iteritems():
            print('failed to create script: ', error_name)
            # raise error


if __name__ == '__main__':
     # export_default_instruments('C:\\Users\\Experiment\\PycharmProjects\\PythonLab\\b26_files\\instruments_auto_generated\\')
    export_default_scripts('C:\\Users\\Experiment\\PycharmProjects\\PythonLab\\b26_files\\scripts_auto_generated\\')