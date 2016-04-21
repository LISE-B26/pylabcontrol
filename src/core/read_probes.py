# from src.core import Script
from PySide.QtCore import Signal, QThread

class ReadProbes(QThread):
    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    # updateProgress = QtCore.Signal(int)

    _DEFAULT_SETTINGS = None

    updateProgress = Signal(int)

    def __init__(self, probes, refresh_interval = 0.5):
        """
        probes: dictionary of probes where keys are names and values are Probe objects
        refresh_interval: time between reads in s
        """
        assert isinstance(probes, dict)
        assert isinstance(refresh_interval, float)

        self.refresh_interval = refresh_interval
        self._running = False
        self.probes = probes
        self.probes_values = None

        QThread.__init__(self)


    def run(self):
        import time
        self._running = True
        while self._running:

            self.probes_values = {key: probe.value for key, probe in self.probes.iteritems()}

            self.updateProgress.emit(1)

            time.sleep(self.refresh_interval)


    def stop(self):
        self._running == False

if __name__ == '__main__':

    from src.core import instantiate_instruments, instantiate_probes
    instruments = {'inst_dummy': 'DummyInstrument'}

    instruments = instantiate_instruments(instruments)
    print(instruments)
    probes = {
        'random': {'probe_name': 'value1', 'instrument_name': 'inst_dummy'},
        'value2': {'probe_name': 'value2', 'instrument_name': 'inst_dummy'},
    }

    probes = instantiate_probes(probes, instruments)


    r = ReadProbes(probes)
    r.run()




