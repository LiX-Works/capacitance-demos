/** Compile editable source; include complete notices in every distribution. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import ts from 'typescript';
const root=path.resolve(import.meta.dirname,'..'),project=path.resolve(root,'..');
const config=JSON.parse(fs.readFileSync(path.join(project,'project.json'),'utf8'));
const out=path.join(project,'dist');
if(path.dirname(out)!==project)throw Error('Unsafe build target');
fs.rmSync(out,{recursive:true,force:true});fs.mkdirSync(out,{recursive:true});
fs.cpSync(path.join(root,'public'),out,{recursive:true});
const modules=[];
function compile(file,key){
 const text=fs.readFileSync(file,'utf8'),relative=path.relative(root,file).replaceAll(path.sep,'/');
 const opts={target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022,sourceMap:true,inlineSources:true};
 const esm=ts.transpileModule(text,{compilerOptions:opts,fileName:relative});
 const dest=path.join(out,'js',key);fs.mkdirSync(path.dirname(dest),{recursive:true});
 fs.writeFileSync(dest,esm.outputText);if(esm.sourceMapText)fs.writeFileSync(dest+'.map',esm.sourceMapText);
 const cjs=ts.transpileModule(text,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.CommonJS},fileName:relative});
 modules.push(`${JSON.stringify(key)}:function(require,module,exports){\n${cjs.outputText}\n}`);
}
function walk(dir){for(const entry of fs.readdirSync(dir,{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name,'en'))){const p=path.join(dir,entry.name);if(entry.isDirectory())walk(p);else if(p.endsWith('.ts'))compile(p,path.relative(path.join(root,'src'),p).replaceAll(path.sep,'/').replace(/\.ts$/,'.js'));}}
walk(path.join(root,'src'));compile(path.join(root,'public/vendor/katex.js'),'vendor/katex.js');
const bundle=`/* ${config.bundleName}: offline TypeScript bundle. No external runtime assets. */\n(function(){'use strict';const modules={${modules.join(',\n')}};const cache={};function normalize(p){const parts=[];p.split('/').forEach(x=>{if(x==='..')parts.pop();else if(x&&x!=='.')parts.push(x)});return parts.join('/')}function load(id,parent=''){const key=normalize(id.startsWith('.')?parent.split('/').slice(0,-1).join('/')+'/'+id:id);if(cache[key])return cache[key].exports;if(!modules[key])throw Error('Missing local module '+key);const m={exports:{}};cache[key]=m;modules[key](p=>load(p,key),m,m.exports);return m.exports;}globalThis.__vendorMath=load('vendor/katex.js');load('main.js');})();\n`;
fs.writeFileSync(path.join(out,'app.js'),bundle);
const notices=['PROJECT-MIT.txt','KaTeX-MIT.txt'].map(name=>fs.readFileSync(path.join(project,'licenses',name),'utf8')).join('\n\n');
const notice=`<!--\nProject and runtime library notices\n${notices.replaceAll('--','- -')}\n-->\n`;
const html=fs.readFileSync(path.join(root,'index.html'),'utf8').replace('<script type="module" src="./js/main.js"></script>','<script src="./app.js"></script>');
if(!html.includes('<script src="./app.js"></script>'))throw Error('Missing source entry placeholder');
fs.writeFileSync(path.join(out,'index.html'),html.replace('</body>',notice+'</body>'));
const standalone=html.replace('<link rel="stylesheet" href="./style.css">',()=>'<style>'+fs.readFileSync(path.join(out,'style.css'),'utf8')+'</style>').replace('<script src="./app.js"></script>',()=>'<script>'+bundle.replaceAll('</script','<\\/script')+'</script>').replace('</body>',notice+'</body>');
fs.writeFileSync(path.join(out,config.offlineFile),standalone);fs.writeFileSync(path.join(project,'index.html'),standalone);
fs.cpSync(path.join(project,'licenses'),path.join(out,'licenses'),{recursive:true});
const site=path.join(project,'site');if(path.dirname(site)!==project)throw Error('Unsafe site target');
fs.rmSync(site,{recursive:true,force:true});fs.mkdirSync(site,{recursive:true});
fs.writeFileSync(path.join(site,'index.html'),standalone);fs.writeFileSync(path.join(site,'.nojekyll'),'');
fs.cpSync(path.join(project,'licenses'),path.join(site,'licenses'),{recursive:true});
fs.copyFileSync(path.join(project,'licenses/PROJECT-MIT.txt'),path.join(site,'LICENSE.txt'));
if(fs.existsSync(path.join(project,'previews')))fs.cpSync(path.join(project,'previews'),path.join(site,'previews'),{recursive:true});
console.log(`Built ${config.title}: ${modules.length} modules; SHA-256 ${crypto.createHash('sha256').update(standalone).digest('hex')}`);
