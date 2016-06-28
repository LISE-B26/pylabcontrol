from unittest import TestCase
from src.instruments.NIDAQ import DAQ

class TestDAQ(TestCase):
    def setUp(self):
        self.someDAQ = DAQ()

    def test_gated_read(self):
        #number of counts expected for result depends on sample and pulseblaster duration
        self.someDAQ.gated_DI_init('ctr0', 5)
        self.someDAQ.gated_DI_run()
        result = self.someDAQ.gated_DI_read(timeout=30)
        for i in range(0, 5):
            print(result[0][i])
        self.someDAQ.gated_DI_stop()