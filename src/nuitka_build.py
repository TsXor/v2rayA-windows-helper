# For some unknown reason, executing nuitka command will stop a batch script.

import os, subprocess
from pathlib import Path

NUITKA = ['python', '-m', 'nuitka']

dp0 = Path(__file__).parent
os.chdir(dp0)

subprocess.run([*NUITKA, '--standalone', '--nofollow-import-to=numpy', 'open_webview.py'])
subprocess.run([*NUITKA, '--standalone', '--nofollow-import-to=numpy', '--nofollow-import-to=PIL', '--disable-console', 'helper.py'])