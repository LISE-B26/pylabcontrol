/*
 * FPGA Interface C API example for GCC for computers running Linux.
 *
 * NOTE: In order to run this example, you must compile a LabVIEW FPGA bitfile
 *       and generate a C API for it. For more information about using this
 *       example, refer to the Examples topic of the FPGA Interface C API Help,
 *       located under
 *       Start>>All Programs>>National Instruments>>FPGA Interface C API.
 */
 
#include "NiFpga_GalvoScan.h"

#include <stdio.h>
#include <stdlib.h>

// overwrite the definition of the header file created by Labview because FPGA bitcode will be located in the subdir lib
// #define "NiFpga_GalvoScan.lvbitx" 


void start_fpga(NiFpga_Session* session, NiFpga_Status* status)
{
	// must be called before any other calls 
	*status = NiFpga_Initialize();
	printf("initializing FPGA Galvo Scan \n");
	printf("bitfile expected at:\n");
	printf(NiFpga_GalvoScan_Bitfile);
	printf("\n");
	
	if (NiFpga_IsNotError(*status))
	{
		// opens a session, downloads the bitstream, and runs the FPGA 
		NiFpga_MergeStatus(status, NiFpga_Open(NiFpga_GalvoScan_Bitfile,
												NiFpga_GalvoScan_Signature,
												"RIO0",
												NiFpga_OpenAttribute_NoRun,
												session));
		if (NiFpga_IsNotError(*status))
		{
			// run the FPGA application 
			NiFpga_MergeStatus(status, NiFpga_Run(*session, 0));
		}
		else{
			// print warning
			printf("error occurred at FPGA open");
			printf("%d", *status);
			
		}
	}
	
	fflush(stdout);
	
}

void stop_fpga(NiFpga_Session* session, NiFpga_Status* status)
{
	// close the session now that we're done 
	NiFpga_MergeStatus(status, NiFpga_Close(*session, 0));

	// must be called after all other calls 
	NiFpga_MergeStatus(status, NiFpga_Finalize());
}


// read times
uint32_t read_LoopTimeAcq(NiFpga_Session* session, NiFpga_Status* status)
{
	int32_t value;
	NiFpga_MergeStatus(status, NiFpga_ReadU32(*session,NiFpga_GalvoScan_ControlU32_looptimeCountTicks,&value));
	return value;
}

// read logical indicators
_Bool read_LoopRateLimitAcq(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_Bool state;
	NiFpga_MergeStatus(status, NiFpga_ReadBool(*session,NiFpga_GalvoScan_IndicatorBool_loopratelimitacquisition,&state));
	return state;
}
_Bool read_Stop(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_Bool state;
	NiFpga_MergeStatus(status, NiFpga_ReadBool(*session,NiFpga_GalvoScan_ControlBool_stop,&state));
	return state;
}
_Bool read_DMATimeOut(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_Bool state;
	NiFpga_MergeStatus(status, NiFpga_ReadBool(*session,NiFpga_GalvoScan_IndicatorBool_DMAtimeout,&state));
	return state;
}


// set logical values
void set_Stop(_Bool state, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteBool(*session,NiFpga_GalvoScan_ControlBool_stop, state));
}

// set parameters
void set_Nx(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_GalvoScan_ControlI16_N_x,value));
}

void set_Vmin_x(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_GalvoScan_ControlI16_Vmin_x,value));
}

void set_dVmin_x(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_GalvoScan_ControlI16_dVmin_x,value));
}

void set_Ny(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_GalvoScan_ControlI16_N_y,value));
}

void set_Vmin_y(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_GalvoScan_ControlI16_Vmin_y,value));
}

void set_dVmin_y(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_GalvoScan_ControlI16_dVmin_y,value));
}

void set_scanmode(uint8_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteU8(*session,NiFpga_GalvoScan_ControlU8_scanmode,value));
}

void set_forward_y(_Bool state, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteBool(*session,NiFpga_GalvoScan_ControlBool_forwardy, state));
}
void set_settle_time(uint32_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteU32(*session,NiFpga_GalvoScan_ControlU32_settletimeCountTicks,value));
}

void set_loop_time(uint32_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteU32(*session,NiFpga_GalvoScan_ControlU32_looptimeCountTicks,value));
}


// read parameters
int16_t read_elements_written_to_dma(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_GalvoScan_IndicatorI16_datasenttoDMA,&value));
	return value;
}

int16_t read_detector_signal(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_GalvoScan_IndicatorI16_Detectorsignal,&value));
	return value;
}



// =========================================================
// ============ FIFO =======================================
// =========================================================
size_t configure_FIFO(size_t requestedDepth, NiFpga_Session* session, NiFpga_Status* status)
{
	size_t actualDepth;
	NiFpga_MergeStatus(status, NiFpga_ConfigureFifo2(*session, NiFpga_GalvoScan_TargetToHostFifoI16_DMA, requestedDepth, &actualDepth));
	return actualDepth;
}

void start_FIFO(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_StartFifo(*session, NiFpga_GalvoScan_TargetToHostFifoI16_DMA));
}

void stop_FIFO(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_StopFifo(*session, NiFpga_GalvoScan_TargetToHostFifoI16_DMA));
}


void read_FIFO(int16_t* input, size_t size, NiFpga_Session* session, NiFpga_Status* status,size_t* elementsRemaining)
{
	/* copy FIFO data from the FPGA */
	NiFpga_MergeStatus(status,
					   NiFpga_ReadFifoI16(*session,
							   	   	   	  NiFpga_GalvoScan_TargetToHostFifoI16_DMA,
										  input,
										  size,
										  NiFpga_InfiniteTimeout,
										  elementsRemaining));
}

