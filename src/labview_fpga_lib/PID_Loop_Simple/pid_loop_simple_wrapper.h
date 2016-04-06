/*
 * Fpga.h
 *
 *  Created on: 08.10.2014
 *      Author: ehebestreit
 *  Edited on 13.01.2016 
 * 		Author JanGieseler
 */
 
#include "./PID_Loop_Simple/NiFpga_PID_Loop_Simple.h"
#include <stdio.h>


#ifndef FPGA_H_
#define FPGA_H_


// todo: define path dynamically: #define LIB_PATH "..\\lib\\"

void start_fpga(NiFpga_Session* session, NiFpga_Status* status);
void stop_fpga(NiFpga_Session* session, NiFpga_Status* status);

// read times
uint32_t read_LoopTimeAcq(NiFpga_Session* session, NiFpga_Status* status);
uint32_t read_LoopTimePID(NiFpga_Session* session, NiFpga_Status* status);


// read logical indicators
_Bool read_LoopRateLimitPID(NiFpga_Session* session, NiFpga_Status* status);
_Bool read_LoopRateLimitAcq(NiFpga_Session* session, NiFpga_Status* status);
_Bool read_TimeOutAcq(NiFpga_Session* session, NiFpga_Status* status);
_Bool read_AcquireData(NiFpga_Session* session, NiFpga_Status* status);
_Bool read_LowPassActive(NiFpga_Session* session, NiFpga_Status* status);
_Bool read_PIDActive(NiFpga_Session* session, NiFpga_Status* status);
_Bool read_OutputSine(NiFpga_Session* session, NiFpga_Status* status);
_Bool read_FPGARunning(NiFpga_Session* session, NiFpga_Status* status);
_Bool read_DMATimeOut(NiFpga_Session* session, NiFpga_Status* status);

// set logical values
void set_LowPassActive(_Bool state, NiFpga_Session* session, NiFpga_Status* status);
void set_PIDActive(_Bool state, NiFpga_Session* session, NiFpga_Status* status);
void set_AcquireData(_Bool state, NiFpga_Session* session, NiFpga_Status* status); 
void set_Stop(_Bool state, NiFpga_Session* session, NiFpga_Status* status);
void set_OutputSine(_Bool state, NiFpga_Session* session, NiFpga_Status* status);

// set parameters
void set_SamplePeriodsPID(uint32_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_SamplePeriodsAcq(uint32_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_ElementsToWrite(int32_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_ScaledCoefficient_1(int32_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_ScaledCoefficient_2(int32_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_ScaledCoefficient_2(int32_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_PiezoOut(int16_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_PI_gain_prop(uint32_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_PI_gain_int(uint32_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_Setpoint(int16_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_TimeoutBuffer(int32_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_AmplitudeScaleCoefficient(int16_t value, NiFpga_Session* session, NiFpga_Status* status);


// read parameters
int32_t read_ElementsWritten(NiFpga_Session* session, NiFpga_Status* status);
uint32_t read_AcqTime(NiFpga_Session* session, NiFpga_Status* status);

// read values
int16_t read_Min(NiFpga_Session* session, NiFpga_Status* status);
int16_t read_Max(NiFpga_Session* session, NiFpga_Status* status);
uint16_t read_StdDev(NiFpga_Session* session, NiFpga_Status* status);
int16_t read_Mean(NiFpga_Session* session, NiFpga_Status* status);

// read FIFO
//size_t configure_FIFO_AI(size_t requestedDepth, NiFpga_Session* session, NiFpga_Status* status);
//void start_FIFO_DMA(NiFpga_Session* session, NiFpga_Status* status);
//void stop_FIFO_DMA(NiFpga_Session* session, NiFpga_Status* status);
//void read_FIFO_DMA(uint64_t* input, size_t size, NiFpga_Session* session, NiFpga_Status* status,size_t* elementsRemaining);
//void unpack_data(uint64_t* input, int16_t* AI0, int16_t* AI1, int16_t* AI2, uint16_t* ticks, size_t size);
//void read_FIFO_DMA_unpack(int16_t* AI0, int16_t* AI1, int16_t* AI2, uint16_t* ticks, size_t size, NiFpga_Session* session, NiFpga_Status* status,size_t* elementsRemaining);

// read analog inputs 
int16_t read_AI1(NiFpga_Session* session, NiFpga_Status* status);
int16_t read_AI1_Filtered(NiFpga_Session* session, NiFpga_Status* status);
int16_t read_AI2(NiFpga_Session* session, NiFpga_Status* status);
int16_t read_DeviceTemperature(NiFpga_Session* session, NiFpga_Status* status);
// reat piezo output created by PID
int16_t read_PiezoOut(NiFpga_Session* session, NiFpga_Status* status);


// set analog outputs
void set_PiezoOut(int16_t value, NiFpga_Session* session, NiFpga_Status* status);

//void set_DIO0(_Bool state, NiFpga_Session* session, NiFpga_Status* status);

//_Bool read_DIO12(NiFpga_Session* session, NiFpga_Status* status);

// ====== FIFO ===
size_t configure_FIFO_AI(size_t requestedDepth, NiFpga_Session* session, NiFpga_Status* status);
void start_FIFO_AI(NiFpga_Session* session, NiFpga_Status* status);
void stop_FIFO_AI(NiFpga_Session* session, NiFpga_Status* status);
void read_FIFO_AI(uint32_t* input, size_t size, NiFpga_Session* session, NiFpga_Status* status,size_t* elementsRemaining);
void unpack_data(uint32_t* input, int16_t* AI1, int16_t* AI2, size_t size);
void read_FIFO_AI_unpack(int16_t* AI1, int16_t* AI2, size_t size, NiFpga_Session* session, NiFpga_Status* status,size_t* elementsRemaining);

#endif /* FPGA_H_ */
