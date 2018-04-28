
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


# B26 Lab Code
# Last Update: 2/3/15
import serial

def scan():
    """
    scan for available ports. return a list of tuples (num, name)
    Returns:

    """
    available = []
    for i in range(256):
        try:
            s = serial.Serial('COM'+str(i))
            available.append((i, s.portstr))
            s.close()
        except serial.SerialException:
            pass
    return available

if __name__ == '__main__':
    print("Found ports:")
    for n,s in scan(): print("(%d) %s" % (n,s))
    print('done')