import time
from unittest import TestCase

import numpy as np
from src.labview_fpga_lib.labview_helper_functions.labview_conversion import int_to_voltage

from b26_toolkit.src.instruments import NI7845RReadWrite


class TestNI7845RReadAnalogIO(TestCase):
    def test_init(self):
        fpga = NI7845RReadWrite()

        print(fpga.settings)

        print(fpga.AI0)
        print(fpga.AI1)
        print(fpga.AI2)
        print(fpga.AI3)

    def test_input_output(self):

        # important for this test to pass, connect output AO4 to input AI7!!!!!

        values = np.arange(-5.0, 5.0, 0.4)
        fpga = NI7845RReadWrite()
        def similar(val1, val2):
            """
            compare if value val1 and val2 are similar

            Args:
                val1:
                val2:

            Returns:

            """

            passed = False
            err = abs((val1-val2) / (val1+val2))

            if err<0.03:
                passed =True

            print(val1, val2, err)

            return passed


        for value in values:
            fpga.update({'AO4': float(value)})
            time.sleep(0.05)

            read_value = int_to_voltage(fpga.AI7)

            if similar(value, read_value) == False:
                raise ValueError

