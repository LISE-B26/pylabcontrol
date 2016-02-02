#The recipe gives simple implementation of a Discrete Proportional-Integral-Derivative (PID) controller. PID controller gives output value for error between desired reference input and measurement feedback to minimize error value.
#More information: http://en.wikipedia.org/wiki/PID_controller
#
#cnr437@gmail.com
#
#######	Example	#########
#
#p=PID(3.0,0.4,1.2)
#p.setPoint(5.0)
#while True:
#     pid = p.update(measurement_value)
#
#


class PI:
    """
    Discrete PI control
    """
    def __init__(self, set_point = 0, P=2.0, I=0.0, timestep = 1, output_range = {'min': -10000, 'max': 10000}, integrator=0):
        '''
        P = proportional gain
        I = integral gain in Hz
        timestep: time_step in seconds
        '''
        self.Kp=P
        self.Ki=I
        self.u_P = 0
        self.u_I = 0
        self._output_range=output_range
        self.error = 0
        self.set_point = set_point
        self.timestep = timestep

    def update(self,current_value):
        """
        Calculate PI output value for given reference input and feedback
        """

        error_new = self.set_point - current_value
        #proportional action
        self.u_P = self.Kp * error_new * self.timestep

        #integral action
        self.u_I += self.Kp * self.Ki * (error_new+self.error) / 2.0 * self.timestep

        self.error = error_new

        # anti-windup
        if self.u_P + self.u_I > self._output_range['max']:
            self.u_I = self._output_range['max']-self.u_P
        if self.u_P + self.u_I < self._output_range['min']:
            self.u_I = self._output_range['min']-self.u_P

        output = self.u_P + self.u_I

        return output

    @property
    def set_point(self):
        '''
        set or read setpoint
        '''
        return self._set_point
    @set_point.setter
    def set_point(self, value):
        self._set_point = value

    @property
    def Kp(self):
        return self._Kp
    @Kp.setter
    def Kp(self, value):
        self._Kp = value

    @property
    def Ki(self):
        return self._Ki
    @Ki.setter
    def Ki(self, value):
        self._Ki = value

    @property
    def error(self):
        return self._error
    @error.setter
    def error(self, value):
        self._error = value

    @property
    def timestep(self):
        return self._timestep
    @timestep.setter
    def timestep(self, value):
        self._timestep = value