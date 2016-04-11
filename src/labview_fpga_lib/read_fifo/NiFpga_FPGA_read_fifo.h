/*
 * Generated with the FPGA Interface C API Generator 15.0.0
 * for NI-RIO 15.0.0 or later.
 */

#ifndef __NiFpga_FPGA_read_fifo_h__
#define __NiFpga_FPGA_read_fifo_h__

#ifndef NiFpga_Version
   #define NiFpga_Version 1500
#endif

#include "NiFpga.h"

/**
 * The filename of the FPGA bitfile.
 *
 * This is a #define to allow for string literal concatenation. For example:
 *
 *    static const char* const Bitfile = "C:\\" NiFpga_FPGA_read_fifo_Bitfile;
 */
//#define NiFpga_FPGA_read_fifo_Bitfile "NiFpga_FPGA_read_fifo.lvbitx"
#define NiFpga_FPGA_read_fifo_Bitfile "C:\\Users\\Experiment\\PycharmProjects\\PythonLab\\src\\labview_fpga_lib\\read_fifo\\NiFpga_FPGA_read_fifo.lvbitx" 

/**
 * The signature of the FPGA bitfile.
 */
static const char* const NiFpga_FPGA_read_fifo_Signature = "40A41B56195E4BFCDBCFDB40E0214B2B";

typedef enum
{
   NiFpga_FPGA_read_fifo_IndicatorBool_DMAtimeout = 0x12,
   NiFpga_FPGA_read_fifo_IndicatorBool_TimedOutacquisition = 0x3E,
   NiFpga_FPGA_read_fifo_IndicatorBool_loopratelimitacquisition = 0x1E,
} NiFpga_FPGA_read_fifo_IndicatorBool;

typedef enum
{
   NiFpga_FPGA_read_fifo_IndicatorI16_AI0raw = 0x2A,
   NiFpga_FPGA_read_fifo_IndicatorI16_AI1raw = 0x2E,
} NiFpga_FPGA_read_fifo_IndicatorI16;

typedef enum
{
   NiFpga_FPGA_read_fifo_IndicatorI32_DMAloop = 0x14,
   NiFpga_FPGA_read_fifo_IndicatorI32_Numeric = 0x40,
   NiFpga_FPGA_read_fifo_IndicatorI32_elemetswrittenAcq = 0x30,
} NiFpga_FPGA_read_fifo_IndicatorI32;

typedef enum
{
   NiFpga_FPGA_read_fifo_IndicatorU32_looptimeacqticks = 0x24,
} NiFpga_FPGA_read_fifo_IndicatorU32;

typedef enum
{
   NiFpga_FPGA_read_fifo_ControlBool_acquiredatafast = 0x3A,
   NiFpga_FPGA_read_fifo_ControlBool_stop = 0x1A,
} NiFpga_FPGA_read_fifo_ControlBool;

typedef enum
{
   NiFpga_FPGA_read_fifo_ControlI32_elemetstowriteAcq = 0x34,
} NiFpga_FPGA_read_fifo_ControlI32;

typedef enum
{
   NiFpga_FPGA_read_fifo_ControlU32_sampleperiodacquisitionticks = 0x20,
} NiFpga_FPGA_read_fifo_ControlU32;

typedef enum
{
   NiFpga_FPGA_read_fifo_TargetToHostFifoU32_DMA = 0,
} NiFpga_FPGA_read_fifo_TargetToHostFifoU32;

#endif
