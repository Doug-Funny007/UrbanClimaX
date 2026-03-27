@echo off
setlocal
cd /d "%~dp0"

if not exist .venv (
    py -3.11 -m venv .venv 2>nul
    if errorlevel 1 (
        py -3.10 -m venv .venv 2>nul
    )
    if errorlevel 1 (
        python -m venv .venv
    )
)

call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller

pyinstaller ^
  --noconfirm ^
  --clean ^
  --name UrbanClimaX_RSEI ^
  --add-data "assets\logo.png;assets" ^
  start_urbanclimax.py

echo.
echo Executavel gerado em: dist\UrbanClimaX_RSEI\
pause
endlocal
