from src.core import Instrument, Parameter
import time, datetime
import pandas as pd
import os
class CryoStation(Instrument):

    _DEFAULT_SETTINGS = Parameter(
        Parameter('path', 'C:/Cryostation/Temperature Data/', str, 'path to log file of cryostation'),
    )

    '''
    instrument class to talk to get infos from Montana Cryostation
    Now this doesn't actually communicate with the Cryostation but only reads data from a log-file
    '''
    def __init__(self, name = None, settings = None):

        super(CryoStation, self).__init__(name, settings)
        # apply all settings to instrument
        self.update(self.settings)

        try:
            # create available probes dynamically from headers of logfile
            filepath = "{:s}/MI_DiagnosticsDataLog {:s}.csv".format(self.settings['path'], time.strftime('%m_%d_%Y'))
            data = pd.read_csv(filepath)
            self._dynamic_probes = {
                elem.lstrip().lower().replace(' ', '_').replace('.', '').replace( ')', '').replace( '(', '').replace('/', '-'): elem
                for elem in data.columns}
            self._is_connected = True

        except IOError:
            self._is_connected = False
        except:
            raise

    def update(self, settings):
        '''
        updates the internal dictionary, just call function of super class

        '''
        super(CryoStation, self).update(settings)


    @property
    def is_connected(self):
        '''
        check if instrument is active and connected and return True in that case
        :return: bool
        '''
        return self._is_connected

    @property
    def _PROBES(self):
        '''

        Returns: a dictionary that contains the values that can be read from the instrument
        the key is the name of the value and the value of the dictionary is an info

        '''
        user_specific_probes = {
            'Platform_Temp': 'temperature of platform',
            'Stage_1_Temp': 'temperature of stage 1',
            'Stage_2_Temp': 'temperature of stage 2'
        }

        user_specific_probes.update(self._dynamic_probes)

        return user_specific_probes

    def read_probes(self, key):
        '''

        requests value from the instrument and returns it
        Args:
            key: name of requested value

        Returns: reads values from instrument

        '''
        assert key in self._PROBES.keys(), "key assertion failed {:s}".format(str(key))



        # catch change of date
        time_tag = datetime.datetime.now()
        filepath = "{:s}/MI_DiagnosticsDataLog {:s}.csv".format(self.settings['path'],time_tag.strftime('%m_%d_%Y'))
        while os.path.exists(filepath) == False:
            time_tag -= datetime.timedelta(hours=1)
            filepath = "{:s}/MI_DiagnosticsDataLog {:s}.csv".format(self.settings['path'],time_tag.strftime('%m_%d_%Y'))

        data = pd.read_csv(filepath)

        # create dictionary with last row as values
        data = dict(data.iloc[-1])

        # since we striped some characters when defining the probes we have to find the right key,
        # which is give by the valeu in self._dynamic_probes
        key = self._dynamic_probes[key]

        return data[key]
