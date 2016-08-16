"""
    This file is part of PyLabControl, software for laboratory equipment control for scientific experiments.
    Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell


    PyLabControl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyLabControl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PyLabControl.  If not, see <http://www.gnu.org/licenses/>.

"""

import os, inspect
# from importlib import import_module
# from PyLabControl.src.core import Instrument, Script


def module_name_from_path(folder_name):
    """
    takes in a path to a folder or file and return the module path and the path to the module
    Args:
        folder_name:

    Returns:
        module: a string of the form module.submodule.submodule ...
        path: a string with the path to the module

    """
    # strip off endings
    folder_name = folder_name.split('.pyc')[0]
    folder_name = folder_name.split('.py')[0]

    folder_name = os.path.normpath(folder_name)
    path = folder_name + '/'
    module = []
    while path not in os.sys.path:
        path = os.path.dirname(path)
        if path == os.path.dirname(path):
            path, module = None, None
            break
        module.append(os.path.basename(path))

    module = module[:-1]
    # print('mod', module)
    # from the list construct the path like b26_toolkit.src.scripts and load it
    module.reverse()
    module = '.'.join(module)

    return module, path






if __name__ == '__main__':



    print('aaa')
    for x in os.sys.path:
        print(x)

    folder_name = 'C://Users//Experiment//PycharmProjects//PyLabControl//src//core'
    print(module_name_from_path(folder_name))