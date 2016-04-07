/*
 * Fpga.h
 *
 *  Created on: 08.10.2014
 *      Author: ehebestreit
 *  Edited on 13.01.2016 
 * 		Author JanGieseler
 */
 
#include "NiFpga_FPGA_read_ai_ao.h"
#include <stdio.h>

#ifndef FPGA_H_
#define FPGA_H_

void start_fpga(NiFpga_Session* session, NiFpga_Status* status);
void stop_fpga(NiFpga_Session* session, NiFpga_Status* status);

//int16_t read_DeviceTemperature(NiFpga_Session* session, NiFpga_Status* status);

//uint16_t read_LoopTicks(NiFpga_Session* session, NiFpga_Status* status);
//void set_LoopTicks(uint16_t value, NiFpga_Session* session, NiFpga_Status* status);
//void set_FifoTimeout(int32_t value, NiFpga_Session* session, NiFpga_Status* status);

//size_t configure_FIFO_AI(size_t requestedDepth, NiFpga_Session* session, NiFpga_Status* status);
//void start_FIFO_AI(NiFpga_Session* session, NiFpga_Status* status);
//void stop_FIFO_AI(NiFpga_Session* session, NiFpga_Status* status);
//void read_FIFO_AI(uint64_t* input, size_t size, NiFpga_Session* session, NiFpga_Status* status,size_t* elementsRemaining);
//void unpack_data(uint64_t* input, int16_t* AI0, int16_t* AI1, int16_t* AI2, uint16_t* ticks, size_t size);
//void read_FIFO_AI_unpack(int16_t* AI0, int16_t* AI1, int16_t* AI2, uint16_t* ticks, size_t size, NiFpga_Session* session, NiFpga_Status* status,size_t* elementsRemaining);

int16_t read_AI0(NiFpga_Session* session, NiFpga_Status* status);
int16_t read_AI1(NiFpga_Session* session, NiFpga_Status* status);
int16_t read_AI2(NiFpga_Session* session, NiFpga_Status* status);
int16_t read_AI3(NiFpga_Session* session, NiFpga_Status* status);
int16_t read_AI4(NiFpga_Session* session, NiFpga_Status* status);
int16_t read_AI5(NiFpga_Session* session, NiFpga_Status* status);
int16_t read_AI6(NiFpga_Session* session, NiFpga_Status* status);
int16_t read_AI7(NiFpga_Session* session, NiFpga_Status* status);

void set_AO0(int16_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_AO1(int16_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_AO2(int16_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_AO3(int16_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_AO4(int16_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_AO5(int16_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_AO6(int16_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_AO7(int16_t value, NiFpga_Session* session, NiFpga_Status* status);

//void set_DIO0(_Bool state, NiFpga_Session* session, NiFpga_Status* status);

//_Bool read_DIO12(NiFpga_Session* session, NiFpga_Status* status);


#endif /* FPGA_H_ */
