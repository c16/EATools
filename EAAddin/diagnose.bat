@echo off
echo EA Addin Diagnostics
echo =====================
echo.

echo 1. Checking if DLL exists...
if exist "bin\x64\Release\EADocGenerator.dll" (
    echo    FOUND: bin\x64\Release\EADocGenerator.dll
) else (
    echo    NOT FOUND: bin\x64\Release\EADocGenerator.dll
)
echo.

echo 2. Checking EA Addins registry...
reg query "HKEY_CURRENT_USER\Software\Sparx Systems\EAAddins" /s
echo.

echo 3. Checking COM registration (ProgId)...
reg query "HKEY_CLASSES_ROOT\EADocGenerator.EADocGeneratorAddin" 2>nul
if %errorlevel% equ 0 (
    echo    ProgId is registered
) else (
    echo    ProgId NOT registered
)
echo.

echo 4. Checking COM registration (CLSID)...
reg query "HKEY_CLASSES_ROOT\CLSID\{8A6C6AC1-8B5E-4F5D-9E3C-2A4B5C6D7E8F}" 2>nul
if %errorlevel% equ 0 (
    echo    CLSID is registered
    reg query "HKEY_CLASSES_ROOT\CLSID\{8A6C6AC1-8B5E-4F5D-9E3C-2A4B5C6D7E8F}" /s
) else (
    echo    CLSID NOT registered
)
echo.

echo 5. Checking file properties...
dir "bin\x64\Release\EADocGenerator.dll"
echo.

pause
