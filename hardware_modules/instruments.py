
import numpy as np

class Parameter(object):

    def __init__(self, name, value = None, valid_values = None, info = None):
        '''
        Parameter(name (str), value (anything) )
        Parameter(name (str), value (anything), valid_values (type, tuple of types, list), info (str) )
        Parameter({name : value })


        :param name: name of parameter,
        :param value = None:
        :param valid_values = None: if empty valid_values = type(value) otherwise can be a list of valid values, a type or a tuple of types
        :param info = None: string describing the parameter
        :return:
        '''



        # if input is only a dictionary we take the first key as name and the first value as value
        if isinstance(name, dict) and value is None:
            name, value = name.keys()[0], name[name.keys()[0]]
            # is the value is again a dict, we convert it into a parameter
            if isinstance(value, dict):
                value = Parameter(value)

        if valid_values is None:
            valid_values = type(value)

        if info is None:
            info = 'N/A'

        self._data = {}
        self.name = name
        self.valid_values = valid_values
        self.value = value
        self.info = info

        assert self.isvalid(value), "value is not if valid type"

    def __repr__(self):
        return str(self.dict)

    def dict_to_str(self, dictonary):
        '''
        casts dict into a (nested) string name : value
        :return:
        '''
        # todo: correct indentation
        return_str = ''

        for key, val in dictonary.iteritems():
            if isinstance(val, dict):
                return_str += '{:s}:\n{:s}\n'.format(key, self.dict_to_str(val))
            else:
                return_str += '{:s}:\t {:s}\n'.format(key, str(val))

        return return_str.replace('\n','\n\t')
    @property
    def dict(self):
        def parameter_to_dict(parameter):
            '''
            casts parameter into a (nested) dictonary {name : value}
            :return:
            '''
            return_dict = {}
            # if value is a list of parameters
            if isinstance(parameter.value, list) and isinstance(parameter.value[0],Parameter):
                sub_dict = {}
                for element in parameter.value:
                    sub_dict.update(parameter_to_dict(element))
                return_dict.update({parameter.name : sub_dict})
            elif isinstance(parameter.value, Parameter):
                return_dict.update({parameter.name : parameter_to_dict(parameter.value)})
            elif isinstance(parameter, Parameter):
                return_dict.update({parameter.name : parameter.value})

            return return_dict

        return parameter_to_dict(self)
    @property
    def name(self):
        return self._data['name']

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self._data.update({'name' : value.replace(' ', '_')}) # replace spaces with underscores
        else:
            raise TypeError('Wrong type! \
                             name should be a string')
    @property
    def value(self):
        return self._data['value']

    @value.setter
    def value(self, value):
        if self.isvalid(value):
            self._data.update({'value':value})
        else:
            raise TypeError('Wrong type! \
                             Type should be .. improve msg here')
    @property
    def info(self):
        return self._data['info']
    @info.setter
    def info(self, value):
        if isinstance(value, str):
            self._data.update({'info' : value})
        else:
            raise TypeError('Wrong type! \
                             info should be a string')

    def isvalid(self, value):
        '''
        checks if value is a valid parameter value
        :param value:
        :return: True or False depending if value is valid
        '''
        valid = False
        if isinstance(self._data['valid_values'], list):
            if value in self._data['valid_values']:
                valid = True
        elif isinstance(self._data['valid_values'], tuple):
            if type(value) in self._data['valid_values']:
                valid = True
        elif isinstance(self._data['valid_values'], type):
            if type(value) is self._data['valid_values']:
                valid = True

        return valid

    @property
    def valid_values(self):
        return self._data['valid_values']
    @valid_values.setter
    def valid_values(self, value):
        '''
        check if valid value is a valid input
        :param value:
        :return: True or False
        '''
        valid = False
        if isinstance(value, list):
            valid = True
        elif isinstance(value, tuple):
            valid = True
            for element in value:
                if not isinstance(element, type):
                    valid = False
        elif isinstance(value, type):
            valid = True

        if valid:
            self._data.update({'valid_values':value})


    def __eq__(self, other):
        '''
        checks if two parameters have the same valid_values and name
        :param other:
        :return:
        '''

        is_equal = True
        if self.name != other.name:
            is_equal = False
        if self.valid_values != other.valid_values:
            is_equal = False
        return is_equal

    def update(self, other):
        if not isinstance(other, Parameter):
            other = Parameter(other)

        if self == other:
            self.value = other.value
            self.info = other.info
        else:
            raise TypeError('Parameters are not of the same type! \
                             They should have the same name and same valid values')

class Instrument(object):
    '''
    generic instrument class
    '''
    def __init__(self, name = None, parameter_list = []):


        self._parameters = self.parameters_default
        self.update_parameters(parameter_list)

        if name is None:
            name = self.__class__.__name__

        self.name = name

        # dynamically create attribute based on parameters,
        # i.e if there is a parameter called p it can be accessed via Instrument.p
        for parameter in self.parameters:
            setattr(self, parameter.name, parameter.value)

    def __str__(self):

        def parameter_to_string(parameter):
            return_string = ''
            # if value is a list of parameters
            if isinstance(parameter.value, list) and isinstance(parameter.value[0],Parameter):
                return_string += '{:s}\n'.format(parameter.name)
                for element in parameter.value:
                    return_string += parameter_to_string(element)
            elif isinstance(parameter, Parameter):
                return_string += '\t{:s}:\t {:s}\n'.format(parameter.name, str(parameter.value))

            return return_string

        output_string = '{:s} (class type: {:s})\n'.format(self.name, self.__class__.__name__)

        for parameter in self.parameters:
            # output_string += parameter_to_string(parameter)
            output_string += str(parameter)+'\n'
        return output_string

    @property
    def status(self):
        '''
        check if instrument is active and connected and return True in that case
        :return: bool
        '''
        pass

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        assert isinstance(value, str)
        self._name = value
    @property
    def dict(self):
        '''
        returns the configuration of the instrument as a dictionary
        :return: nested dictionary with entries name and value
        '''
        # build dictionary

        config = {}
        for p in self._parameters:
            config.update(p.dict)

        return config

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
        return self._parameters

    def update_parameters(self, parameters_new):
        '''
        updates the parameters if they exist
        :param parameters_new:
        :return:
        '''

        def check_parameter_list(parameters):
            '''
            check if parameters is a list of parameters or a dictionary
            if it is a dictionary we create a parameter list from it
            '''
            if isinstance(parameters, dict):
                parameters_new = []
                for key, value in parameters.iteritems():
                    parameters_new.append(Parameter(key, value))
            elif isinstance(parameters, list):
                # if listelement is not a  parameter cast it into a parameter
                parameters_new = [p if isinstance(p, Parameter) else Parameter(p) for p in parameters]
            elif isinstance(parameters, Parameter):
                parameters_new = [parameters]
            else:
                raise TypeError('parameters should be a list, dictionary or Parameter! However it is {:s}'.format(str(type(parameters))))

            return parameters_new


        for parameter in check_parameter_list(parameters_new):
            # get index of parameter in default list
            index = [i for i, p in enumerate(self.parameters_default) if p == parameter]
            if len(index)>1:
                raise TypeError('Error: Dublicate parameter in default list')
            elif len(index)==1:
                self.parameters[index[0]].update(parameter)

class Instrument_Dummy(Instrument):
    '''
    dummy instrument class, just to see how the creation of a new instrument works
    '''
    def __init__(self, name = None, parameter_list = []):
        super(Instrument_Dummy, self).__init__(name, parameter_list)
        # self.update_parameters(parameter_list)

    @property
    def parameters_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''
        parameter_list_default = [
            Parameter('parameter1', 0),
            Parameter('parameter2', 2.0),
            Parameter('parameter string', 'a')
        ]
        return parameter_list_default
# =============== MAESTRO ==================================
# ==========================================================

class Maestro_Controller(Instrument):
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

    def __init__(self,name, parameter_list = []):

        super(Maestro_Controller, self).__init__(name)
        self.update_parameters(parameter_list)
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

    @property
    def parameters_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''
        parameter_list_default = [
            Parameter('port', 'COM5', ['COM5', 'COM3'])
        ]
        return parameter_list_default
    def update_parameters(self, parameters_new):
        # call the update_parameter_list to update the parameter list
        super(Maestro_Controller, self).update_parameters(parameters_new)
        # now we actually apply these newsettings to the hardware
        for parameter in parameters_new:
            if parameter.name == 'port':
                self.usb = self.serial.Serial(parameter.value)
    # Cleanup by closing USB serial port
    def __del__(self):
        self.usb.close()

    # Set channels min and max value range.  Use this as a safety to protect
    # from accidentally moving outside known safe parameters. A setting of 0
    # allows unrestricted movement.
    #
    # ***Note that the Maestro itself is configured to limit the range of servo travel
    # which has precedence over these values.  Use the Maestro Control Center to configure
    # ranges that are saved to the controller.  Use setRange for software controllable ranges.
    def setRange(self, chan, min, max):
        self.Mins[chan] = min
        self.Maxs[chan] = max

    # Return Minimum channel range value
    def getMin(self, chan):
        return self.Mins[chan]

    # Return Minimum channel range value
    def getMax(self, chan):
        return self.Maxs[chan]

    # Set channel to a specified target value.  Servo will begin moving based
    # on Speed and Acceleration parameters previously set.
    # Target values will be constrained within Min and Max range, if set.
    # For servos, target represents the pulse width in of quarter-microseconds
    # Servo center is at 1500 microseconds, or 6000 quarter-microseconds
    # Typcially valid servo range is 3000 to 9000 quarter-microseconds
    # If channel is configured for digital output, values < 6000 = Low ouput
    def setTarget(self, chan, target):
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
    def setSpeed(self, chan, speed):
        lsb = speed & 0x7f #7 bits for least significant byte
        msb = (speed >> 7) & 0x7f #shift 7 and take next 7 bits for msb
        # Send Pololu intro, device number, command, channel, speed lsb, speed msb
        cmd = self.PololuCmd + chr(0x07) + chr(chan) + chr(lsb) + chr(msb)
        self.usb.write(cmd)

    # Set acceleration of channel
    # This provide soft starts and finishes when servo moves to target position.
    # Valid values are from 0 to 255. 0=unrestricted, 1 is slowest start.
    # A value of 1 will take the servo about 3s to move between 1ms to 2ms range.
    def setAccel(self, chan, accel):
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
    def getPosition(self, chan):
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
    def goHome(self):
        cmd = self.PololuCmd + chr(0x22)
        self.usb.write(cmd)


class Maestro_BeamBlock(Instrument):
    from time import sleep
    def __init__(self, maestro, name,  parameter_list = []):
        '''
        :param maestro: maestro servo controler to which motor is connected
        :param channel: channel to which motor is connected
        :param position_list: dictonary that contains the target positions, a factor 4 is needed to get the same values as in the maestro control center
        :return:
        '''
        super(Maestro_BeamBlock, self).__init__(name)
        self.update_parameters(parameter_list)

    @property
    def parameters_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''
        parameter_list_default = [
            Parameter('channel', 0, int, 'channel to which motor is connected'),
            Parameter('open', True, bool, 'beam block open or closed'),
            Parameter('settle_time', 0.2, (int, float),'settling time'),
            Parameter('position_open', 4*1900, int,'position corresponding to open'),
            Parameter('position_closed', 4*950, int,'position corresponding to closed')
        ]
        return parameter_list_default

    def update_parameters(self, parameters_new):
        # call the update_parameter_list to update the parameter list
        super(Maestro_BeamBlock, self).update_parameters(parameters_new)
        # now we actually apply these newsettings to the hardware
        for parameter in parameters_new:
            if parameter.name == 'open':
                if parameter.value == True:
                    self.goto(self.position_open)
                else:
                    self.goto(self.position_closed)
    def goto(self, position):
        self.servo.setTarget(self.channel, position)
        self.sleep(self.settle_time)
        self.servo.disable(self.channel)

# =============== ZURCIH INSTRUMENTS =======================
# ==========================================================

class ZIHF2(Instrument):

    try:
        import zhinst.utils as utils
        _status = True
    except ImportError:
        # make a fake ZI instrument
        _status = False
    except:
        raise

    '''
    instrument class to talk to Zurich instrument HF2 lock in ampifier
    '''
    def __init__(self, name = None, parameter_list = []):

        if self._status:
            self.daq = self.utils.autoConnect(8005,1) # connect to ZI, 8005 is the port number
            self.device = self.utils.autoDetect(self.daq)
            self.options = self.daq.getByte('/%s/features/options' % self.device)
        else:
            self.daq = None
            self.device = None
            self.options = None
        super(ZIHF2, self).__init__(name, parameter_list)

    @property
    def parameters_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''
        parameter_list_default = [
            Parameter('freq', 1e6, (int, float), 'frequency of output channel'),
            Parameter('sigins',
                      [
                          Parameter('channel', 0, [0,1], 'signal input channel'),
                          Parameter('imp50', 1, [0,1], '50Ohm impedance on (1) or off (0)'),
                          Parameter('ac', False, bool, 'ac coupling on (1) or off (0)'),
                          Parameter('range', 10, [0.01, 0.1, 1, 10], 'range of signal input'),
                          Parameter('diff',  False, bool, 'differential signal on (1) or off (0)')
                       ]
                      ),
            Parameter('sigouts',
                      [
                          Parameter('channel', 0, [0,1], 'signal output channel'),
                          Parameter('on',  False, bool, 'output on (1) or off (0)'),
                          Parameter('add',  False, bool, 'add aux signal on (1) or off (0)'),
                          Parameter('range', 10, [0.01, 0.1, 1, 10], 'range of signal output')
                       ]
                      ),
            Parameter('demods',
                      [
                          Parameter('channel', 0, [0,1], 'demodulation channel'),
                          Parameter('order', 4, int, 'filter order'),
                          Parameter('rate', 10e3, [10e3], 'rate'),
                          Parameter('harmonic', 1, int, 'harmonic at which to demodulate'),
                          Parameter('phaseshift', 0, (int, float), 'phaseshift of demodulation'),
                          Parameter('oscselect', 0, [0,1], 'oscillator for demodulation'),
                          Parameter('adcselect', 0, int, 'adcselect')
                       ]
                      ),
            Parameter('aux',
                      [
                          Parameter('channel', 0, [0,1], 'auxilary channel'),
                          Parameter('offset', 1, (int, float), 'offset in volts')
                       ]
                      )
        ]

        return parameter_list_default




        return self.harware_detected
    # Poll the value of input 1 for polltime seconds and return the magnitude of the average data. Timeout is in milisecond.
    def poll(self,  pollTime, variable = 'R', timeout = 500):
        '''
        :param variable: string or list of string, which varibale to poll ('R', 'x', 'y')
        :param pollTime:
        :param timeout:
        :return:
        '''

        valid_variables = ['R','X','Y']

        if self.is_connected:
            path = '/%s/demods/%d/sample' % (self.device, self.demod_c)
            self.daq.subscribe(path)
            flat_dictionary_key = True
            data_poll = self.daq.poll(pollTime,timeout,1,flat_dictionary_key)
            data = {}
            for var in ['X','Y']:
                data.update({var: data_poll[path][var.lower()]})
            data.update({'R': np.sqrt(np.square(data['x'])+np.square(data['y']))})

            if isinstance(variable,str):
                variable = [variable]
            return_variable = {k: data[k] for k in variable}
        else:
            return_variable = None

        return return_variable

    def dict_to_settings(self, dictionary):
        '''
        converts dictionary to list of  setting, which can then be passed to the zi controler
        :param dictionary = dictionary that contains the settings
        :return: settings = list of settings, which can then be passed to the zi controler
        '''
        # create list that is passed to the ZI controler


        settings = []



        for key, element in sorted(dictionary.iteritems()):
            if isinstance(element, dict) and key in ['sigins', 'sigouts', 'demods']:
                channel = element['channel']
                for sub_key, val in sorted(element.iteritems()):
                    if not sub_key == 'channel':
                        settings.append(['/%s/%s/%d/%s'%(self.device, key, channel, sub_key), val])
            elif isinstance(element, dict) and key in ['aux']:
                settings.append(['/%s/AUXOUTS/%d/OFFSET'% (self.device, element['channel']), element['offset']])
            elif key in ['freq']:
                settings.append(['/%s/oscs/%d/freq' % (self.device, self.dict['sigouts']['channel']), dictionary['freq']])
                # settings.append(['/%s/oscs/%d/freq' % (self.device, dictionary['sigouts']['channel']), dictionary['freq']])
            elif isinstance(element, dict) == False:
                settings.append([key, element])


        return settings

    def update_parameters(self, parameters_new):
        # call the update_parameter_list to update the parameter list

        super(ZIHF2, self).update_parameters(parameters_new)

        # now we actually apply these newsettings to the hardware

        if isinstance(parameters_new, dict):
            parameters_new = Parameter(parameters_new)
        if isinstance(parameters_new, Parameter):
            parameters_new = [parameters_new]

        dictonary = {}
        for parameter in parameters_new:
            dictonary.update(parameter.dict)

        commands = self.dict_to_settings(dictonary)
        if self.status:
            self.daq.set(commands)


def test_parameter(qweqwerq):

    passed =True

    try:

        p1 = Parameter('param', 0.0)
        p2 = Parameter('param', 0, int, 'test int')
        p3 = Parameter('param', 0.0, (int, float), 'test tupple')
        p4 = Parameter('param', 0.0, [0.0, 0.1], 'test list')
        print('passed single parameter test')

        p_nested = Parameter('param nested', p1, None, 'test list')
        p_nested = Parameter('param nested', p4, [p1,p4], 'test list')
        print('passed nested parameter test')

        p_dict = Parameter({'param dict': 0 })
        print(p_dict)
        print('passed dictionary test')
        p_dict_nested = Parameter({'param dict': {'sub param dict': 1 } })
        print(p_dict_nested.name, p_dict_nested.value, p_dict_nested.info)
        print('passed nested dictionary test')
    except:
        passed =False

    return passed

# import unittest
#
# class TestInstrumentObjects(unittest.TestCase):
#
#     def test_parameter(self):
#         passed =True
#
#         try:
#
#             p1 = Parameter('param', 0.0)
#             p2 = Parameter('param', 0, int, 'test int')
#             p3 = Parameter('param', 0.0, (int, float), 'test tupple')
#             p4 = Parameter('param', 0.0, [0.0, 0.1], 'test list')
#             print('passed single parameter test')
#
#             p_nested = Parameter('param nested', p1, None, 'test list')
#             p_nested = Parameter('param nested', p4, [p1,p4], 'test list')
#             print('passed nested parameter test')
#
#             p_dict = Parameter({'param dict': 0 })
#             print(p_dict)
#             print('passed dictionary test')
#             p_dict_nested = Parameter({'param dict': {'sub param dict': 1 } })
#             print(p_dict_nested.name, p_dict_nested.value, p_dict_nested.info)
#             print('passed nested dictionary test')
#         except:
#             passed =False
#         self.assertTrue(passed)
#
#     def test_intrument_dummy(self):
#
#         passed =True
#         try:
#             inst = Instrument_Dummy('my dummny')
#             print(inst)
#
#             print(inst.parameters)
#
#             p_new = Parameter('parameter 1', 1)
#             inst.update_parameters([p_new])
#
#             inst = Instrument_Dummy('my dummny', [p_new])
#
#             inst = Instrument_Dummy('my dummny', [{'parameter 2': 2.0},{'parameter 1': 2.0}])
#             inst = Instrument_Dummy('my dummny', {'parameter 2': 2.0, 'parameter 1': 2.0})
#         except:
#             passed =False
#
#         self.assertTrue(passed)
#
#     def test_intrument_ZIHF2(self):
#         passed =True
#         try:
#             zi = ZIHF2('my zi instrument')
#             # test updating parameter
#             zi.update_parameters([Parameter('freq', 2e6)])
#
#         except:
#             passed =False
# if __name__ == '__main__':
#     unittest.main()
if __name__ == '__main__':
    # inst = Instrument_Dummy('my dummny', {'parameter1': 1})

    print(Parameter( {'freq':1.0}))

    inst = ZIHF2('my dummny', {'freq':1.0, 'sigins': {'diff': True}})
    if inst.status:
        print("hardware success")
    else:
        print('failed')





    # if inst.status:
    #     print("hardware success")
    # else:
    #     print('failed')


