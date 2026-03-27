import os
import sys
from pathlib import Path
import streamlit.web.cli as stcli

ROOT = Path(__file__).resolve().parent
APP = ROOT / 'app.py'

if __name__ == '__main__':
    sys.argv = [
        'streamlit', 'run', str(APP),
        '--server.headless=false',
        '--browser.gatherUsageStats=false',
        '--server.maxUploadSize=2048',
    ]
    sys.exit(stcli.main())
