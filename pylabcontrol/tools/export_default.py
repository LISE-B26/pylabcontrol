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


import inspect, os, sys
from pylabcontrol.core import Instrument, Script, ScriptIterator
from importlib import import_module
from pylabcontrol.core.helper_functions import module_name_from_path

import glob

def find_exportable_in_python_files(folder_name, class_type, verbose = True):
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
        classes_dict.update(find_exportable_in_python_files(subdir, class_type))

    if class_type.lower() == 'instrument':
        class_type = Instrument
    elif class_type.lower() == 'script':
        class_type = Script

    for python_file in [f for f in glob.glob(os.path.join(folder_name, "*.py"))if '__init__' not in f and 'setup' not in f]:
        module, path = module_name_from_path(python_file)

        #appends path to this module to the python path if it is not present so it can be used
        if path not in sys.path:
            sys.path.append(path)

        try:
            module = import_module(module)

            classes_dict.update({name: {'class': name, 'filepath': inspect.getfile(obj), 'info': inspect.getdoc(obj)} for name, obj in
                               inspect.getmembers(module) if inspect.isclass(obj) and issubclass(obj, class_type)
                             and not obj in (Instrument, Script, ScriptIterator)})

        except (ImportError, ModuleNotFoundError) as e:
            print(e)
            if verbose:
                print('Could not import module', module)

    return classes_dict

def find_scripts_in_python_files(folder_name, verbose = False):
    return find_exportable_in_python_files(folder_name, 'Script', verbose)

def find_instruments_in_python_files(folder_name, verbose = False):
    return find_exportable_in_python_files(folder_name, 'Instrument', verbose)

def python_file_to_b26(list_of_python_files, target_folder, class_type, raise_errors = False):
    if class_type == 'Script':
        loaded, failed, loaded_instruments = Script.load_and_append(list_of_python_files, raise_errors=raise_errors)
    elif class_type == 'Instrument':
        loaded, failed = Instrument.load_and_append(list_of_python_files, raise_errors=raise_errors)

    print('loaded', loaded)

    for name, value in loaded.items():
        filename = os.path.join(target_folder, '{:s}.b26'.format(name))
        value.save_b26(filename)

if __name__ == '__main__':
    # module = import_module('b26_toolkit.pylabcontrol.scripts.test_script')
    # print('JJJJJJ')
    # export scripts
    # source_folders = 'b26_toolkit'
    source_folders = 'C:\\Users\\Experiment\\PycharmProjects\\b26_toolkit\\b26_toolkit\\scripts\\'
    # source_folders = 'C:\\Users\\Experiment\\PycharmProjects\\pylabcontrol\\pylabcontrol\\scripts\\'
    # # target_folder = 'C:\\Users\\NV Experiment\\PycharmProjects\\user_data\\scripts_auto_generated\\'
    # target_folder = 'C:\\Users\\Experiment\\PycharmProjects\\user_data\\scripts_auto_generated'
    # source_folders = 'C:\\Users\\Experiment\\PycharmProjects\\b26_toolkit\\pylabcontrol\\instruments'
    # # export instruments
    # source_folders = 'C:\\Users\\NV Experiment\\PycharmProjects\\b26_toolkit\\pylabcontrol\\instruments\\'
    # target_folder = 'C:\\Users\\NV Experiment\\PycharmProjects\\user_data\\instruments_auto_generated\\'
    # export(target_folder, source_folders=source_folders, class_type='instruments', raise_errors=False)
    # instruments_to_load = get_classes_in_folder('C:\\Users\\Experiment\\PycharmProjects\\b26_toolkit\\pylabcontrol\\instruments\\', Instrument)
    #
    # print(instruments_to_load.keys())

    # import pkgutil
    #
    # print('--------')
    # for importer, modname, ispkg in pkgutil.walk_packages(path='b26_toolkit.pylabcontrol.scripts',
    #                                                       # prefix=package.__name__ + '.',
    #                                                       onerror=lambda x: None):
    #     print(modname, importer)
    #



    # import glob
    #
    # from pylabcontrol.core.helper_functions import module_name_from_path
    #
    #
    # for f in glob.glob(os.path.join(source_folders, "*.py")):
    #     module, path = module_name_from_path(f)
    #     print(f, module, path)
    #
    # # source_folders = '/Users/rettentulla/PycharmProjects/b26_toolkit/pylabcontrol/'
    # subdirs = [os.path.join(source_folders, x) for x in os.listdir(source_folders) if
    #            os.path.isdir(os.path.join(source_folders, x)) and not x.startswith('.')]
    #
    # print('asa', source_folders)
    #
    # for subdir in subdirs:
    #     print(subdir)

    print(find_scripts_in_python_files(source_folders))

