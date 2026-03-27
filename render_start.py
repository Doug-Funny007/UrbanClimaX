import os
import sys
from pathlib import Path
import streamlit.web.cli as stcli

ROOT = Path(__file__).resolve().parent
APP = ROOT / 'app.py'
PORT = os.environ.get('PORT', '10000')

if __name__ == '__main__':
    sys.argv = [
        'streamlit', 'run', str(APP),
        '--server.headless=true',
        '--server.address=0.0.0.0',
        f'--server.port={PORT}',
        '--browser.gatherUsageStats=false',
        '--server.maxUploadSize=2048',
    ]
    raise SystemExit(stcli.main())
