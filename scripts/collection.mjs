import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';

export const root = path.resolve(import.meta.dirname, '..');
export const projects = ['proxitouch', 'mutual-capacitance'];
export function node(file, cwd, args = []) {
  const result = spawnSync(process.execPath, [file, ...args], {cwd, stdio: 'inherit'});
  if (result.error) throw result.error;
  if (result.status !== 0) throw Error(`${path.basename(file)} failed (${result.status})`);
}
const mode = process.argv[2];
if (!['build', 'check', 'test', 'verify'].includes(mode)) throw Error('Expected build, check, test, or verify');
if (Number(process.versions.node.split('.')[0]) < 22) throw Error('Use Node.js 22 or newer.');

for (const name of projects) {
  const project = path.join(root, 'projects', name), source = path.join(project, 'source');
  if (mode === 'build') {
    node('scripts/setup-offline.mjs', source);
    node('scripts/build.mjs', source);
  } else if (mode === 'check') {
    node('node_modules/typescript/lib/tsc.js', source, ['--noEmit']);
  } else if (mode === 'test') {
    node('tests/source-sync.mjs', source);
    const regression = name === 'proxitouch' ? 'proxi-regressions.mjs' : 'model-regressions.mjs';
    node(`tests/${regression}`, source);
  }
}
if (mode === 'build') {
  const site = path.join(root, 'site');
  if (path.dirname(site) !== root) throw Error('Unsafe output directory');
  fs.rmSync(site, {recursive: true, force: true});
  fs.mkdirSync(site, {recursive: true});
  for (const name of projects) fs.cpSync(path.join(root, 'projects', name, 'site'), path.join(site, name), {recursive: true});
  fs.cpSync(path.join(root, 'licenses'), path.join(site, 'licenses'), {recursive: true});
  fs.copyFileSync(path.join(root, 'LICENSE'), path.join(site, 'LICENSE.txt'));
  fs.copyFileSync(path.join(root, 'THIRD_PARTY_NOTICES.md'), path.join(site, 'THIRD_PARTY_NOTICES.md'));
  const template = fs.readFileSync(path.join(root, 'web/index.html'), 'utf8');
  const style = fs.readFileSync(path.join(root, 'web/style.css'), 'utf8');
  const home = (prefix, license) => template.replaceAll('{{STYLE}}', style)
    .replaceAll('{{PROXI}}', `${prefix}proxitouch/`).replaceAll('{{MUTUAL}}', `${prefix}mutual-capacitance/`)
    .replaceAll('{{LICENSE}}', license);
  fs.writeFileSync(path.join(site, 'index.html'), home('./', './LICENSE.txt'));
  fs.writeFileSync(path.join(root, 'index.html'), home('./projects/', './LICENSE'));
  fs.writeFileSync(path.join(site, '.nojekyll'), '');
  console.log('Built one collection entrance and two standalone demo routes.');
}
if (mode === 'build' || mode === 'test' || mode === 'verify') node('scripts/verify-site.mjs', root, mode === 'build' ? ['--allow-stale-previews'] : []);
