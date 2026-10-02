from harness import *
import json,sys,time,traceback,hashlib
folder=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'qa/iterations/v1-scenes'
folder.mkdir(parents=True,exist_ok=True)
selected=sys.argv[2:]
with sync_playwright() as p:
 b,page,errors=launch(p,int(os.environ.get("PT_WIDTH",1920)),int(os.environ.get("PT_HEIGHT",1080)))
 page.evaluate('window.__PT.captureMode(true)')
 scenes=page.evaluate('window.__PT.scenes')
 report=[]
 try:
  for scene in scenes:
   name=scene['id']
   if selected and name not in selected:continue
   phase={'F19':2/3,'D05':.70,'D13':.84}.get(name,1)
   page.evaluate('([id,t])=>window.__PT.goTo(id,t)',[name,phase])
   page.wait_for_timeout(350)
   page.evaluate('window.__PT.flush()')
   page.screenshot(path=str(folder/f'{name}.png'),timeout=15000)
   diag=page.evaluate('window.__PT.diagnostics()')
   report.append(diag)
   print(name,phase,'GL',diag['glError'],'overflow',diag['overflow'],'labels',diag['labelOverlapCount'],'triangles',diag['triangles'],flush=True)
   (folder/'report.json').write_text(json.dumps({'sourceSha256':hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest(),'errors':errors,'scenes':report},ensure_ascii=False,indent=2))
 except Exception as e:
  print('EXCEPTION',repr(e),flush=True);traceback.print_exc()
 finally:
  (folder/'errors.json').write_text(json.dumps(errors,indent=2))
  b.close()
print('DONE',len(report),flush=True)
