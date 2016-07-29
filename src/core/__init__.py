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
# some usefull superclasses for the PythonLab project
#Qvariant only need for gui

# try:
#     import sip
#     sip.setapi('QVariant', 2)# set to version to so that the old_gui returns QString objects and not generic QVariants
# except ValueError:
#     pass

from PyLabControl.src.core.instruments import Instrument
from PyLabControl.src.core.parameter import Parameter
from PyLabControl.src.core.probe import Probe
from PyLabControl.src.core.scripts import Script
from PyLabControl.src.core.script_iterator import ScriptIterator
try:
    from read_probes import ReadProbes
except:
    pass
# try:
#     from PyLabControl.src.core.script_sequence import ScriptIterator
# except:
#     pass

__all__ = ['Instrument', 'Parameter']