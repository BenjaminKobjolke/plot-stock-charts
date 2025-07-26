@echo off
echo Stock Chart Plotter
echo ==================
echo.
echo Usage: run.bat input.csv EXCHANGE_CODE
echo Example: run.bat input.csv XETR
echo.

if "%1"=="" (
    echo Error: Please provide input CSV file
    echo Usage: run.bat input.csv EXCHANGE_CODE
    pause
    exit /b 1
)

if "%2"=="" (
    echo Error: Please provide exchange code
    echo Usage: run.bat input.csv EXCHANGE_CODE
    echo Example: run.bat input.csv XETR
    pause
    exit /b 1
)

echo Running Stock Chart Plotter...
echo Input file: %1
echo Exchange: %2
echo.

call python main.py --input %1 --exchange %2 --days 1  --indicators "ema_50|red,ema_200|#00FF00"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error occurred while running the application.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Application completed successfully.
pause
