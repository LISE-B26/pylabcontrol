INSTRUMENT_LOCATION = 'src.instruments'
#INSTRUMENTS = ['MicrowaveGenerator']
INSTRUMENTS = ['PressureGauge']
LOCATIONS = ['gauge_controller']

#from src.instruments.gauge_controller import PressureGauge

import importlib
import sys
import os

sys.path.insert(0, os.path.abspath('../src'))
# for path in sys.path:
#     print(path + '\n')
importlib.import_module('src.instruments.pressure_gauge.PressureGauge')
successful_imports = []
failed_imports = []
for instrument in INSTRUMENTS:
    try:
        importlib.import_module(instrument, LOCATIONS[0])
        successful_imports.append(instrument)
    except ImportError:
        failed_imports.append(instrument)

print successful_imports
print failed_imports
