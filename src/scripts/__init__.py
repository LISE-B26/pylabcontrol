# from pulse_blaser_derived_scripts import Rabi_Loop
# ==== import dummy scripts ==================================================================================
# ============================================================================================================
from script_dummy import ScriptDummyPlotMemoryTest, ScriptDummy, ScriptDummyWithInstrument, ScriptDummyWithSubScript, \
    ScriptDummyWithNestedSubScript, ScriptDummyCounter, ScriptMinimalDummy

# ============================================================================================================



# ==== import NI DAQ scripts ==================================================================================
# =============================================================================================================
try:
    from galvo_scan import GalvoScan
except:
    print("./src/scripts/__init__ warning! GalvoScan did not load")
try:
    from legacy_src.old_scripts.GalvoScanWithLightControl import GalvoScanWithLightControl
except:
    print("./src/scripts/__init__ warning! GalvoScanWithLightControl did not load")

try:
    from legacy_src.old_scripts.GalvoScanWithTwoRoI import GalvoScanWithTwoRoI
except:
    print("./src/scripts/__init__ warning! GalvoScanWithTwoRoI did not load")
try:
    from autofocus import AutoFocusDAQ
except:
    print("./src/scripts/__init__ warning! AutoFocus did not load")
try:
    from set_laser import SetLaser
except:
    print("./src/scripts/__init__ warning! SetLaser did not load")
try:
    from daq_read_counter import Daq_Read_Counter
except:
    print("./src/scripts/__init__ warning! Daq_Read_Counter did not load")
# =============================================================================================================

# try:
#     from Find_Points import Find_Points
# except:
#     print("./src/scripts/__init__ warning! Find_Points did not load")

# ==== import NI FPGA scripts =================================================================================
# =============================================================================================================
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
try:
    from autofocus import AutoFocusNIFPGA
except:
    print("./src/scripts/__init__ warning! AutoFocusNIFPGA did not load")

try:
    from galvo_scan_ni_fpga import GalvoScanNIFpga
except:
    print("./src/scripts/__init__ warning! GalvoScanNIFpga did not load")

try:
    from legacy_src.old_scripts.galvo_scan_ni_fpga_loop import GalvoScanNIFPGALoop
except:
    print("./src/scripts/__init__ warning! GalvoScanNIFPGALoop did not load")

# =============================================================================================================

# ==== import some other scripts ==============================================================================
# =============================================================================================================
try:
    from Select_NVs import Select_NVs
except:
    print("./src/scripts/__init__ warning! Select_NVs did not load")

try:
    from Select_NVs import Select_NVs
except:
    print("./src/scripts/__init__ warning! Select_NVs did not load")

try:
    from Correlate_Images import Take_And_Correlate_Images_2
except:
    print("./src/scripts/__init__ warning! Take_And_Correlate_Images_2 did not load")

try:
    from find_max_counts_point_2d import FindMaxCounts2D
except:
    print("./src/scripts/__init__ warning! FindMaxCounts2D did not load")

try:
    from atto_scan import AttoStep
except:
    print("./src/scripts/__init__ warning! Attostep did not load")

try:
    from legacy_src.old_scripts.refind_NVs import Refind_NVs
except:
    print("./src/scripts/__init__ warning! Refind_NVs did not load")

# =============================================================================================================



# ==== import Stanford instruments ESR scripts=================================================================
# =============================================================================================================
try:
    from StanfordResearch_ESR import StanfordResearch_ESR
except:
    print("./src/scripts/__init__ warning! StanfordResearch_ESR did not load")

try:
    from legacy_src.old_scripts.ESR_Selected_NVs import ESR_Selected_NVs
except:
    print("./src/scripts/__init__ warning! ESR_Selected_NVs did not load")
try:
    from legacy_src.old_scripts.ESR_and_push import ESR_And_Push
except:
    print("./src/scripts/__init__ warning! ESR_And_Push did not load")

# =============================================================================================================




# ==== import Pulse blaster scripts============================================================================
# =============================================================================================================
try:
    from exec_pulse_blaster_sequence import ExecutePulseBlasterSequence
except:
    print("./src/scripts/__init__ warning! ExecutePulseBlasterSequence did not load")

try:
    from pulse_delays import PulseDelays
except:
    print("./src/scripts/__init__ warning! PulseDelays did not load")
try:
    from legacy_src.old_scripts.pulse_blaser_derived_scripts import Rabi_Power_Sweep
except:
    print("./src/scripts/__init__ warning! Rabi_Power_Sweep did not load")
try:
    from pulse_blaster_scripts import Rabi
except:
    print("./src/scripts/__init__ warning! Rabi did not load")
try:
    from pulse_blaster_scripts import PulsedESR
except:
    print("./src/scripts/__init__ warning! Pulsed_ESR did not load")
try:
    from legacy_src.old_scripts.MW_Power_Broadening import MWPowerBroadening
except:
    print("./src/scripts/__init__ warning! MWPowerBroadening did not load")
try:
    from pulse_blaster_scripts import CalibrateMeasurementWindow
except:
    print("./src/scripts/__init__ warning! CalibrateMeasurementWindow did not load")

try:
    from pulse_blaster_scripts import Rabi_Power_Sweep_Single_Tau
except:
    print("./src/scripts/__init__ warning! Rabi_Power_Sweep_Single_Tau did not load")
try:
    from legacy_src.old_scripts.pulse_blaser_derived_scripts import RoundPiPulseTime
except:
    print("./src/scripts/__init__ warning! RoundPiPulseTime did not load")

try:
    from legacy_src.old_scripts.pulse_blaser_derived_scripts import Rabi_Loop
except:
    print("./src/scripts/__init__ warning! Rabi_Loop did not load")

try:
    from pulse_blaster_scripts import T1
except:
    print("./src/scripts/__init__ warning! T1 did not load")

try:
    from pulse_blaster_scripts import CPMG
except:
    print("./src/scripts/__init__ warning! CPMG did not load")

    # =============================================================================================================

try:
    from keysight_get_spectrum import KeysightGetSpectrum
except:
    print("./src/scripts/__init__ warning! KeysightGetSpectrum did not load")
    # from pulse_blaser_derived_scripts import Rabi_Loop