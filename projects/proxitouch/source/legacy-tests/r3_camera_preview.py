from harness import *
out=ROOT/'qa/iterations/hero-framing';out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b,page,errors=launch(p)
 page.evaluate('__PT.captureMode(true);__PT.goTo("S22",1)')
 for name,pos in [('a',[15,7.2,10.8]),('b',[12,7.2,14]),('c',[10,7.2,15])]:
  page.evaluate('(pos)=>{__PT.app.def.camera[1].position=pos;__PT.render();__PT.flush();}',pos)
  page.screenshot(path=str(out/(name+'.png')));print(name,flush=True)
 b.close()
 print(errors)
