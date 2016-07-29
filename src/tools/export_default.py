"""
    This file is part of PyLabControl, software for laboratory equipment control for scientific experiments.
    Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell

    Foobar is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
"""
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

def export_default_scripts(target_folder, source_folder = None, raise_errors = False):
    """
    tries to instantiate all the scripts that are imported in /scripts/__init__.py
    saves each script that could be instantiated into a .b26 file in the folder path
    Args:
        target_folder: target path for .b26 files
        source_folder: location of python script files
    """
    loaded_instruments = {}
    loaded_scripts = {}
    from PyLabControl.src.core.scripts import Script
    module_name = source_folder
    if module_name is '':
        module_name = 'src.scripts'

    if len(module_name.split('src.scripts'))==1:
        module_name += '.src.scripts'

    module = import_module(module_name)


    scripts_to_load = {name:name for name, obj in inspect.getmembers(module) if inspect.isclass(obj)}
    print('attempt to load {:d} scripts: '.format(len(scripts_to_load)))
    loaded_scripts, failed, loaded_instruments = Script.load_and_append(scripts_to_load)

    for name, value in loaded_scripts.iteritems():
        filename = '{:s}{:s}.b26'.format(target_folder, name)
        value.save_b26(filename)

    print('\n================================================')
    print('================================================')
    print('saved {:d} scripts, {:d} failed'.format(len(loaded_scripts), len(failed)))
    if failed != {}:
        for error_name, error in failed.iteritems():
            print('failed to create script: ', error_name, error)

            # raise error


def export(target_folder, source_folders = None, class_type ='all', raise_errors = False):
    """
    exports the existing scripts/intruments (future: probes) into folder as .b26 files
    Args:
        target_folder: target location of created .b26 script files
        source_folder: location of python script files or a list of folders
        class_type: string, one of the 4 following options
            -probes (exports probes) --not implemented yet--
            -scripts (exports scripts)
            -instruments (exports instruments)
            -all (exports instruments, scripts and probes)
        target_folder: target folder where .b26 files are created
    Returns:

    """
    if not class_type in ('all', 'scripts', 'instruments', 'probes'):
        print('unknown type to export')
        return


    if isinstance(source_folders, str):
        module_list = [source_folders]
    elif isinstance(source_folders, list):
        module_list = source_folders
    else:
        raise TypeError('unknown type for source_folders')


    # path_to_config = '/'.join(os.path.dirname(inspect.getfile(export)).split('/')[0:-2]) + '/config.txt'
    #
    # module_list = ['']
    # module_list += get_config_value('SCRIPT_MODULES', path_to_config).split(';')


    print(module_list)
    for module in module_list:

        # stripping off subfolders
        if os.path.basename(module) == '':
            module = os.path.dirname(module)
        if os.path.basename(module) in ('scripts', 'instruments'):
            module = os.path.dirname(module)
        if os.path.basename(module) in ('src'):
            module = os.path.dirname(module)


        if class_type in ('all', 'scripts'):
            export_default_scripts(target_folder, source_folder=module, raise_errors=raise_errors)
        if class_type in ('all', 'instruments'):
            export_default_instruments(target_folder, module, raise_errors)
        if class_type in ('all', 'probes'):
            export_default_probes(target_folder, module, raise_errors)


if __name__ == '__main__':

    # export('C:\\Users\\Experiment\\PycharmProjects\\user_data\\instruments_auto_generated\\', class_type='instruments', raise_errors =False)
    export(target_folder='C:\\Users\\Experiment\\PycharmProjects\\user_data\\scripts_auto_generated\\',
           source_folders='C:\\Users\\Experiment\\PycharmProjects\\b26_toolkit\\',
           class_type='scripts')
    #
    # import b26_toolkit.src.instruments


    # module_name = 'src.instrumentas'
    # print(len(module_name.split('src.instruments')))
    # # module = import_module(module_name)
    # # print(module)