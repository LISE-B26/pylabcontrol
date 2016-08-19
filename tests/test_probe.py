
# This file is part of PyLabControl, software for laboratory equipment control for scientific experiments.
# Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell
#
#
# PyLabControl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyLabControl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyLabControl.  If not, see <http://www.gnu.org/licenses/>.

from unittest import TestCase
from src.core import instantiate_instruments, Probe

class TestProbe(TestCase):

    def test_init(self):
        from src.core import instantiate_instruments
        instruments = {'inst_dummy': 'DummyInstrument'}

        instrument = instantiate_instruments(instruments)['inst_dummy']

        p = Probe(instrument, 'value1', 'random')

        print(instruments['inst_dummy'])

        print(p.name)
        print(p.value)
        print(p.value)
