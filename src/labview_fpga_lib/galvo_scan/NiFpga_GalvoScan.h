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
//#define NiFpga_GalvoScan_Bitfile "NiFpga_GalvoScan.lvbitx"
#define NiFpga_GalvoScan_Bitfile "C:\\Users\\Experiment\\PycharmProjects\\PythonLab\\src\\labview_fpga_lib\\galvo_scan\\NiFpga_GalvoScan.lvbitx" 
/**
 * The signature of the FPGA bitfile.
 */
static const char* const NiFpga_GalvoScan_Signature = "4EB4C8250C6C57AE94BBF51B91F9F0A6";

typedef enum
{
   NiFpga_GalvoScan_IndicatorBool_DMAtimeout = 0x2E,
} NiFpga_GalvoScan_IndicatorBool;

typedef enum
{
   NiFpga_GalvoScan_IndicatorI16_Detectorsignal = 0x32,
   NiFpga_GalvoScan_IndicatorI16_datasenttoDMA = 0x2A,
} NiFpga_GalvoScan_IndicatorI16;

typedef enum
{
   NiFpga_GalvoScan_IndicatorI32_ix = 0x14,
   NiFpga_GalvoScan_IndicatorI32_iy = 0x18,
} NiFpga_GalvoScan_IndicatorI32;

typedef enum
{
   NiFpga_GalvoScan_IndicatorU32_TickCount = 0x20,
} NiFpga_GalvoScan_IndicatorU32;

typedef enum
{
   NiFpga_GalvoScan_ControlBool_acquire = 0x26,
} NiFpga_GalvoScan_ControlBool;

typedef enum
{
   NiFpga_GalvoScan_ControlU8_scanmodex = 0x52,
   NiFpga_GalvoScan_ControlU8_scanmodey = 0x1E,
} NiFpga_GalvoScan_ControlU8;

typedef enum
{
   NiFpga_GalvoScan_ControlI16_N_x = 0x3E,
   NiFpga_GalvoScan_ControlI16_N_y = 0x3A,
   NiFpga_GalvoScan_ControlI16_Vmin_x = 0x46,
   NiFpga_GalvoScan_ControlI16_Vmin_y = 0x4A,
   NiFpga_GalvoScan_ControlI16_dVmin_x = 0x42,
   NiFpga_GalvoScan_ControlI16_dVmin_y = 0x4E,
} NiFpga_GalvoScan_ControlI16;

typedef enum
{
   NiFpga_GalvoScan_ControlU32_settletimeCountTicks = 0x10,
   NiFpga_GalvoScan_ControlU32_time_per_pt = 0x34,
} NiFpga_GalvoScan_ControlU32;

typedef enum
{
   NiFpga_GalvoScan_TargetToHostFifoI16_DMA = 0,
} NiFpga_GalvoScan_TargetToHostFifoI16;

#endif
