"""Verify real collection URLs, frozen scientific visuals and repaired interactions."""
from pathlib import Path
import json, base64, hashlib, sys
from playwright.sync_api import sync_playwright
from browser_support import ROOT,NAMES,read_json,write_json,sha,launch,server

report={'method':'Real Chromium isolated profile, HTTP project subpath and offline file navigation',
        'rendererScope':'SwiftShader functional checks, no hardware FPS claim',
        'checks':[],'errors':[],'externalRequests':[],'projects':{}}
artifacts=ROOT/'qa/browser-artifacts';artifacts.mkdir(parents=True,exist_ok=True)
def check(name,ok,detail=None):
    report['checks'].append({'name':name,'passed':bool(ok),'detail':detail})
    if not ok:print('FAIL',name,flush=True)
    return bool(ok)
def ev(page,api,expression,arg=None):
    return page.evaluate(expression.replace('API',api),arg)
def attach(page):
    page.on('pageerror',lambda error:report['errors'].append(str(error)))
    page.on('request',lambda req:report['externalRequests'].append(req.url) if url_external(req.url) else None)
def url_external(url):return not url.startswith(('http://127.0.0.1:','file:','data:','about:'))
def pixel_hash(page,api):
    image=ev(page,api,"API.app.renderer.canvas.toDataURL('image/png').split(',')[1]")
    return hashlib.sha256(base64.b64decode(image)).hexdigest()

with sync_playwright() as pw, server() as base:
    browser=launch(pw)
    report['browserVersion']=browser.version
    try:
        page=browser.new_page(viewport={'width':1280,'height':900});attach(page)
        response=page.goto(base,wait_until='networkidle');check('Collection entrance loads by HTTP',response.status==200)
        check('Both demo entries visible',page.get_by_role('link',name='进入演示').count()==2)
        check('Entrance images loaded',page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)'))
        page.screenshot(path=str(artifacts/'collection-desktop.png'),full_page=True)
        page.set_viewport_size({'width':390,'height':844})
        check('Collection mobile entrance has no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
        page.screenshot(path=str(artifacts/'collection-mobile.png'),full_page=True)
        page.set_viewport_size({'width':1920,'height':1080})
        for name in NAMES:
            project=ROOT/'projects'/name;config=read_json(project/'project.json');api='__PT' if name=='proxitouch' else '__LAB'
            response=page.goto(base+name+'/',wait_until='load');check(name+' real project route',response.status==200)
            page.wait_for_function(f'window.{api}?.ready',timeout=60000)
            ev(page,api,'API.captureMode(true);API.stop();')
            ids=ev(page,api,'API.scenes.map(s=>s.id)')
            check(name+' scene count',len(ids)==config['sceneCount'])
            record={'runtimeSha256':sha(project/'index.html'),'scenes':len(ids),'renderer':ev(page,api,'API.diagnostics().renderer')}
            report['projects'][name]=record
            ref=browser.new_page(viewport={'width':1920,'height':1080});attach(ref);ref.context.set_offline(True)
            ref.set_content((project/config['baseline']).read_text(encoding='utf-8'),wait_until='load',timeout=90000)
            ref.wait_for_function(f'window.{api}?.ready',timeout=60000)
            ev(ref,api,'API.captureMode(true);API.stop();')
            for sid in ids:
                for phase in (0,.5,1):
                    if name=='proxitouch':ev(page,api,'a=>{API.ambientTime(6.8);API.goTo(a[0],a[1]);API.flush();}',[sid,phase])
                    else:ev(page,api,'a=>{API.goTo(a[0],a[1]);API.flush();}',[sid,phase])
                    d=ev(page,api,'API.diagnostics()')
                    check(f'{name} {sid} phase {phase}: renders without GL, math or runtime errors',d.get('glError')==0 and d.get('mathErrors')==0 and not d.get('errors'),{'glError':d.get('glError'),'mathErrors':d.get('mathErrors'),'errors':d.get('errors')})
                    check(f'{name} {sid} phase {phase}: finite camera and model',ev(page,api,"()=>{const s=API.snapshot();return Object.values(s.camera).every(v=>typeof v!=='number'||Number.isFinite(v))&&s.camera.position.every(Number.isFinite);}"))
                if name=='proxitouch':ev(ref,api,'s=>{API.ambientTime(6.8);API.goTo(s,1);API.flush();}',sid)
                else:ev(ref,api,'s=>{API.goTo(s,1);API.flush();}',sid)
                check(f'{name} {sid}: scientific 3D pixels preserve historical state',pixel_hash(page,api)==pixel_hash(ref,api))
                check(f'{name} {sid}: explanation text preserved',page.locator('.copy-scroll').inner_text()==ref.locator('.copy-scroll').inner_text())
            ref.close()
            check(name+' no private homepage block',page.locator('.author-info').count()==0)
            if name=='proxitouch':
                ev(page,api,"API.captureMode(false);API.goTo('S03',0);")
                hint=page.locator('.navigation-hint').inner_text()
                check('Proxi live loop navigation hint is accurate','中断' in hint and '再按' not in hint,hint)
                page.locator('#next-button').click();check('Proxi button immediately interrupts loop',ev(page,api,'API.snapshot().scene')=='S04')
                ev(page,api,"API.captureMode(true);API.goTo('S14',1);")
                before=ev(page,api,'API.snapshot().scene');page.locator('#menu-button').press('Space')
                check('Proxi focused menu Space opens menu without changing scene',page.locator('.chapter-menu').is_visible() and ev(page,api,'API.snapshot().scene')==before)
                page.keyboard.press('Escape');page.locator('#notes-button').press('Space')
                check('Proxi focused notes Space toggles notes without changing scene',not ev(page,api,'API.snapshot().notes') and ev(page,api,'API.snapshot().scene')==before)
                page.locator('#notes-button').click()
                before=ev(page,api,'API.snapshot()');page.locator('#explore-button').click();page.locator('#depth-input').press('End');page.keyboard.press('Escape')
                after=ev(page,api,'API.snapshot()');check('Proxi explore exit restores capture model/camera',before['camera']==after['camera'] and before['model']==after['model'])
                page.screenshot(path=str(artifacts/'proxitouch.png'))
            else:
                ev(page,api,"API.captureMode(false);API.goTo('05',0,true);")
                page.wait_for_function('__LAB.snapshot().state.field==="potential"',timeout=30000)
                check('Lab real completed loop advances field mode',True)
                page.locator('[data-field="strength"]').click();check('Lab manual field mode selects strength',ev(page,api,'API.snapshot().state.field')=='strength')
                page.locator('#next').click();check('Lab Next interrupts field loop',ev(page,api,'API.snapshot().scene')=='06')
                ev(page,api,"API.captureMode(true);API.goTo('06',1);API.captureMode(false);API.stop();")
                page.locator('#menu-toggle').press('Space');check('Lab focused menu Space leaves phase and scene unchanged',page.locator('.menu').is_visible() and ev(page,api,'API.snapshot().scene')=='06')
                page.keyboard.press('Escape');page.locator('#explore-toggle').click();page.locator('#theta').press('Home');page.locator('#material-toggle').click()
                check('Lab displayed dielectric trace matches chosen material',page.locator('.trace.diel').count()>0 and ev(page,api,'API.snapshot().state.er')==4)
                marker=page.locator('.marker').get_attribute('cy');clip=page.locator('#plot-clip rect').get_attribute('y')
                check('Lab dielectric marker remains in chart',float(marker)-5.5>=float(clip))
                page.keyboard.press('Escape');ev(page,api,"API.goTo('12',1);API.field('potential');API.flush();")
                page.screenshot(path=str(artifacts/'mutual-capacitance.png'))
            # Representative viewport check at the normal 1280x720 desktop breakpoint.
            page.set_viewport_size({'width':1280,'height':720})
            d=ev(page,api,'API.diagnostics()');check(name+' desktop document fits viewport',not d.get('documentOverflow'),d.get('overflow'))
            page.set_viewport_size({'width':1920,'height':1080})
            response=page.goto(base+name+'/previews/',wait_until='networkidle')
            image_sources=page.locator('img').evaluate_all('(xs)=>xs.map(x=>x.src)')
            check(name+' project-path gallery and all image URLs load',response.status==200 and image_sources and all(page.request.get(src).status==200 for src in image_sources))
            context=browser.new_context(offline=True,viewport={'width':1280,'height':720});offline=context.new_page();attach(offline)
            offline.goto((project/'index.html').as_uri(),wait_until='load',timeout=90000)
            offline.wait_for_function(f'window.{api}?.ready',timeout=60000)
            check(name+' standalone file opens with network disabled',ev(offline,api,'API.diagnostics().glError')==0)
            context.close()
            print('BROWSER VERIFIED',name,len(ids),'scenes at 3 phases, real navigation and file://',flush=True)
        check('No browser runtime exceptions',not report['errors'],report['errors'])
        check('No external runtime requests',not report['externalRequests'],report['externalRequests'])
    except Exception as error:
        page.screenshot(path=str(artifacts/'failure.png'),full_page=True)
        check('Browser verification completed',False,repr(error));raise
    finally:
        browser.close();write_json(ROOT/'qa/browser-qa.json',report)
failures=[c for c in report['checks'] if not c['passed']]
print('BROWSER QA',len(report['checks']),'checks;',len(failures),'failures',flush=True)
sys.exit(bool(failures))
