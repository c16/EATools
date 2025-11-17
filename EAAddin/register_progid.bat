@echo off
REM Alternative registration using ProgId
echo.
echo Registering with ProgId instead of custom name...
echo.

REM Get the full path to the DLL
set DLL_PATH=%CD%\bin\Release\EADocGenerator.dll

REM Try using the ProgId as the key name
reg add "HKEY_CURRENT_USER\Software\Sparx Systems\EAAddins\EADocGenerator.EADocGeneratorAddin" /v "Location" /t REG_SZ /d "%DLL_PATH%" /f

if %errorlevel% equ 0 (
    echo.
    echo Registry entry added with ProgId!
    echo Please restart EA and check again.
) else (
    echo ERROR: Failed to add registry entry
)

pause
