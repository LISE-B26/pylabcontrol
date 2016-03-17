
import numpy as np
from PyQt4 import QtCore


def get_elemet(name, element_list):
    '''
    get the element with name 'name'
    list should be a list of objects that have a property name, e.g. Instrument, Parameter, Script
    :param name:
    :param element_list:
    :return:
    '''
    assert isinstance(name, str)
    assert isinstance(element_list, list)
    assert [elem.name for elem in element_list] # check that all elements have a property name

    element = [elem for elem in element_list if elem.name == name][0]

    return element

class Parameter(dict):
    def __init__(self, name, value = None, valid_values = None, info = None):
        '''

        Parameter(name, value, valid_values, info)
        Parameter(name, value, valid_values)
        Parameter(name, value)
        Parameter({name: value})

        Future updates:
        Parameter({name1: value1, name2: value2})
        Parameter([p1, p2]), where p1 and p2 are parameter objects

        Args:
            name: name of parameter
            value: value of parameter can be any basic type or a list
            valid_values: defines which values are accepted for value can be a type or a list if not provided => type(value)
            info: description of parameter, if not provided => empty string

        '''
        if info is None:
            info = ''
        assert isinstance(info, str)
        self.__doc__ = info


        if isinstance(name, str):

            if valid_values is None:
                valid_values = type(value)

            assert isinstance(valid_values, (type,list))
            assert self.is_valid(value, valid_values)

            if isinstance(value, list) and isinstance(value[0], Parameter):
                # this should create a Parameter object and not a dict!
                self._valid_values = {name: {k: v for d in value for k, v in d.valid_values.iteritems()}}
                self.update({name: {k: v for d in value for k, v in d.iteritems()}})

            else:
                self._valid_values = {name: valid_values}
                self.update({name: value})

        elif isinstance(name, (list, dict)) and value is None:

            self._valid_values = {}
            if isinstance(name, dict):
                for k, v in name.iteritems():
                    # convert to Parameter if value is a dict
                    if isinstance(v, dict):
                        v = Parameter(v)
                    self._valid_values.update({k: type(v)})
                    self.update({k: v})
            elif isinstance(name, list) and isinstance(name[0], Parameter):
                for p in name:
                    for k, v in p.iteritems():
                        self._valid_values.update({k: p.valid_values[k]})
                        self.update({k: v})
            else:
                raise TypeError('unknown input: ', name)


    def __setitem__(self, key, value):

#         if self.is_valid(value,  self.valid_values[key]) ==False:
#             print(key, '|',value, '|',self.valid_values[key])

        assert self.is_valid(value, self.valid_values[key])
        if isinstance(value, dict) and len(self)>0:
            for k, v in value.iteritems():
                self[key].update({k:v})
        else:
            super(Parameter, self).__setitem__(key, value)

    def update(self, *args):
        for d in args:
            for key, value in d.iteritems():
                self.__setitem__(key, value)

    @property
    def valid_values(self):
        return self._valid_values

    @property
    def info(self):
        return self.__doc__

    @staticmethod
    def is_valid(value, valid_values):
        valid = False

        if isinstance(valid_values, type) and type(value) is valid_values:
            valid = True
        elif isinstance(value, dict) and isinstance(valid_values, dict):
            # check that all values actually exist in valid_values
            # assert value.keys() & valid_values.keys() == value.keys() # python 3 syntax
            assert set(value.keys()) & set(valid_values.keys()) == set(value.keys()) # python 2
            valid = True
            for k ,v in value.items():
                if type(v) is not valid_values[k]:
                    valid = True

#             print('aaaa', value, valid_values)
#         elif isinstance(value, (unicode)):
#             print('unico?de')
        elif isinstance(valid_values, list) and value in valid_values:
            valid = True
        return valid


class Instrument(object):
    '''
    generic instrument class
    '''
    _is_connected = False #internal flag that indicated if instrument is actually connected
    def __init__(self, name = None, parameter_list = []):


        self._parameters = self.parameters_default
        self.update_parameters(parameter_list)

        if name is None:
            name = self.__class__.__name__

        self.name = name

        # dynamically create attribute based on parameters,
        # i.e if there is a parameter called p it can be accessed via Instrument.p
        # try:
        #     for parameter in self.parameters:
        #         setattr(self, parameter.name, parameter.value)
        # except:
        #     pass

        self._is_connected = False

    # do not override this, override get_values instead
    def __getattr__(self, name):
        try:
            return self.get_values(name)
        except KeyError:
            #restores standard behavior for missing keys
            raise AttributeError('class ' + type(self).__name__ +' has no attribute ' + str(name))

    def get_values(self, name):
        return self.as_dict()[str(name)]

    def __setattr__(self, key, value):
        try:
            self.update_parameters(Parameter(key, value))
        except Exception:
            object.__setattr__(self, key, value)

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
    def is_connected(self):
        '''
        check if instrument is active and connected and return True in that case
        :return: bool
        '''
        return self._is_connected

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        assert isinstance(value, str)
        self._name = value

    def as_dict(self):
        '''
        returns the configuration of the instrument as a dictionary
        :return: nested dictionary with entries name and value
        '''
        # build dictionary

        config = {}
        for p in self._parameters:
            config.update(p.as_dict())
        return config

    @property
    def parameters_default(self):
        '''
        returns the default parameter_list of the instrument this function should be over written in any subclass
        :return: a list of parameter objects
        '''
        parameter_list_default = [
            Parameter('test1', 0, int, 'test parameter (int)'),
            Parameter('test2' ,
                      [Parameter('test2_1', 'string', str, 'test parameter (str)'),
                       Parameter('test2_2', 0.0, float, 'test parameter (float)')
                       ])
        ]
        return parameter_list_default

    @property
    def parameters(self):
        return self._parameters

    def update_parameters(self, parameters_new):
        '''
        updates the parameters if they exist
        :param parameters_new: can be a
            - dictionary of type {'param1':value1, 'param2':value2, etc.}
            - list of dictionaries of form [{'param1':value1}, {'param2':value2}, etc.]
            - list of parameters [param1, param2, etc.,  where param1, param2 are Parameter objects
            - a single parameter object
        :returns: a dictionary of the form {'param1':value1, 'param2':value2, etc.} of  parameters_new
        '''

        def convert_to_dict(parameters):
            '''
            :param parameters: can be a
            - dictionary of type {'param1':value1, 'param2':value2, etc.}
            - list of dictionaries of form [{'param1':value1}, {'param2':value2}, etc.]
            - list of parameters [param1, param2, etc.],  where param1, param2 are Parameter objects
            - a single parameter object
            :return a dictionary of type {'param1':value1, 'param2':value2, etc.}
            '''
            if isinstance(parameters, dict):
                parameters_new = parameters
            elif isinstance(parameters, list):
                # if listelement is not a  dict cast it into a dict
                parameters_new = {}
                for p in parameters:
                    if isinstance(p, dict):
                        parameters_new.update(p)
                    elif isinstance(p, Parameter):
                        parameters_new.update({p.name: p.value})
                    else:
                        raise TypeError('list of unknown type {:s}'.format(str(type(p))))
            elif isinstance(parameters, Parameter):
                parameters_new = {parameters.name: parameters.value}
            else:
                raise TypeError('parameters should be a list, dictionary or Parameter! However it is {:s}'.format(str(type(parameters))))
            return parameters_new

        parameters_new = convert_to_dict(parameters_new)

        for key, value in parameters_new.iteritems():
            # get index of parameter in default list
            index = [i for i, p in enumerate(self.parameters_default) if p.name == key]
            if len(index)>1:
                raise TypeError('Error: Dublicate parameter in default list')
            elif len(index) == 1:
                self.parameters[index[0]].value = value
            else:
                raise ValueError('Parameter {:s} not in default parameter list for {:s}!'.format(key, self.name))

        return parameters_new

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

    def __init__(self, name = None, parameters = []):

        super(Maestro_Controller, self).__init__(name, parameters)
        self.update_parameters(self.parameters)
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
            Parameter('port', 'COM5', ['COM5', 'COM3'], 'com port to which maestro controler is connected')
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
    def __init__(self, maestro, name, parameters = []):
        '''
        :param maestro: maestro servo controler to which motor is connected
        :param channel: channel to which motor is connected
        :param position_list: dictonary that contains the target positions, a factor 4 is needed to get the same values as in the maestro control center
        :return:
        '''
        super(Maestro_BeamBlock, self).__init__(name)
        self.update_parameters(parameters)
        self.maestro = maestro

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

        # parameters_new = convert_to_parameter_list(parameters_new)

        def convert_to_parameter_list(parameters):
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


        # now we actually apply these newsettings to the hardware
        for parameter in convert_to_parameter_list(parameters_new):
            if parameter.name == 'open':
                if parameter.value == True:
                    # todo: this work once we have the dynamically get/set functions of the super class
                    # self.goto(self.position_open)
                    # until then:
                    self.goto(get_elemet('position_open',self.parameters).value)
                else:
                    # todo: this work once we have the dynamically get/set functions of the super class
                    # self.goto(self.position_closed)
                    # until then:
                    self.goto(get_elemet('position_closed',self.parameters).value)

    def goto(self, position):
        self.maestro.setTarget(self.channel, position)
        # todo: this work once we have the dynamically get/set functions of the super class
        # self.sleep(self.settle_time)
        # until then:
        self.sleep(get_elemet('settle_time',self.parameters).value)
        self.maestro.disable(self.channel)
    # todo: this should by taken care of in the dynamically get/set functions of the super class
    @property
    def channel(self):
        return get_elemet('channel',self.parameters).value

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
                # channel = element['channel']
                channel = get_elemet('sigouts', self.parameters).as_dict()['sigouts']['channel']
                for sub_key, val in sorted(element.iteritems()):
                    if not sub_key == 'channel':
                        settings.append(['/%s/%s/%d/%s'%(self.device, key, channel, sub_key), val])
            elif isinstance(element, dict) and key in ['aux']:
                channel = get_elemet('aux', self.parameters).as_dict()['aux']['channel']
                settings.append(['/%s/AUXOUTS/%d/OFFSET'% (self.device, channel), element['offset']])
            elif key in ['freq']:
                channel = get_elemet('sigouts', self.parameters).as_dict()['sigouts']['channel']
                settings.append(['/%s/oscs/%d/freq' % (self.device, channel), dictionary['freq']])
                # settings.append(['/%s/oscs/%d/freq' % (self.device, dictionary['sigouts']['channel']), dictionary['freq']])
            elif isinstance(element, dict) == False:
                settings.append([key, element])


        return settings

    def update_parameters(self, parameters_new):
        # call the update_parameter_list to update the parameter list
        parameters_new = super(ZIHF2, self).update_parameters(parameters_new)
        # now we actually apply these newsettings to the hardware

        commands = self.dict_to_settings(parameters_new)
        if self.is_connected:
            self.daq.set(commands)



# class Instrument_Dummy(Instrument):
#     '''
#     dummy instrument class, just to see how the creation of a new instrument works
#     '''
#     def __init__(self, name = None, parameter_list = []):
#         super(Instrument_Dummy, self).__init__(name, parameter_list)
#
#     @property
#     def parameters_default(self):
#         '''
#         returns the default parameter_list of the instrument
#         :return:
#         '''
#         parameter_list_default = [
#             Parameter('parameter1', 0, [0,1]),
#             Parameter('parameter2', 2.0),
#             Parameter('parameter_string', 'a'),
#             Parameter('parameter_string', [
#                 Parameter('parameter_sub1', 'a_1'),
#                 Parameter('parameter_sub2', 'a_1')
#             ])
#         ]
#         return parameter_list_default

if __name__ == '__main__':
    inst = Instrument_Dummy('my dummny')
