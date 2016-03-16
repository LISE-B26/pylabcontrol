import serial
from src.core import Instrument

class PressureGauge(Instrument):
    """
    This class implements the AGC100 pressure gauge.
    """

    # Translations of the controller's status messages
    MEASUREMENT_STATUS = {
        '0': 'Measurement data okay',
        '1': 'Underrange',
        '2': 'Overrange',
        '3': 'Sensor error',
        '4': 'Sensor off',
        '5': 'No sensor',
        '6': 'Identification error',
        '7': 'Error FRG-720, FRG-730'
    }

    # Translation of the controller's units check  messages
    MEASUREMENT_UNITS = {
        '0': 'mbar/bar',
        '1': 'Torr',
        '2': 'Pascal',
        '3': 'Micron'
    }

    # ASCII Characters used for controller communication
    ETX = chr(3)  # \x03
    CR = chr(13)
    LF = chr(10)
    ENQ = chr(5)  # \x05
    ACK = chr(6)  # \x06
    NAK = chr(21)  # \x15

    def __init__(self, name='PressureGauge', parameter_list=[]):
        # The serial connection should be setup with the following parameters:
        # 1 start bit, 8 data bits, No parity bit, 1 stop bit, no hardware
        # handshake. These are all default for Serial and therefore not input
        # below

        super(PressureGauge, self).__init__(name, parameter_list)
        self.ser = serial.Serial(port=self.port, timeout=self.timeout)
        self.probes = ['pressure', 'units']

    @property
    def parameters_default(self):
        """
        returns the default parameter_list of the instrument
        :return:
        """

        parameter_list_default = [
            Parameter('port', 'COM3', ['COM1', 'COM3', 'COM17'], 'com port to which maestro controler is connected'),
            Parameter('timeout', 1, (int, float), 'com port to which maestro controler is connected')
        ]

        return parameter_list_default

    @staticmethod
    def __check_acknowledgement(self, response):
        """
        check_acknowledgement raises an error if the response passed in indicates an negatice response from the guage.

        :param response: the string response from the Guage Controller
        """

        if (response == NAK + CR + LF):
            message = 'Serial communication returned negative acknowledge (NAK). ' \
                      'Check AGC100 documentation for more details.'
            raise IOError(message)

        elif (response != ACK + CR + LF):
            message = 'Serial communication returned unknown response:\n{}' \
                ''.format(repr(response))
            raise IOError(message)

    def get_pressure(self):
        """
        Returns the pressure currently read by the guage controller.

        :return: pressure
        """
        assert self.ser.isOpen()

        self.ser.write('PR1' + CR + LF)
        acknowledgement = self.ser.readline()
        self.__check_acknowledgement(acknowledgement)

        self.ser.write(ENQ)
        err_msg_and_pressure = self.ser.readline().rstrip(LF).rstrip(CR)

        err_msg = err_msg_and_pressure[0]
        pressure = float(err_msg_and_pressure[3:])

        if err_msg != '0':
            message = 'Pressure query resulted in an error: ' + MEASUREMENT_STATUS[err_msg]
            raise IOError(message)

        self.ser.write(CR + LF)
        return pressure

    def get_model(self):
        """
        Returns the model of the connected gauge controller.
        :return: model name
        """
        assert self.ser.isOpen()

        self.ser.write('TID' + CR + LF)
        acknowledgement = self.ser.readline(25)
        self.__check_acknowledgement(acknowledgement)

        self.ser.write(ENQ)
        model = self.ser.readline().rstrip(LF).rstrip(CR)

        self.ser.write(CR + LF)

        return model

    def get_units(self):
        """
        Returns the units that are in use by the guage controller.

        :return: gauge units (either bar, Torr, Pascal, or Micron)
        """
        assert self.ser.isOpen()

        self.ser.write('UNI' + CR + LF)
        acknowledgement = self.ser.readline()
        self.__check_acknowledgement(acknowledgement)

        self.ser.write(ENQ)
        unit = MEASUREMENT_UNITS[self.ser.readline().rstrip(LF).rstrip(CR)]

        self.ser.write(CR + LF)

        return unit

    def is_connected(self):
        """
        checks if serial connection is still open with instrument.

        :return: boolean connection status
        """
        return self.ser.isOpen()

    def __del__ (self):
        """
        Destructor, to close the serial connection when the instance is this class is garbage-collected
        """
        self.ser.close()
