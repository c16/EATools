@echo off
echo Registering Test Addin...
echo.

"%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\RegAsm.exe" "bin\x64\Release\EADocGenerator.dll" /codebase

REM For EA 64-bit, use EAAddins64 key with ProgId format
reg add "HKEY_CURRENT_USER\Software\Sparx Systems\EAAddins64\TestAddin" /ve /t REG_SZ /d "EADocGenerator.TestAddin" /f

echo.
echo Test addin registered!
echo Restart EA and look for "Test Menu"
echo.
pause
