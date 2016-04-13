/*
 * FPGA Interface C API example for GCC for computers running Linux.
 *
 * NOTE: In order to run this example, you must compile a LabVIEW FPGA bitfile
 *       and generate a C API for it. For more information about using this
 *       example, refer to the Examples topic of the FPGA Interface C API Help,
 *       located under
 *       Start>>All Programs>>National Instruments>>FPGA Interface C API.
 */
 
#include "NiFpga_FPGA_PID_Loop_Simple.h"

#include <stdio.h>
#include <stdlib.h>

// overwrite the definition of the header file created by Labview because FPGA bitcode will be located in the subdir lib
// #define "NiFpga_FPGA_PID_Loop_Simple.lvbitx" 


void start_fpga(NiFpga_Session* session, NiFpga_Status* status)
{
	// must be called before any other calls 
	*status = NiFpga_Initialize();
	printf("initializing FPGA PID Simple Loop \n");
	printf("bitfile expected at:\n");
	printf(NiFpga_FPGA_PID_Loop_Simple_Bitfile);
	printf("\n");
	
	if (NiFpga_IsNotError(*status))
	{
		// opens a session, downloads the bitstream, and runs the FPGA 
		NiFpga_MergeStatus(status, NiFpga_Open(NiFpga_FPGA_PID_Loop_Simple_Bitfile,
												NiFpga_FPGA_PID_Loop_Simple_Signature,
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
uint32_t read_LoopTicksPID(NiFpga_Session* session, NiFpga_Status* status)
{
	int32_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadU32(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorU32_looptimePIDticks,&value));
	return value;
}

uint32_t read_LoopTicksAcq(NiFpga_Session* session, NiFpga_Status* status)
{
	int32_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadU32(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorU32_looptimeacqticks,&value));
	return value;
}


// ============ read logical indicators ==================
_Bool read_LoopRateLimitPID(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_Bool state;
	NiFpga_MergeStatus(status, NiFpga_ReadBool(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorBool_loopratelimitPID,&state));
	return state;
}


_Bool read_LoopRateLimitAcq(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_Bool state;
	NiFpga_MergeStatus(status, NiFpga_ReadBool(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorBool_loopratelimitacquisition,&state));
	return state;
}

_Bool read_TimeOutAcq(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_Bool state;
	NiFpga_MergeStatus(status, NiFpga_ReadBool(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorBool_TimedOutacquisition,&state));
	return state;
}

_Bool read_AcquireData(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_Bool state;
	NiFpga_MergeStatus(status, NiFpga_ReadBool(*session,NiFpga_FPGA_PID_Loop_Simple_ControlBool_acquiredata,&state));
	return state;
}

_Bool read_LowPassActive(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_Bool state;
	NiFpga_MergeStatus(status, NiFpga_ReadBool(*session,NiFpga_FPGA_PID_Loop_Simple_ControlBool_Lowpassactive,&state));
	return state;
}

_Bool read_PIDActive(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_Bool state;
	NiFpga_MergeStatus(status, NiFpga_ReadBool(*session,NiFpga_FPGA_PID_Loop_Simple_ControlBool_PIDactive,&state));
	return state;
}

_Bool read_OutputSine(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_Bool state;
	NiFpga_MergeStatus(status, NiFpga_ReadBool(*session,NiFpga_FPGA_PID_Loop_Simple_ControlBool_output10kHzSine,&state));
	return state;
}

_Bool read_FPGARunning(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_Bool state;
	NiFpga_MergeStatus(status, NiFpga_ReadBool(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorBool_FPGArunning,&state));
	return state;
}

_Bool read_DMATimeOut(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_Bool state;
	NiFpga_MergeStatus(status, NiFpga_ReadBool(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorBool_DMAtimeout,&state));
	return state;
}

// ============ set logical values ==================
void set_LowPassActive(_Bool state, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteBool(*session,NiFpga_FPGA_PID_Loop_Simple_ControlBool_Lowpassactive, state));
}

void set_PIDActive(_Bool state, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteBool(*session,NiFpga_FPGA_PID_Loop_Simple_ControlBool_PIDactive, state));
}

void set_AcquireData(_Bool state, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteBool(*session,NiFpga_FPGA_PID_Loop_Simple_ControlBool_acquiredata, state));
}

void set_Stop(_Bool state, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteBool(*session,NiFpga_FPGA_PID_Loop_Simple_ControlBool_stop, state));
}

void set_OutputSine(_Bool state, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteBool(*session,NiFpga_FPGA_PID_Loop_Simple_ControlBool_output10kHzSine, state));
}


// ============ set parameters ==================
void set_SamplePeriodsPID(uint32_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteU32(*session,NiFpga_FPGA_PID_Loop_Simple_ControlU32_sampleperiodticksPID,value));
}

void set_SamplePeriodsAcq(uint32_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteU32(*session,NiFpga_FPGA_PID_Loop_Simple_ControlU32_sampleperiodacquisitionticks,value));
}

void set_ElementsToWrite(int32_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI32(*session,NiFpga_FPGA_PID_Loop_Simple_ControlI32_elementstowriteAcq, value));
}

void set_ScaledCoefficient_1(int32_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI32(*session,NiFpga_FPGA_PID_Loop_Simple_ControlI32_scaledcoefficient1, value));
}

void set_ScaledCoefficient_2(int32_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI32(*session,NiFpga_FPGA_PID_Loop_Simple_ControlI32_scaledcoefficient2, value));
}

void set_ScaledCoefficient_3(int32_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI32(*session,NiFpga_FPGA_PID_Loop_Simple_ControlI32_scaledcoefficient3, value));
}


void set_PI_gains(uint32_t value_prop, uint32_t value_int, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteU32(*session,NiFpga_FPGA_PID_Loop_Simple_ControlU32_integralgain,value_int));
	NiFpga_MergeStatus(status, NiFpga_WriteU32(*session,NiFpga_FPGA_PID_Loop_Simple_ControlU32_proportionalgain,value_prop));
}

void set_PI_gain_int(uint32_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteU32(*session,NiFpga_FPGA_PID_Loop_Simple_ControlU32_integralgain,value));

}

void set_PI_gain_prop(uint32_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteU32(*session,NiFpga_FPGA_PID_Loop_Simple_ControlU32_proportionalgain,value));
}
	

void set_Setpoint(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_FPGA_PID_Loop_Simple_ControlI16_Setpoint, value));
}

void set_TimeoutBuffer(int32_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI32(*session,NiFpga_FPGA_PID_Loop_Simple_ControlI32_TimeoutBuffer, value));
}

void set_AmplitudeScaleCoefficient(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_FPGA_PID_Loop_Simple_ControlI16_amplitudescalecoefficient, value));
}



// read parameters
int32_t read_ElementsWritten(NiFpga_Session* session, NiFpga_Status* status)
{
	int32_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI32(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorI32_elementswrittenAcq,&value));
	return value;
}

uint32_t read_AcqTime(NiFpga_Session* session, NiFpga_Status* status)
{
	uint32_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadU32(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorU32_acqtimeticks,&value));
	return value;
}



// read values
int16_t read_Min(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorI16_minxy,&value));
	return value;
}
int16_t read_Max(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorI16_maxxy,&value));
	return value;
}
uint16_t read_StdDev(NiFpga_Session* session, NiFpga_Status* status)
{
	uint16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorU16_standarddeviation,&value));
	return value;
}
int16_t read_Mean(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorI16_mean,&value));
	return value;
}

// ============ read analog inputs ==================
int16_t read_AI1(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorI16_AI1raw,&value));
	return value;
}

int16_t read_AI1_Filtered(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorI16_AI1_filtered,&value));
	return value;
}

int16_t read_AI2(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorI16_AI2raw,&value));
	return value;
}

int16_t read_DeviceTemperature(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_PID_Loop_Simple_IndicatorI16_DeviceTemperature,&value));
	return value;
}

int16_t read_PiezoOut(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_PID_Loop_Simple_ControlI16_PiezoOutAO0,&value));
	return value;
}


// ============ set analog outputs ==================
void set_PiezoOut(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_FPGA_PID_Loop_Simple_ControlI16_PiezoOutAO0,value));
}

// =========================================================
// ============ FIFO =======================================
// =========================================================
size_t configure_FIFO_AI(size_t requestedDepth, NiFpga_Session* session, NiFpga_Status* status)
{
	size_t actualDepth;
	NiFpga_MergeStatus(status, NiFpga_ConfigureFifo2(*session, NiFpga_FPGA_PID_Loop_Simple_TargetToHostFifoU32_DMA, requestedDepth, &actualDepth));
	return actualDepth;
}

void start_FIFO_AI(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_StartFifo(*session, NiFpga_FPGA_PID_Loop_Simple_TargetToHostFifoU32_DMA));
}

void stop_FIFO_AI(NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_StopFifo(*session, NiFpga_FPGA_PID_Loop_Simple_TargetToHostFifoU32_DMA));
}

void read_FIFO_AI(uint32_t* input, size_t size, NiFpga_Session* session, NiFpga_Status* status,size_t* elementsRemaining)
{
	/* copy FIFO data from the FPGA */
	NiFpga_MergeStatus(status,
					   NiFpga_ReadFifoU32(*session,
							   	   	   	  NiFpga_FPGA_PID_Loop_Simple_TargetToHostFifoU32_DMA,
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