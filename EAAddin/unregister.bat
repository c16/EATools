@echo off
REM Unregistration script for EA Doc Generator Addin

echo EA Doc Generator Addin - Unregistration
echo =======================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Please right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Removing registry entries...
echo.

REM Remove EA addin registry entries (both 32-bit and 64-bit)
reg delete "HKEY_CURRENT_USER\Software\Sparx Systems\EAAddins\EADocGenerator" /f 2>nul
reg delete "HKEY_CURRENT_USER\Software\Sparx Systems\EAAddins64\EADocGenerator" /f 2>nul

echo.
echo Unregistering COM component...
echo.

REM Check if DLL exists
if exist "bin\x64\Release\EADocGenerator.dll" (
    "%WINDIR%\Microsoft.NET\Framework\v4.0.30319\RegAsm.exe" "bin\x64\Release\EADocGenerator.dll" /unregister

    if exist "%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\RegAsm.exe" (
        "%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\RegAsm.exe" "bin\x64\Release\EADocGenerator.dll" /unregister
    )
)

echo.
echo =======================================
echo UNREGISTRATION COMPLETE!
echo =======================================
echo.
echo The EA Doc Generator addin has been unregistered.
echo Please restart Enterprise Architect.
echo.
pause
