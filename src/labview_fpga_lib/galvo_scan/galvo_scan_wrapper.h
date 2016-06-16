/*
 * Fpga.h
 *
 *  Created on: 08.10.2014
 *      Author: ehebestreit
 *  Edited on 13.01.2016 
 * 		Author JanGieseler
 */
 
#include "NiFpga_GalvoScan.h"
#include <stdio.h>


#ifndef FPGA_H_
#define FPGA_H_

void reset_fpga(NiFpga_Session* session, NiFpga_Status* status);
void start_fpga(NiFpga_Session* session, NiFpga_Status* status);
void stop_fpga(NiFpga_Session* session, NiFpga_Status* status);

// read times
uint32_t read_loop_time(NiFpga_Session* session, NiFpga_Status* status);
uint32_t read_DMA_elem_to_write(NiFpga_Session* session, NiFpga_Status* status);

// read logical indicators
//_Bool read_LoopRateLimitAcq(NiFpga_Session* session, NiFpga_Status* status);
_Bool read_Stop(NiFpga_Session* session, NiFpga_Status* status);
_Bool read_DMATimeOut(NiFpga_Session* session, NiFpga_Status* status);
_Bool read_output_valid(NiFpga_Session* session, NiFpga_Status* status);

// set logical values
void set_acquire(_Bool state, NiFpga_Session* session, NiFpga_Status* status);
_Bool read_acquire(NiFpga_Session* session, NiFpga_Status* status);
_Bool read_running(NiFpga_Session* session, NiFpga_Status* status);
void set_abort(_Bool state, NiFpga_Session* session, NiFpga_Status* status);
_Bool read_abort(NiFpga_Session* session, NiFpga_Status* status);

// set/read parameters
void set_Nx(int16_t value, NiFpga_Session* session, NiFpga_Status* status);
int16_t read_Nx(NiFpga_Session* session, NiFpga_Status* status);
void set_Vmin_x(int16_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_dVmin_x(int16_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_Ny(int16_t value, NiFpga_Session* session, NiFpga_Status* status);
int16_t read_Ny(NiFpga_Session* session, NiFpga_Status* status);
void set_Vmin_y(int16_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_dVmin_y(int16_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_scanmode_x(uint8_t value, NiFpga_Session* session, NiFpga_Status* status);
void set_scanmode_y(uint8_t state, NiFpga_Session* session, NiFpga_Status* status);
void set_detector_mode(uint8_t state, NiFpga_Session* session, NiFpga_Status* status);
void set_settle_time(uint16_t value, NiFpga_Session* session, NiFpga_Status* status);
uint16_t read_settle_time(NiFpga_Session* session, NiFpga_Status* status);
void set_meas_per_pt(uint16_t value, NiFpga_Session* session, NiFpga_Status* status);
uint16_t read_meas_per_pt(NiFpga_Session* session, NiFpga_Status* status);
void set_piezo_voltage(int16_t value, NiFpga_Session* session, NiFpga_Status* status);
int16_t read_piezo_voltage(NiFpga_Session* session, NiFpga_Status* status);
// read parameters
int32_t read_i(NiFpga_Session* session, NiFpga_Status* status);
int32_t read_elements_written_to_dma(NiFpga_Session* session, NiFpga_Status* status);
int32_t read_detector_signal(NiFpga_Session* session, NiFpga_Status* status);
int32_t read_ix(NiFpga_Session* session, NiFpga_Status* status);
int32_t read_iy(NiFpga_Session* session, NiFpga_Status* status);
int32_t read_failed(NiFpga_Session* session, NiFpga_Status* status)

// set analog outputs
//_Bool read_DIO12(NiFpga_Session* session, NiFpga_Status* status);

// ====== FIFO ===
size_t configure_FIFO(size_t requestedDepth, NiFpga_Session* session, NiFpga_Status* status);
void start_FIFO(NiFpga_Session* session, NiFpga_Status* status);
void stop_FIFO(NiFpga_Session* session, NiFpga_Status* status);
void read_FIFO(uint32_t* input, size_t size, NiFpga_Session* session, NiFpga_Status* status,size_t* elementsRemaining);

#endif /* FPGA_H_ */
