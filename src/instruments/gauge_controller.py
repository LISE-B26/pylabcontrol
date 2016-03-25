import serial
from src.core import Instrument, Parameter


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
    ETX = chr(3)
    CR = chr(13)
    LF = chr(10)
    ENQ = chr(5)
    ACK = chr(6)
    NAK = chr(21)

    _possible_com_ports = ['COM' + str(i) for i in range(0, 256)]

    _DEFAULT_SETTINGS = Parameter([
            Parameter('port', 'COM5', _possible_com_ports, 'com port to which the gauge controller is connected'),
            Parameter('timeout', 1.0, float, 'amount of time to wait for a response '
                                             'from the gauge controller for each query'),
            Parameter('baudrate', 9600, int, 'baudrate of serial communication with gauge')
        ])

    def __init__(self, name='PressureGauge', settings=None):
        """
        The serial connection should be setup with the following parameters:
        1 start bit, 8 data bits, No parity bit, 1 stop bit, no hardware
        handshake. These are all default for Serial and therefore not input
        below
        """

        super(PressureGauge, self).__init__(name, settings)
        self.serial_connection = serial.Serial(port=self.settings['port'], baudrate=self.settings['baudrate'],
                                               timeout=self.settings['timeout'])

    @property
    def _probes(self):
        """

        Returns: A dictionary of key-value string-string pairs. keys: probe names, values: probe descriptions

        """
        return {
            'pressure': 'numerical pressure read from Pressure Gauge',
            'units': 'Units used by pressure gauge',
            'model': 'Model of the pressure gauge'
        }

    def update(self, settings):
        pass

    def read_probes(self, probe_name):
        """
        Args:
            probe_name: Name of the probe to get the value of from the Pressure Gauge (e.g., 'pressure')

        Returns:
            value of the probe from the Pressure Gauge
        """

        probe_name = probe_name.lower()  # catch stupid errors, making sure the probe is lowercase

        if probe_name == 'pressure':
            return self._get_pressure()
        elif probe_name == 'units':
            return self._get_units()
        elif probe_name == 'model':
            return self._get_model()
        else:
            message = '\'{0}\' not found as a probe in the class. ' \
                      'Expected either \'pressure\', \'units\', or \'model\''.format(probe_name)
            raise AttributeError(message)

    def _check_acknowledgement(self, response):
        """
        _check_acknowledgement raises an error if the response passed in indicates an negatice response from the guage.

        :param response: the string response from the Guage Controller
        """

        if response == self.NAK + self.CR + self.LF:
            message = 'Serial communication returned negative acknowledge (NAK). ' \
                      'Check AGC100 documentation for more details.'
            raise IOError(message)

        elif response != self.ACK + self.CR + self.LF:
            message = 'Serial communication returned unknown response:\n{}' \
                ''.format(repr(response))
            raise AssertionError(message)

    def _get_pressure(self):
        """
        Returns the pressure currently read by the guage controller.

        :return: pressure
        """
        assert self.serial_connection.isOpen()

        self.serial_connection.write('PR1' + self.CR + self.LF)
        acknowledgement = self.serial_connection.readline()
        self._check_acknowledgement(acknowledgement)

        self.serial_connection.write(self.ENQ)
        err_msg_and_pressure = self.serial_connection.readline().rstrip(self.LF).rstrip(self.CR)

        err_msg = err_msg_and_pressure[0]
        pressure = float(err_msg_and_pressure[3:])

        if err_msg != '0':
            message = 'Pressure query resulted in an error: ' + self.MEASUREMENT_STATUS[err_msg]
            raise IOError(message)

        self.serial_connection.write(self.CR + self.LF)
        return pressure

    def _get_model(self):
        """
        Returns the model of the connected gauge controller.
        :return: model name
        """
        assert self.serial_connection.isOpen()

        self.serial_connection.write('TID' + self.CR + self.LF)
        acknowledgement = self.serial_connection.readline(25)
        self._check_acknowledgement(acknowledgement)

        self.serial_connection.write(self.ENQ)
        model = self.serial_connection.readline().rstrip(self.LF).rstrip(self.CR)

        self.serial_connection.write(self.CR + self.LF)

        return model

    def _get_units(self):
        """
        Returns the units that are in use by the guage controller.

        :return: gauge units (either bar, Torr, Pascal, or Micron)
        """
        #assert self.ser.isOpen()

        self.serial_connection.write('UNI' + self.CR + self.LF)
        acknowledgement = self.serial_connection.readline()
        self._check_acknowledgement(acknowledgement)

        self.serial_connection.write(self.ENQ)
        unit = self.MEASUREMENT_UNITS[self.serial_connection.readline().rstrip(self.LF).rstrip(self.CR)]

        self.serial_connection.write(self.CR + self.LF)

        return unit

    def is_connected(self):
        """
        checks if serial connection is still open with instrument.

        :return: boolean connection status
        """
        return self.serial_connection.isOpen()

    def __del__(self):
        """
        Destructor, to close the serial connection when the instance is this class is garbage collected
        """
        self.serial_connection.close()
