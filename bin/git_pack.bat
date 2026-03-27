@echo off
cd /d "%~dp0\.."
echo ========================================
echo Packing project to zip
echo ========================================

if not exist "bin\dist" mkdir bin\dist

echo.
echo Generating timestamp...
for /f "tokens=2 delims==" %%a in ('wmic os get localdatetime /value') do set datetime=%%a
set filename=ypxq-generate-qa_%datetime:~0,12%.zip

echo Creating %filename%...
git archive -o bin\dist\%filename% HEAD

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Pack failed! Please check error messages.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Pack completed!
echo File location: bin\dist\%filename%
echo ========================================

pause
