from harness import *
import json,hashlib,sys
out=ROOT/'qa/final-patch';folder=out/'2560x1440';folder.mkdir(parents=True,exist_ok=True)
checks=[];errors_all=[]
def add(n,o,d=None): checks.append({'name':n,'passed':bool(o),'detail':d});print('PASS' if o else 'FAIL',n,flush=True)
with sync_playwright() as p:
 b,page,errors=launch(p,2560,1440);errors_all+=errors;page.evaluate('__PT.quality("high");__PT.captureMode(true)')
 try:
  for label,phase in [('touch',.45),('pressure',1)]:
   page.evaluate('p=>{__PT.goTo("S11",p);__PT.flush()}',phase);page.screenshot(path=str(folder/f'S11-{label}.png'));d=page.evaluate('__PT.diagnostics()');add(f'2560 S11 {label} layout clean',not d['overflow'] and not d['documentOverflow'] and not d['overlayOverlapPairs'] and d['labelOverlapCount']==0 and d['mathErrors']==0,d)
  page.evaluate('__PT.goTo("S10",1);__PT.flush()');body=page.locator('.copy-scroll').inner_text();labels=' '.join(x['text'] for x in page.evaluate('__PT.diagnostics().labels'));add('2560 S10 copy/labels final','C_bottom ≫ C_top' not in body and '面积大、稳定' not in body and '可变上界面' not in labels and '稳定下界面' not in labels and '两侧 EDL 不发生明显重叠' in body,{'labels':labels})
  page.evaluate('__PT.goTo("S11",1);__PT.flush()');body=page.locator('.copy-scroll').inner_text();labels=' '.join(x['text'] for x in page.evaluate('__PT.diagnostics().labels'));add('2560 S11 copy/labels final','离子凝胶微穹顶' not in body and '而不是简单的' not in body and '微结构' in body and '微结构' in labels,{'labels':labels})
 finally:b.close()
 b,page,errors=launch(p,1920,1080);errors_all+=errors
 try:
  page.evaluate('__PT.quality("safe");__PT.captureMode(false);__PT.app.goTo("S05",1,false)');before=page.evaluate('__PT.snapshot()');page.wait_for_timeout(900);after=page.evaluate('__PT.snapshot()');add('S05 ambient advances without changing main phase',after['model']['ambientTime']>before['model']['ambientTime'] and after['phase']==1 and not after['playing'])
  page.keyboard.press('ArrowRight');add('S05 ambient does not block Next',page.evaluate('__PT.snapshot().scene')=='S06')
  page.evaluate('__PT.app.goTo("S10",0,true)');add('S10 starts as finite main animation',page.evaluate('__PT.snapshot().playing'))
  page.keyboard.press('ArrowRight');s=page.evaluate('__PT.snapshot()');add('S10 first Next finishes animation',s['scene']=='S10' and s['phase']==1 and not s['playing'],s)
  page.keyboard.press('ArrowRight');add('S10 second Next advances',page.evaluate('__PT.snapshot().scene')=='S11')
  page.evaluate('__PT.goTo("S10",1)');add('S10 is not ambient',not page.evaluate('__PT.diagnostics().ambient.active'))
 finally:b.close()
report={'sourceSha256':hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest(),'checks':checks,'browserErrors':errors_all}
(out/'tail-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
if errors_all or any(not c['passed'] for c in checks):sys.exit(1)
