@echo off
setlocal

cd /d "%~dp0"

set "ACTION=%~1"
if "%ACTION%"=="" set "ACTION=sim"

if /I "%ACTION%"=="sim" goto sim
if /I "%ACTION%"=="build" goto sim_build
if /I "%ACTION%"=="run" goto sim_run
if /I "%ACTION%"=="clean" goto clean
if /I "%ACTION%"=="vivado" goto vivado
if /I "%ACTION%"=="synth" goto synth
if /I "%ACTION%"=="bitstream" goto bitstream

echo [ERROR] Unknown action: %ACTION%
echo Usage: build.bat [sim^|build^|run^|clean^|vivado^|synth^|bitstream]
exit /b 1

:sim
pushd source-sc >nul
call build.bat
set "RC=%ERRORLEVEL%"
popd >nul
exit /b %RC%

:sim_build
pushd source-sc >nul
call build.bat build
set "RC=%ERRORLEVEL%"
popd >nul
exit /b %RC%

:sim_run
pushd source-sc >nul
call build.bat run
set "RC=%ERRORLEVEL%"
popd >nul
exit /b %RC%

:vivado
call :run_vivado_script scripts\create_vivado_project.tcl vivado\lab6_sid_sort_fpga\lab6_sid_sort_fpga.xpr
exit /b %ERRORLEVEL%

:synth
call :run_vivado_script scripts\run_synthesis_check.tcl vivado\lab6_sid_sort_fpga\lab6_sid_sort_fpga.runs\synth_1
exit /b %ERRORLEVEL%

:bitstream
call :run_vivado_script scripts\run_bitstream_check.tcl vivado\bitstream_check\lab6_sid_sort_fpga_top.bit
exit /b %ERRORLEVEL%

:run_vivado_script
set "SCRIPT=%~1"
set "EXPECT=%~2"

where vivado >nul 2>nul
if not errorlevel 1 (
    vivado -mode batch -source "%SCRIPT%"
    if exist "%EXPECT%" exit /b 0
    exit /b %ERRORLEVEL%
)

set "VIVADO_BAT="
for %%V in (
    "C:\Xilinx\2025.2.1\Vivado\bin\vivado.bat"
    "C:\Xilinx\2025.2\Vivado\bin\vivado.bat"
    "C:\Xilinx\Vivado\2024.2\bin\vivado.bat"
    "C:\Xilinx\Vivado\2024.1\bin\vivado.bat"
    "C:\Xilinx\Vivado\2023.2\bin\vivado.bat"
    "C:\Xilinx\Vivado\2023.1\bin\vivado.bat"
    "D:\Xilinx\2025.2.1\Vivado\bin\vivado.bat"
    "D:\Xilinx\2025.2\Vivado\bin\vivado.bat"
    "D:\Xilinx\Vivado\2024.2\bin\vivado.bat"
    "D:\Xilinx\Vivado\2024.1\bin\vivado.bat"
    "D:\Xilinx\Vivado\2023.2\bin\vivado.bat"
    "D:\Xilinx\Vivado\2023.1\bin\vivado.bat"
) do (
    if exist %%~V set "VIVADO_BAT=%%~V"
)

if defined VIVADO_BAT (
    call "%VIVADO_BAT%" -mode batch -source "%SCRIPT%"
    if exist "%EXPECT%" exit /b 0
    exit /b %ERRORLEVEL%
)

echo [ERROR] Cannot find Vivado.
echo Install Vivado, or run this command from "Vivado Tcl Shell".
echo If Vivado is installed in another path, add its bin directory to PATH first.
exit /b 1

:clean
pushd source-sc >nul
call build.bat clean
popd >nul
if exist *.log del /f /q *.log
if exist *.jou del /f /q *.jou
if exist dfx_runtime.txt del /f /q dfx_runtime.txt
echo [OK] Clean finished.
exit /b 0
