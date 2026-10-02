from harness import *
import json,hashlib,sys
from PIL import Image,ImageOps,ImageDraw
out=ROOT/'qa/final-patch';out.mkdir(parents=True,exist_ok=True)
checks=[]
def add(name,ok,detail=None):
    checks.append({'name':name,'passed':bool(ok),'detail':detail});print(('PASS' if ok else 'FAIL'),name,flush=True)
with sync_playwright() as p:
  all_errors=[]
  for width,height in [(1920,1080),(2560,1440)]:
    folder=out/f'{width}x{height}';folder.mkdir(exist_ok=True)
    b,page,errors=launch(p,width,height);all_errors+=errors
    page.evaluate('__PT.quality("high");__PT.captureMode(true)')
    try:
      # S05 four-stage deterministic ambient loop.
      for label,t in [('default',0),('region-i',2.2),('layer-j',4.4),('materials',6.8),('return',9.59)]:
        page.evaluate('([t])=>{__PT.ambientTime(t);__PT.goTo("S05",1);__PT.flush()}',[t]);page.screenshot(path=str(folder/f'S05-{label}.png'))
        d=page.evaluate('__PT.diagnostics()');add(f'{width} S05 {label} layout clean',not d['overflow'] and not d['documentOverflow'] and not d['overlayOverlapPairs'] and d['labelOverlapCount']==0 and d['mathErrors']==0,d)
      # deterministic pixel repeat for heterogeneous-material state.
      page.evaluate('__PT.ambientTime(6.8);__PT.goTo("S05",1);__PT.flush()');a=folder/'S05-materials-repeat-a.png';page.screenshot(path=str(a));page.wait_for_timeout(250);page.evaluate('__PT.render();__PT.flush()');bb=folder/'S05-materials-repeat-b.png';page.screenshot(path=str(bb));add(f'{width} S05 deterministic fixed-seed capture',a.read_bytes()==bb.read_bytes())
      # S10 causal animation stages.
      for label,phase in [('base',0),('screening',.43),('compress-mid',.76),('compressed',1)]:
        page.evaluate('p=>{__PT.goTo("S10",p);__PT.flush()}',phase);page.screenshot(path=str(folder/f'S10-{label}.png'))
        d=page.evaluate('__PT.diagnostics()');add(f'{width} S10 {label} layout clean',not d['overflow'] and not d['documentOverflow'] and not d['overlayOverlapPairs'] and d['labelOverlapCount']==0 and d['mathErrors']==0,d)
      # S11 existing mechanics with revised copy/label.
      for label,phase in [('initial',0),('touch',.45),('pressure',1)]:
        page.evaluate('p=>{__PT.goTo("S11",p);__PT.flush()}',phase);page.screenshot(path=str(folder/f'S11-{label}.png'))
        d=page.evaluate('__PT.diagnostics()');add(f'{width} S11 {label} layout clean',not d['overflow'] and not d['documentOverflow'] and not d['overlayOverlapPairs'] and d['labelOverlapCount']==0 and d['mathErrors']==0,d)
      # Text and labels.
      page.evaluate('__PT.goTo("S10",1);__PT.flush()');body=page.locator('.copy-scroll').inner_text();labels=' '.join(x['text'] for x in page.evaluate('__PT.diagnostics().labels'))
      add(f'{width} S10 removed area-dominance copy','C_bottom ≫ C_top' not in body and '面积大、稳定' not in body and '可变上界面' not in labels and '稳定下界面' not in labels,{'body':body,'labels':labels})
      add(f'{width} S10 includes overlap caveat and screening copy','两侧 EDL 不发生明显重叠' in body and '宏观电场被强烈屏蔽' in body)
      page.evaluate('__PT.goTo("S11",1);__PT.flush()');body11=page.locator('.copy-scroll').inner_text();labels11=' '.join(x['text'] for x in page.evaluate('__PT.diagnostics().labels'))
      add(f'{width} S11 generic wording','离子凝胶微穹顶' not in body11 and '而不是简单的' not in body11 and '微结构' in body11 and '微结构' in labels11,{'body':body11,'labels':labels11})
    finally:b.close()
  # Navigation/ambient semantics at standard resolution.
  b,page,errors=launch(p,1920,1080);all_errors+=errors
  try:
    page.evaluate('__PT.quality("safe");__PT.captureMode(false);__PT.app.goTo("S05",1,false)');before=page.evaluate('__PT.snapshot()');page.wait_for_timeout(900);after=page.evaluate('__PT.snapshot()')
    add('S05 ambient advances without changing main phase',after['model']['ambientTime']>before['model']['ambientTime'] and after['phase']==1 and not after['playing'],{'before':before,'after':after})
    page.keyboard.press('ArrowRight');add('S05 ambient does not block Next',page.evaluate('__PT.snapshot().scene')=='S06')
    page.evaluate('__PT.app.goTo("S10",0,true)');add('S10 starts as main animation',page.evaluate('__PT.snapshot().playing'))
    page.keyboard.press('ArrowRight');s=page.evaluate('__PT.snapshot()');add('S10 first Next finishes main animation',s['scene']=='S10' and s['phase']==1 and not s['playing'],s)
    page.keyboard.press('ArrowRight');add('S10 second Next advances to S11',page.evaluate('__PT.snapshot().scene')=='S11')
    add('S10 not ambient according to diagnostics',not page.evaluate('__PT.diagnostics().ambient.active'))
  finally:b.close()
report={'sourceSha256':hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest(),'checks':checks,'browserErrors':all_errors}
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
if all_errors or any(not c['passed'] for c in checks):sys.exit(1)
