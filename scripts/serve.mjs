import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';

const root = path.resolve(import.meta.dirname, '../site');
const port = Number(process.env.PORT || 4173);
if (!Number.isInteger(port) || port < 1 || port > 65535) throw Error('PORT must be an integer between 1 and 65535');
// Optional mount simulates the repository name used by GitHub Pages.
const prefix = '/' + (process.env.PREVIEW_BASE || '').replace(/^\/+|\/+$/g, '');
const base = prefix === '/' ? '/' : prefix + '/';
const mime = {'.html':'text/html; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.css':'text/css; charset=utf-8', '.png':'image/png', '.jpg':'image/jpeg', '.json':'application/json', '.md':'text/plain; charset=utf-8', '.txt':'text/plain; charset=utf-8'};
http.createServer((req, res) => {
  let pathname;
  try { pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname); }
  catch { res.writeHead(400); res.end('Bad request'); return; }
  if (base !== '/' && pathname === prefix) { res.writeHead(301, {'Location':base}); res.end(); return; }
  if (!pathname.startsWith(base)) { res.writeHead(404); res.end('Not found'); return; }
  const relative = pathname.slice(base.length);
  const file = path.resolve(root, relative + (pathname.endsWith('/') ? 'index.html' : ''));
  if (!file.startsWith(root + path.sep)) { res.writeHead(403); res.end('Forbidden'); return; }
  fs.readFile(file, (error, data) => {
    if (error) { res.writeHead(404); res.end('Not found'); return; }
    res.writeHead(200, {'Content-Type':mime[path.extname(file)] || 'application/octet-stream', 'Cache-Control':'no-store'});
    res.end(req.method === 'HEAD' ? undefined : data);
  });
}).listen(port, '127.0.0.1', () => console.log(`Preview http://127.0.0.1:${port}${base}`));
