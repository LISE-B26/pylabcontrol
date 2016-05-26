from src.core import Script, Parameter
from src.instruments import MaestroLightControl


class CameraOn(Script):

    _DEFAULT_SETTINGS = Parameter([
        Parameter('On', True, bool, '')
    ])

    _INSTRUMENTS = {
        'light_control' : MaestroLightControl
    }
    _SCRIPTS = {}

    def __init__(self, instruments, name = None, settings = None, log_function = None):
        """
        Example of a script that makes use of an instrument
        Args:
            instruments: instruments the script will make use of
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """

        # call init of superclass
        Script.__init__(self, name, settings, instruments, log_function= log_function)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in _DEFAULT_SETTINGS
        for this dummy example we just implement a counter
        """

        if self.settings['On'] == True:
            # fluorescence filter
            self.instruments['white_light'].update({'open': False})
            self.instruments['filter_wheel'].update({'current_position': 'position_3'})
            self.instruments['block_ir'].update({'open': True})
            self.instruments['block_green'].update({'open': True})

            self.log('camera on')
        else:
            # high ND
            self.instruments['filter_wheel'].update({'current_position': 'position_1'})
            self.instruments['block_ir'].update({'open': False})
            self.instruments['block_green'].update({'open': False})
            self.instruments['white_light'].update({'open': True})



            self.log('camera off')