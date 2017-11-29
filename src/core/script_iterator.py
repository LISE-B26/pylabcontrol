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

    TYPE_LOOP = 0
    TYPE_SWEEP_PARAMETER = 1
    TYPE_ITER_NVS = 2
    TYPE_ITER_POINTS = 3

    def __init__(self, scripts, name = None, settings = None, log_function = None, data_path = None):
        """
        Default script initialization
        """
        Script.__init__(self, name, scripts = scripts, settings = settings, log_function= log_function, data_path = data_path)

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
                iterator_type = ScriptIterator.TYPE_LOOP
            elif script_settings['iterator_type'] == 'Parameter Sweep':
                iterator_type = ScriptIterator.TYPE_SWEEP_PARAMETER
            elif script_settings['iterator_type'] == 'Iter NVs':
                iterator_type = ScriptIterator.TYPE_ITER_NVS
            elif script_settings['iterator_type'] == 'Iter Points':
                iterator_type = ScriptIterator.TYPE_ITER_POINTS
            else:
                raise TypeError('unknown iterator type')
        else:
            # asign the correct iterator script type
            if 'sweep_param' in script_settings:
                iterator_type = ScriptIterator.TYPE_SWEEP_PARAMETER
            elif 'find_nv' in subscripts and 'select_points' in subscripts:
                iterator_type = ScriptIterator.TYPE_ITER_NVS
            elif 'set_laser' in subscripts and 'select_points' in subscripts:
                iterator_type = ScriptIterator.TYPE_ITER_POINTS
            elif 'N' in script_settings:
                iterator_type = ScriptIterator.TYPE_LOOP
            else:
                print(script_settings, subscripts)
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

        if self.iterator_type == self.TYPE_SWEEP_PARAMETER:


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

        elif self.iterator_type == self.TYPE_LOOP:

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
        if self.iterator_type == self.TYPE_LOOP:
            number_of_iterations = self.settings['N']
        elif self.iterator_type == self.TYPE_SWEEP_PARAMETER:
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

        return dictator


    @staticmethod
    def create_dynamic_script_class(script_information):
        '''
        creates all the dynamic classes in the script and the class of the script itself
        and updates the script info with these new classes

        Args:
            script_information: A dictionary describing the ScriptIterator, or an existing object

        Returns: script_information:  The updated dictionary describing the newly created ScriptIterator class
        Poststate: Dynamically created classes inheriting from ScriptIterator are added to src.scripts

        '''


        def set_up_dynamic_script(script_information):
            '''

            Args:
                script_information: information about the script as required by Script.get_script_information()

            Returns: script_default_settings: the default settings of the dynamically created script as a list of parameters

            '''

            def populate_sweep_param(scripts, parameter_list, trace=''):
                '''

                Args:
                    scripts: a dict of {'class name': <class object>} pairs

                Returns: A list of all parameters of the input scripts

                '''

                def get_parameter_from_dict(trace, dic, parameter_list, valid_values = None):
                    """
                    appends keys in the dict to a list in the form trace.key.subkey.subsubkey...
                    Args:
                        trace: initial prefix (path through scripts and parameters to current location)
                        dic: dictionary
                        parameter_list: list to which append the parameters

                        valid_values: valid values of dictionary values if None dic should be a dictionary

                    Returns:

                    """
                    if valid_values is None and isinstance(dic, Parameter):
                        valid_values = dic.valid_values

                    for key, value in dic.iteritems():
                        if isinstance(value, dict):  # for nested parameters ex {point: {'x': int, 'y': int}}
                            parameter_list = get_parameter_from_dict(trace + '.' + key, value, parameter_list, dic.valid_values[key])
                        elif (valid_values[key] in (float,int)) or\
                                (isinstance(valid_values[key], list) and valid_values[key][0] in (float,int)):
                            parameter_list.append(trace + '.' + key)
                        else:  # once down to the form {key: value}
                            # in all other cases ignore parameter
                            print('ignoring sweep parameter', key)


                    return parameter_list

                for script_name in scripts.keys():
                    from PyLabControl.src.core import ScriptIterator
                    script_trace = trace
                    if script_trace == '':
                        script_trace = script_name
                    else:
                        script_trace = script_trace + '->' + script_name
                    if issubclass(scripts[script_name], ScriptIterator):  # gets subscripts of ScriptIterator objects
                        populate_sweep_param(vars(scripts[script_name])['_SCRIPTS'], parameter_list=parameter_list,trace=script_trace)
                    else:
                        # use inspect instead of vars to get _DEFAULT_SETTINGS also for classes that inherit _DEFAULT_SETTINGS from a superclass
                        for setting in [elem[1] for elem in inspect.getmembers(scripts[script_name]) if elem[0] == '_DEFAULT_SETTINGS'][0]:
                            parameter_list = get_parameter_from_dict(script_trace, setting, parameter_list)

                return parameter_list

            sub_scripts = {}  # dictonary of script classes that are to be subscripts of the dynamic class. Should be in the dictionary form {'class_name': <class_object>} (btw. class_object is not the instance)
            script_order = []  # A list of parameters giving the order that the scripts in the ScriptIterator should be executed. Must be in the form {'script_name': int}. Scripts are executed from lowest number to highest
            script_execution_freq = [] # A list of parameters giving the frequency with which each script should be executed
            _, script_class_name, script_settings, _, script_sub_scripts, _ = Script.get_script_information(script_information)

            iterator_type = ScriptIterator.get_iterator_type(script_settings, script_sub_scripts)

            if isinstance(script_information, dict):

                for sub_script_name, sub_script_class in script_sub_scripts.iteritems():
                    if isinstance(sub_script_class, Script):
                        print('JG: script name ', Script.name)
                        # script already exists
                        raise NotImplementedError
                    elif script_sub_scripts[sub_script_name]['class'] == 'ScriptIterator':
                        subscript_class_name = ScriptIterator.create_dynamic_script_class(script_sub_scripts[sub_script_name])['class']
                        # import PyLabControl.src.scripts
                        import PyLabControl.src.core.script_iterator
                        sub_scripts.update({sub_script_name: getattr(PyLabControl.src.core.script_iterator, subscript_class_name)})
                    else:
                        # script_dict = {script_sub_scripts[sub_script_name]['class']}
                        module, _, _, _, _, _ = Script.get_script_information(script_sub_scripts[sub_script_name])
                        sub_scripts.update({sub_script_name: getattr(module, script_sub_scripts[sub_script_name]['class'])})

                # for point iteration we add some default scripts
                if iterator_type == ScriptIterator.TYPE_ITER_NVS:

                    module, _, _, _, _, _ = Script.get_script_information('SelectPoints')
                    sub_scripts.update(
                        {'select_points': getattr(module, 'SelectPoints')}
                    )
                    module, _, _, _, _, _ = Script.get_script_information('FindNV')
                    sub_scripts.update(
                  #      {'find_nv': getattr(module, 'FindNV_cDAQ')}
                        {'find_nv': getattr(module, 'FindNV')}
                    )
                    module, _, _, _, _, _ = Script.get_script_information('Take_And_Correlate_Images')
                    sub_scripts.update(
                        {'correlate_iter': getattr(module, 'Take_And_Correlate_Images')}
                    )
                    script_settings['script_order'].update(
                        {'select_points': -3, 'correlate_iter': -2, 'find_nv': -1}
                    )
                elif iterator_type == ScriptIterator.TYPE_ITER_POINTS:
                    module, _, _, _, _, _ = Script.get_script_information('SelectPoints')
                    sub_scripts.update(
                        {'select_points': getattr(module, 'SelectPoints')}
                    )
                    module, _, _, _, _, _ = Script.get_script_information('SetLaser')
                    sub_scripts.update(
                        {'set_laser': getattr(module, 'SetLaser')}
                    )
                    module, _, _, _, _, _ = Script.get_script_information('Take_And_Correlate_Images')
                    sub_scripts.update(
                        {'correlate_iter': getattr(module, 'Take_And_Correlate_Images')}
                    )
                    script_settings['script_order'].update(
                        {'select_points': -3, 'correlate_iter': -2, 'set_laser': -1}
                    )
            elif isinstance(script_information, Script):
                # if the script already exists, just update the script order parameter
                sub_scripts.update({script_class_name: script_information})

            else:
                raise TypeError('create_dynamic_script_class: unknown type of script_information')

            # update the script order
            for sub_script_name in script_settings['script_order'].keys():
                script_order.append(Parameter(sub_script_name, script_settings['script_order'][sub_script_name], int,
                                              'Order in queue for this script'))
                if sub_script_name == 'select_points':
                    script_execution_freq.append(Parameter(sub_script_name, 0, int,
                                              'How often the script gets executed ex. 1 is every loop, 3 is every third loop, 0 is never'))
                else:
                    script_execution_freq.append(Parameter(sub_script_name, 1, int,
                                                           'How often the script gets executed ex. 1 is every loop, 3 is every third loop, 0 is never'))

            # assigning the actual script settings depending on the interator type
            if iterator_type == ScriptIterator.TYPE_SWEEP_PARAMETER:
                sweep_params = populate_sweep_param(sub_scripts, [])

                script_default_settings = [
                    Parameter('script_order', script_order),
                    Parameter('script_execution_freq', script_execution_freq),
                    Parameter('sweep_param', sweep_params[0], sweep_params, 'variable over which to sweep'),
                    Parameter('sweep_range',
                              [Parameter('min_value', 0, float, 'min parameter value'),
                               Parameter('max_value', 0, float, 'max parameter value'),
                               Parameter('N/value_step', 0, float,
                                         'either number of steps or parameter value step, depending on mode')]),
                    Parameter('stepping_mode', 'N', ['N', 'value_step'],
                              'Switch between number of steps and step amount'),
                    Parameter('run_all_first', True, bool, 'Run all scripts with nonzero frequency in first pass')
                ]
            elif iterator_type == ScriptIterator.TYPE_LOOP:
                script_default_settings = [
                    Parameter('script_order', script_order),
                    Parameter('script_execution_freq', script_execution_freq),
                    Parameter('N', 0, int, 'times the subscripts will be executed'),
                    Parameter('run_all_first', True, bool, 'Run all scripts with nonzero frequency in first pass')
                ]
            elif iterator_type in (ScriptIterator.TYPE_ITER_NVS, ScriptIterator.TYPE_ITER_POINTS):
                script_default_settings = [
                    Parameter('script_order', script_order),
                    Parameter('script_execution_freq', script_execution_freq),
                    Parameter('run_all_first', True, bool, 'Run all scripts with nonzero frequency in first pass')
                ]
            else:
                raise TypeError('unknown iterator type')

            return script_default_settings, sub_scripts

        def create_script_iterator_class(sub_scripts, script_settings):
            '''
            A 'factory' to create a ScriptIterator class at runtime with the given inputs.

            Args:
                sub_scripts: dictonary of script classes that are to be subscripts of the dynamic class. Should be in the dictionary
                         form {'class_name': <class_object>} (btw. class_object is not the instance)
                script_default_settings: the default settings of the dynamically created object. Should be a list of Parameter objects.

            Returns: A newly created class inheriting from ScriptIterator, with the given subscripts and default settings

            '''
            from PyLabControl.src.core import ScriptIterator

            class_name = 'class' + str(ScriptIterator._number_of_classes)

            dynamic_class = type(class_name, (ScriptIterator,),{'_SCRIPTS': sub_scripts, '_DEFAULT_SETTINGS': script_settings, '_INSTRUMENTS': {}})
            # Now we place the dynamic script into the scope of src.scripts as regular scripts.
            # This is equivalent to importing the module in src.scripts.__init__, but because the class doesn't exist until runtime it must be done here.
            # old ===== start
            # import PyLabControl.src.scripts
            # setattr(PyLabControl.src.scripts, class_name, dynamic_class)
            # old ===== end
            import PyLabControl.src.core.script_iterator
            setattr(PyLabControl.src.core.script_iterator, class_name, dynamic_class)

            ScriptIterator._class_list.append(dynamic_class)
            ScriptIterator._number_of_classes += 1

            return class_name, dynamic_class

            # todo: prevent multiple importation of the same script with different names
            # for someclass in cls._class_list:
            #     if (vars(ss)['_SCRIPTS'] == vars(someclass)['_SCRIPTS']):
            #         print('CLASSNAME', vars(someclass)['_CLASS'])
            #         return vars(someclass)['_CLASS']

        script_default_settings, sub_scripts = set_up_dynamic_script(script_information)
        class_name, dynamic_class = create_script_iterator_class(sub_scripts, script_default_settings)

        # update the generic name (e.g. ScriptIterator) to a unique name  (e.g. ScriptIterator_01)
        script_information['class'] = class_name

        if 'iterator_type' in script_information['settings']:
            # if script_information['settings'] contains only the iterator type
            # update the script settings
            #       from  {'script_order': DICT_WITH_SUBSCRIPT_ORDER, 'iterator_type': ITERATOR_TYPE}
            #       to {'script_order': DICT_WITH_SUBSCRIPT_ORDER, 'param1': ACTUAL PARAMETER 1, , 'param2': ACTUAL PARAMETER 2, ..}
            script_settings = {}
            for elem in script_default_settings:
                script_settings.update(elem)
            script_information['settings'] = script_settings
        return script_information

if __name__ == '__main__':
    pass

    #TODO: update example code
    #OLD SAMPLE CODE WITH OUTDATED API
    # from src.scripts import ScriptMinimalDummy
    #
    # import src.scripts
    # smc = ScriptMinimalDummy()
    # scripts = {'ScriptMinimalDummy': ScriptMinimalDummy}
    # settings = [Parameter('repetitions', 0, int, 'times the subscript will be executed')]
    # script_loop = ScriptIterator.script_sequence_factory('loop', scripts, settings)
    # ScriptIterator.import_dynamic_script(src.scripts, 'loop', script_loop)
    # # a = script_loop({'SMC': smc})
    # # a._function()
    #
    # script, failed, instr = Script.load_and_append({'loop':
    #                                                     {'class': 'loop',
    #                                                      'settings': {'repetitions': 1},
    #                                                      'scripts': {'ScriptMinimalDummy': {'class': 'ScriptMinimalDummy', 'settings': {'parameter': 3}}}
    #                                                      }
    #                                                 }
    #                                                )
    # print(script['loop'].settings)
    # print(script)
    # print(failed)
    # print(instr)
