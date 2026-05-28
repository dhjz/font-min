@echo off
cd /d "%~dp0"
echo ========================================
echo Start building Windows executable
echo ========================================

if not exist ".\dist" mkdir .\dist

echo.
echo [1/3] Cleaning old build files...
if exist "build" rmdir /s /q build
if exist ".\dist\dfont.exe" del /f /q ".\dist\dfont.exe"

echo.
echo [2/3] Building with PyInstaller...
uv run pyinstaller --onefile --clean --name dfont --distpath ./dist --add-data "../web;web" ../main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Build failed! Please check error messages.
    pause
    exit /b 1
)

echo.
echo [3/3] Cleaning temporary files...
if exist "build" rmdir /s /q build

echo.
echo ========================================
echo Build completed!
echo Executable location: .\dist\dfont.exe
echo ========================================

pause
