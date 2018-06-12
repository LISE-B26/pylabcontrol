
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


from unittest import TestCase

import os, inspect
from pylabcontrol.core.helper_functions import module_name_from_path
from pylabcontrol.scripts.example_scripts import ExampleScript



class TestHelperFunctions(TestCase):

    # def __init__(self):
    #     self.filename = inspect.getmodule(ScriptDummy).__file__


    def test_module_name_from_path_1(self):


        package_name = 'pylabcontrol'

        filename = inspect.getmodule(ExampleScript).__file__
        # check that file actually exists
        assert os.path.isfile(filename)

        module, path = module_name_from_path(filename, verbose=False)


        assert module == 'pylabcontrol.scripts.script_dummy'
        assert path == os.path.normpath(filename.split(package_name)[0])
