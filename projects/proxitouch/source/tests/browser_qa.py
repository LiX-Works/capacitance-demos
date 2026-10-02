"""Run the maintained collection browser suite."""
from pathlib import Path
import subprocess,sys
collection=Path(__file__).resolve().parents[4]
subprocess.run([sys.executable,str(collection/'scripts/browser_qa.py')],cwd=collection,check=True)
