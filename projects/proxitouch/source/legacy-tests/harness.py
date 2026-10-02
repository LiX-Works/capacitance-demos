"""Render the project's own offline HTML without changing browser policy.
CHROMIUM_PATH selects a local Chromium binary; otherwise use system Chromium
or Playwright's installed Chromium. PT_HEADLESS=0 enables a visible window. An available X display defaults to
headed mode, since this managed Chromium sometimes loses headless WebGL.
The default QA renderer is SwiftShader; PT_SOFTWARE=0 permits native selection.
PT_OFFLINE_BROWSER=1 disables network in the isolated context before app load.
"""
from pathlib import Path
import os,shutil,subprocess,time,atexit
# Start a local virtual display when a stale DISPLAY is inherited. No browser policy changes.
if os.name=='posix':
 display=os.environ.get('DISPLAY','')
 live=bool(display) and Path('/tmp/.X11-unix/X'+display.split(':')[-1].split('.')[0]).exists()
 if not live and shutil.which('Xvfb'):
  number=next(i for i in range(96,130) if not Path('/tmp/.X11-unix/X'+str(i)).exists())
  _xvfb=subprocess.Popen(['Xvfb',':'+str(number),'-screen','0','2560x1440x24','-nolisten','tcp'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  atexit.register(_xvfb.terminate);time.sleep(.7);os.environ['DISPLAY']=':'+str(number)
 elif not live:os.environ.pop('DISPLAY',None)
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
def launch(p,width=1920,height=1080,html_path=None):
    executable=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
    args=['--no-sandbox'] if os.name=='posix' else []
    if os.environ.get('PT_SOFTWARE','1')!='0':args+=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']
    default_headless='0' if os.environ.get('DISPLAY') else '1'
    options={'headless':os.environ.get('PT_HEADLESS',default_headless)!='0','args':args}
    if executable:options['executable_path']=executable
    browser=p.chromium.launch(**options)
    page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
    if os.environ.get('PT_OFFLINE_BROWSER')=='1':page.context.set_offline(True)
    errors=[];page.pt_requests=[]
    page.on('request',lambda r:page.pt_requests.append({'url':r.url,'type':r.resource_type}))
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
    page.set_content((Path(html_path) if html_path else ROOT/'dist/ProxiTouch-offline.html').read_text(),wait_until='load',timeout=60000)
    try:
        page.wait_for_function('window.__PT !== undefined',timeout=60000)
    except Exception as exc:
        detail={'errors':errors,'body':page.locator('body').inner_text()[:1600]}
        browser.close()
        raise RuntimeError('Application startup failed: '+str(detail)) from exc
    return browser,page,errors
