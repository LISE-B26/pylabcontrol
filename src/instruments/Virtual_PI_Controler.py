	#########
#
#p=PID(3.0,0.4,1.2)
#p.setPoint(5.0)
#while True:
#     pid = p.update(measurement_value)
#
#
from src.core import Instrument,Parameter

class PIControler(Instrument):
    """
    Discrete PI control
    """
    _DEFAULT_SETTINGS = Parameter([
        Parameter('set_point', 0.0, float, 'setpoint to which to stabilize'),
        Parameter('gains',[
            Parameter('proportional', 0.0, float, 'proportional gain'),
            Parameter('integral', 0.0, float, 'integral gain')
        ]),
        Parameter('time_step', 1.0, float, 'time_step of loop'),
        Parameter('output_range', [
            Parameter('min', -10000, float, 'min allowed value for PI-loop output'),
            Parameter('max', 10000, float, 'max allowed value for PI-loop output')
        ]),
    ])
    _PROBES = {}
    def __init__(self, name = None, settings = None):
        super(PIControler, self).__init__(name, settings)
        self.reset()
    def update(self, settings):
        super(PIControler, self).update(settings)

    def read_probes(self, key = None):

        if key is None:
            super(PIControler, self).read_probes()
        else:
            assert key in self._PROBES.keys(), "key assertion failed %s" % str(key)

        return None

    def reset(self):
        self.u_P = 0
        self.u_I = 0
        self.error = 0

    def output(self,current_value):
        """
        Calculate PI output value for given reference input and feedback
        """

        set_point = self.settings['set_point']
        Kp = self.settings['gains']['proportional']
        Ki = self.settings['gains']['integral']
        output_range = self.settings['output_range']
        time_step = self.settings['time_step']

        error_new = set_point - current_value
        #proportional action
        self.u_P = Kp * error_new * time_step

        #integral action
        self.u_I += Kp * Ki * (error_new + self.error) / 2.0 * time_step

        self.error = error_new

        # anti-windup
        if self.u_P + self.u_I > self._output_range['max']:
            self.u_I = self._output_range['max']-self.u_P
        if self.u_P + self.u_I < self._output_range['min']:
            self.u_I = self._output_range['min']-self.u_P

        output = self.u_P + self.u_I

        return output



if __name__ == '__main__':
    pi = PIControler()
