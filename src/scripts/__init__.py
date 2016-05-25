# from script_dummy import ScriptDummy, ScriptDummyWithInstrument, ScriptDummyWithQtSignal
try:
    from script_dummy import ScriptDummyWithInstrument
except:
    print("./src/scripts/__init__ warning! ScriptDummyWithInstrument did not load")
from script_dummy import  ScriptDummy, ScriptDummyWithQtSignal
# from zi_sweeper import ZISweeper
# from zi_high_res_sweep import ZISweeperHighResolution
# from MWSpectraVsPower import MWSpectraVsPower
# from keysight_get_spectrum import KeysightGetSpectrum
# from keysight_spectra_vs_power import KeysightSpectrumVsPower
from galvo_scan import GalvoScan
from Find_Points import Find_Points
# from StanfordResearch_ESR import StanfordResearch_ESR
from autofocus import AutoFocus
# from light_control import CameraOn
from Select_NVs import Select_NVs
from Select_NVs import Select_NVs_Simple
from set_laser import SetLaser
from Correlate_Images import Correlate_Images
from center_on_NVs import Center_On_NVs

from StanfordResearch_ESR import StanfordResearch_ESR

from ESR_Selected_NVs import ESR_Selected_NVs

# from labview_fpga_get_timetrace import LabviewFpgaTimetrace
try:
    from labview_fpga_get_timetrace import LabviewFpgaTimetrace
except:
    print("./src/scripts/__init__ warning! LabviewFpgaTimetrace did not load")

try:
    from FPGA_PolarizationController import FPGA_PolarizationController
except:
    print("./src/scripts/__init__ warning! FPGA_PolarizationController did not load")

try:
    from FPGA_PolarizationController import FPGA_PolarizationSignalMap
except:
    print("./src/scripts/__init__ warning! FPGA_PolarizationSignalMap did not load")

try:
    from FPGA_PolarizationController import FPGA_PolarizationSignalScan
except:
    print("./src/scripts/__init__ warning! FPGA_PolarizationSignalScan did not load")


from Multiple_ESR import ESR_Selected_NVs_Simple