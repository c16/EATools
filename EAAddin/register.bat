@echo off
REM Registration script for EA Doc Generator Addin
REM This script registers the addin DLL with Windows and adds registry entries for EA

echo EA Doc Generator Addin - Registration
echo =====================================
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

REM Check if DLL exists
if not exist "bin\x64\Release\EADocGenerator.dll" (
    echo ERROR: EADocGenerator.dll not found!
    echo Please build the project first by running build.bat
    echo.
    pause
    exit /b 1
)

echo Unblocking DLL file (in case Windows blocked it)...
powershell -Command "Unblock-File -Path 'bin\x64\Release\EADocGenerator.dll'" 2>nul
echo.

echo Registering COM component (64-bit for EA 17)...
echo.

REM Register with 64-bit regasm for EA 17 (64-bit only)
"%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\RegAsm.exe" "bin\x64\Release\EADocGenerator.dll" /codebase

if errorlevel 1 goto TRY_32BIT
goto REGISTRATION_OK

:TRY_32BIT
echo.
echo 64-bit registration failed. Trying 32-bit registration as fallback...
"%WINDIR%\Microsoft.NET\Framework\v4.0.30319\RegAsm.exe" "bin\x64\Release\EADocGenerator.dll" /codebase
if errorlevel 1 goto REGISTRATION_FAILED
goto REGISTRATION_OK

:REGISTRATION_FAILED
echo.
echo ERROR: Both 32-bit and 64-bit registration failed!
pause
exit /b 1

:REGISTRATION_OK
echo.
echo Registration successful!
echo.

echo.
echo Adding EA addin registry entries...
echo.

REM Add registry entry for EA 64-bit to load the addin
REM For EA 64-bit, use EAAddins64 key with ProgId as default value
reg add "HKEY_CURRENT_USER\Software\Sparx Systems\EAAddins64\EADocGenerator" /ve /t REG_SZ /d "EADocGenerator.EADocGeneratorAddin" /f

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to add registry entry!
    echo.
    pause
    exit /b %errorlevel%
)

echo.
echo =====================================
echo REGISTRATION SUCCESSFUL!
echo =====================================
echo.
echo The EA Doc Generator addin has been registered.
echo.
echo Next steps:
echo 1. Close Enterprise Architect if it's running
echo 2. Start Enterprise Architect
echo 3. Look for "EA Doc Generator" in the Extensions menu
echo.
echo If you don't see the menu:
echo - Go to Extensions ^> Add-Ins...
echo - Find "EADocGenerator" in the list
echo - Check the box to enable it
echo.
pause
