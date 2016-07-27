from importlib import import_module
from PyLabControl.src.core.read_write_functions import get_config_value
import inspect, os
from PyLabControl.src.core  import Instrument

def export_default_probes(path, module_name = ''):
    """
    NOT IMPLEMENTED YET
    tries to instantiate all the instruments that are imported in /instruments/__init__.py
    and the probes of each instrument that could be instantiated into a .b26 file in the folder path
    Args:
        path: target path for .b26 files
    """

    raise NotImplementedError


    import b26_toolkit.src.instruments as instruments
    from PyLabControl.src.core import Probe

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

def export_default_instruments(target_folder, module_name = '', raise_errors = False):
    """
    tries to instantiate all the instruments that are imported in /instruments/__init__.py
    and saves instruments that could be instantiate into a .b2 file in the folder path
    Args:
        target_folder: target path for .b26 files
    """

    if module_name is '':
        module_name = 'src.instruments'

    if len(module_name.split('src.instruments'))==1:
        module_name += '.src.instruments'


    module = import_module(module_name)

    for name, obj in inspect.getmembers(module):

        if inspect.isclass(obj) and issubclass(obj, Instrument):
            print('instrument: ', name)
            try:
                instrument = obj()
                print('created ', name)
                filename = '{:s}{:s}.b26'.format(target_folder, name)
                instrument.save_b26(filename)
                print('saved ', name)
            except Exception, err:
                if raise_errors:
                    raise err
                else:
                    print('failed to create instrument file for: {:s}'.format(obj.__name__))

def export_default_scripts(path, module_name = '', raise_errors = False):
    """
    tries to instantiate all the scripts that are imported in /scripts/__init__.py
    saves each script that could be instantiated into a .b26 file in the folder path
    Args:
        path: target path for .b26 files
    """
    loaded_instruments = {}
    loaded_scripts = {}
    from PyLabControl.src.core.scripts import Script

    if module_name is '':
        module_name = 'src.scripts'

    if len(module_name.split('src.scripts'))==1:
        module_name += '.src.scripts'

    module = import_module(module_name)


    scripts_to_load = {name:name for name, obj in inspect.getmembers(module) if inspect.isclass(obj)}
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


def export(folder, class_type = 'all', raise_errors = False):
    """
    exports the existing scripts/intruments (future: probes) into folder as .b26 files
    Args:
        class_type: string, one of the 4 following options
            -probes (exports probes) --not implemented yet--
            -scripts (exports scripts)
            -instruments (exports instruments)
            -all (exports instruments, scripts and probes)
        folder: target folder where .b26 files are created
    Returns:

    """
    if not class_type in ('all', 'scripts', 'instruments', 'probes'):
        print('unknown type to export')
        return




    path_to_config = '/'.join(os.path.dirname(inspect.getfile(export)).split('/')[0:-2]) + '/config.txt'

    module_list = ['']
    module_list += get_config_value('SCRIPT_MODULES', path_to_config).split(';')



    for module in module_list:
        if class_type in ('all', 'scripts'):
            export_default_scripts(folder, module, raise_errors)
        if class_type in ('all', 'instruments'):
            export_default_instruments(folder, module, raise_errors)
        if class_type in ('all', 'probes'):
            export_default_probes(folder, module, raise_errors)


if __name__ == '__main__':

    # export('C:\\Users\\Experiment\\PycharmProjects\\user_data\\instruments_auto_generated\\', class_type='instruments', raise_errors =False)
    export('C:\\Users\\Experiment\\PycharmProjects\\user_data\\scripts_auto_generated\\', class_type='scripts')
    #
    # import b26_toolkit.src.instruments


    # module_name = 'src.instrumentas'
    # print(len(module_name.split('src.instruments')))
    # # module = import_module(module_name)
    # # print(module)