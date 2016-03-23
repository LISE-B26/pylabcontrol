from src.core.scripts import Script

from PyQt4 import QtCore


class ZI_Sweeper(QtCore.QThread, Script):
    updateProgress = QtCore.pyqtSignal(int)

    def __init__(self, zihf2, name = None, settings = None):
        '''

        :param zihf2: ZIHF2 instrument object
        :param name:
        :param parameter_list:
        :return:
        '''
        self.zihf2 = zihf2
        self._recording = False

        QtCore.QThread.__init__(self)
        super(ZI_Sweeper, self).__init__(name, settings)

        self.update_parameters(self.parameters_default)


    # @property
    def _settings_default(self):
        """

        Returns:  the default setting of the script

        """
        settings_default = Parameter([
            Parameter('start', 1.8e6, float, 'start value of sweep'),
            Parameter('stop', 1.9e6, float, 'end value of sweep'),
            Parameter('samplecount', 101, int, 'number of data points'),
            Parameter('gridnode', 'oscs/0/freq', ['oscs/0/freq', 'oscs/1/freq'], 'start value of sweep'),
            Parameter('xmapping', 0, [0, 1], 'mapping 0 = linear, 1 = logarithmic'),
            Parameter('bandwidthcontrol', 2, [2], '2 = automatic bandwidth control'),
            Parameter('scan', 0, [0, 1, 2], 'scan direction 0 = sequential, 1 = binary (non-sequential, each point once), 2 = bidirecctional (forward then reverse)'),
            Parameter('loopcount', 1, int, 'number of times it sweeps'),
            Parameter('averaging/sample', 1, int, 'number of samples to average over')

        ])
        return settings_default

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        # some generic function
        import time
        print('I am a test function counting to 3...')
        for i in range(3):
            time.sleep(0.1)
            print(i)