"""Refresh both maintained project galleries from actual current Chromium renders."""
import subprocess,sys
from browser_support import ROOT,NAMES
for name in NAMES:
    project=ROOT/'projects'/name
    subprocess.run([sys.executable,str(project/'source/tests/capture_previews.py')],cwd=project,check=True)
print('Both galleries rerendered. Run npm run build and npm test.',flush=True)
