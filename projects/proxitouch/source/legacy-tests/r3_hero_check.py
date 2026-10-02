from harness import *
from PIL import Image
out=ROOT/'qa/iterations/final-hero';out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b,page,errors=launch(p);page.evaluate('__PT.captureMode(true)')
 for phase in [0,.62,1]:
  page.evaluate('p=>{__PT.goTo("S22",p);__PT.flush()}',phase);f=out/f'S22-{phase}.png';page.screenshot(path=str(f));print(phase,flush=True)
  if phase==.62:Image.open(f).crop((1240,300,1460,720)).resize((440,840)).save(out/'touch-detail.png')
 b.close();print(errors)
