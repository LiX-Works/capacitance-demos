"""Isolated browser-test utilities for the owned collection, no user profile."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote, urlparse
from contextlib import contextmanager
import threading, os, json, hashlib

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('proxitouch', 'mutual-capacitance')
def read_json(file):
    return json.loads(Path(file).read_text(encoding='utf-8'))
def write_json(file, value):
    file=Path(file);file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(file):
    return hashlib.sha256(Path(file).read_bytes()).hexdigest()
def launch(playwright):
    options={'headless':True,'args':['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']}
    if os.environ.get('CHROMIUM_PATH'): options['executable_path']=os.environ['CHROMIUM_PATH']
    return playwright.chromium.launch(**options)
@contextmanager
def server(prefix='/scientific-demos/'):
    site=(ROOT/'site').resolve()
    class Handler(SimpleHTTPRequestHandler):
        def log_message(self,*args): pass
        def translate_path(self,url):
            pathname=unquote(urlparse(url).path)
            if not pathname.startswith(prefix):return str(site/'__not_found__')
            target=(site/pathname[len(prefix):]).resolve()
            if target!=site and site not in target.parents:return str(site/'__not_found__')
            return str(target)
    http=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
    try:yield f'http://127.0.0.1:{http.server_port}{prefix}'
    finally:http.shutdown();http.server_close();thread.join(timeout=3)
