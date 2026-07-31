@echo off
setlocal
cd /d "%~dp0\..\..\.."
if defined PYTHON (set "PYTHON_CMD=%PYTHON%") else (set "PYTHON_CMD=python")
%PYTHON_CMD% -m examples.scripts.lab04_retained_metadata.step_01_connect_topics %*
if errorlevel 1 exit /b 1
%PYTHON_CMD% -m examples.scripts.lab04_retained_metadata.step_02_read_validate %*
if errorlevel 1 exit /b 1
echo Lab 04 summary: all steps passed.