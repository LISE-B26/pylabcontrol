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


import inspect, os
from pylabcontrol.core import Instrument, Script, ScriptIterator
from importlib import import_module
from pylabcontrol.core.helper_functions import module_name_from_path

import glob

def get_classes_in_folder(folder_name, class_type, verbose=False):
    """
    load all the instruments or script objects that are located in folder_name and
    return a dictionary with the script class name and path_to_python_file
    Args:
        folder_name (string): folder in which to search for class objects / or name of module
        class_type (string or class): class type for which to look for

    Returns:
        a dictionary with the class name and path_to_python_file:
        {
        'class': class_of_instruments,
        'filepath': path_to_python_file
        }

    """

    assert class_type == Instrument or class_type == Script or class_type.lower() in ['instrument', 'script']

    if isinstance(class_type, str):
        if class_type.lower() == 'instrument':
            class_type = Instrument
        elif class_type.lower() == 'script':
            class_type = Script


    # if the module name was passed instead of a filename, figure out the path to the module
    if not os.path.isdir(folder_name):
        try:
            folder_name = os.path.dirname(inspect.getfile(import_module(folder_name)))
        except ImportError:
            raise ImportError('could not find module ' + folder_name)


    subdirs = [os.path.join(folder_name, x) for x in os.listdir(folder_name) if
               os.path.isdir(os.path.join(folder_name, x)) and not x.startswith('.')]

    classes_dict = {}
    # if there are subdirs in the folder recursively check all the subfolders for scripts
    for subdir in subdirs:
        classes_dict.update(get_classes_in_folder(subdir, class_type))


    for python_file in [f for f in glob.glob(os.path.join(folder_name, "*.py"))if '__init__' not in f]:
        module, path = module_name_from_path(python_file)

        try:
            module = import_module(module)

            classes_dict.update({name: {'class': name, 'filepath': inspect.getfile(obj)} for name, obj in
                               inspect.getmembers(module) if inspect.isclass(obj) and issubclass(obj, class_type)
                             and not obj in (Instrument, Script, ScriptIterator)})
        except ImportError as e:
            if verbose:
                print(('Could not import module', module))
                print(e)

    return classes_dict

def export_default_probes(path, module_name = '', raise_errors = False):
    """
    NOT IMPLEMENTED YET
    tries to instantiate all the instruments that are imported in /instruments/__init__.py
    and the probes of each instrument that could be instantiated into a .b26 file in the folder path
    Args:
        path: target path for .b26 files
    """

    raise NotImplementedError


    import b26_toolkit.b26_toolkit.instruments as instruments
    from pylabcontrol.core import Probe

    for name, obj in inspect.getmembers(instruments):

        if inspect.isclass(obj):

            try:
                instrument = obj()
                print(('--- created ', obj.__name__, ' -- '))
                for probe_name, probe_info in instrument._PROBES.items():
                    probe = Probe(instrument, probe_name, info = probe_info)
                    filename = os.path.join(path, '{:s}.b26'.format(instrument.name))
                    probe.save(filename)
            except:
                print(('failed to create probe file for: {:s}'.format(obj.__name__)))
                print(('failed to create probe file for: {:s}'.format(obj.__name__)))

def export_default_instruments(target_folder, source_folder = None, raise_errors = False, verbose=True):
    """
    tries to instantiate all the instruments that are imported in /instruments/__init__.py
    and saves instruments that could be instantiate into a .b2 file in the folder path
    Args:
        target_folder: target path for .b26 files
    """
    print('export_def_instr called')
    instruments_to_load = get_classes_in_folder(source_folder, Instrument, verbose = True)
    print('instruments to load:')
    print(instruments_to_load)

    if verbose:
        print(('attempt to load {:d} instruments: '.format(len(instruments_to_load))))
    loaded_instruments, failed = Instrument.load_and_append(instruments_to_load, raise_errors = raise_errors)
    print('loaded instruments:')
    print(loaded_instruments, failed)

    for name, value in loaded_instruments.items():
        filename = os.path.join(target_folder, '{:s}.b26'.format(name))

        value.save_b26(filename)

    if verbose:
        print('\n================================================')
        print('================================================')
        print(('saved {:d} instruments, {:d} failed'.format(len(loaded_instruments), len(failed))))
        if failed != {}:
            for error_name, error in failed.items():
                print(('failed to create instruments: ', error_name, error))

def export_default_scripts(target_folder, source_folder = None, raise_errors = False, verbose=False):
    """
    tries to instantiate all the scripts that are imported in /scripts/__init__.py
    saves each script that could be instantiated into a .b26 file in the folder path
    Args:
        target_folder: target path for .b26 files
        source_folder: location of python script files
    """

    scripts_to_load = get_classes_in_folder(source_folder, Script)

    if verbose:
        print(('attempt to load {:d} scripts: '.format(len(scripts_to_load))))

    loaded_scripts, failed, loaded_instruments = Script.load_and_append(scripts_to_load, raise_errors=raise_errors)

    for name, value in loaded_scripts.items():
        filename = os.path.join(target_folder, '{:s}.b26'.format(name))
        value.save_b26(filename)

    if verbose:
        print('\n================================================')
        print('================================================')
        print(('saved {:d} scripts, {:d} failed'.format(len(loaded_scripts), len(failed))))
        if failed != {}:
            for error_name, error in failed.items():
                print(('failed to create script: ', error_name, error))


def export(target_folder, source_folders = None, class_type ='all', raise_errors = False):
    """
    exports the existing scripts/instruments (future: probes) into folder as .b26 files
    Args:
        target_folder: target location of created .b26 script files
        source_folder: singel path or list of paths that contains the location of python script files can also be just the name of a module
        class_type: string, one of the 4 following options
            -probes (exports probes) --not implemented yet--
            -scripts (exports scripts)
            -instruments (exports instruments)
            -all (exports instruments, scripts and probes)
        target_folder: target folder whereb   .b26 files are created
    Returns:

    """
    if class_type not in ('all', 'scripts', 'instruments', 'probes'):
        print('unknown type to export')
        return

    if not os.path.isdir(target_folder):
        try:
            os.mkdir(target_folder)
        except:
            print((target_folder, ' is invalid target folder'))
            target_folder = None

    if target_folder is not None:
        if source_folders is None:
            module_list = [os.path.dirname(os.path.dirname(inspect.getfile(inspect.currentframe())))]
        elif isinstance(source_folders, str):
            module_list = [source_folders]
        elif isinstance(source_folders, list):
            module_list = source_folders
        else:
            raise TypeError('unknown type for source_folders')

        for path_to_module in module_list:
            if class_type in ('all', 'scripts'):
                export_default_scripts(target_folder, source_folder=path_to_module, raise_errors=raise_errors)
            if class_type in ('all', 'instruments'):
                print('about to call export_default_instruments')
                export_default_instruments(target_folder, path_to_module,  raise_errors=raise_errors)
            if class_type in ('all', 'probes'):
                print('WARNING: probes currently not supported')
                # export_default_probes(target_folder, path_to_module,  raise_errors=raise_errors)


if __name__ == '__main__':

    source_folders = 'C:\\Users\Experiment\\PycharmProjects\\b26_toolkit\\pylabcontrol\\scripts'
    target_folder = 'C:\\Users\\Experiment\\PycharmProjects\\user_data\\scripts_auto_generated'
    export(target_folder, source_folders=source_folders, class_type='scripts', raise_errors=False)




