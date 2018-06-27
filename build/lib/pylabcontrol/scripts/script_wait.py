
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


import numpy as np
import datetime
import time

from pylabcontrol.core import Script, Parameter

class Wait(Script):
    """
Script that waits. This is useful to execute scripts in a loop at given intervals.
There are two modes of operation:
    wait_mode = absolute: the script waits the time defined in wait_time
    wait_mode = loop_interval: the script waits as long such that the loop time equals the time defined in wait_time
    """
    _DEFAULT_SETTINGS = [
        Parameter('wait_time', 1.0, float, 'time to wait in seconds'),
        Parameter('wait_mode', 'absolute', ['absolute', 'loop_interval'], 'absolute: wait for wait_time,  loop_interval: wait such that this script is executed every wait_time')
    ]

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    def __init__(self, instruments = None, scripts = None, name = None, settings = None, log_function = None, data_path = None):
        """
        Select points by clicking on an image
        """
        Script.__init__(self, name, settings = settings, instruments = instruments, scripts = scripts, log_function= log_function, data_path = data_path)

        self.last_execution = None

    def _function(self):
        """
        Waits until stopped to keep script live. Gui must handle calling of Toggle_NV function on mouse click.
        """

        start_time = datetime.datetime.now()

        # calculate stop time
        if self.settings['wait_mode'] == 'absolute':
            stop_time = start_time + datetime.timedelta(seconds= self.settings['wait_time'])
        elif self.settings['wait_mode'] == 'loop_interval':
            if self.last_execution is None:
                stop_time = start_time
            else:
                loop_time = start_time - self.last_execution
                wait_time = datetime.timedelta(seconds= self.settings['wait_time'])
                if wait_time.total_seconds() <0:
                    stop_time = start_time
                else:
                    stop_time = start_time + wait_time
        else:
            TypeError('unknown wait_mode')

        current_time = start_time
        while current_time<stop_time:
            if self._abort:
                break
            current_time = datetime.datetime.now()

            time.sleep(1)

            self.progress = 100.*(current_time- start_time).total_seconds() / (stop_time - start_time).total_seconds()
            self.updateProgress.emit(int(self.progress))

        if self.settings['wait_mode'] == 'absolute':
            self.last_execution = None
        else:
            self.last_execution = start_time



if __name__ == '__main__':

    pass