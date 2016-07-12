from script_dummy import ScriptDummyPlotMemoryTest, ScriptDummy, ScriptDummyWithInstrument, ScriptDummyWithSubScript, \
    ScriptDummyWithNestedSubScript, ScriptDummyCounter

# try:
#     from script_dummy import ScriptDummyWithInstrument
# except:
#     print("./src/scripts/__init__ warning! ScriptDummyWithInstrument did not load")

# from script_dummy import  ScriptDummy, ScriptDummyWithQtSignal, ScriptDummyPlotting

# try:
#     from galvo_scan import GalvoScan
# except:
#     print("./src/scripts/__init__ warning! GalvoScan did not load")

from galvo_scan import GalvoScan

try:
    from GalvoScanWithLightControl import GalvoScanWithLightControl
except:
    print("./src/scripts/__init__ warning! GalvoScanWithLightControl did not load")
try:
    from GalvoScanWithTwoRoI import GalvoScanWithTwoRoI
except:
    print("./src/scripts/__init__ warning! GalvoScanWithTwoRoI did not load")
try:
    from Find_Points import Find_Points
except:
    print("./src/scripts/__init__ warning! Find_Points did not load")


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
try:
    from FPGA_PolarizationController import FPGA_BalancePolarization
except:
    print("./src/scripts/__init__ warning! FPGA_BalancePolarization did not load")



# from StanfordResearch_ESR import StanfordResearch_ESR
try:
    from autofocus_ni_fpga import AutoFocusDAQ
except:
    print("./src/scripts/__init__ warning! AutoFocusDAQ did not load")

try:
    from autofocus_ni_fpga import AutoFocusNIFPGA
except:
    print("./src/scripts/__init__ warning! AutoFocusNIFPGA did not load")
# from light_control import CameraOn
from Select_NVs import Select_NVs_Simple
try:
    from set_laser import SetLaser
except:
    print("./src/scripts/__init__ warning! SetLaser did not load")
try:
    from find_max_counts_point_2d import FindMaxCounts2D
except:
    print("./src/scripts/__init__ warning! FindMaxCounts2D did not load")
try:
    from Select_NVs import Select_NVs
except:
    print("./src/scripts/__init__ warning! Select_NVs did not load")

try:
    from Select_NVs import Select_NVs_Simple
except:
    print("./src/scripts/__init__ warning! Select_NVs_Simple did not load")

try:
    from set_laser import SetLaser
except:
    print("./src/scripts/__init__ warning! AutoFocus did not load")

try:
    from Correlate_Images import Take_And_Correlate_Images_2
except:
    print("./src/scripts/__init__ warning! Correlate_Images did not load")


# try:
#     from find_max_counts_point_2d import FindMaxCounts2D
# except:
#     print("./src/scripts/__init__ warning! FindMaxCounts2D did not load")
try:
    from find_max_counts_point_2d import FindMaxCounts2D
except:
    print("./src/scripts/__init__ warning! FindMaxCounts2D did not load")

try:
    from StanfordResearch_ESR import StanfordResearch_ESR
except:
    print("./src/scripts/__init__ warning! StanfordResearch_ESR did not load")

try:
    from ESR_Selected_NVs import ESR_Selected_NVs
except:
    print("./src/scripts/__init__ warning! ESR_Selected_NVs did not load")

# from labview_fpga_get_timetrace import LabviewFpgaTimetrace


try:
    from galvo_scan_ni_fpga import GalvoScanNIFpga
except:
    print("./src/scripts/__init__ warning! GalvoScanNIFpga did not load")

try:
    from autofocus_ni_fpga import AutoFocusNIFPGA
except:
    print("./src/scripts/__init__ warning! AutoFocusNIFPGA did not load")


try:
    from galvo_scan_ni_fpga_loop import GalvoScanNIFPGALoop
except:
    print("./src/scripts/__init__ warning! GalvoScanNIFPGALoop did not load")


# try:
#     from Multiple_ESR import ESR_Selected_NVs_Simple
# except:
#     print("./src/scripts/__init__ warning! ESR_Selected_NVs_Simple did not load")


try:
    from atto_scan import AttoStep
except:
    print("./src/scripts/__init__ warning! Attostep did not load")

try:
    from refind_NVs import Refind_NVs
except:
    print("./src/scripts/__init__ warning! Refind_NVs did not load")

try:
    from ESR_and_push import ESR_And_Push
except:
    print("./src/scripts/__init__ warning! ESR_And_Push did not load")

# try:
#     from pulse_delays import PulseDelays
# except:
#     print("./src/scripts/__init__ warning! PulseDelays did not load")
from exec_pulse_blaster_sequence import ExecutePulseBlasterSequence

from pulse_delays import PulseDelays

from pulse_blaster_scripts import Rabi, Rabi_Power_Sweep

from daq_read_counter import Daq_Read_Counter

from MW_Power_Broadening import MWPowerBroadening

try:
    from pulse_blaster_scripts import PulsedESR
except:
    print("./src/scripts/__init__ warning! Pulsed_ESR did not load")

from pulse_blaster_scripts import CalibrateMeasurementWindow

from pulse_blaster_scripts import Rabi_Power_Sweep_Single_Tau

from pulse_blaster_scripts import RoundPiPulseTime

try:
    from pulse_blaster_scripts import Rabi_Loop
except:
    print("./src/scripts/__init__ warning! Rabi_Loop did not load")
