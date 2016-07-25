from src.core import Parameter, Script
import src.scripts
import numpy as np
from PyQt4.QtCore import pyqtSlot
import datetime


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

        self.iterator_type = self.get_iterator_type(settings, scripts)
        # self._skip_next = False

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
            elif 'find_nv' in subscripts and 'select_nvs' in subscripts:
                iterator_type = ScriptIterator.TYPE_ITER_NVS
            elif 'select_nvs' in subscripts:
                iterator_type = ScriptIterator.TYPE_ITER_POINTS
            elif 'N' in script_settings:
                iterator_type = ScriptIterator.TYPE_LOOP
            else:
                print(script_settings, subscripts)
                raise TypeError('unknown iterator type')

        return iterator_type


    def _function(self):
        '''
        Runs either a loop or a parameter sweep over the subscripts in the order defined by the setting 'script_order'
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
            param_values = get_sweep_parameters()
            for value in param_values:

                split_trace = self.settings['sweep_param'].split('.')
                script = split_trace[0]
                setting = split_trace[1:]

                script_settings = self.scripts[script].settings
                curr_type = type(reduce(lambda x,y: x[y], setting, script_settings)) #traverse nested dict to get type of variable
                update_dict = reduce(lambda y, x: {x: y}, reversed(setting), curr_type(value)) #creates nested dictionary from list
                script_settings.update(update_dict)

                self.log('setting parameter {:s} to {:0.2e}'.format(self.settings['sweep_param'], value))
                for script_name in sorted_script_names:
                    if self._abort:
                        break
                    self.log('starting {:s}'.format(script_name))
                    self.scripts[script_name].run()

        elif self.iterator_type == self.TYPE_LOOP:
            for i in range(0, self.settings['N']):
                for script_name in sorted_script_names:
                    if self._abort:
                        break
                    self.log('starting {:s} {:03d}/{:03d}'.format(script_name, i + 1, self.settings['N']))
                    self.scripts[script_name].run()
        elif self.iterator_type in (self.TYPE_ITER_NVS, self.TYPE_ITER_POINTS):

            if self.iterator_type == self.TYPE_ITER_NVS:
                set_point = self.scripts['find_nv'].settings['initial_point']
            elif self.iterator_type == self.TYPE_ITER_POINTS:
                set_point = self.scripts['set_laser'].settings['point']

            points = self.scripts['select_nvs'].data['nv_locations']

            for pt in points:
                set_point.update({'x': pt[0], 'y': pt[1]})
                self.log('find NV near x = {:0.3e}, y = {:0.3e}'.format(pt[0], pt[1]))
                # scip first script since that is the select NV script!
                for script_name in sorted_script_names[1:]:
                    if self._abort:
                        break
                    self.log('starting {:s}'.format(script_name))
                    self.scripts[script_name].run()
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
            if sweep_range['N/value_step'] == 'value_step':
                number_of_iterations = len(np.linspace(sweep_range['min_value'], sweep_range['max_value'],
                                                       (sweep_range['max_value'] - sweep_range['min_value']) /
                                                       sweep_range['N/value_step'] + 1, endpoint=True).tolist())
            else:
                number_of_iterations = sweep_range['N/value_step']
        elif self.iterator_type == self.TYPE_ITER_NVS:
            # todo: implement this for iteration over points,should be something like the following:
            number_of_iterations = len(self.scripts['select_nvs'].data['nv_locations'])
            number_of_iterations = 1
            number_of_subscripts -= 1  # substract 2 because we don't iterate over select nv
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

            current_subscript_elapsed_time = (datetime.datetime.now() - current_subscript.start_time).total_seconds()

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
        if self._current_subscript_stage['current_subscript'] is not None:
            self._current_subscript_stage['current_subscript'].plot(figure_list)

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

                def get_parameter_from_dict(trace, dic, parameter_list):
                    """
                    appends keys in the dict to a list in the form trace.key.subkey.subsubkey...
                    Args:
                        trace: initial prefix (path through scripts and parameters to current location)
                        dic: dictionary
                        parameter_list: list to which append the parameters

                    Returns:

                    """
                    for key, value in dic.iteritems():
                        if isinstance(value, dict):  # for nested parameters ex {point: {'x': int, 'y': int}}
                            parameter_list = get_parameter_from_dict(trace + '.' + key, value, parameter_list)
                        else:  # once down to the form {key: value}
                            parameter_list.append(trace + '.' + key)
                    return parameter_list

                for script_name in scripts.keys():
                    from src.core import ScriptIterator
                    if trace == '':
                        trace = script_name
                    else:
                        trace = trace + '.' + script_name
                    if issubclass(scripts[script_name], ScriptIterator):  # gets subscripts of ScriptIterator objects
                        populate_sweep_param(vars(scripts[script_name])['_SCRIPTS'], parameter_list=parameter_list,
                                             trace=trace)
                    else:
                        for setting in vars(scripts[script_name])['_DEFAULT_SETTINGS']:
                            parameter_list = get_parameter_from_dict(trace, setting, parameter_list)

                return parameter_list

            sub_scripts = {}  # dictonary of script classes that are to be subscripts of the dynamic class. Should be in the dictionary form {'class_name': <class_object>} (btw. class_object is not the instance)
            script_order = []  # A list of parameters giving the order that the scripts in the ScriptIterator should beexecuted. Must be in the form {'script_name': int}. Scripts are executed from lowest number to highest
            _, script_class_name, script_settings, _, script_sub_scripts = Script.get_script_information(
                script_information)

            iterator_type = ScriptIterator.get_iterator_type(script_settings, script_sub_scripts)

            if isinstance(script_information, dict):
                import src.scripts

                for sub_script in script_sub_scripts:
                    if script_sub_scripts[sub_script]['class'] == 'ScriptIterator':
                        subscript_class_name = \
                        ScriptIterator.create_dynamic_script_class(script_sub_scripts[sub_script])['class']
                        sub_scripts.update({sub_script: eval('src.scripts.' + subscript_class_name)})
                    else:
                        sub_scripts.update(
                            {sub_script: eval('src.scripts.' + script_sub_scripts[sub_script]['class'])})

                # for point iteration we add some default scripts
                if iterator_type == ScriptIterator.TYPE_ITER_NVS:
                    sub_scripts.update(
                        {'select_nvs': eval('src.scripts.Select_NVs'), 'find_nv': eval('src.scripts.FindMaxCounts2D')}
                    )
                    script_settings['script_order'].update(
                        {'select_nvs': -2, 'find_nv': -1}
                    )
                elif iterator_type == ScriptIterator.TYPE_ITER_POINTS:
                    sub_scripts.update(
                        {'select_nvs': eval('src.scripts.Select_NVs'), 'set_laser': eval('src.scripts.SetLaser')}
                    )
                    script_settings['script_order'].update(
                        {'select_nvs': -2, 'set_laser': -1}
                    )
            elif isinstance(script_information, Script):
                # if the script already exists, just update the script order parameter
                sub_scripts.update({script_class_name: script_information})

            else:
                raise TypeError('create_dynamic_script_class: unknown type of script_information')

            # update the script order
            for sub_script in script_settings['script_order'].keys():
                script_order.append(Parameter(sub_script, script_settings['script_order'][sub_script], int,
                                              'Order in queue for this script'))

            # assigning the actual script settings depending on the interator type
            if iterator_type == ScriptIterator.TYPE_SWEEP_PARAMETER:
                sweep_params = populate_sweep_param(sub_scripts, [])
                script_default_settings = [
                    Parameter('script_order', script_order),
                    Parameter('sweep_param', sweep_params[0], sweep_params, 'variable over which to sweep'),
                    Parameter('sweep_range',
                              [Parameter('min_value', 0, float, 'min parameter value'),
                               Parameter('max_value', 0, float, 'max parameter value'),
                               Parameter('N/value_step', 0, float,
                                         'either number of steps or parameter value step, depending on mode')]),
                    Parameter('stepping_mode', 'N', ['N', 'value_step'],
                              'Switch between number of steps and step amount')
                ]
            elif iterator_type == ScriptIterator.TYPE_LOOP:
                script_default_settings = [
                    Parameter('script_order', script_order),
                    Parameter('N', 0, int, 'times the subscripts will be executed')
                ]
            elif iterator_type in (ScriptIterator.TYPE_ITER_NVS, ScriptIterator.TYPE_ITER_POINTS):
                script_default_settings = [
                    Parameter('script_order', script_order)
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
            from src.core import ScriptIterator

            class_name = 'class' + str(ScriptIterator._number_of_classes)

            dynamic_class = type(class_name, (ScriptIterator,),
                                 {'_SCRIPTS': sub_scripts, '_DEFAULT_SETTINGS': script_settings, '_INSTRUMENTS': {}})
            # Now we place the dynamic script into the scope of src.scripts as regular scripts.
            # This is equivalent to importing the module in src.scripts.__init__, but because the class doesn't exist until runtime it must be done here.
            import src.scripts
            setattr(src.scripts, class_name, dynamic_class)

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
