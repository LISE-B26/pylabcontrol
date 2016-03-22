try:
    from gauge_controller import PressureGauge
except:
    pass

try:
    from spectrum_analyzer import SpectrumAnalyzer
except:
    pass

try:
    from instruments_DAQ import DAQ
except:
    pass

try:
    from piezo_controller import PiezoController
except:
    pass

try:
    from zurich_instruments import ZIHF2
except:
    pass

try:
    from maestro import MaestroBeamBlock, MaestroController
except:
    pass

try:
    from attocube import Attocube
except:
    pass

try:
    from spectrum_analyzer import SpectrumAnalyzer
except:
    pass


# __all__ = ['PressureGauge', 'DAQ', 'PiezoController', 'SpectrumAnalyzer', 'Attocube', 'MaestroBeamBlock', 'MaestroController', 'ZIHF2']
# __all__ = ['PressureGauge', 'DAQ', 'PiezoController', 'SpectrumAnalyzer', 'Attocube', 'MaestroBeamBlock', 'MaestroController', 'ZIHF2']