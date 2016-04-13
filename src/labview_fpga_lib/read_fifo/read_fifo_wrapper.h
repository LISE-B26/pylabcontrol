/*
 * Fpga.h
 *
 *  Created on: 08.10.2014
 *      Author: ehebestreit
 *  Edited on 13.01.2016 
 * 		Author JanGieseler
 */
 
#include "./read_fifo/NiFpga_read_fifo.h"
#include <stdio.h>


#ifndef FPGA_H_
#define FPGA_H_


void start_fpga(NiFpga_Session* session, NiFpga_Status* status);
void stop_fpga(NiFpga_Session* session, NiFpga_Status* status);

// read times
uint32_t read_LoopTimeAcq(NiFpga_Session* session, NiFpga_Status* status);


// read logical indicators
_Bool read_LoopRateLimitAcq(NiFpga_Session* session, NiFpga_Status* status);
_Bool read_TimeOutAcq(NiFpga_Session* session, NiFpga_Status* status);
_Bool read_AcquireData(NiFpga_Session* session, NiFpga_Status* status);
_Bool read_FPGARunning(NiFpga_Session* session, NiFpga_Status* status);
_Bool read_DMATimeOut(NiFpga_Session* session, NiFpga_Status* status);

// set logical values
void set_AcquireData(_Bool state, NiFpga_Session* session, NiFpga_Status* status); 
void set_Stop(_Bool state, NiFpga_Session* session, NiFpga_Status* status);

// set parameters
void set_SamplePeriodsAcq(uint32_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_ElementsToWrite(int32_t value, NiFpga_Session* session, NiFpga_Status* status);


// read parameters
int32_t read_ElementsWritten(NiFpga_Session* session, NiFpga_Status* status);


// read analog inputs 
int16_t read_AI0(NiFpga_Session* session, NiFpga_Status* status);
int16_t read_AI1(NiFpga_Session* session, NiFpga_Status* status);


// set analog outputs

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
