from src.core import Parameter, Script
import src.scripts
import numpy as np
from PyQt4.QtCore import pyqtSlot

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
    TYPE_ITER_POINTS = 2

    def __init__(self, scripts, name = None, settings = None, log_function = None, data_path = None):
        """
        Default script initialization
        """

        Script.__init__(self, name, scripts = scripts, settings = settings, log_function= log_function, data_path = data_path)

        self.iterator_type = self.get_iterator_type(settings, scripts)
        # # asign the correct iterator script type
        # if 'sweep_param' in self.settings:
        #     self.iterator_type = self.TYPE_SWEEP_PARAMETER
        # elif 'find_nv_points' in self.scripts:
        #     self.iterator_type = self.TYPE_ITER_POINTS
        # else:
        #     self.iterator_type = self.TYPE_LOOP

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
            elif script_settings['iterator_type'] == 'Iter Points':
                iterator_type = ScriptIterator.TYPE_ITER_POINTS
            else:
                raise TypeError('unknown iterator type')
        else:
            # asign the correct iterator script type
            if 'sweep_param' in script_settings:
                iterator_type = ScriptIterator.TYPE_SWEEP_PARAMETER
            elif 'find_nv_points' in subscripts:
                iterator_type = ScriptIterator.TYPE_ITER_POINTS
            elif 'N' in script_settings:
                iterator_type = ScriptIterator.TYPE_LOOP
            else:
                raise TypeError('unknown iterator type')

        return iterator_type


    def _function(self):
        '''
        Runs either a loop or a parameter sweep over the subscripts in the order defined by the setting 'script_order'
        '''
        def get_sweep_parameters():
            #in both cases, param values have tolist to make sure that they are python types (ex float) rather than numpy
            #types (ex np.float64), the latter of which can cause typing issues
            if self.settings['stepping_mode'] == 'N':
                param_values = np.linspace(self.settings['min_value'], self.settings['max_value'], int(self.settings['N/value_step']), endpoint=True).tolist()
            elif self.settings['stepping_mode'] == 'value_step':
                param_values = np.linspace(self.settings['min_value'], self.settings['max_value'], (self.settings['max_value'] - self.settings['min_value'])/self.settings['N/value_step'] + 1, endpoint=True).tolist()
            return param_values

        script_names = self.settings['script_order'].keys()
        script_indices = [self.settings['script_order'][name] for name in script_names]
        _, sorted_script_names = zip(*sorted(zip(script_indices, script_names)))

        if self.iterator_type == self.TYPE_SWEEP_PARAMETER:
            param_values = get_sweep_parameters()
            for value in param_values:
                if self.settings['sweep_param'] == '':
                    self.log('Choose a sweep parameter!')
                    return
                split_trace = self.settings['sweep_param'].split('.')
                script = split_trace[0]
                setting = split_trace[1:]

                script_settings = self.scripts[script].settings
                curr_type = type(reduce(lambda x,y: x[y], setting, script_settings)) #traverse nested dict to get type of variable
                update_dict = reduce(lambda y, x: {x: y}, reversed(setting), curr_type(value)) #creates nested dictionary from list
                script_settings.update(update_dict)
                for script_name in sorted_script_names:
                    self.scripts[script_name].run()
        elif self.iterator_type == self.TYPE_LOOP:
            for i in range(0, self.settings['N']):
                for script_name in sorted_script_names:
                    self.scripts[script_name].run()
        elif self.iterator_type == self.TYPE_ITER_POINTS:
            raise NotImplementedError
        else:
            raise TypeError('wrong iterator type')

    @pyqtSlot(int)
    def _receive_signal(self, progress):
        """
        this function takes care of signals emitted by the subscripts
        Args:
            progress: progress of subscript
        """

        # ==== get the current subscript and the time it takes to execute it =====
        current_subscript = self._current_subscript_stage['current_subscript']

        # ==== get typical duration of current subscript ======================
        if current_subscript is not None:
            current_subscript_exec_duration = self._current_subscript_stage['subscript_exec_duration'][
                current_subscript.name]
        else:
            current_subscript_exec_duration = 0  # typical duration of subscript

        # ==== get number of iterations and loop index ======================

        if self.iterator_type == self.TYPE_LOOP:
            number_of_iterations = self.settings['N']
        elif self.iterator_type == self.TYPE_SWEEP_PARAMETER:
            if self.settings['N/value_step'] == 'value_step':
                number_of_iterations = len(np.linspace(self.settings['min_value'], self.settings['max_value'],
                                                       (self.settings['max_value'] - self.settings['min_value']) /
                                                       self.settings['N/value_step'] + 1, endpoint=True).tolist())
            else:
                number_of_iterations = self.settings['N/value_step']
        elif self.iterator_type == self.TYPE_ITER_POINT:
            raise NotImplementedError

            number_of_iterations = len(self.scripts.data['points'])

        # get number of completed loops
        loop_index = self.loop_index

        # time for a single loop execution
        loop_execution_time = 0
        # progress of current loop iteration
        sub_progress = 0
        for subscript_name, duration in self._current_subscript_stage['subscript_exec_duration'].iteritems():
            loop_execution_time += duration
            if self._current_subscript_stage['subscript_exec_count'][subscript_name] > loop_index:
                # this subscript has already been executed in this iteration
                sub_progress += duration

        print(
        'current loop index: ', loop_index, 'loop_execution time', loop_execution_time, 'sub_progress', sub_progress)

        self.progress = 50.
        self.updateProgress.emit(int(self.progress))

    @property
    def loop_index(self):
        loop_index = min(self._current_subscript_stage['subscript_exec_count'].values())
        return loop_index

    def plot(self, figure_list):
        '''
        When each subscript is called, uses its standard plotting

        Args:
            figure_list: list of figures passed from the guit

        '''
        #TODO: be smarter about how we plot ScriptIterator
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
            script_order = []  # A dictionary of parameters giving the order that the scripts in the ScriptIterator should beexecuted. Must be in the form {'script_name': int}. Scripts are executed from lowest number to highest
            _, script_class_name, script_settings, _, script_sub_scripts = Script.get_script_information(
                script_information)

            iterator_type = ScriptIterator.get_iterator_type(script_settings)
            if isinstance(script_information, dict):
                for sub_script in script_sub_scripts:
                    import src.scripts
                    if script_sub_scripts[sub_script]['class'] == 'ScriptIterator':
                        subscript_class_name = \
                        ScriptIterator.create_dynamic_script_class(script_sub_scripts[sub_script])['class']
                        sub_scripts.update({sub_script: eval('src.scripts.' + subscript_class_name)})
                    else:
                        sub_scripts.update(
                            {sub_script: eval('src.scripts.' + script_sub_scripts[sub_script]['class'])})
                        # JG: 7/20/16: moved the following lines after if clause
                        # for sub_script in script_settings['script_order'].keys():
                        #     script_order.append(
                        #         Parameter(sub_script, script_settings['script_order'][sub_script], int,
                        #                   'Order in queue for this script'))
            elif isinstance(script_information, Script):
                # if the script already exists, just update the script order parameter
                sub_scripts.update({script_class_name: script_information})

                # JG: 7/20/16: moved the following lines after if clause
                # for sub_script in script_settings['script_order'].keys():
                #     script_order.append(
                #         Parameter(sub_script, script_settings['script_order'][sub_script], int,
                #                   'Order in queue for this script'))
            else:
                raise TypeError('create_dynamic_script_class: unknown type of script_information')

            # update the script order
            for sub_script in script_settings['script_order'].keys():
                script_order.append(Parameter(sub_script, script_settings['script_order'][sub_script], int,
                                              'Order in queue for this script'))

            # assigning the actual script settings depending on the interator type
            if iterator_type == ScriptIterator.TYPE_SWEEP_PARAMETER:
                sweep_params = populate_sweep_param(sub_scripts, [''])
                script_default_settings = [
                    Parameter('script_order', script_order),
                    Parameter('sweep_param', sweep_params[0], sweep_params, 'variable over which to sweep'),
                    Parameter('sweep_specifier',
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
            elif iterator_type == ScriptIterator.TYPE_ITER_POINTS:
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

            # prevent multiple importation of the same script with different names
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
