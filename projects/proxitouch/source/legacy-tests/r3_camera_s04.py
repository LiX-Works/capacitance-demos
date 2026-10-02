from harness import *
out=ROOT/'qa/iterations/circuit-framing';out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b,page,errors=launch(p)
 page.evaluate('__PT.captureMode(true);__PT.goTo("S04",1)')
 for name,pos in [('a',[16,5.4,7.5]),('b',[-8,8.5,18]),('c',[16,16,7.5])]:
  page.evaluate('(pos)=>{__PT.app.def.camera[1].position=pos;__PT.render();__PT.flush();}',pos)
  page.screenshot(path=str(out/(name+'.png')));print(name,flush=True)
 b.close();print(errors)
