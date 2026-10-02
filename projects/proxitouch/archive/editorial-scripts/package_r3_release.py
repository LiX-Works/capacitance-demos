"""Package the already-tested R3 snapshot, with integrity verification."""
from pathlib import Path
import hashlib, json, shutil, zipfile
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((ROOT/'qa/RELEASE_SUMMARY.json').read_text())['sourceSha256']
assert sha(ROOT/'dist/ProxiTouch-offline.html')==freeze

def included(p):
 rel=p.relative_to(ROOT)
 if any(x in ('node_modules','__pycache__','.git') for x in rel.parts):return False
 if p.name in ('.DS_Store','BUILD_MANIFEST.json'):return False
 if p.suffix.lower() in ('.pyc','.pyo','.ttf','.otf','.woff','.woff2','.eot'):return False
 return p.is_file()
files=sorted(p for p in ROOT.rglob('*') if included(p))
manifest={'release':'ProxiTouch R3 / 3.0.0','offlineHTMLSha256':freeze,
 'scope':'Package file integrity, not a claim of complete hardware or experimental validation. Manifest excludes itself and the external ZIP/checksum text.',
 'exclusions':['node_modules','__pycache__','.git','font files'],
 'fileCountExcludingManifest':len(files),
 'files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
mp=ROOT/'BUILD_MANIFEST.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
files.append(mp)
zip_path=DEST/'ProxiTouch_R3_FINAL_DELIVERY.zip'
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,'ProxiTouch_R3/'+p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(zip_path) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(files)
 for f in manifest['files']:
  assert hashlib.sha256(z.read('ProxiTouch_R3/'+f['path'])).hexdigest()==f['sha256'],f['path']
 assert hashlib.sha256(z.read('ProxiTouch_R3/BUILD_MANIFEST.json')).hexdigest()==sha(mp)
exports=[
 ('dist/ProxiTouch-offline.html','ProxiTouch_R3-offline.html'),
 ('QA_REPORT.md','ProxiTouch_R3_QA_REPORT.md'),
 ('docs/CHANGELOG.md','ProxiTouch_R3_CHANGELOG.md'),
 ('PRESENTATION_GUIDE.md','ProxiTouch_R3_PRESENTATION_GUIDE.md'),
 ('qa/VISUAL_WALL.png','ProxiTouch_R3_VISUAL_WALL.png')]
outputs=[zip_path]
for src,name in exports:
 d=DEST/name;shutil.copy2(ROOT/src,d);outputs.append(d)
checks=DEST/'ProxiTouch_R3_CHECKSUMS.txt'
checks.write_text('ProxiTouch R3 - SHA-256\n\n'+''.join(f'{sha(p)}  {p.name}\n' for p in outputs)+f'\nZIP entries verified: {len(files)}\nZIP CRC test: passed\nAll manifest file hashes: passed\nFrozen offline HTML: {freeze}\n')
print(json.dumps({'zip':str(zip_path),'zipBytes':zip_path.stat().st_size,'verifiedEntries':len(files),'manifestFiles':len(manifest['files']),'offlineSHA256':freeze,'outputs':[{'path':str(p),'bytes':p.stat().st_size} for p in outputs+[checks]]},indent=2))
