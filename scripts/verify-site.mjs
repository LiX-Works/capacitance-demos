import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';

const root = path.resolve(import.meta.dirname, '..'), site = path.join(root, 'site');
const allowStale = process.argv.includes('--allow-stale-previews');
const sha = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const files = [];
function walk(dir) { for (const entry of fs.readdirSync(dir, {withFileTypes:true})) { const p=path.join(dir,entry.name); if(entry.isDirectory())walk(p);else files.push(p); } }
walk(site);
let links = 0;
for (const file of files.filter(f=>f.endsWith('.html'))) {
  const text=fs.readFileSync(file,'utf8');
  // App HTML embeds generated JavaScript. Restrict URL inspection to markup outside scripts.
  const markup=text.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,'');
  for (const [,target] of markup.matchAll(/(?:href|src)\s*=\s*["']([^"']+)["']/gi)) {
    if (/^(?:#|https?:|data:|mailto:)/.test(target)) continue;
    assert(!target.startsWith('/'), `Absolute link breaks project-repository paths: ${target}`);
    const resolved=path.resolve(path.dirname(file),decodeURIComponent(target.split(/[?#]/)[0]));
    assert(resolved.startsWith(site+path.sep),`Link escapes deployed site: ${target}`);
    const candidate=fs.existsSync(resolved)&&fs.statSync(resolved).isDirectory()?path.join(resolved,'index.html'):resolved;
    assert(fs.existsSync(candidate),`Broken local asset: ${path.relative(site,file)} -> ${target}`); links++;
  }
}
for (const name of ['proxitouch','mutual-capacitance']) {
  const project=path.join(root,'projects',name), published=path.join(site,name);
  assert.equal(sha(path.join(published,'index.html')),sha(path.join(project,'index.html')),`${name}: deployed runtime differs`);
  const manifest=JSON.parse(fs.readFileSync(path.join(project,'previews/manifest.json'),'utf8'));
  const runtimeCurrent=manifest.runtimeSha256===sha(path.join(project,'index.html'));
  if(allowStale&&!runtimeCurrent)console.log(`NOTICE ${name}: run npm run previews, rebuild, and test before release.`);
  else assert(runtimeCurrent,`${name}: rerender previews after a runtime change`);
  for(const item of manifest.images) assert.equal(sha(path.join(published,'previews',item.file)),item.sha256,`${name}: preview hash differs (${item.file})`);
  const overview=manifest.overview;
  assert(overview?.columns===2&&overview.rows===2&&overview.images.length===4,`${name}: expected a selected 2x2 overview`);
  const overviewFile=path.join(published,'previews/overview.png'), png=fs.readFileSync(overviewFile);
  assert.equal(sha(overviewFile),overview.sha256,`${name}: overview hash differs`);
  assert.equal(png.readUInt32BE(16),overview.width,`${name}: overview width differs`);
  assert.equal(png.readUInt32BE(20),overview.height,`${name}: overview height differs`);
  assert(fs.existsSync(path.join(published,'licenses/KaTeX-MIT.txt')));
}
const size=files.reduce((total,file)=>total+fs.statSync(file).size,0);
assert(size<1024**3,'Website exceeds the published Pages size limit');
console.log(`PASS collection routes, ${links} local links, current preview hashes, notices; ${(size/1024**2).toFixed(2)} MiB deployed`);
