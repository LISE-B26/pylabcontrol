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


from PyLabControl.src.core import Parameter, Script
import numpy as np
from PyQt4.QtCore import pyqtSlot
from collections import deque
import datetime
import warnings
import inspect
import PyLabControl.src.core.helper_functions as hf
import importlib

class ScriptIterator(Script):
    '''
This is a template class for scripts that iterate over a series of subscripts in either a loop /
a parameter sweep / future: list of points.
CAUTION: This class has some circular dependencies with Script that are avoided by only importing it in very local scope
in Script (since this inherits from Script, it can't be imported globally in Script). Use caution when making changes in
Script.
    '''

    _DEFAULT_SETTINGS = []

    _INSTRUMENTS = {}
    _SCRIPTS = {}
    #_SCRIPTS is populated dynamically with the required subscripts

    _number_of_classes = 0 # keeps track of the number of dynamically created ScriptIterator classes that have been created
    _class_list = [] # list of current dynamically created ScriptIterator classes

    ITER_TYPES = ['loop', 'sweep']

    def __init__(self, scripts, name = None, settings = None, log_function = None, data_path = None):
        """
        Default script initialization
        """
        Script.__init__(self, name, scripts = scripts, settings = settings, log_function= log_function, data_path = data_path)
        print('asdasdada------1111')
        self.iterator_type = self.get_iterator_type(self.settings, scripts)

        self._current_subscript_stage = None

        self._skippable = True

    @staticmethod
    def get_iterator_type(script_settings, subscripts={}):
        """
        figures out the iterator type based on the script settings and (optionally) subscripts
        Args:
            script_settings: iterator_type
            subscripts: subscripts
        Returns:

        """

        if 'iterator_type' in script_settings:
            # figure out the iterator type
            if script_settings['iterator_type'] == 'Loop':
                iterator_type = 'loop'
            elif script_settings['iterator_type'] == 'Parameter Sweep':
                iterator_type = 'sweep'
            else:
                print('XXXXX', script_settings['iterator_type'])
                raise TypeError('unknown iterator type')
        else:
            # asign the correct iterator script type
            if 'sweep_param' in script_settings:
                iterator_type = 'sweep'
            elif 'N' in script_settings:
                iterator_type = 'loop'
            else:
                print(script_settings)
                raise TypeError('unknown iterator type')

        return iterator_type

    def _function(self):
        '''
        Runs either a loop or a parameter sweep over the subscripts in the order defined by the parameter_list 'script_order'
        '''
        def get_sweep_parameters():
            """
            Returns: the paramter values over which to sweep
            """
            #in both cases, param values have tolist to make sure that they are python types (ex float) rather than numpy
            #types (ex np.float64), the latter of which can cause typing issues
            sweep_range = self.settings['sweep_range']
            if self.settings['stepping_mode'] == 'N':
                param_values = np.linspace(sweep_range['min_value'], sweep_range['max_value'],
                                           int(sweep_range['N/value_step']), endpoint=True).tolist()
            elif self.settings['stepping_mode'] == 'value_step':
                param_values = np.linspace(sweep_range['min_value'], sweep_range['max_value'],
                                           (sweep_range['max_value'] - sweep_range['min_value']) / sweep_range[
                                               'N/value_step'] + 1, endpoint=True).tolist()
            return param_values

        script_names = self.settings['script_order'].keys()
        script_indices = [self.settings['script_order'][name] for name in script_names]
        _, sorted_script_names = zip(*sorted(zip(script_indices, script_names)))

        if self.iterator_type == 'sweep':


            def get_script_and_settings_from_str(sweep_param):
                """
                Args:
                    sweep_param: astring with the path to the sweep parameter
                        e.g. script.param.subparam or script->subscript.parameter

                Returns:
                    script_list: a list with the scripts, e.g. [script] or [script, subscript]
                    parameter_list: a list with the paraemeters, e.g. [param, subparam] or [parameter] for the cases above
                """
                split_trace = sweep_param.split('.')
                script_list = split_trace[0].split('->')
                parameter_list = split_trace[1:]

                return script_list, parameter_list

            param_values = get_sweep_parameters()
            for i, value in enumerate(param_values):
                self.iterator_progress = 1. * i / len(param_values)

                script_list, parameter_list = get_script_and_settings_from_str(self.settings['sweep_param'])
                script = self
                while len(script_list)>0:
                    script = script.scripts[script_list[0]]
                    script_list = script_list[1:]

                curr_type = type(reduce(lambda x,y: x[y], parameter_list, script.settings)) #traverse nested dict to get type of variable

                update_dict = reduce(lambda y, x: {x: y}, reversed(parameter_list), curr_type(value)) #creates nested dictionary from list

                script.settings.update(update_dict)
                parameter_name = parameter_list[-1]
                self.log('setting parameter {:s} to {:0.2e}'.format(self.settings['sweep_param'], value))
                for script_name in sorted_script_names:
                    if self._abort:
                        break
                    j = i if self.settings['run_all_first'] else (i+1)
                    if self.settings['script_execution_freq'][script_name] == 0 \
                            or not (j % self.settings['script_execution_freq'][script_name] == 0):  # i+1 so first execution is mth loop, not first
                        continue
                    self.log('starting {:s}'.format(script_name))

                    tag = self.scripts[script_name].settings['tag']
                    self.scripts[script_name].settings['tag'] = '{:s}_{:s}_{:0.3e}'.format(tag, parameter_name, value)
                    self.scripts[script_name].run()
                    self.scripts[script_name].settings['tag'] = tag

        elif self.iterator_type == 'loop':

            N_points = self.settings['N']
            if N_points == 0:
                print('Loop set to run 0 times')
                return
            self.data = {}

            for i in range(0, N_points):
                self.iterator_progress = 1.*i / N_points

                for script_name in sorted_script_names:
                    if self._abort:
                        break
                    j = i if self.settings['run_all_first'] else (i+1)
                    if self.settings['script_execution_freq'][script_name] == 0 \
                            or not (j % self.settings['script_execution_freq'][script_name] == 0):  # i+1 so first execution is mth loop, not first
                        continue
                    self.log('starting {:s} {:03d}/{:03d}'.format(script_name, i + 1, N_points))

                    tag = self.scripts[script_name].settings['tag']
                    tmp = tag + '_{' + ':0{:d}'.format(len(str(N_points))) + '}'
                    self.scripts[script_name].settings['tag'] = tmp.format(i)
                    self.scripts[script_name].run()
                    self.scripts[script_name].settings['tag'] = tag

                # from the last script we take the average of the data as the data of the iterator script
                if isinstance(self.scripts[script_name].data, dict):
                    data = self.scripts[script_name].data
                elif isinstance(self.scripts[script_name].data, deque):
                    data = self.scripts[script_name].data[-1]
                if i == 0:
                    self.data.update(data)
                else:
                    if self._abort:
                        break

                    for key in data.keys():
                        print('sadada script_name', script_name, key)

                        # can't add None values
                        if data[key] is None:
                            continue
                        else:
                            # if subscript data have differnet length, e.g. fitparameters can be differet, depending on if there is one or two peaks
                            if len(self.data[key]) != len(data[key]):
                                print('warning subscript data {:s} have differnt lenghts'.format(key))
                                continue

                            if isinstance(self.data[key], list):
                                self.data[key] += np.array(data[key])
                            elif isinstance(self.data[key], dict):
                                self.data[key] = {x: self.data[key].get(x, 0) + data[key].get(x, 0) for x in self.data[key].keys()}
                            else:
                                self.data[key] += data[key]

            if not self._abort and N_points >0:

                # normalize data because we just kept adding the values
                for key in data.keys():
                    if isinstance(self.data[key], list):
                        self.data[key] = np.array(self.data[key]) / N_points
                    elif isinstance(self.data[key], dict):
                        self.data[key] = {k:v/N_points for k, v in self.data[key].iteritems()}
                    elif self.data[key] is None:
                        print('JG none type in data!! check code')
                        pass
                    elif isinstance(self.data[key], int):
                        self.data[key] = float(self.data[key]) / N_points # if int we can not devide. Thus we convert explicitely to float
                    else:
                        self.data[key] = self.data[key] / N_points

        elif self.iterator_type in (self.TYPE_ITER_NVS, self.TYPE_ITER_POINTS):

            if self.iterator_type == self.TYPE_ITER_NVS:
                set_point = self.scripts['find_nv'].settings['initial_point']
            elif self.iterator_type == self.TYPE_ITER_POINTS:
                set_point = self.scripts['set_laser'].settings['point']

            #shift found by correlation
            [x_shift, y_shift] = [0,0]
            shifted_pt = [0,0]

            self.scripts['correlate_iter'].data['baseline_image'] = self.scripts['select_points'].data['image_data']
            self.scripts['correlate_iter'].data['image_extent'] = self.scripts['select_points'].data['extent']

            points = self.scripts['select_points'].data['nv_locations']
            N_points = len(points)

            for i, pt in enumerate(points):

                # account for displacements found by correlation
                shifted_pt[0] = pt[0] + x_shift
                shifted_pt[1] = pt[1] + y_shift

                print('NV num: {:d}, shifted_pt: {:.3e}, {:.3e}', i, shifted_pt[0], shifted_pt[1])

                self.iterator_progress = 1. * i / N_points

                set_point.update({'x': shifted_pt[0], 'y': shifted_pt[1]})
                self.log('found NV {:03d} near x = {:0.3e}, y = {:0.3e}'.format(i, shifted_pt[0], shifted_pt[1]))
                # skip first script since that is the select NV script!
                for script_name in sorted_script_names[1:]:
                    if self._abort:
                        break
                    j = i if self.settings['run_all_first'] else (i+1)
                    if self.settings['script_execution_freq'][script_name] == 0 \
                            or not (j % self.settings['script_execution_freq'][script_name] == 0):
                        continue
                    self.log('starting {:s}'.format(script_name))
                    tag = self.scripts[script_name].settings['tag']
                    tmp = tag + '_pt_{' + ':0{:d}'.format(len(str(N_points))) + '}'
                    self.scripts[script_name].settings['tag'] = tmp.format(i)
                    self.scripts[script_name].run()
                    self.scripts[script_name].settings['tag'] = tag
                    #after correlation script runs, update new shift value
                    if script_name == 'correlate_iter':
                        [x_shift, y_shift] = self.scripts['correlate_iter'].data['shift']
                        shifted_pt[0] = pt[0] + x_shift
                        shifted_pt[1] = pt[1] + y_shift
                        set_point.update({'x': shifted_pt[0], 'y': shifted_pt[1]})

                        print('NV num: {:d}, shifted_pt: {:.3e}, {:.3e}', i, shifted_pt[0], shifted_pt[1])


        else:
            raise TypeError('wrong iterator type')

    @pyqtSlot(int)
    def _receive_signal(self, progress_subscript):
        """
        this function takes care of signals emitted by the subscripts
        Args:
            progress_subscript: progress of subscript
        """

        # ==== get the current subscript and the time it takes to execute it =====
        current_subscript = self._current_subscript_stage['current_subscript']

        # ==== get the number of subscripts =====
        number_of_subscripts = len(self.scripts)

        # ==== get number of iterations and loop index ======================
        if self.iterator_type == 'loop':
            number_of_iterations = self.settings['N']
        elif self.iterator_type == 'sweep':
            sweep_range = self.settings['sweep_range']
            if self.settings['stepping_mode'] == 'value_step':
                number_of_iterations = len(np.linspace(sweep_range['min_value'], sweep_range['max_value'],
                                                       (sweep_range['max_value'] - sweep_range['min_value']) /
                                                       sweep_range['N/value_step'] + 1, endpoint=True).tolist())
            elif self.settings['stepping_mode'] == 'N':
                number_of_iterations = sweep_range['N/value_step']
            else:
                raise KeyError('unknown key' + self.settings['stepping_mode'])

        elif self.iterator_type == self.TYPE_ITER_NVS:
            number_of_iterations = len(self.scripts['select_points'].data['nv_locations'])
            number_of_subscripts -= 1  # substract 2 because we don't iterate over select nv
        elif self.iterator_type == self.TYPE_ITER_POINTS:

            number_of_iterations = len(self.scripts['select_points'].data['nv_locations'])
            number_of_subscripts -= 1  # substract 1 because we don't iterate over select nv
            print('JG 20171122 testing time prediction: number_of_subscripts', number_of_subscripts)
        else:
            raise TypeError('unknown iterator type')

        # get number of loops (completed + 1)
        loop_index = self.loop_index


        if number_of_subscripts > 1:
            # estimate the progress based on the duration the individual subscripts

            loop_execution_time = 0.  # time for a single loop execution in s
            sub_progress_time = 0.  # progress of current loop iteration in s

            # ==== get typical duration of current subscript ======================
            if current_subscript is not None:
                current_subscript_exec_duration = self._current_subscript_stage['subscript_exec_duration'][
                    current_subscript.name].total_seconds()
            else:
                current_subscript_exec_duration = 0.

            print('JG 20171122 testing time prediction: current_subscript', current_subscript)
            print('JG 20171122 testing time prediction: current_subscript_exec_duration', current_subscript_exec_duration)

            current_subscript_elapsed_time = (datetime.datetime.now() - current_subscript.start_time).total_seconds()
            print(
            'JG 20171122 testing time prediction: current_subscript_elapsed_time', current_subscript_elapsed_time)
            # estimate the duration of the current subscript if the script hasn't been executed once fully and subscript_exec_duration is 0
            if current_subscript_exec_duration == 0.0:
                remaining_time = current_subscript.remaining_time.total_seconds()
                current_subscript_exec_duration = remaining_time + current_subscript_elapsed_time

            # ==== get typical duration of one loop iteration ======================
            remaining_scripts = 0  # script that remain to be executed for the first time
            for subscript_name, duration in self._current_subscript_stage['subscript_exec_duration'].iteritems():
                if duration.total_seconds() == 0.0:
                    remaining_scripts += 1
                loop_execution_time += duration.total_seconds()
                # add the times of the subscripts that have been executed in the current loop
                # ignore the current subscript, because that will be taken care of later
                if self._current_subscript_stage['subscript_exec_count'][
                    subscript_name] == loop_index and subscript_name is not current_subscript.name:
                    # this subscript has already been executed in this iteration
                    sub_progress_time += duration.total_seconds()

            # add the proportional duration of the current subscript given by the subscript progress
            sub_progress_time += current_subscript_elapsed_time

            # if there are scripts that have not been executed yet
            # assume that all the scripts that have not been executed yet take as long as the average of the other scripts
            if remaining_scripts == number_of_subscripts:
                # none of the subscript has been finished. assume that all the scripts take as long as the first
                loop_execution_time = number_of_subscripts * current_subscript_exec_duration
            elif remaining_scripts > 1:
                loop_execution_time = 1. * number_of_subscripts / (number_of_subscripts - remaining_scripts)
            elif remaining_scripts == 1:
                # there is only one script left which is the current script
                loop_execution_time += current_subscript_exec_duration

            if loop_execution_time > 0:
                progress_subscript = 100. * sub_progress_time / loop_execution_time
            else:
                progress_subscript = 1. * progress_subscript / number_of_subscripts

        print('JG 20171122 testing time prediction: loop_index', loop_index)
        print('JG 20171122 testing time prediction: progress_subscript', progress_subscript)
        print('JG 20171122 testing time prediction: number_of_iterations', number_of_iterations)

        # print(' === script iterator progress estimation loop_index = {:d}/{:d}, progress_subscript = {:f}'.format(loop_index, number_of_iterations, progress_subscript))
        self.progress = 100. * (loop_index - 1. + 0.01 * progress_subscript) / number_of_iterations

        self.updateProgress.emit(int(self.progress))

    def skip_next(self):
        for script in self.scripts.itervalues():
            script.stop()

    @property
    def loop_index(self):
        loop_index = max(self._current_subscript_stage['subscript_exec_count'].values())
        return loop_index

    def plot(self, figure_list):
        '''
        When each subscript is called, uses its standard plotting

        Args:
            figure_list: list of figures passed from the guit

        '''

        #TODO: be smarter about how we plot ScriptIterator
        if self._current_subscript_stage is not None:
            if self._current_subscript_stage['current_subscript'] is not None:
                self._current_subscript_stage['current_subscript'].plot(figure_list)

        if (self.is_running is False) and not (self.data == {} or self.data is None):

            script_names = self.settings['script_order'].keys()
            script_indices = [self.settings['script_order'][name] for name in script_names]
            _, sorted_script_names = zip(*sorted(zip(script_indices, script_names)))

            last_script = self.scripts[sorted_script_names[-1]]

            last_script.force_update()  # since we use the last script plot function we force it to refresh

            axes_list = last_script.get_axes_layout(figure_list)

            # catch error is _plot function doens't take optional data argument
            try:
                last_script._plot(axes_list, self.data)
            except TypeError, err:
                print(warnings.warn('can\'t plot average script data because script.plot function doens\'t take data as optional argument. Plotting last data set instead'))
                print(err.message)
                last_script.plot(figure_list)


    def to_dict(self):
        """
        Returns: itself as a dictionary
        """
        dictator = Script.to_dict(self)
        # the dynamically created ScriptIterator classes have a generic name
        # replace this with ScriptIterator to indicate that this class is of type ScriptIterator
        dictator[self.name]['class'] = 'ScriptIterator'


        #todo JG: try to replace by following to keep track of real class
        # dictator[self.name]['class'] = self.__module__.split('.')[0]


        return dictator
    @staticmethod
    def get_iterator_default_script(iterator_type):
        """
        This function might be overwritten by functions that inherit from ScriptIterator
        Returns:
            sub_scripts: a dictionary with the default scripts for the script_iterator
            script_settings: a dictionary with the script_settingsfor the default scripts

        """

        sub_scripts = {}
        script_settings = {}
        return sub_scripts, script_settings

    @staticmethod
    def get_script_order(script_order):
        """

        Args:
            script_order:
                a dictionary giving the order that the scripts in the ScriptIterator should be executed.
                Must be in the form {'script_name': int}. Scripts are executed from lowest number to highest

        Returns:
            script_order_parameter:
                A list of parameters giving the order that the scripts in the ScriptIterator should be executed.
            script_execution_freq:
                A list of parameters giving the frequency with which each script should be executed

        """
        script_order_parameter = []
        script_execution_freq = []
        # update the script order
        for sub_script_name in script_order.keys():
            script_order_parameter.append(Parameter(sub_script_name, script_order[sub_script_name], int,
                                          'Order in queue for this script'))

            script_execution_freq.append(Parameter(sub_script_name, 1, int,
                                                       'How often the script gets executed ex. 1 is every loop, 3 is every third loop, 0 is never'))

        return script_order_parameter, script_execution_freq

    @staticmethod
    def get_default_settings(sub_scripts, script_order, script_execution_freq, iterator_type):
        """
        assigning the actual script settings depending on the iterator type

        this might be overwritten by classes that inherit form ScriptIterator

        Args:
            sub_scripts: dictionary with the subscripts
            script_order: execution order of subscripts
            script_execution_freq: execution frequency of subscripts

        Returns:
            the default setting for the iterator

        """

        if iterator_type == 'loop':
            script_default_settings = [
                Parameter('script_order', script_order),
                Parameter('script_execution_freq', script_execution_freq),
                Parameter('N', 0, int, 'times the subscripts will be executed'),
                Parameter('run_all_first', True, bool, 'Run all scripts with nonzero frequency in first pass')
            ]
        else:
            print('unknown iterator type ' + iterator_type)
            raise TypeError('unknown iterator type ' + iterator_type)

        return script_default_settings

    @staticmethod
    def create_dynamic_script_class(script_information, script_iterators={},verbose=False):
        '''
        creates all the dynamic classes in the script and the class of the script itself
        and updates the script info with these new classes

        Args:
            script_information: A dictionary describing the ScriptIterator, or an existing object
            script_iterators: dictionary with the scriptiterators (optional)

        Returns:
            script_information:  The updated dictionary describing the newly created ScriptIterator class
            script_iterators: updated dictionary with the scriptiterators
        Poststate: Dynamically created classes inheriting from ScriptIterator are added to src.scripts

        '''


        def set_up_dynamic_script(script_information, script_iterators, verbose=verbose):
            '''

            Args:
                script_information: information about the script as required by Script.get_script_information()

            Returns:
                script_default_settings: the default settings of the dynamically created script as a list of parameters
                sub_scripts

                script_iterators: dictionary of the script_iterator classes of the form {'package_name': <script_iterator_classe>}
                package: name of the package of the script_iterator

            '''

            if verbose:
                print('script_information', script_information)
            sub_scripts = {}  # dictonary of script classes that are to be subscripts of the dynamic class. Should be in the dictionary form {'class_name': <class_object>} (btw. class_object is not the instance)
            script_order = []  # A list of parameters giving the order that the scripts in the ScriptIterator should be executed. Must be in the form {'script_name': int}. Scripts are executed from lowest number to highest
            script_execution_freq = [] # A list of parameters giving the frequency with which each script should be executed
            _, script_class_name, script_settings, _, script_sub_scripts, _, package = Script.get_script_information(script_information)
            # module, script_class_name, script_settings, script_instruments, script_sub_scripts, package


            if not package in script_iterators:
                script_iterators.update(ScriptIterator.get_script_iterator(package))

            assert package in script_iterators

            iterator_type = getattr(script_iterators[package], 'get_iterator_type')(script_settings, script_sub_scripts)
            if verbose:
                print('iterator_type  JG', iterator_type)

            if isinstance(script_information, dict):

                for sub_script_name, sub_script_class in script_sub_scripts.iteritems():
                    if isinstance(sub_script_class, Script):
                        print('JG: script name is script', Script.name)
                        # script already exists
                        raise NotImplementedError
                    elif script_sub_scripts[sub_script_name]['class'] == 'ScriptIterator':
                        print('JG: script name is iterator', Script.name)
                        # raise NotImplementedError # has to be dynamic maybe???
                        script_information_subclass,  script_iterators = ScriptIterator.create_dynamic_script_class(script_sub_scripts[sub_script_name], script_iterators)
                        subscript_class_name = script_information_subclass['class']
                        # import PyLabControl.src.scripts
                        import PyLabControl.src.core.script_iterator
                        sub_scripts.update({sub_script_name: getattr(PyLabControl.src.core.script_iterator, subscript_class_name)})
                    else:
                        if verbose:
                            print('script_sub_scripts[sub_script_name]', sub_script_class)

                        # script_dict = {script_sub_scripts[sub_script_name]['class']}
                        module = Script.get_script_module(sub_script_class, verbose=verbose)

                        if verbose:
                            print('module', module)
                        new_subscript = getattr(module, script_sub_scripts[sub_script_name]['class'])

                        print('new_subscript', new_subscript)
                        sub_scripts.update({sub_script_name: new_subscript})

                print('gggggg', sub_scripts)

                # for some iterators have default scripts, e.g. point iteration has select points
                default_sub_scripts, default_script_settings = getattr(script_iterators[package], 'get_iterator_default_script')(iterator_type)
                sub_scripts.update(default_sub_scripts)
                print('gggggg', sub_scripts)

                print('oo', script_settings)
                print('oo script_settings', script_settings)
                script_settings.update(default_script_settings)
                print('oo', script_settings)

                # if verbose:
                print('default_sub_scripts', default_sub_scripts)
                print('default_script_settings', default_script_settings)

            elif isinstance(script_information, Script):

                print('old code - DOUBLE CHECK')
                raise NotImplementedError
                # if the script already exists, just update the script order parameter
                sub_scripts.update({script_class_name: script_information})
            else:
                raise TypeError('create_dynamic_script_class: unknown type of script_information')

            script_order, script_execution_freq = getattr(script_iterators[package], 'get_script_order')(script_settings['script_order'])

            script_default_settings = getattr(script_iterators[package], 'get_default_settings')(sub_scripts, script_order, script_execution_freq, iterator_type)
            if verbose:
                print('()()()()()', script_default_settings)
                print('()()()()()', sub_scripts)
                print('()()()()()', script_iterators, package)

            return script_default_settings, sub_scripts, script_iterators, package

        def create_script_iterator_class(sub_scripts, script_settings, script_iterator_base_class, verbose=verbose):
            '''
            A 'factory' to create a ScriptIterator class at runtime with the given inputs.

            Args:
                sub_scripts: dictonary of script classes that are to be subscripts of the dynamic class. Should be in the dictionary
                         form {'class_name': <class_object>} (btw. class_object is not the instance)
                script_default_settings: the default settings of the dynamically created object. Should be a list of Parameter objects.

            Returns: A newly created class inheriting from ScriptIterator, with the given subscripts and default settings

            '''


            # from PyLabControl.src.core import ScriptIterator
            #


            if verbose:
                print('\n\n======== create_script_iterator_class ========\n')
                print('sub_scripts', sub_scripts)
                print('script_settings', script_settings)
                print('script_iterator_base_class', script_iterator_base_class)

            class_name = 'dynamic_script_iterator' + str(script_iterator_base_class._number_of_classes)

            if verbose:
                print('class_name', class_name)

            dynamic_class = type(class_name, (script_iterator_base_class,), {'_SCRIPTS': sub_scripts, '_DEFAULT_SETTINGS': script_settings, '_INSTRUMENTS': {}})
            # JG old with ScriptIterator hard coded the above should be good!
            #  dynamic_class = type(class_name, (ScriptIterator,),
            #                      {'_SCRIPTS': sub_scripts, '_DEFAULT_SETTINGS': script_settings, '_INSTRUMENTS': {}})


            if verbose:
                print('dynamic_class', dynamic_class)
                print('__bases__', dynamic_class.__bases__)


            # Now we place the dynamic script into the scope of src.scripts as regular scripts.
            # This is equivalent to importing the module in src.scripts.__init__, but because the class doesn't exist until runtime it must be done here.
            # OLD START
            import PyLabControl.src.core.script_iterator
            setattr(PyLabControl.src.core.script_iterator, class_name, dynamic_class)
            # OLD END

            # importlib.import_module(package + '.src.core.script_iterator')
            # setattr
            # import PyLabControl.src.core.scripts
            # setattr(PyLabControl.src.core.scripts, class_name, dynamic_class)

            ScriptIterator._class_list.append(dynamic_class)
            ScriptIterator._number_of_classes += 1


            if verbose:
                print('ScriptIterator._class_list', ScriptIterator._class_list)

            if verbose:
                print('\n===== end create_script_iterator_class ========\n')

            return class_name, dynamic_class

            # todo: prevent multiple importation of the same script with different names
            # for someclass in cls._class_list:
            #     if (vars(ss)['_SCRIPTS'] == vars(someclass)['_SCRIPTS']):
            #         print('CLASSNAME', vars(someclass)['_CLASS'])
            #         return vars(someclass)['_CLASS']


        # if verbose:
        print('       <======> JG script_information', script_information['class'])

        # get default setting, load subscripts, load the script_iterators and identify the package
        script_default_settings, sub_scripts, script_iterators, package = set_up_dynamic_script(script_information, script_iterators, verbose=False)

        # now actually create the classs
        class_name, dynamic_class = create_script_iterator_class(sub_scripts, script_default_settings, script_iterators[package], verbose = True)

        # update the generic name (e.g. ScriptIterator) to a unique name  (e.g. ScriptIterator_01)
        script_information['class'] = class_name

        if 'iterator_type' in script_information['settings']:

            if verbose:
                print('WONDER IF WE EVER HAVE THIS CASE: iterator_type in script_information[setting]')
            # if script_information['settings'] contains only the iterator type
            # update the script settings
            #       from  {'script_order': DICT_WITH_SUBSCRIPT_ORDER, 'iterator_type': ITERATOR_TYPE}
            #       to {'script_order': DICT_WITH_SUBSCRIPT_ORDER, 'param1': ACTUAL PARAMETER 1, , 'param2': ACTUAL PARAMETER 2, ..}
            script_settings = {}
            for elem in script_default_settings:
                script_settings.update(elem)
            script_information['settings'] = script_settings

        if verbose:
            print('\n\n======== create_dynamic_script_class ========\n')

            print('dynamic_class', dynamic_class)
            print('sub_scripts', sub_scripts)
            print('script_settings', script_settings)

        if verbose:
            print('\n======== end create_dynamic_script_class ========\n')

        return script_information, script_iterators

    @staticmethod
    def get_script_iterator(package, verbose = False):
        """


        Args:
            package: name of package

        Returns: the script_iterators of the package as a dictionary

        """

        packs = hf.explore_package(package + '.src.core')
        script_iterator = {}

        for p in packs:

            for name, c in inspect.getmembers(importlib.import_module(p), inspect.isclass):

                if verbose:
                    print(p, name, c)

                if issubclass(c, ScriptIterator):
                    # update dictionary with 'Package name , e.g. PyLabControl or b26_toolkit': <ScriptIterator_class>
                    script_iterator.update({c.__module__.split('.')[0]: c})


        return script_iterator



if __name__ == '__main__':




    # test get_script_iterator
    package = 'PyLabControl'
    # package = 'b26_toolkit'

    script_iterator = ScriptIterator.get_script_iterator(package, verbose = True)
    print('script_iterator', script_iterator)
    #
    # inspect.getmembers(importlib.import_module(p), inspect.isclass)
    # script_iterator = importlib.import_module(script_iterator)








    #
    # from PyLabControl.src.scripts.script_dummy import ScriptDummy
    # path_to_script_file = inspect.getmodule(ScriptDummy).__file__.replace('.pyc', '.py')
    #
    # iterator_type = 'Loop'# 'Iter Pts'
    #
    # package = 'PyLabControl' #'b26_toolkit'
    #
    # script_info = {'iter_script':
    #                    {'info': 'Enter docstring here',
    #                     'scripts': {'ScriptDummy':
    #                         {
    #                             'info': '\nExample Script that has all different types of parameters (integer, str, fload, point, list of parameters). Plots 1D and 2D data.\n    ',
    #                             'settings': {'count': 3, 'name': 'this is a counter', 'wait_time': 0.1,
    #                                          'point2': {'y': 0.1, 'x': 0.1}, 'tag': 'scriptdummy',
    #                                          'path': '', 'save': False, 'plot_style': 'main'},
    #                             'class': 'ScriptDummy',
    #                             'filepath': path_to_script_file}},
    #                     'class': 'ScriptIterator',
    #                     'settings': {'script_order': {'ScriptDummy': 0}, 'iterator_type': iterator_type},
    #                     'package': package}}
    #
    # si = ScriptIterator.create_dynamic_script_class(script_info['iter_script'], verbose=True)
    #
    # print(si)