"""Verify a fresh copy can build using only the included compiler archive."""
from pathlib import Path
import tempfile,shutil,subprocess,hashlib,json,sys
R=Path(__file__).resolve().parents[2];out=R/'qa/rebuild';out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='proxitouch-r3-clean-') as t:
 d=Path(t)/'ProxiTouch_R3';d.mkdir()
 shutil.copytree(R/'source',d/'source',ignore=shutil.ignore_patterns('node_modules','__pycache__','*.pyc'))
 shutil.copytree(R/'tools',d/'tools');shutil.copytree(R/'revision-spec',d/'revision-spec');(d/'docs/r3').mkdir(parents=True)
 shutil.copy2(R/'docs/r3/R2_BASELINE.json',d/'docs/r3/R2_BASELINE.json');(d/'qa').mkdir();(d/'package.json').write_text('{"type":"module"}')
 checks=[];log=[]
 for command in [['npm','run','setup:offline'],['npm','run','check'],['npm','test']]:
  result=subprocess.run(command,cwd=d/'source',capture_output=True,text=True);log.append('$ '+' '.join(command)+'\n'+result.stdout+result.stderr);checks.append({'command':command,'exitCode':result.returncode});
  if result.returncode:break
 (out/'clean-build.log').write_text('\n'.join(log))
 built=d/'dist/ProxiTouch-offline.html';same=built.exists() and sha(built)==sha(R/'dist/ProxiTouch-offline.html')
 before=sha(d/'source/src/scenes/copy.ts');imported=subprocess.run([sys.executable,'scripts/import_revision_copy.py'],cwd=d/'source',capture_output=True,text=True);after=sha(d/'source/src/scenes/copy.ts')
 report={'sourceSha256':sha(R/'dist/ProxiTouch-offline.html'),'startedWithoutNodeModules':True,'compilerFromIncludedTar':True,'commands':checks,'rebuiltHTMLSha256':sha(built) if built.exists() else None,'offlineHTMLByteIdentical':same,'copyImportExitCode':imported.returncode,'copyImportByteIdentical':before==after,'copyImportLog':imported.stdout+imported.stderr,'scope':'Node offline build on this Linux runtime; not a claim of Windows/Mac browser verification.'}
 (out/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
 if not same or imported.returncode or any(c['exitCode'] for c in checks):sys.exit(1)
