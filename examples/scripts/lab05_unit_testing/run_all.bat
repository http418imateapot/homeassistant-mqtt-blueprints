@echo off
setlocal
cd /d "%~dp0\..\..\.."
if defined PYTHON (set "PYTHON_CMD=%PYTHON%") else (set "PYTHON_CMD=python")
%PYTHON_CMD% -m examples.scripts.lab05_unit_testing.step_01_arrange_act_assert
if errorlevel 1 exit /b 1
%PYTHON_CMD% -m examples.scripts.lab05_unit_testing.step_02_run_suite
if errorlevel 1 exit /b 1
%PYTHON_CMD% -m examples.scripts.lab05_unit_testing.step_03_run_single_param
if errorlevel 1 exit /b 1
%PYTHON_CMD% -m examples.scripts.lab05_unit_testing.step_04_read_failure
if errorlevel 1 exit /b 1
echo Lab 05 summary: all steps passed.