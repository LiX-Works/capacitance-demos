"""Current upload vs rebuilt source, real Chromium renders, selected previews.
Run from repository root with `npm run qa`. No server credentials are used.
Managed-browser fallback loads owned HTML into about:blank, not a fake renderer.
"""
from pathlib import Path
import os,sys,json,time,shutil,subprocess,atexit,hashlib,base64
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
CONFIG=json.loads((ROOT/'project.json').read_text(encoding='utf-8'));KIND=CONFIG['id'];API='__PT' if KIND=='proxi' else '__LAB'
if os.name=='posix':
    value=os.environ.get('DISPLAY','');live=value and Path('/tmp/.X11-unix/X'+value.split(':')[-1].split('.')[0]).exists()
    if not live and shutil.which('Xvfb'):
        number=next(i for i in range(96,130) if not Path('/tmp/.X11-unix/X'+str(i)).exists())
        xvfb=subprocess.Popen(['Xvfb',':'+str(number),'-screen','0','2560x1440x24','-nolisten','tcp'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        atexit.register(xvfb.terminate);time.sleep(.6);os.environ['DISPLAY']=':'+str(number)
checks=[];errors=[];requests=[];report={'kind':KIND,'sourceSha256':hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest(),'referenceSha256':hashlib.sha256((ROOT/CONFIG['baseline']).read_bytes()).hexdigest(),'checks':checks,'errors':errors,'networkRequests':requests,'loadedVia':'set_content owned complete HTML on about:blank; no browser policy changes','screenshots':[]}
(ROOT/'qa').mkdir(exist_ok=True);(ROOT/'previews').mkdir(exist_ok=True)
def save(): (ROOT/'qa/browser-sync.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
def check(name,passed,details=None):
    checks.append({'name':name,'passed':bool(passed),'details':details});print('PASS' if passed else 'FAIL',name,flush=True);save()
def ev(page,expression,arg=None):return page.evaluate(expression.replace('API',API),arg)
def load(browser,file,label):
    page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
    page.context.set_offline(True)
    page.on('pageerror',lambda e:errors.append({'page':label,'error':str(e)}))
    page.on('console',lambda e:errors.append({'page':label,'error':e.text}) if e.type=='error' else None)
    page.on('request',lambda r:requests.append({'page':label,'url':r.url}))
    page.set_content(file.read_text(encoding='utf-8'),wait_until='load',timeout=90000)
    page.wait_for_function(f'window.{API}?.ready===true',timeout=60000)
    ev(page,'API.captureMode(true); API.stop();')
    return page
PROXI=[('01-cover','S00',1,0,None),('02-materials','S05',1,6.8,None),('03-fringing-field','S08',.65,0,None),('04-ionic-interface','S09',1,0,None),('05-two-interfaces','S10',1,0,None),('06-contact-area','S11',1,0,None),('07-shared-electrodes','S14',1,0,None),('08-dual-signals','S19',.83,0,None),('09-addressable-array','S20',1,0,None),('10-egg-grasp','S22',1,0,None)]
LAB=[('01-opening','01',.33,0,'lines'),('02-tilted-plates','02',.48,0,'potential'),('03-ideal-sector','04',1,0,'lines'),('04-numerical-field','05',.70,0,'lines'),('05-angle-models','06',.78,0,'potential'),('06-dielectric-edge','09',.6,0,'strength'),('07-permittivity','10',.67,0,'potential'),('08-coplanar-result','12',1,0,'lines')]
with sync_playwright() as p:
    args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'];
    if os.name=='posix':args+=['--no-sandbox']
    exe=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
    options={'headless':not bool(os.environ.get('DISPLAY')),'args':args}
    if exe:options['executable_path']=exe
    browser=p.chromium.launch(**options)
    try:
        reference=load(browser,ROOT/CONFIG['baseline'],'sanitized-upload');page=load(browser,ROOT/'index.html','rebuilt-source')
        report['renderer']=ev(page,'API.diagnostics().renderer')
        ids=ev(page,'API.scenes.map(s=>s.id)')
        for sid in ids:
            data=[]
            for pg in [reference,page]:
                if KIND=='proxi':ev(pg,'s=>{API.ambientTime(6.8);API.goTo(s,1);API.flush();}',sid)
                else:ev(pg,'s=>{API.goTo(s,1);API.flush();}',sid)
                snap=ev(pg,'API.snapshot()');
                # R3 snapshot has elapsed performance measurements elsewhere, not in model.
                image=ev(pg,"API.app.renderer.canvas.toDataURL('image/png').split(',')[1]")
                data.append({'snapshot':snap,'canvasSha256':hashlib.sha256(base64.b64decode(image)).hexdigest(),'copy':pg.locator('.copy-scroll').inner_text(),'title':pg.locator('h1').first.inner_text()})
            fields=['scene','phase','camera','model'] if KIND=='proxi' else ['scene','phase','camera','state','sample']
            check(sid+' synchronized runtime state / camera',all(data[0]['snapshot'].get(k)==data[1]['snapshot'].get(k) for k in fields))
            check(sid+' uploaded title / copy preserved',data[0]['copy']==data[1]['copy'] and data[0]['title']==data[1]['title'])
            check(sid+' uploaded 3-D pixels unchanged',data[0]['canvasSha256']==data[1]['canvasSha256'],{'reference':data[0]['canvasSha256'],'rebuilt':data[1]['canvasSha256']})
        check('Homepage personal information block absent',page.locator('.author-info').count()==0 and reference.locator('.author-info').count()==0)
        for name,sid,phase,ambient,field in (PROXI if KIND=='proxi' else LAB):
            if KIND=='proxi':ev(page,'a=>{API.ambientTime(a[2]);API.goTo(a[0],a[1]);API.flush();}',[sid,phase,ambient])
            else:ev(page,'a=>{API.goTo(a[0],a[1]);API.field(a[2]);API.flush();}',[sid,phase,field])
            path=ROOT/'previews'/f'{name}.png';page.screenshot(path=str(path),timeout=30000)
            d=ev(page,'API.diagnostics()');rec={'file':path.name,'scene':sid,'phase':phase,'ambientSeconds':ambient,'field':field,'viewport':[1920,1080],'imageSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'diagnostics':d};report['screenshots'].append(rec);save();print('CAPTURE',name,flush=True)
        # Check both actual loop behavior and immediate navigation, at safe quality for testing only.
        ev(page,"API.quality('safe');API.captureMode(false);")
        if KIND=='proxi':
            ev(page,"()=>{API.goTo('S03',0);window.__cycleStates=[];const app=API.app;const originalDraw=app.draw.bind(app);app.draw=function(){originalDraw();if(this.def.id==='S03')__cycleStates.push({phase:this.phase,to:this.animation?.to});};}")
            page.wait_for_function('window.__cycleStates.some(s=>s.to===0)',timeout=30000)
            check('Final-upload A-B-A loop reaches reverse motion',True)
            page.keyboard.press('ArrowRight');check('Right immediately interrupts loop and enters next scene',ev(page,'API.snapshot().scene')=='S04')
            ev(page,"API.goTo('S05',1)");before=ev(page,'API.snapshot().model.ambientTime');page.wait_for_function('(t)=>window.__PT.snapshot().model.ambientTime>t+.6',arg=before,timeout=15000)
            check('Existing material ambient loop still advances',True)
            page.keyboard.press('ArrowRight');check('Ambient page never blocks Next',ev(page,'API.snapshot().scene')=='S06')
            ev(page,"API.captureMode(true);API.stop();API.goTo('S11',.6)");before=ev(page,'API.snapshot()');page.keyboard.press('e');ev(page,'API.setDepth(.7)');page.keyboard.press('Escape');after=ev(page,'API.snapshot()')
            check('Explore exit restores capture-state model and camera',all(before[k]==after[k] for k in ['scene','phase','model','camera']))
            for sid in ['S03','S07','S10','S18']:
                ev(reference,'s=>{API.captureMode(false);API.goTo(s,0);API.app.animation=undefined;}',sid);ev(page,'s=>{API.captureMode(false);API.goTo(s,0);API.app.animation=undefined;}',sid)
                # Identical synthetic timestamp schedules exercise typed integration vs original patch.
                if sid!='S18':
                    result=[]
                    for pg in [reference,page]:
                        result.append(ev(pg,"()=>{const a=API.app;a.capture=false;a.animation={from:0,to:1,start:100,duration:100};const raf=window.requestAnimationFrame;window.requestAnimationFrame=()=>0;const states=[];for(const t of [150,200,10000]){a.tick(t);states.push({phase:a.phase,to:a.animation?.to,direction:a.loopDirection});}window.requestAnimationFrame=raf;a.stop();return states;}"))
                    check(sid+' integrated loop matches uploaded patch transition state',result[0]==result[1])
        else:
            ev(page,"API.goTo('05',0,true)");
            check('Cycle starts with field lines',ev(page,'API.snapshot().state.field')=='lines')
            page.wait_for_function('window.__LAB.snapshot().state.field==="potential"',timeout=25000)
            check('Next completed cycle selects potential',True)
            page.wait_for_function('window.__LAB.snapshot().state.field==="strength"',timeout=25000)
            check('Following cycle selects field strength',True)
            page.locator('[data-field="potential"]').click();check('Manual mode immediately selects potential',ev(page,'API.snapshot().state.field')=='potential')
            style=page.locator('[data-field="potential"]').evaluate('e=>({active:e.classList.contains("active"),background:getComputedStyle(e).backgroundColor})');check('Selected mode is visibly light blue',style['active'] and style['background'] in ['rgb(185, 220, 244)','rgb(200, 229, 247)'],style)
            page.keyboard.press('ArrowRight');check('Right interrupts field cycle',ev(page,'API.snapshot().scene')=='06')
            for sid in ['04','09']:
                ev(page,'s=>API.goTo(s,0,true)',sid);a=ev(page,'API.snapshot().state.field');ev(page,'API.app.advanceFieldCycle();API.render()');check(sid+' specialized display excluded from generic cycle',ev(page,'API.snapshot().state.field')==a)
        ev(page,"API.captureMode(true);API.stop();API.quality('high');")
        # Actual viewport resize; no special redesign to match a mockup.
        page.set_viewport_size({'width':2560,'height':1440});ev(page,"API.goTo('S22',1);API.flush();" if KIND=='proxi' else "API.goTo('09',.6);API.field('strength');API.flush();")
        page.screenshot(path=str(ROOT/'previews'/'hero-2560.png'),timeout=30000);report['screenshots'].append({'file':'hero-2560.png','viewport':[2560,1440],'scene':'S22' if KIND=='proxi' else '09','phase':1 if KIND=='proxi' else .6,'field':None if KIND=='proxi' else 'strength'})
        check('Final high-resolution render has no GL error',ev(page,'API.diagnostics().glError')==0)
        check('Cold offline contexts made no network requests',not requests,requests)
        check('No browser JavaScript or console errors',not errors,errors)
    except Exception as e:
        check('Browser QA completed',False,repr(e));raise
    finally:browser.close();save()
# Actual renders are composed into a GitHub README preview wall; no image generation.
files=[ROOT/'previews'/x['file'] for x in report['screenshots'] if x['file']!='hero-2560.png']
cols=3;tw=640;th=360;cellh=388
wall=Image.new('RGB',(cols*tw,((len(files)+cols-1)//cols)*cellh),'#edf3f7');draw=ImageDraw.Draw(wall)
for i,f in enumerate(files):
    x=i%cols*tw;y=i//cols*cellh;wall.paste(Image.open(f).convert('RGB').resize((tw,th),Image.Resampling.LANCZOS),(x,y+28));draw.text((x+10,y+7),f.stem,fill='#2b526a')
wall.save(ROOT/'previews'/'overview.png')
if any(not c['passed'] for c in checks):sys.exit(1)
print('DONE',KIND,len(checks),'checks',len(report['screenshots']),'raw previews',flush=True)
