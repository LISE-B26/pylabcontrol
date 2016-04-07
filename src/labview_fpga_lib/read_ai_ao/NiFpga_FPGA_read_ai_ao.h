/*
 * Generated with the FPGA Interface C API Generator 15.0.0
 * for NI-RIO 15.0.0 or later.
 */

#ifndef __NiFpga_FPGA_read_ai_ao_h__
#define __NiFpga_FPGA_read_ai_ao_h__

#ifndef NiFpga_Version
   #define NiFpga_Version 1500
#endif

#include "NiFpga.h"

/**
 * The filename of the FPGA bitfile.
 *
 * This is a #define to allow for string literal concatenation. For example:
 *
 *    static const char* const Bitfile = "C:\\" NiFpga_FPGA_read_ai_ao_Bitfile;
 */
// #define NiFpga_FPGA_read_ai_ao_Bitfile "NiFpga_FPGA_read_ai_ao.lvbitx"
#define NiFpga_FPGA_read_ai_ao_Bitfile "../labview_fpga_lib/read_ai_ao/NiFpga_FPGA_read_ai_ao.lvbitx" 
/**
 * The signature of the FPGA bitfile.
 */
static const char* const NiFpga_FPGA_read_ai_ao_Signature = "C640294A8D331E43BEAF7008E4888BBE";

typedef enum
{
   NiFpga_FPGA_read_ai_ao_IndicatorI16_Connector1AI0 = 0x4E,
   NiFpga_FPGA_read_ai_ao_IndicatorI16_Connector1AI1 = 0x4A,
   NiFpga_FPGA_read_ai_ao_IndicatorI16_Connector1AI2 = 0x46,
   NiFpga_FPGA_read_ai_ao_IndicatorI16_Connector1AI3 = 0x42,
   NiFpga_FPGA_read_ai_ao_IndicatorI16_Connector1AI4 = 0x36,
   NiFpga_FPGA_read_ai_ao_IndicatorI16_Connector1AI5 = 0x3A,
   NiFpga_FPGA_read_ai_ao_IndicatorI16_Connector1AI6 = 0x3E,
   NiFpga_FPGA_read_ai_ao_IndicatorI16_Connector1AI7 = 0x12,
} NiFpga_FPGA_read_ai_ao_IndicatorI16;

typedef enum
{
   NiFpga_FPGA_read_ai_ao_ControlI16_Connector1AO0 = 0x32,
   NiFpga_FPGA_read_ai_ao_ControlI16_Connector1AO1 = 0x2E,
   NiFpga_FPGA_read_ai_ao_ControlI16_Connector1AO2 = 0x2A,
   NiFpga_FPGA_read_ai_ao_ControlI16_Connector1AO3 = 0x26,
   NiFpga_FPGA_read_ai_ao_ControlI16_Connector1AO4 = 0x22,
   NiFpga_FPGA_read_ai_ao_ControlI16_Connector1AO5 = 0x1E,
   NiFpga_FPGA_read_ai_ao_ControlI16_Connector1AO6 = 0x1A,
   NiFpga_FPGA_read_ai_ao_ControlI16_Connector1AO7 = 0x16,
} NiFpga_FPGA_read_ai_ao_ControlI16;

#endif
