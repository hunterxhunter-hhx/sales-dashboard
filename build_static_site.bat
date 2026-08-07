@echo off
setlocal
cd /d "%~dp0"

if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
  "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" build_static_site.py
) else (
  py build_static_site.py
)

echo.
echo Static files are in: %cd%\dist
pause
