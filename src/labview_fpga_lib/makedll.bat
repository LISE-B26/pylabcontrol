cls
@echo off

set folder=%1
set wrapper_file=%folder%_wrapper
set lib_file=%folder%.dll

REM ==== find the files we need for compilation =====
for /R .\%folder% %%F IN (NiFpg_FPGA*.c) do set NiFpga_file=%%~nF

echo ---- starting conversion ---
echo    NiFpga file: %NiFpga_file%.c
echo    Wrapper file: %wrapper_file%.c
echo    Lib file: %lib_file%
cd %folder%
call gcc -c %wrapper_file%.c %NiFpga_file%.c
call gcc -shared -o %lib_file% %wrapper_file%.o %NiFpga_file%.o

echo cleaning up ...
call del %wrapper_file%.o
call del %NiFpga_file%.o
IF EXIST %lib_file% echo %lib_file% successfully created !!

cd ..
goto:eof

:wrongfiletype
@echo this is not a .c file
:usage
@echo please provide a source .c file
@echo usage: %0 source.c

