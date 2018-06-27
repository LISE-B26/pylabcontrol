
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


from pylabcontrol.core import Parameter, Script
from pylabcontrol.instruments import DummyInstrument
import numpy as np
import datetime

from pylabcontrol.instruments import Plant, PIControler
import time
from collections import deque
from copy import deepcopy
from pylabcontrol.data_processing.signal_processing import power_spectral_density

class ScriptMinimalDummy(Script):
    """
Minimal Example Script that has only a single parameter (execution time)
    """

    _DEFAULT_SETTINGS = [
        Parameter('execution_time', 0.1, float, 'execution time of script (s)')
    ]

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    def __init__(self, name=None, settings=None,
                 log_function = None, data_path = None):
        """
        Example of a script
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings, log_function= log_function, data_path = data_path)


    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        import time
        time.sleep(self.settings['execution_time'])


class ScriptDummy(Script):
    """
Example Script that has all different types of parameters (integer, str, fload, point, list of parameters). Plots 1D and 2D data.
    """

    _DEFAULT_SETTINGS = [
        Parameter('count', 3, int),
        Parameter('name', 'this is a counter'),
        Parameter('wait_time', 0.1, float),
        Parameter('point2',
                  [Parameter('x', 0.1, float, 'x-coordinate'),
                   Parameter('y', 0.1, float, 'y-coordinate')
                  ]),
        Parameter('plot_style', 'main', ['main', 'aux', '2D', 'two'])
    ]

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    def __init__(self, name=None, settings=None, log_function = None, data_path = None):
        """
        Example of a script
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings, log_function= log_function, data_path = data_path)



    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        # some generic function
        import time
        import random
        self.data['random data'] = None
        self.data['image data'] = None
        count = self.settings['count']
        name = self.settings['name']
        wait_time = self.settings['wait_time']

        data = []
        self.log('I ({:s}) am a test function counting to {:d} and creating random values'.format(self.name, count))
        for i in range(count):
            time.sleep(wait_time)
            self.log('{:s} count {:02d}'.format(self.name, i))
            data.append(random.random())
            self.data = {'random data': data}
            self.progress = 100. * (i + 1) / count
            self.updateProgress.emit(self.progress)


        self.data = {'random data':data}


        # create image data
        Nx = int(np.sqrt(len(self.data['random data'])))
        img = np.array(self.data['random data'][0:Nx ** 2])
        img = img.reshape((Nx, Nx))
        self.data.update({'image data': img})


    def _plot(self, axes_list, data = None):
        """
        plots the data only the axes objects that are provided in axes_list
        Args:
            axes_list: a list of axes objects, this should be implemented in each subscript
            data: data to be plotted if empty take self.data
        Returns: None

        """

        plot_type = self.settings['plot_style']
        if data is None:
            data = self.data

        if data is not None and data is not {}:
            if plot_type in ('main', 'two'):
                if not data['random data'] is None:
                    axes_list[0].plot(data['random data'])
                    axes_list[0].hold(False)
            if plot_type in ('aux', 'two', '2D'):
                if not data['random data'] is None:
                    axes_list[1].plot(data['random data'])
                    axes_list[1].hold(False)
            if plot_type == '2D':
                if 'image data' in data and not data['image data'] is None:
                    fig = axes_list[0].get_figure()
                    implot = axes_list[0].imshow(data['image data'], cmap='pink', interpolation="nearest", extent=[-1,1,1,-1])
                    fig.colorbar(implot, label='kcounts/sec')

    def _update(self, axes_list):
        """
        updates the data in already existing plots. the axes objects are provided in axes_list
        Args:
            axes_list: a list of axes objects, this should be implemented in each subscript

        Returns: None

        """
        plot_type = self.settings['plot_style']
        if plot_type == '2D':
            # we expect exactely one image in the axes object (see ScriptDummy.plot)
            implot = axes_list[1].get_images()[0]
            # now update the data
            implot.set_data(self.data['random data'])

            colorbar = implot.colorbar

            if not colorbar is None:
                colorbar.update_bruteforce(implot)

        else:
            # fall back to default behaviour
            Script._update(self, axes_list)

class ScriptDummyWrapper(Script):
    """
Example Script that has all different types of parameters (integer, str, fload, point, list of parameters). Plots 1D and 2D data.
    """

    _DEFAULT_SETTINGS = []

    _INSTRUMENTS = {}
    _SCRIPTS = {'ScriptDummy': ScriptDummy}

    def __init__(self, instruments = None, scripts = None, name=None, settings=None, log_function = None, data_path = None):
        """
        Example of a script
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        super(ScriptDummyWrapper, self).__init__(self, name, settings, log_function= log_function, data_path=data_path)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        self.scripts['ScriptDummy'].run()


    def _plot(self, axes_list, data = None):
        """
        plots the data only the axes objects that are provided in axes_list
        Args:
            axes_list: a list of axes objects, this should be implemented in each subscript
            data: data to be plotted if empty take self.data
        Returns: None

        """

        self.scripts['ScriptDummy']._plot(axes_list)

    def _update(self, axes_list):
        """
        updates the data in already existing plots. the axes objects are provided in axes_list
        Args:
            axes_list: a list of axes objects, this should be implemented in each subscript

        Returns: None

        """
        self.scripts['ScriptDummy']._update(axes_list)


class DummyPlantWithControler(Script):
    """
    script to bring the detector response to zero
    two channels are set to a fixed voltage while the signal of the third channel is varied until the detector response is zero
    """

    _DEFAULT_SETTINGS = [
        Parameter('sample rate', 0.5, float, 'sample rate in Hz'),
        Parameter('on/off', True, bool, 'control is on/off'),
        Parameter('buffer_length', 500, int, 'length of data buffer')
    ]

    _INSTRUMENTS = {
        'plant': Plant,
        'controler': PIControler
    }

    _SCRIPTS = {

    }

    def __init__(self, instruments, scripts = None, name=None, settings=None, log_function=None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """

        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments, log_function=log_function, data_path = data_path)
        self.data = {'plant_output': deque(maxlen=self.settings['buffer_length']),
                     'control_output': deque(maxlen=self.settings['buffer_length'])}
    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        plant = self.instruments['plant']['instance']
        controler = self.instruments['controler']['instance']
        plant.update(self.instruments['plant']['settings'])
        controler.update(self.instruments['controler']['settings'])

        time_step = 1./self.settings['sample rate']

        controler.update({'time_step': time_step})
        self.last_plot = datetime.datetime.now()

        controler.reset()
        # if length changed we have to redefine the queue and carry over the data
        if self.data['plant_output'].maxlen != self.settings['buffer_length']:
            plant_output = deepcopy(self.data['plant_output'])
            control_output = deepcopy(self.data['control_output'])
            self.data = {'plant_output': deque(maxlen=self.settings['buffer_length']),
                         'control_output': deque(maxlen=self.settings['buffer_length'])}

            x = list(range(min(len(plant_output), self.settings['buffer_length'])))
            x.reverse()
            for i in x:
                self.data['plant_output'].append(plant_output[-i-1])
                self.data['control_output'].append(control_output[-i - 1])

        while not self._abort:

            measurement = plant.output

            self.data['plant_output'].append(measurement)
            control_value = controler.controler_output(measurement)
            self.data['control_output'].append(control_value)

            if self.settings['on/off']:
                print(('set plant control', control_value))
                plant.control = float(control_value)

            self.progress = 50
            self.updateProgress.emit(self.progress)

            time.sleep(time_step)






    def _plot(self, axes_list):

        if len(self.data['plant_output']) >0:
            time_step = 1. / self.settings['sample rate']
            axes1, axes2 = axes_list

            # plot time domain signals
            axes1.hold(False)
            signal = self.data['plant_output']
            control_value = self.data['control_output']

            t = np.linspace(0, len(signal)*time_step, len(signal))
            axes1.plot(t, signal, '-o')
            axes1.hold(True)
            axes1.plot(t, control_value, '-o')


            axes1.set_title('time signal')
            axes1.set_xlabel('time (s)')


            # only plot spectra if there is a sufficiently long signal and only refresh after 5 seconds


            if (len(signal)>2 and (datetime.datetime.now()-self.last_plot).total_seconds() > 5) or self.is_running is False:
                # plot freq domain signals
                axes2.hold(False)
                f, psd = power_spectral_density(signal, time_step)
                axes2.loglog(f, psd, '-o')
                axes2.hold(True)
                f, psd = power_spectral_density(control_value, time_step)
                axes2.loglog(f, psd, '-o')
                axes2.set_title('spectra')
                axes1.set_xlabel('frequency (Hz)')
                self.last_plot = datetime.datetime.now()








if __name__ == '__main__':
    d_instr = Plant()
    d = DummyPlantWithControler(instruments = {'plant' : Plant(), 'controler': PIControler()})

    print(d)
