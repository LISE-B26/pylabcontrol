/*
 * Generated with the FPGA Interface C API Generator 15.0.0
 * for NI-RIO 15.0.0 or later.
 */

#ifndef __NiFpga_GalvoScan_h__
#define __NiFpga_GalvoScan_h__

#ifndef NiFpga_Version
   #define NiFpga_Version 1500
#endif

#include "NiFpga.h"

/**
 * The filename of the FPGA bitfile.
 *
 * This is a #define to allow for string literal concatenation. For example:
 *
 *    static const char* const Bitfile = "C:\\" NiFpga_GalvoScan_Bitfile;
 */
#define NiFpga_GalvoScan_Bitfile "C:\\Users\\Experiment\\PycharmProjects\\PythonLab\\src\\labview_fpga_lib\\galvo_scan\\NiFpga_GalvoScan.lvbitx" 

/**
 * The signature of the FPGA bitfile.
 */
static const char* const NiFpga_GalvoScan_Signature = "27E416A745105EDA0C100E7662417CE9";

typedef enum
{
   NiFpga_GalvoScan_IndicatorBool_DMAtimeout = 0x5A,
   NiFpga_GalvoScan_IndicatorBool_outputvalid = 0x1A,
   NiFpga_GalvoScan_IndicatorBool_running = 0x42,
} NiFpga_GalvoScan_IndicatorBool;

typedef enum
{
   NiFpga_GalvoScan_IndicatorI32_Detectorsignal = 0x14,
   NiFpga_GalvoScan_IndicatorI32_datasenttoDMA = 0x54,
   NiFpga_GalvoScan_IndicatorI32_failed = 0x24,
   NiFpga_GalvoScan_IndicatorI32_i = 0x38,
   NiFpga_GalvoScan_IndicatorI32_ix = 0x44,
   NiFpga_GalvoScan_IndicatorI32_iy = 0x48,
   NiFpga_GalvoScan_IndicatorI32_number_pts_to_acquire = 0x20,
} NiFpga_GalvoScan_IndicatorI32;

typedef enum
{
   NiFpga_GalvoScan_IndicatorU32_DMA_elem_to_write = 0x28,
   NiFpga_GalvoScan_IndicatorU32_loop_time = 0x2C,
} NiFpga_GalvoScan_IndicatorU32;

typedef enum
{
   NiFpga_GalvoScan_ControlBool_abort = 0x12,
   NiFpga_GalvoScan_ControlBool_acquire = 0x52,
   NiFpga_GalvoScan_ControlBool_stopfpga = 0x3E,
} NiFpga_GalvoScan_ControlBool;

typedef enum
{
   NiFpga_GalvoScan_ControlU8_detector_mode = 0x36,
   NiFpga_GalvoScan_ControlU8_scanmodex = 0x7A,
   NiFpga_GalvoScan_ControlU8_scanmodey = 0x4E,
} NiFpga_GalvoScan_ControlU8;

typedef enum
{
   NiFpga_GalvoScan_ControlI16_Connector1AO2 = 0x1E,
   NiFpga_GalvoScan_ControlI16_N_x = 0x66,
   NiFpga_GalvoScan_ControlI16_N_y = 0x62,
   NiFpga_GalvoScan_ControlI16_Vmin_x = 0x6E,
   NiFpga_GalvoScan_ControlI16_Vmin_y = 0x72,
   NiFpga_GalvoScan_ControlI16_dVmin_x = 0x6A,
   NiFpga_GalvoScan_ControlI16_dVmin_y = 0x76,
} NiFpga_GalvoScan_ControlI16;

typedef enum
{
   NiFpga_GalvoScan_ControlU16_measurements_per_pt = 0x32,
   NiFpga_GalvoScan_ControlU16_settle_time_us = 0x5E,
} NiFpga_GalvoScan_ControlU16;

typedef enum
{
   NiFpga_GalvoScan_TargetToHostFifoI32_DMA = 0,
} NiFpga_GalvoScan_TargetToHostFifoI32;

#endif
