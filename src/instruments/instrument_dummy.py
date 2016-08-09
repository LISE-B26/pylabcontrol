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
from PyLabControl.src.core import Instrument, Parameter
from PyQt4.QtCore import QThread
import random, time

class DummyInstrument(Instrument):
    '''
    Dummy instrument
    a implementation of a dummy instrument
    '''

    _DEFAULT_SETTINGS = Parameter([
        Parameter('test1', 0, int, 'some int parameter'),
        Parameter('output probe2', 0, int, 'return value of probe 2 (int)'),
        Parameter('test2',
                  [Parameter('test2_1', 'string', str, 'test parameter (str)'),
                   Parameter('test2_2', 0.0, float, 'test parameter (float)')
                   ])
    ])

    _PROBES = {'value1': 'this is some value from the instrument',
               'value2': 'this is another',
               'internal': 'gives the internal state variable',
               'deep_internal': 'gives another internal state variable'
               }

    def __init__(self, name =  None, settings = None):
        self._test_variable = 1
        super(DummyInstrument, self).__init__(name, settings)
        self._internal_state = None
        self._internal_state_deep = None


    def update(self, settings):
        '''
        updates the internal dictionary and sends changed values to instrument
        Args:
            settings: parameters to be set
        # mabe in the future:
        # Returns: boolean that is true if update successful

        '''
        Instrument.update(self, settings)

        for key, value in settings.iteritems():
            if key == 'test1':
                self._internal_state = value



    def read_probes(self, key):
        """
        requestes value from the instrument and returns it
        Args:
            key: name of requested value

        Returns: reads values from instrument

        """
        assert key in self._PROBES.keys()

        import random
        if key == 'value1':
            value = random.random()
        elif key == 'value2':
            value = self.settings['output probe2']
        elif key == 'internal':
            value = self._internal_state
        elif key == 'deep_internal':
            value = self._internal_state_deep

        return value

    @property
    def is_connected(self):
        '''
        check if instrument is active and connected and return True in that case
        :return: bool
        '''
        return self._is_connected


class DummyInstrumentThreaded(Instrument, QThread):

    _DEFAULT_SETTINGS = Parameter([
        Parameter('update frequency', 0.2, float, 'update frequency of signal in Hz'),
        Parameter('noise_strength',1.0, float, 'strength of noise (float)'),
        Parameter('controler', 0.0, float, 'strength of noise (float)')
    ])

    _PROBES = {'output': 'this is some random output signal (float)'
               }

    def __init__(self, name =  None, settings = None):

        QThread.__init__(self)
        Instrument.__init__(self, name, settings)
        self._is_connected = True
        self._output = 0
        self.start()

    def start(self, *args, **kwargs):
        """
        start the read_probe thread
        """
        print('starting')
        self._stop = False
        super(DummyInstrumentThreaded, self).start(*args, **kwargs)


    def quit(self, *args, **kwargs):  # real signature unknown
        """
        quit the  read_probe thread
        """
        print('stopping')
        self._stop = True
        super(DummyInstrumentThreaded, self).quit(*args, **kwargs)

    def run(self):
        """
        this is the actual execution of the ReadProbes thread: continuously read values from the probes
        """

        while self._stop is False:

            self._output = random.random()

            # self.updateProgress.emit(1)

            self.msleep(int(1e3*self.settings['update frequency']))




    def read_probes(self, key):
        """
        requestes value from the instrument and returns it
        Args:
            key: name of requested value

        Returns: reads values from instrument

        """
        assert key in self._PROBES.keys()

        if key == 'output':
            value = self._output

        return value

    @property
    def is_connected(self):
        '''
        check if instrument is active and connected and return True in that case
        :return: bool
        '''
        return self._is_connected

if __name__ == '__main__':

    d = DummyInstrumentThreaded()
    for i in range(15):
        time.sleep(0.1)
        print(d.read_probes('output'))
    print('done')
