import time
import numpy as np



class Script(object):
    def __init__(self, name = None):
        if name is None:
            name = self.__class__.__name__
        self.name = name
    def __str__(self):
        pass
        #todo: implement
        # def parameter_to_string(parameter):
        #     # print('parameter', parameter)
        #     return_string = ''
        #     # if value is a list of parameters
        #     if isinstance(parameter.value, list) and isinstance(parameter.value[0],Parameter):
        #         return_string += '{:s}\n'.format(parameter.name)
        #         for element in parameter.value:
        #             return_string += parameter_to_string(element)
        #     elif isinstance(parameter, Parameter):
        #         return_string += '\t{:s}:\t {:s}\n'.format(parameter.name, str(parameter.value))
        #
        #     return return_string
        #
        # output_string = '{:s} (class type: {:s})\n'.format(self.name, self.__class__.__name__)
        #
        # for parameter in self.parameter_list:
        #     # output_string += parameter_to_string(parameter)
        #     output_string += str(parameter)+'\n'
        #
        # return output_string
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self._name = value
        else:
            raise TypeError('Name has to be a string')

    @property
    def parameters_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''
        parameter_list_default = []
        return parameter_list_default

    @property
    def parameters(self):
        return self._parameter_list


    def update_parameters(self, parameters_new):
        '''
        updates the parameters if they exist
        :param parameters_new:
        :return:
        '''
        for parameter in parameters_new:
            # get index of parameter in default list
            index = [i for i, p in enumerate(self.parameter_list_default) if p == parameter]
            if len(index)>1:
                raise TypeError('Error: Dublicate parameter in default list')
            elif len(index)==1:
                self.parameter_list[index[0]].update(parameter)

    @property
    def dict(self):
        '''
        returns the configuration of the script as a dictionary
        that contains {'parameters': parameters, 'instruments':instruments, 'scripts': scripts}
        :return: nested dictionary with entries name and value
        '''
        # build dictionary

        config = {}
        # todo: implement
        # for p in self._parameter_list:
        #     config.update(p.dict)

        return config

    def run(self):
        pass

    def stop(self):
        pass


class Script_Dummy(object):
    def __init__(self):

        self.signal = None
    def run(self):
        self.running  = True
        while self.running:
            time.sleep(0.1)
            self.signal = np.random.random()
    def stop(self):
        self.running  = False



if __name__ == '__main__':

    inst = fake_inst()
    inst.run()
    for i in range(10):
        print(inst.signal)
    inst.stop()

