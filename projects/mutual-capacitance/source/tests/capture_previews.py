"""Re-render the curated preview manifest against the current built application.
Run from any working directory; npm run previews also copies results into site/.
--refresh-only rebuilds the montage/hashes without claiming another browser run.
"""
from pathlib import Path
import argparse,json,hashlib,os,shutil,subprocess,time,atexit
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--refresh-only',action='store_true');args=parser.parse_args()
manifest=json.loads((ROOT/'previews/manifest.json').read_text(encoding='utf-8'))
config=json.loads((ROOT/'project.json').read_text(encoding='utf-8'));proxi=config['id']=='proxi';api='__PT' if proxi else '__LAB'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
runtime=sha(ROOT/'index.html');errors=[];requests=[]
if args.refresh_only:
    if manifest['runtimeSha256']!=runtime:raise RuntimeError('Runtime changed. Render the full previews instead of relabelling old screenshots.')
else:
    from playwright.sync_api import sync_playwright
    if os.name=='posix':
        display=os.environ.get('DISPLAY','');live=display and Path('/tmp/.X11-unix/X'+display.split(':')[-1].split('.')[0]).exists()
        if not live and shutil.which('Xvfb'):
            n=next(i for i in range(96,130) if not Path('/tmp/.X11-unix/X'+str(i)).exists())
            proc=subprocess.Popen(['Xvfb',':'+str(n),'-screen','0','2560x1440x24','-nolisten','tcp'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            atexit.register(proc.terminate);time.sleep(.6);os.environ['DISPLAY']=':'+str(n)
    with sync_playwright() as p:
        options={'headless':not bool(os.environ.get('DISPLAY')),'args':['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']}
        if os.name=='posix':options['args'].append('--no-sandbox')
        executable=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
        if executable:options['executable_path']=executable
        browser=p.chromium.launch(**options)
        try:
            page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
            page.context.set_offline(True)
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('console',lambda e:errors.append(e.text) if e.type=='error' else None)
            page.on('request',lambda r:requests.append(r.url))
            page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load',timeout=90000)
            page.wait_for_function(f'window.{api}?.ready',timeout=60000)
            page.evaluate(f'{api}.captureMode(true);{api}.stop();')
            for item in manifest['images']:
                page.set_viewport_size({'width':item['width'],'height':item['height']})
                if proxi:page.evaluate('a=>{__PT.ambientTime(a[2]);__PT.goTo(a[0],a[1]);__PT.flush();}',[item['scene'],item['phase'],item.get('ambientSeconds') or 0])
                else:page.evaluate('a=>{__LAB.goTo(a[0],a[1]);__LAB.field(a[2]);__LAB.flush();}',[item['scene'],item['phase'],item['field']])
                page.screenshot(path=str(ROOT/'previews'/item['file']),timeout=30000)
                print('CAPTURE',item['file'],flush=True)
        finally:browser.close()
    if errors or requests:raise RuntimeError(json.dumps({'errors':errors,'unexpectedNetwork':requests}))
    manifest['runtimeSha256']=runtime
    (ROOT/'qa/curated-preview-refresh.json').write_text(json.dumps({'runtimeSha256':runtime,'count':len(manifest['images']),'errors':errors,'networkRequests':requests,'method':'Real Chromium owned-document render in an offline context.'},indent=2),encoding='utf-8')
for item in manifest['images']:
    file=ROOT/'previews'/item['file'];item['sha256']=sha(file)
    with Image.open(file) as image:assert image.size==(item['width'],item['height'])
# Overview layout is configured by the manifest and survives full preview refreshes.
overview=manifest['overview'];preferred=overview['images']
columns,rows=overview['columns'],overview['rows']
cw,ch,gap=overview['cellWidth'],overview['cellHeight'],overview['gutter']
assert columns==rows==2 and len(preferred)==4, 'The overview must contain four selected frames.'
assert set(preferred).issubset({item['file'] for item in manifest['images']})
wall=Image.new('RGB',(columns*cw+(columns-1)*gap,rows*ch+(rows-1)*gap),'#edf3f7')
for i,name in enumerate(preferred):
    x=i%columns*(cw+gap);y=i//columns*(ch+gap)
    with Image.open(ROOT/'previews'/name) as im:
        assert im.width*ch==im.height*cw, 'Preserve the screenshot aspect ratio.'
        wall.paste(im.convert('RGB').resize((cw,ch),Image.Resampling.LANCZOS),(x,y))
wall.save(ROOT/'previews/overview.png')
overview.update({'file':'overview.png','width':wall.width,'height':wall.height,'sha256':sha(ROOT/'previews/overview.png')})
(ROOT/'previews/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Curated preview files verified and overview refreshed. Run npm run build to copy them into site/.')
