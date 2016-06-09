from ctypes import c_long

error_codes = {
'-61460':'Control and indicator names with newline characters are only supported when the VI execution mode is set to Execute VI on Development Computer with Simulated I/O and the FPGA VI reference is configured for Dynamic mode.',
'-61251':'The bitfile is incompatible with the configuration of the FPGA interface reference wire.',
'-61221':'Close and reset is not supported when the FPGA target execution mode is configured to Execute VI on Third-Party Simulator.',
'-61219':'The number of elements requested must be less than or equal to the number of unacquired elements left in the host memory DMA FIFO. There are currently fewer unacquired elements left in the FIFO than are being requested. Use the Delete Data Value Reference function to release some acquired elements before acquiring more elements.',
'-61218':'FIFO.Configure is not supported when configured with greater than 65536 elements and when the FPGA target execution mode is configured to Third-Party Simulation.',
'-61217':'A session cannot be closed or reset and a bitfile cannot be downloaded while DMA FIFO region references are outstanding for the specified session. Use a Delete Data Value Reference function to delete any regions acquired from Acquire Read Region or Acquire Write Region before taking any of these actions.',
'-61216':'A gated clock has violated the handshaking protocol. If you are using external gated clocks, ensure that they follow the required clock gating protocol. If you are generating your clocks internally, please contact National Instruments Technical Support.',
'-61215':'Bitfiles that allow removal of implicit enable signals in single-cycle Timed Loops can run only once. Download the bitfile again before re-running the VI.',
'-61214':'For bitfiles that allow removal of implicit enable signals in single-cycle Timed Loops, LabVIEW FPGA does not support this method prior to running the bitfile.',
'-61213':'LabVIEW FPGA does not support Close and Reset if Last Reference for bitfiles that allow removal of implicit enable signals in single-cycle Timed Loops. Right-click the Close FPGA VI Reference function and select Close instead.',
'-61212':'LabVIEW FPGA does not support the Abort method for bitfiles that allow removal of implicit enable signals in single-cycle Timed Loops.',
'-61211':'LabVIEW FPGA does not support the Reset method for bitfiles that allow removal of implicit enable signals in single-cycle Timed Loops.',
'-61210':'There was an error initializing the LabVIEW FPGA Simulation.',
'-61209':'This function is not supported when the FPGA target execution mode is configured to Execute VI on Third-Party Simulator.',
'-61208':'This function is supported only when the FPGA VI reference is configured for Dynamic mode and the FPGA target execution mode is configured to Execute VI on Third-Party Simulator.',
'-61206':'The configured item does not exist.',
'-61205':'An item of the selected name is present but is a different data type than that configured in the Open FPGA VI Reference.',
'-61204':'The operation could not be performed because the FPGA is busy operating in Simulation mode. Stop all activities on the FPGA before requesting this operation.',
'-61203':'The operation could not be performed because the FPGA is busy operating in Interactive mode. Stop all activities on the FPGA before requesting this operation.',
'-61202':'LabVIEW could not perform the operation because an FPGA VI reference to another VI is currently open. You must close the currently open FPGA VI reference before attempting to perform this operation.',
'-61201':'The chassis is in Scan Interface programming mode. In order to run FPGA VIs, you must go to the chassis properties page, select FPGA programming mode, and deploy the settings.',
'-61200':'The operation could not be performed because the FPGA is busy operating in FPGA Interface C API mode. Stop all activities on the FPGA before requesting this operation.',
'-61183':'The transfer function order exceeds the maximum order allowed.',
'-61182':'The transfer function is improper. The order of the numerator must be less than or equal to the order of the denominator.',
'-61181':'The notch width or Q factor must be greater than zero.',
'-61180':'All frequencies, f, within the notch region must meet: 0 < f < fs/2, where fs is the sample rate.',
'-61170':'The real and imaginary input data arrays must be the same size.',
'-61169':'The input parameter is not achievable on the FPGA at the given clock rate.',
'-61168':'The channel index input is out of the range of the configured number of channels.',
'-61167':'This function is not supported when the FPGA target is configured to execute on the development computer.',
'-61165':'You cannot execute this FPGA VI on the development computer because the FPGA VI is broken.',
'-61159':'This function is not supported when the FPGA target is configured to execute on the development computer with real I/O.',
'-61141':'The operation could not be performed because the FPGA is busy. Stop all activities on the FPGA before requesting this operation. If the target is in Scan Interface programming mode, put it in FPGA Interface programming mode.',
'-61078':'The requested memory could not be allocated.',
'-61077':'Terminated DMA FIFO. The FPGA was reconfigured while the DMA FIFO was in use.',
'-61076':'The DMA transfer did not complete within the timeout period.',
'-61075':'The DMA transfer was aborted and did not complete.',
'-61074':'The timeout parameter must be -1, 0, or a positive integer.',
'-61073':'The number of elements to read or write must be less than or equal to the depth of the host memory DMA FIFO.',
'-61072':'The requested FIFO depth is invalid. It is either 0 or an amount not supported by the hardware.',
'-61071':'The selected DMA FIFO was not found in the bitfile or FPGA design or is out of sync with the bitfile.',
'-61059':'The selected control was not found or is out of sync.',
'-61021':'FPGA Interface is out of date with the FPGA VI. Right-click and select Refresh.',
'-61017':'You must recompile the VI for the selected target.',
'-61016':'You must compile the VI for this target.',
'-61015':'No bitfile was found for download. You must compile the VI for this target.',
'61003':'The FPGA VI specified by the Invoke Method function with the Run method is already running. The interaction of the FPGA VI and the host VI might produce unexpected results. For example, executing this host VI may modify front panel values on the running FPGA VI. User interaction with the front panel of the FPGA VI may affect the execution of the host VI. Terminating either the FPGA VI or the host VI may terminate the other.',
'-61060':'The Wait on IRQ method timed out before the specified interrupt was received.',
'-61211':'Multiple resources with the same name are present in this VI. The Dynamic Mode of the FPGA Interface can only access a single resource of a given name.',
'-63195':'NI-RIO FPGA Communications Framework: (Hex 0xFFF0925) The handle for device communication is invalid.',
'-63101':'NI-RIO:  A valid .lvbitx bitfile is required. If you are using a valid .lvbitx bitfile, the bitfile may not be compatible with the software you are using. Determine which version of LabVIEW was used to make the bitfile, update your software to that version or later, and try again.'
}




class LabviewFPGAException(Exception):
    def __init__(self, error_code):
        if isinstance(error_code, c_long):
            error_code = str(error_code.value)
        if str(error_code) in error_codes:
            message = error_codes[str(error_code)]
        else:
            message = "unknown error code {:s}:".format(str(error_code))
        self.message = message
        self.code = error_code

    def __str__(self):
        return repr(self.message)

if __name__ =='__main__':

    try:
        raise LabviewFPGAException(61211)
    except LabviewFPGAException as e:
        print "Received error with code:", e.message, e.code

    try:
        raise LabviewFPGAException(-61015)
    except LabviewFPGAException as e:
        print "Received error with code:", e.message, e.code
