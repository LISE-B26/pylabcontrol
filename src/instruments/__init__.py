try:
    from gauge_controller import PressureGauge
except:
    print("./src/instrument/__init__ warning! PressureGauge did not load")

try:
    from spectrum_analyzer import SpectrumAnalyzer
except:
    print("./src/instrument/__init__ warning! SpectrumAnalyzer did not load")

try:
    from NIDAQ import DAQ
except:
    print("./src/instrument/__init__ warning! DAQ did not load")

try:
    from piezo_controller import PiezoController
except:
    print("./src/instrument/__init__ warning! PiezoController did not load")

try:
    from zurich_instruments import ZIHF2
except:
    print("./src/instrument/__init__ warning! ZIHF2 did not load")

# try:
#     from maestro import MaestroBeamBlock
# except:
#     print("./src/instrument/__init__ warning! MaestroBeamBlock did not load")
#
# try:
#     from maestro import MaestroController
# except:
#     print("./src/instrument/__init__ warning! MaestroController did not load")
#
# try:
#     from maestro import MaestroFilterWheel
# except:
#     print("./src/instrument/__init__ warning! MaestroFilterWheel did not load")

try:
    from maestro import MaestroLightControl
except:
    print("./src/instrument/__init__ warning! MaestroLightControl did not load")


try:
    from attocube import Attocube
except:
    print("./src/instrument/__init__ warning! Attocube did not load")

try:
    from spectrum_analyzer import SpectrumAnalyzer
except:
    print("./src/instrument/__init__ warning! SpectrumAnalyzer did not load")

try:
    from instrument_dummy import DummyInstrument
except:
    print("./src/instrument/__init__ warning! DummyInstrument did not load")

try:
    from microwave_generator import MicrowaveGenerator
except:
    print("./src/instrument/__init__ warning! MicrowaveGenerator did not load")


try:
    from labview_fpga import NI7845RReadWrite
except:
    print("./src/instrument/__init__ warning! NI7845RReadAnalogIO did not load")

try:
    from labview_fpga import NI7845RPidSimpleLoop
except:
    print("./src/instrument/__init__ warning! NI7845RPidSimpleLoop did not load")

try:
    from labview_fpga import NI7845RGalvoScan
except:
    print("./src/instrument/__init__ warning! NI7845RGalvoScan did not load")


try:
    from labview_fpga import NI7845RReadFifo
except:
    print("./src/instrument/__init__ warning! NI7845RReadFifo did not load")

# try:
#     from montana import CryoStation
# except:
#     print("./src/instrument/__init__ warning! CryoStation did not load")

    # __all__ = ['PressureGauge', 'DAQ', 'PiezoController', 'SpectrumAnalyzer', 'Attocube', 'MaestroBeamBlock', 'MaestroController', 'ZIHF2']
# __all__ = ['PressureGauge', 'DAQ', 'PiezoController', 'SpectrumAnalyzer', 'Attocube', 'MaestroBeamBlock', 'MaestroController', 'ZIHF2']