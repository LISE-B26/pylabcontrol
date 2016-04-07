/*
 * FPGA Interface C API example for GCC for computers running Linux.
 *
 * NOTE: In order to run this example, you must compile a LabVIEW FPGA bitfile
 *       and generate a C API for it. For more information about using this
 *       example, refer to the Examples topic of the FPGA Interface C API Help,
 *       located under
 *       Start>>All Programs>>National Instruments>>FPGA Interface C API.
 */
 
#include "NiFpga_FPGA_read_ai_ao.h"

#include <stdio.h>
#include <stdlib.h>





void start_fpga(NiFpga_Session* session, NiFpga_Status* status)
{
	// must be called before any other calls 
	*status = NiFpga_Initialize();
	printf("initializing FPGA \n");

	if (NiFpga_IsNotError(*status))
	{
		// opens a session, downloads the bitstream, and runs the FPGA 
		NiFpga_MergeStatus(status, NiFpga_Open(NiFpga_FPGA_read_ai_ao_Bitfile,
												NiFpga_FPGA_read_ai_ao_Signature,
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
/*
int16_t read_DeviceTemperature(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_read_ai_ao_IndicatorI16_DeviceTemperature,&value));
	return value;
}
*/

int16_t read_AI0(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_read_ai_ao_IndicatorI16_Connector1AI0,&value));
	return value;
}

int16_t read_AI1(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_read_ai_ao_IndicatorI16_Connector1AI1,&value));
	return value;
}

int16_t read_AI2(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_read_ai_ao_IndicatorI16_Connector1AI2,&value));
	return value;
}

int16_t read_AI3(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_read_ai_ao_IndicatorI16_Connector1AI3,&value));
	return value;
}

int16_t read_AI4(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_read_ai_ao_IndicatorI16_Connector1AI4,&value));
	return value;
}

int16_t read_AI5(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_read_ai_ao_IndicatorI16_Connector1AI5,&value));
	return value;
}

int16_t read_AI6(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_read_ai_ao_IndicatorI16_Connector1AI6,&value));
	return value;
}

int16_t read_AI7(NiFpga_Session* session, NiFpga_Status* status)
{
	int16_t value;

	NiFpga_MergeStatus(status, NiFpga_ReadI16(*session,NiFpga_FPGA_read_ai_ao_IndicatorI16_Connector1AI7,&value));
	return value;
}


void set_AO0(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_FPGA_read_ai_ao_ControlI16_Connector1AO0,value));
}


void set_AO1(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_FPGA_read_ai_ao_ControlI16_Connector1AO1,value));
}

void set_AO2(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_FPGA_read_ai_ao_ControlI16_Connector1AO2,value));
}

void set_AO3(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_FPGA_read_ai_ao_ControlI16_Connector1AO3,value));
}

void set_AO4(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_FPGA_read_ai_ao_ControlI16_Connector1AO4,value));
}

void set_AO5(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_FPGA_read_ai_ao_ControlI16_Connector1AO5,value));
}

void set_AO6(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_FPGA_read_ai_ao_ControlI16_Connector1AO6,value));
}

void set_AO7(int16_t value, NiFpga_Session* session, NiFpga_Status* status)
{
	NiFpga_MergeStatus(status, NiFpga_WriteI16(*session,NiFpga_FPGA_read_ai_ao_ControlI16_Connector1AO7,value));
}