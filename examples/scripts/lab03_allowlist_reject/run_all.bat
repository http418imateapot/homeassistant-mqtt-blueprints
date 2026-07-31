@echo off
setlocal
cd /d "%~dp0\..\..\.."
if defined PYTHON (set "PYTHON_CMD=%PYTHON%") else (set "PYTHON_CMD=python")
%PYTHON_CMD% -m examples.scripts.lab03_allowlist_reject.step_01_build_scenarios %*
if errorlevel 1 exit /b 1
%PYTHON_CMD% -m examples.scripts.lab03_allowlist_reject.step_02_publish_observe %*
if errorlevel 1 exit /b 1
echo Lab 03 summary: all steps passed.