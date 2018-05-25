
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

import yaml, json
import os, inspect
from importlib import import_module
import platform


def import_sub_modules(module_type):
    """
    imports all the module_type from additional modules that contain module_type
    This name of those modules is in the config file that is located in the main directory
    module_type: str that specifies the type of module to be loaded (scripts / instruments)

    :return: module_list: a list with modules that contain module_type
    """

    assert module_type in ('scripts', 'instruments')

    path_to_config = '/'.join(os.path.normpath(os.path.dirname(inspect.getfile(import_sub_modules))).split('\\')[0:-2]) + '/config.txt'
    module_list = get_config_value('SCRIPT_MODULES', path_to_config).split(';')
    module_list = [import_module(module_name + '.pylabcontrol.' + module_type) for module_name in module_list]

    return module_list


def get_config_value(name, path_to_file='config.txt'):
    """
    gets the value for "name" from "path_to_file" config file
    Args:
        name: name of varibale in config file
        path_to_file: path to config file

    Returns: path to dll if name exists in the file; otherwise, returns None

    """

    # if the function is called from gui then the file has to be located with respect to the gui folder
    if not os.path.isfile(path_to_file):
        path_to_file = os.path.join('../instruments/', path_to_file)

    path_to_file = os.path.abspath(path_to_file)

    if not os.path.isfile(path_to_file):
        print(('path_to_file', path_to_file))
        #raise IOError('{:s}: config file is not valid'.format(path_to_file))
        return None

    f = open(path_to_file, 'r')
    string_of_file_contents = f.read()

    if name[-1] is not ':':
        name += ':'

    if name not in string_of_file_contents:
        return None
    else:
        config_value = [line.split(name)[1] for line in string_of_file_contents.split('\n')
                        if len(line.split(name)) > 1][0].strip()
        return config_value


def load_b26_file(file_name):
    """
    loads a .b26 file into a dictionary

    Args:
        file_name:

    Returns: dictionary with keys instrument, scripts, probes

    """
    # file_name = "Z:\Lab\Cantilever\Measurements\\tmp_\\a"

    assert os.path.exists(file_name)

    with open(file_name, 'r') as infile:
        data = yaml.safe_load(infile)
    return data


def save_b26_file(filename, instruments=None, scripts=None, probes=None, overwrite=False, verbose=False):
    """
    save instruments, scripts and probes as a json file
    Args:
        filename:
        instruments:
        scripts:
        probes: dictionary of the form {instrument_name : probe_1_of_intrument, probe_2_of_intrument, ...}

    Returns:

    """

    # if overwrite is false load existing data and append to new instruments
    if os.path.isfile(filename) and overwrite == False:
        data_dict = load_b26_file(filename)
    else:
        data_dict = {}

    if instruments is not None:
        if 'instruments' in data_dict:
            data_dict['instruments'].update(instruments)
        else:
            data_dict['instruments'] = instruments

    if scripts is not None:
        if 'scripts' in data_dict:
            data_dict['scripts'].update(scripts)
        else:
            data_dict['scripts'] = scripts

    if probes is not None:
        probe_instruments = list(probes.keys())
        if 'probes' in data_dict:
            # all the instruments required for old and new probes
            probe_instruments= set(probe_instruments + list(data_dict['probes'].keys()))
        else:
            data_dict.update({'probes':{}})

        for instrument in probe_instruments:
            if instrument in data_dict['probes'] and instrument in probes:
                # update the data_dict
                data_dict['probes'][instrument] = ','.join(set(data_dict['probes'][instrument].split(',') + probes[instrument].split(',')))
            else:
                data_dict['probes'].update(probes)

    if verbose:
        print(('writing ', filename))

    if data_dict != {}:

        # if platform == 'Windows':
        #     # windows can't deal with long filenames so we have to use the prefix '\\\\?\\'
        #     if len(filename.split('\\\\?\\')) == 1:
        #         filename = '\\\\?\\'+ filename
        # create folder if it doesn't exist
        if verbose:
            print(('filename', filename))
            print(('exists', os.path.exists(os.path.dirname(filename))))

        if os.path.exists(os.path.dirname(filename)) is False:
            # print(('creating', os.path.dirname(filename)))
            os.makedirs(os.path.dirname(filename))

        with open(filename, 'w') as outfile:
            tmp = json.dump(data_dict, outfile, indent=4)

