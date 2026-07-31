@echo off
setlocal
cd /d "%~dp0\..\..\.."
if defined PYTHON (set "PYTHON_CMD=%PYTHON%") else (set "PYTHON_CMD=python")
%PYTHON_CMD% -m examples.scripts.lab01_telemetry_subscribe.step_01_connect %*
if errorlevel 1 exit /b 1
%PYTHON_CMD% -m examples.scripts.lab01_telemetry_subscribe.step_02_subscribe_validate %*
if errorlevel 1 exit /b 1
echo Lab 01 summary: all steps passed.