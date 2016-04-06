/*
 * Generated with the FPGA Interface C API Generator 15.0.0
 * for NI-RIO 15.0.0 or later.
 */

#ifndef __NiFpga_PID_Loop_Simple_h__
#define __NiFpga_PID_Loop_Simple_h__

#ifndef NiFpga_Version
   #define NiFpga_Version 1500
#endif

#include "NiFpga.h"

/**
 * The filename of the FPGA bitfile.
 *
 * This is a #define to allow for string literal concatenation. For example:
 *
 *    static const char* const Bitfile = "C:\\" NiFpga_PID_Loop_Simple_Bitfile;
 */
#define NiFpga_PID_Loop_Simple_Bitfile "NiFpga_PID_Loop_Simple.lvbitx"

/**
 * The signature of the FPGA bitfile.
 */
static const char* const NiFpga_PID_Loop_Simple_Signature = "B91D651A744935265D3BB75CC0B7C15C";

typedef enum
{
   NiFpga_PID_Loop_Simple_IndicatorBool_DMAtimeout = 0x5E,
   NiFpga_PID_Loop_Simple_IndicatorBool_FPGArunning = 0x12,
   NiFpga_PID_Loop_Simple_IndicatorBool_TimedOutacquisition = 0xA6,
   NiFpga_PID_Loop_Simple_IndicatorBool_loopratelimitPID = 0x66,
   NiFpga_PID_Loop_Simple_IndicatorBool_loopratelimitacquisition = 0x86,
   NiFpga_PID_Loop_Simple_IndicatorBool_outputvalid = 0x1A,
} NiFpga_PID_Loop_Simple_IndicatorBool;

typedef enum
{
   NiFpga_PID_Loop_Simple_IndicatorI16_AI1_filtered = 0x7A,
   NiFpga_PID_Loop_Simple_IndicatorI16_AI1raw = 0x92,
   NiFpga_PID_Loop_Simple_IndicatorI16_AI2raw = 0x96,
   NiFpga_PID_Loop_Simple_IndicatorI16_DeviceTemperature = 0x5A,
   NiFpga_PID_Loop_Simple_IndicatorI16_maxxy = 0x32,
   NiFpga_PID_Loop_Simple_IndicatorI16_mean = 0x1E,
   NiFpga_PID_Loop_Simple_IndicatorI16_minxy = 0x36,
   NiFpga_PID_Loop_Simple_IndicatorI16_reductionfactor = 0x2E,
} NiFpga_PID_Loop_Simple_IndicatorI16;

typedef enum
{
   NiFpga_PID_Loop_Simple_IndicatorU16_standarddeviation = 0x22,
} NiFpga_PID_Loop_Simple_IndicatorU16;

typedef enum
{
   NiFpga_PID_Loop_Simple_IndicatorI32_Numeric = 0xA8,
   NiFpga_PID_Loop_Simple_IndicatorI32_elementswrittenAcq = 0x98,
} NiFpga_PID_Loop_Simple_IndicatorI32;

typedef enum
{
   NiFpga_PID_Loop_Simple_IndicatorU32_acqtimeticks = 0x38,
   NiFpga_PID_Loop_Simple_IndicatorU32_looptimePIDticks = 0x6C,
   NiFpga_PID_Loop_Simple_IndicatorU32_looptimeacqticks = 0x8C,
} NiFpga_PID_Loop_Simple_IndicatorU32;

typedef enum
{
   NiFpga_PID_Loop_Simple_ControlBool_Lowpassactive = 0x82,
   NiFpga_PID_Loop_Simple_ControlBool_PIDactive = 0x7E,
   NiFpga_PID_Loop_Simple_ControlBool_acquiredata = 0xA2,
   NiFpga_PID_Loop_Simple_ControlBool_output10kHzSine = 0x16,
   NiFpga_PID_Loop_Simple_ControlBool_reset = 0x26,
   NiFpga_PID_Loop_Simple_ControlBool_stop = 0x62,
} NiFpga_PID_Loop_Simple_ControlBool;

typedef enum
{
   NiFpga_PID_Loop_Simple_ControlI16_PiezoOutAO0 = 0x72,
   NiFpga_PID_Loop_Simple_ControlI16_Setpoint = 0x76,
   NiFpga_PID_Loop_Simple_ControlI16_amplitudescalecoefficient = 0x2A,
} NiFpga_PID_Loop_Simple_ControlI16;

typedef enum
{
   NiFpga_PID_Loop_Simple_ControlI32_TimeoutBuffer = 0x3C,
   NiFpga_PID_Loop_Simple_ControlI32_elementstowriteAcq = 0x9C,
   NiFpga_PID_Loop_Simple_ControlI32_scaledcoefficient1 = 0x48,
   NiFpga_PID_Loop_Simple_ControlI32_scaledcoefficient2 = 0x44,
   NiFpga_PID_Loop_Simple_ControlI32_scaledcoefficient3 = 0x40,
} NiFpga_PID_Loop_Simple_ControlI32;

typedef enum
{
   NiFpga_PID_Loop_Simple_ControlU32_integralgain = 0x50,
   NiFpga_PID_Loop_Simple_ControlU32_proportionalgain = 0x54,
   NiFpga_PID_Loop_Simple_ControlU32_sampleperiodacquisitionticks = 0x88,
   NiFpga_PID_Loop_Simple_ControlU32_sampleperiodticksPID = 0x68,
} NiFpga_PID_Loop_Simple_ControlU32;

typedef enum
{
   NiFpga_PID_Loop_Simple_TargetToHostFifoU32_DMA = 0,
} NiFpga_PID_Loop_Simple_TargetToHostFifoU32;

#endif
