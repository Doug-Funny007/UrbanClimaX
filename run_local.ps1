Set-Location $PSScriptRoot

if (-not (Test-Path ".venv")) {
    try { py -3.11 -m venv .venv } catch {
        try { py -3.10 -m venv .venv } catch {
            python -m venv .venv
        }
    }
}

.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python .\start_urbanclimax.py
