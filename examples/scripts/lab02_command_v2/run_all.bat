@echo off
setlocal
cd /d "%~dp0\..\..\.."
if defined PYTHON (set "PYTHON_CMD=%PYTHON%") else (set "PYTHON_CMD=python")
%PYTHON_CMD% -m examples.scripts.lab02_command_v2.step_01_build_validate %*
if errorlevel 1 exit /b 1
%PYTHON_CMD% -m examples.scripts.lab02_command_v2.step_02_publish %*
if errorlevel 1 exit /b 1
echo Lab 02 summary: all steps passed.