from src.core import Script

class ReadProbes(Script):
    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    # updateProgress = QtCore.Signal(int)

    _DEFAULT_SETTINGS = None

    def __init__(self, probes, instruments, name=None):

        for name, sub_dict in probes.iteritems():
            try:
                assert isinstance(sub_dict, dict)
                assert "probe_name" in sub_dict
                assert "instrument_name" in sub_dict

                probe_name = sub_dict['probe_name']
                instrument_name = sub_dict['instrument_name']

                assert instrument_name in instruments
                assert probe_name in instruments[instrument_name]._probes

                def fun():
                    getattr(instruments[instrument_name], probe_name)

                probe_instances.update({name: fun})



            except:
                # catches when we try to create a script of a class that doesn't exist!
                # pass
                raise
        Script.__init__(self, name, settings)

    probe_instances = {}
    print('instruments', instruments)


    return probe_instances


    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        # some generic function
        import time

        count = self.settings['count']
        name = self.settings['name']
        wait_time = self.settings['wait_time']

        print('I am a test function counting to {:d}...'.format(count))
        for i in range(count):
            time.sleep(wait_time)
            print(i)