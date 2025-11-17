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
if not exist "bin\Release\EADocGenerator.dll" (
    echo ERROR: EADocGenerator.dll not found!
    echo Please build the project first by running build.bat
    echo.
    pause
    exit /b 1
)

echo Unblocking DLL file (in case Windows blocked it)...
powershell -Command "Unblock-File -Path 'bin\Release\EADocGenerator.dll'"
echo.

echo Registering COM component (32-bit)...
echo.

REM Register the DLL with regasm (32-bit)
"%WINDIR%\Microsoft.NET\Framework\v4.0.30319\RegAsm.exe" "bin\Release\EADocGenerator.dll" /codebase /tlb

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to register COM component (32-bit)!
    echo.
    pause
    exit /b %errorlevel%
)

echo.
echo Registering COM component (64-bit)...
echo.

REM Also register with 64-bit regasm if it exists
if exist "%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\RegAsm.exe" (
    "%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\RegAsm.exe" "bin\Release\EADocGenerator.dll" /codebase /tlb
    if %errorlevel% neq 0 (
        echo WARNING: 64-bit registration failed, but 32-bit succeeded
    ) else (
        echo 64-bit registration succeeded
    )
)
echo.

echo.
echo Adding EA addin registry entries...
echo.

REM Get the full path to the DLL
set DLL_PATH=%CD%\bin\Release\EADocGenerator.dll

REM Add registry entry for EA to load the addin
reg add "HKEY_CURRENT_USER\Software\Sparx Systems\EAAddins\EADocGenerator" /v "Location" /t REG_SZ /d "%DLL_PATH%" /f

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
