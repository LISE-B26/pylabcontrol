# from script_dummy import ScriptDummy, ScriptDummyWithInstrument, ScriptDummyWithQtSignal
try:
    from script_dummy import ScriptDummyWithInstrument
except:
    print("./src/scripts/__init__ warning! ScriptDummyWithInstrument did not load")
from script_dummy import  ScriptDummy, ScriptDummyWithQtSignal
# from zi_sweeper import ZISweeper
# from zi_high_res_sweep import ZISweeperHighResolution
from MWSpectraVsPower import MWSpectraVsPower
from keysight_get_spectrum import KeysightGetSpectrum
from keysight_spectra_vs_power import KeysightSpectrumVsPower
from galvo_scan import GalvoScan
from Find_Points import Find_Points
# from light_control import CameraOn

# from labview_fpga_get_timetrace import LabviewFpgaTimetrace
try:
    from labview_fpga_get_timetrace import LabviewFpgaTimetrace
except:
    print("./src/scripts/__init__ warning! LabviewFpgaTimetrace did not load")
