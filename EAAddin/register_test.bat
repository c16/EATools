@echo off
echo Registering Test Addin...
echo.

"%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\RegAsm.exe" "bin\x64\Release\EADocGenerator.dll" /codebase

set DLL_PATH=%CD%\bin\x64\Release\EADocGenerator.dll

reg add "HKEY_CURRENT_USER\Software\Sparx Systems\EAAddins\TestAddin" /v "Location" /t REG_SZ /d "%DLL_PATH%" /f

echo.
echo Test addin registered!
echo Restart EA and look for "Test Menu"
echo.
pause
