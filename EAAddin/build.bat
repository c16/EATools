@echo off
REM Build script for EA Doc Generator Addin
REM This script builds the C# project using MSBuild

echo Building EA Doc Generator Addin...
echo.

REM Try to find MSBuild in common locations
set MSBUILD_PATH=""

REM Visual Studio 2022
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" (
    set MSBUILD_PATH="C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
)
if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe" (
    set MSBUILD_PATH="C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe"
)
if exist "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\MSBuild\Current\Bin\MSBuild.exe" (
    set MSBUILD_PATH="C:\Program Files\Microsoft Visual Studio\2022\Enterprise\MSBuild\Current\Bin\MSBuild.exe"
)

REM Visual Studio 2019
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe" (
    set MSBUILD_PATH="C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe"
)
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\MSBuild.exe" (
    set MSBUILD_PATH="C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\MSBuild.exe"
)
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\MSBuild\Current\Bin\MSBuild.exe" (
    set MSBUILD_PATH="C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\MSBuild\Current\Bin\MSBuild.exe"
)

REM Visual Studio 2017
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\MSBuild\15.0\Bin\MSBuild.exe" (
    set MSBUILD_PATH="C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\MSBuild\15.0\Bin\MSBuild.exe"
)

if %MSBUILD_PATH%=="" (
    echo ERROR: MSBuild not found!
    echo Please install Visual Studio or the .NET Framework SDK
    echo.
    pause
    exit /b 1
)

echo Found MSBuild at: %MSBUILD_PATH%
echo.

REM Build the project
%MSBUILD_PATH% EADocGenerator.csproj /p:Configuration=Release /p:Platform="Any CPU" /t:Rebuild

if %errorlevel% neq 0 (
    echo.
    echo BUILD FAILED!
    echo.
    pause
    exit /b %errorlevel%
)

echo.
echo BUILD SUCCESSFUL!
echo.
echo Output: bin\Release\EADocGenerator.dll
echo.
echo Next steps:
echo 1. Run register.bat to register the addin with EA
echo 2. Restart Enterprise Architect
echo 3. Look for "EA Doc Generator" in the Extensions menu
echo.
pause
