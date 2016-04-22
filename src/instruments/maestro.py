from src.core import Instrument,Parameter
from time import sleep
# =============== MAESTRO ==================================
# ==========================================================

class MaestroController(Instrument):
    # When connected via USB, the Maestro creates two virtual serial ports
    # /dev/ttyACM0 for commands and /dev/ttyACM1 for communications.
    # Be sure the Maestro is configured for "USB Dual Port" serial mode.
    # "USB Chained Mode" may work as well, but hasn't been tested.
    #
    # Pololu protocol allows for multiple Maestros to be connected to a single
    # communication channel. Each connected device is then indexed by number.
    # This device number defaults to 0x0C (or 12 in decimal), which this module
    # assumes.  If two or more controllers are connected to different serial
    # ports, then you can specify the port number when intiating a controller
    # object. Ports will typically start at 0 and count by twos.  So with two
    # controllers ports 0 and 2 would be used.

    import serial

    _DEFAULT_SETTINGS = Parameter([
        Parameter('port', 'COM5', ['COM5', 'COM3'], 'com port to which maestro controler is connected')
    ])

    _PROBES = {}
    def __init__(self, name = None, settings = None):

        self.usb = None
        super(MaestroController, self).__init__(name, settings)
        self.update(self.settings)
        # Open the command port
        # self.usb = self.serial.Serial(port)
        # Command lead-in and device 12 are sent for each Pololu serial commands.
        self.PololuCmd = chr(0xaa) + chr(0xc)
        # Track target position for each servo. The function isMoving() will
        # use the Target vs Current servo position to determine if movement is
        # occuring.  Upto 24 servos on a Maestro, (0-23). Targets start at 0.
        self.Targets = [0] * 24
        # Servo minimum and maximum targets can be restricted to protect components.
        self.Mins = [0] * 24
        self.Maxs = [0] * 24


    def update(self, settings):
        # call the update_parameter_list to update the parameter list
        super(MaestroController, self).update(settings)
        # now we actually apply these newsettings to the hardware
        for key, value in settings.iteritems():
            if key == 'port':
                try:
                    self.usb = self.serial.Serial(value)
                except OSError:
                    print('Couln\'t connect to maestro controler at port {:s}'.format(value))


    def read_probes(self, key):
        '''
        requestes value from the instrument and returns it
        Args:
            key: name of requested value

        Returns: reads values from instrument

        '''
        # todo: replace getter old_functions with this function
        assert key in self._PROBES.keys()

        value = None

        return value

    @property
    def is_connected(self):
        '''
        check if instrument is active and connected and return True in that case
        :return: bool
        '''
        if self.usb is None:
            self._is_connected = False
        else:
            self._is_connected = True

        #todo: implement check


        return self._is_connected

    # Cleanup by closing USB serial port
    def __del__(self):
        if not self.usb == None:
            self.usb.close()

    # Set channels min and max value range.  Use this as a safety to protect
    # from accidentally moving outside known safe parameters. A setting of 0
    # allows unrestricted movement.
    #
    # ***Note that the Maestro itself is configured to limit the range of servo travel
    # which has precedence over these values.  Use the Maestro Control Center to configure
    # ranges that are saved to the controller.  Use setRange for software controllable ranges.
    def set_range(self, chan, min, max):
        self.Mins[chan] = min
        self.Maxs[chan] = max

    # Return Minimum channel range value
    def get_min(self, chan):
        return self.Mins[chan]

    # Return Minimum channel range value
    def get_max(self, chan):
        return self.Maxs[chan]

    # Set channel to a specified target value.  Servo will begin moving based
    # on Speed and Acceleration parameters previously set.
    # Target values will be constrained within Min and Max range, if set.
    # For servos, target represents the pulse width in of quarter-microseconds
    # Servo center is at 1500 microseconds, or 6000 quarter-microseconds
    # Typcially valid servo range is 3000 to 9000 quarter-microseconds
    # If channel is configured for digital output, values < 6000 = Low ouput
    def set_target(self, chan, target):
        # if Min is defined and Target is below, force to Min
        if self.Mins[chan] > 0 and target < self.Mins[chan]:
            target = self.Mins[chan]
        # if Max is defined and Target is above, force to Max
        if self.Maxs[chan] > 0 and target > self.Maxs[chan]:
            target = self.Maxs[chan]
        #
        lsb = target & 0x7f #7 bits for least significant byte
        msb = (target >> 7) & 0x7f #shift 7 and take next 7 bits for msb
        # Send Pololu intro, device number, command, channel, and target lsb/msb
        cmd = self.PololuCmd + chr(0x04) + chr(chan) + chr(lsb) + chr(msb)
        self.usb.write(cmd)
        # Record Target value
        self.Targets[chan] = target


    def disable(self, chan):

        target = 0
        #
        lsb = target & 0x7f #7 bits for least significant byte
        msb = (target >> 7) & 0x7f #shift 7 and take next 7 bits for msb
        # Send Pololu intro, device number, command, channel, and target lsb/msb
        cmd = self.PololuCmd + chr(0x04) + chr(chan) + chr(lsb) + chr(msb)
        self.usb.write(cmd)
        # Record Target value
        self.Targets[chan] = target

    # Set speed of channel
    # Speed is measured as 0.25microseconds/10milliseconds
    # For the standard 1ms pulse width change to move a servo between extremes, a speed
    # of 1 will take 1 minute, and a speed of 60 would take 1 second.
    # Speed of 0 is unrestricted.
    def set_speed(self, chan, speed):
        lsb = speed & 0x7f #7 bits for least significant byte
        msb = (speed >> 7) & 0x7f #shift 7 and take next 7 bits for msb
        # Send Pololu intro, device number, command, channel, speed lsb, speed msb
        cmd = self.PololuCmd + chr(0x07) + chr(chan) + chr(lsb) + chr(msb)
        self.usb.write(cmd)

    # Set acceleration of channel
    # This provide soft starts and finishes when servo moves to target position.
    # Valid values are from 0 to 255. 0=unrestricted, 1 is slowest start.
    # A value of 1 will take the servo about 3s to move between 1ms to 2ms range.
    def set_accel(self, chan, accel):
        lsb = accel & 0x7f #7 bits for least significant byte
        msb = (accel >> 7) & 0x7f #shift 7 and take next 7 bits for msb
        # Send Pololu intro, device number, command, channel, accel lsb, accel msb
        cmd = self.PololuCmd + chr(0x09) + chr(chan) + chr(lsb) + chr(msb)
        self.usb.write(cmd)

    # Get the current position of the device on the specified channel
    # The result is returned in a measure of quarter-microseconds, which mirrors
    # the Target parameter of setTarget.
    # This is not reading the true servo position, but the last target position sent
    # to the servo. If the Speed is set to below the top speed of the servo, then
    # the position result will align well with the acutal servo position, assuming
    # it is not stalled or slowed.
    def get_position(self, chan):
        cmd = self.PololuCmd + chr(0x10) + chr(chan)
        self.usb.write(cmd)
        lsb = ord(self.usb.read())
        msb = ord(self.usb.read())
        return (msb << 8) + lsb

    # # Test to see if a servo has reached its target position.  This only provides
    # # useful results if the Speed parameter is set slower than the maximum speed of
    # # the servo.
    # # ***Note if target position goes outside of Maestro's allowable range for the
    # # channel, then the target can never be reached, so it will appear to allows be
    # # moving to the target.  See setRange comment.
    # def isMoving(self, chan):
    #     if self.Targets[chan] > 0:
    #         if self.getPosition(chan) <> self.Targets[chan]:
    #             return True
    #     return False

    # # Have all servo outputs reached their targets? This is useful only if Speed and/or
    # # Acceleration have been set on one or more of the channels. Returns True or False.
    # def getMovingState(self):
    #     cmd = self.PololuCmd + chr(0x13)
    #     self.usb.write(cmd)
    #     if self.usb.read() == chr(0):
    #         return False
    #     else:
    #         return True

    # # Run a Maestro Script subroutine in the currently active script. Scripts can
    # # have multiple subroutines, which get numbered sequentially from 0 on up. Code your
    # # Maestro subroutine to either infinitely loop, or just end (return is not valid).
    # def runScriptSub(self, subNumber):
    #     cmd = self.PololuCmd + chr(0x27) + chr(subNumber)
    #     # can pass a param with comman 0x28
    #     # cmd = self.PololuCmd + chr(0x28) + chr(subNumber) + chr(lsb) + chr(msb)
    #     self.usb.write(cmd)
    #
    # # Stop the current Maestro Script
    # def stopScript(self):
    #     cmd = self.PololuCmd + chr(0x24)
    #     self.usb.write(cmd)

    # Stop the current Maestro Script
    def go_home(self):
        cmd = self.PololuCmd + chr(0x22)
        self.usb.write(cmd)


class MaestroBeamBlock(Instrument):
    """
MaestroBeamBlock:
-----------------
motorized mount with two positions, generally used for blocking ir unblocking beams, but can also be used as a flip mount
    """

    _DEFAULT_SETTINGS = Parameter([
        Parameter('channel', 0, int, 'channel to which motor is connected'),
        Parameter('open', True, bool, 'beam block open or closed'),
        Parameter('settle_time', 0.2, float, 'settling time'),
        Parameter('position_open', 4 * 1900, int, 'position corresponding to open'),
        Parameter('position_closed', 4 * 950, int, 'position corresponding to closed')
    ])
    _PROBES = {}
    def __init__(self, maestro = None, name = None, settings = None):
        '''
        :param maestro: maestro servo controler to which motor is connected
        :param channel: channel to which motor is connected
        :param position_list: dictonary that contains the target positions, a factor 4 is needed to get the same values as in the maestro control center
        :return:
        '''

        if maestro is None:
            maestro = MaestroController()
        assert isinstance(maestro, MaestroController)
        self.maestro = maestro

        super(MaestroBeamBlock, self).__init__(name, settings)
        self.update(self.settings)

    def update(self, settings):

        # call the update_parameter_list to update the parameter list
        super(MaestroBeamBlock, self).update(settings)

        # now we actually apply these newsettings to the hardware
        for key, value in settings.iteritems():
            if key == 'open':
                if value is True:
                    self.goto(self.settings['position_open'])
                else:
                    self.goto(self.settings['position_closed'])


    def read_probes(self, key):
        '''
        requestes value from the instrument and returns it
        Args:
            key: name of requested value

        Returns: reads values from instrument

        '''
        assert key in self._PROBES.keys()

        value = None

        return value

    @property
    def is_connected(self):
        """
        check if instrument is active and connected and return True in that case
        :return: bool
        """
        return self.maestro._is_connected

    def goto(self, position):
        self.maestro.set_target(self.settings['channel'], position)
        sleep(self.settings['settle_time'])
        self.maestro.disable(self.settings['channel']) # diconnect to avoid piezo from going crazy


class MaestroFilterWheel(Instrument):


    _DEFAULT_SETTINGS = Parameter([
        Parameter('channel', 0, int, 'channel to which motor is connected'),
        Parameter('settle_time', 0.8, float, 'settling time'),
        Parameter('position_1', 4 * 750, int, 'position corresponding to position 1'),
        Parameter('position_2', 4 * 1700, int, 'position corresponding to position 2'),
        Parameter('position_3', 4 * 2700, int, 'position corresponding to position 3'),
        Parameter('current_position', 'position_1', ['position_1', 'position_2', 'position_3'], 'current position of filter wheel')

    ])

    _PROBES = {}
    def __init__(self, maestro = None, name = None, settings = None):
        '''
        :param maestro: maestro servo controler to which motor is connected
        :param channel: channel to which motor is connected
        :param position_list: dictonary that contains the target positions, a factor 4 is needed to get the same values as in the maestro control center
        :return:
        '''


        if maestro is None:
            maestro = MaestroController()
        assert isinstance(maestro, MaestroController)
        self.maestro = maestro

        super(MaestroFilterWheel, self).__init__(name, settings)
        self.update(self.settings)


    def update(self, settings):
        # call the update_parameter_list to update the parameter list
        super(MaestroFilterWheel, self).update(settings)

        # now we actually apply these newsettings to the hardware
        for key, value in settings.iteritems():
            if key == 'current_position':
                self.goto(self.settings[value])



    def read_probes(self, key):
        '''
        requestes value from the instrument and returns it
        Args:
            key: name of requested value

        Returns: reads values from instrument

        '''
        assert key in self._PROBES.keys()

        value = None

        return value


    @property
    def is_connected(self):
        """
        check if instrument is active and connected and return True in that case
        :return: bool
        """
        return self.maestro._is_connected


    def goto(self, position):
        self.maestro.set_target(self.settings['channel'], position)
        sleep(self.settings['settle_time'])
        self.maestro.disable(self.settings['channel'])  # diconnect to avoid piezo from going crazy
