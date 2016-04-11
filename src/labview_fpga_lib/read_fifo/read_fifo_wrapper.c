/*
 * FPGA Interface C API example for GCC for computers running Linux.
 *
 * NOTE: In order to run this example, you must compile a LabVIEW FPGA bitfile
 *       and generate a C API for it. For more information about using this
 *       example, refer to the Examples topic of the FPGA Interface C API Help,
 *       located under
 *       Start>>All Programs>>National Instruments>>FPGA Interface C API.
 */
 
#include "NiFpga_FPGA_read_fifo.h"

#include <stdio.h>
#include <stdlib.h>

// overwrite the definition of the header file created by Labview because FPGA bitcode will be located in the subdir lib
// #define "NiFpga_FPGA_read_fifo.lvbitx" 


void start_fpga(NiFpga_Session* session, NiFpga_Status* status)
{
	// must be called before any other calls 
	*status = NiFpga_Initialize();
	printf("initializing FPGA PID Simple Loop \n");
	printf("bitfile expected at:\n");
	printf(NiFpga_FPGA_read_fifo_Bitfile);
	printf("\n");
	
	if (NiFpga_IsNotError(*status))
	{
		// opens a session, downloads the bitstream, and runs the FPGA 
		NiFpga_MergeStatus(status, NiFpga_Open(NiFpga_FPGA_read_fifo_Bitfile,
												NiFpga_FPGA_read_fifo_Signature,
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

uint32_t read_LoopTicksAcq(NiFpga_Session* session, NiFpga_Status* status)
{
	int32_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadU32(*session,NiFpga_FPGA_read_fifo_IndicatorU32_looptimeacqticks,&value));
	return value;
}


// ============ read logical indicators ==================


_Bool read_LoopRateLimitAcq(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_Bool state;
	NiFpga_MergeStatus(status, NiFpga_ReadBool(*session,NiFpga_FPGA_read_fifo_IndicatorBool_loopratelimitacquisition,&state));
	return state;
}

_Bool read_TimeOutAcq(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_Bool state;
	NiFpga_MergeStatus(status, NiFpga_ReadBool(*session,NiFpga_FPGA_read_fifo_IndicatorBool_TimedOutacquisition,&state));
	return state;
}

_Bool read_AcquireData(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_Bool state;
	NiFpga_MergeStatus(status, NiFpga_ReadBool(*session,NiFpga_FPGA_read_fifo_ControlBool_acquiredatafast,&state));
	return state;
}


_Bool read_DMATimeOut(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_Bool state;
	NiFpga_MergeStatus(status, NiFpga_ReadBool(*session,NiFpga_FPGA_read_fifo_IndicatorBool_DMAtimeout,&state));
	return state;
}

// ============ set logical values ==================

void set_AcquireData(_Bool state, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteBool(*session,NiFpga_FPGA_read_fifo_ControlBool_acquiredatafast, state));
}

void set_Stop(_Bool state, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteBool(*session,NiFpga_FPGA_read_fifo_ControlBool_stop, state));
}



// ============ set parameters ==================

void set_SamplePeriodsAcq(uint32_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteU32(*session,NiFpga_FPGA_read_fifo_ControlU32_sampleperiodacquisitionticks,value));
}

void set_ElementsToWrite(int32_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI32(*session,NiFpga_FPGA_read_fifo_ControlI32_elemetstowriteAcq, value));
}


// read parameters
int32_t read_ElementsWritten(NiFpga_Session* session, NiFpga_Status* status)
{
	int32_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI32(*session,NiFpga_FPGA_read_fifo_IndicatorI32_elemetswrittenAcq,&value));
	return value;
}



// ============ read analog inputs ==================
int16_t read_AI0(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_read_fifo_IndicatorI16_AI0raw,&value));
	return value;
}


int16_t read_AI1(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_read_fifo_IndicatorI16_AI1raw,&value));
	return value;
}


// ============ set analog outputs ==================

// =========================================================
// ============ FIFO =======================================
// =========================================================
size_t configure_FIFO_AI(size_t requestedDepth, NiFpga_Session* session, NiFpga_Status* status)
{
	size_t actualDepth;
	NiFpga_MergeStatus(status, NiFpga_ConfigureFifo2(*session, NiFpga_FPGA_read_fifo_TargetToHostFifoU32_DMA, requestedDepth, &actualDepth));
	return actualDepth;
}

void start_FIFO_AI(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_StartFifo(*session, NiFpga_FPGA_read_fifo_TargetToHostFifoU32_DMA));
}

void stop_FIFO_AI(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_StopFifo(*session, NiFpga_FPGA_read_fifo_TargetToHostFifoU32_DMA));
}

void read_FIFO_AI(uint32_t* input, size_t size, NiFpga_Session* session, NiFpga_Status* status,size_t* elementsRemaining)
{
	/* copy FIFO data from the FPGA */
	NiFpga_MergeStatus(status,
					   NiFpga_ReadFifoU32(*session,
							   	   	   	  NiFpga_FPGA_read_fifo_TargetToHostFifoU32_DMA,
										  input,
										  size,
										  NiFpga_InfiniteTimeout,
										  elementsRemaining));
}


void unpack_data(uint32_t* input, int16_t* AI1, int16_t* AI2, size_t size)
{
	int iter;
	for (iter = 0; iter < size; ++iter) {
		uint32_t incoming = input[iter];
		AI1[iter] = (int16_t) ((incoming >> 16) & 0xffff);
		AI2[iter] = incoming & 0xffff;
	}
}

void read_FIFO_AI_unpack(int16_t* AI1, int16_t* AI2, size_t size, NiFpga_Session* session, NiFpga_Status* status,size_t* elementsRemaining)
{
	uint32_t input[size];

	read_FIFO_AI(input, size, session, status, elementsRemaining);

	unpack_data(input,AI1,AI2,size);
}