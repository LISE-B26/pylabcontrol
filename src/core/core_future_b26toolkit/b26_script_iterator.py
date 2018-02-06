from PyLabControl.src.core import ScriptIterator




class ScriptIteratorB26(ScriptIterator):

    def __init__(self, scripts, name=None, settings=None, log_function=None, data_path=None):
        super(ScriptIteratorB26, self).__init__(scripts=scripts, name=name, settings=settings, log_function=log_function, data_path=data_path)


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
            if script_settings['iterator_type'] == 'Iter NVs':
                iterator_type = ScriptIterator.TYPE_ITER_NVS
            elif script_settings['iterator_type'] == 'Iter Points':
                iterator_type = ScriptIterator.TYPE_ITER_POINTS
            else:
                ScriptIterator.get_iterator_type(script_settings, subscripts)
        else:
            # asign the correct iterator script type
            if 'find_nv' in subscripts and 'select_points' in subscripts:
                iterator_type = ScriptIterator.TYPE_ITER_NVS
            elif 'set_laser' in subscripts and 'select_points' in subscripts:
                iterator_type = ScriptIterator.TYPE_ITER_POINTS
            else:
                ScriptIterator.get_iterator_type(script_settings, subscripts)

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


        if self.iterator_type in (self.TYPE_ITER_NVS, self.TYPE_ITER_POINTS):

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
            super(ScriptIteratorB26, self).function()



    def to_dict(self):
        """
        Returns: itself as a dictionary
        """
        dictator = super(ScriptIteratorB26, self).to_dict()
        # the dynamically created ScriptIterator classes have a generic name
        # replace this with ScriptIterator to indicate that this class is of type ScriptIteratorB26
        dictator[self.name]['class'] = 'ScriptIteratorB26'

        return dictator


