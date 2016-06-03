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
#define NiFpga_GalvoScan_Bitfile "NiFpga_GalvoScan.lvbitx"

/**
 * The signature of the FPGA bitfile.
 */
static const char* const NiFpga_GalvoScan_Signature = "F470330F4C7B67D3EAB84098F69656AF";

typedef enum
{
   NiFpga_GalvoScan_IndicatorBool_DMAtimeout = 0x1E,
   NiFpga_GalvoScan_IndicatorBool_loopratelimitacquisition = 0x1A,
} NiFpga_GalvoScan_IndicatorBool;

typedef enum
{
   NiFpga_GalvoScan_IndicatorI16_Detectorsignal = 0x26,
   NiFpga_GalvoScan_IndicatorI16_datasenttoDMA = 0x16,
} NiFpga_GalvoScan_IndicatorI16;

typedef enum
{
   NiFpga_GalvoScan_ControlBool_forwardy = 0x46,
   NiFpga_GalvoScan_ControlBool_stop = 0x22,
} NiFpga_GalvoScan_ControlBool;

typedef enum
{
   NiFpga_GalvoScan_ControlU8_scanmode = 0x4A,
} NiFpga_GalvoScan_ControlU8;

typedef enum
{
   NiFpga_GalvoScan_ControlI16_N_x = 0x32,
   NiFpga_GalvoScan_ControlI16_N_y = 0x2E,
   NiFpga_GalvoScan_ControlI16_Vmin_x = 0x3A,
   NiFpga_GalvoScan_ControlI16_Vmin_y = 0x3E,
   NiFpga_GalvoScan_ControlI16_dVmin_x = 0x36,
   NiFpga_GalvoScan_ControlI16_dVmin_y = 0x42,
} NiFpga_GalvoScan_ControlI16;

typedef enum
{
   NiFpga_GalvoScan_ControlU32_looptimeCountTicks = 0x28,
   NiFpga_GalvoScan_ControlU32_settletimeCountTicks = 0x10,
} NiFpga_GalvoScan_ControlU32;

typedef enum
{
   NiFpga_GalvoScan_TargetToHostFifoI16_DMA = 0,
} NiFpga_GalvoScan_TargetToHostFifoI16;

#endif
