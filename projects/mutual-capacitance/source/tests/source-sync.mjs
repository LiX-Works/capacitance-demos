/** Exact release contract plus immutable scientific inputs; historical baseline is never rewritten. */
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {pathToFileURL} from 'node:url';import ts from 'typescript';
const root=path.resolve(import.meta.dirname,'../..'),config=JSON.parse(fs.readFileSync(path.join(root,'project.json'),'utf8'));
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
export function readBundle(html){
 const scripts=[...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(x=>x[1]);
 const source=ts.createSourceFile('bundle.js',scripts[0],ts.ScriptTarget.ES2022,true,ts.ScriptKind.JS);let object;
 function walk(n){if(ts.isVariableDeclaration(n)&&ts.isIdentifier(n.name)&&n.name.text==='modules'&&n.initializer&&ts.isObjectLiteralExpression(n.initializer))object=n.initializer;if(!object)ts.forEachChild(n,walk)}walk(source);assert(object,'Bundle modules found');
 const modules={};for(const p of object.properties){const fn=p.initializer;modules[p.name.text]=scripts[0].slice(fn.body.getStart(source)+1,fn.body.end-1).trim()+'\n';}
 return {modules,scripts,css:[...html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)].map(x=>x[1]).join('\n')};
}
export const normalize=s=>ts.createPrinter({removeComments:true,newLine:ts.NewLineKind.LineFeed}).printFile(ts.createSourceFile('m.js',s,ts.ScriptTarget.ES2022,true,ts.ScriptKind.JS));
const refHtml=fs.readFileSync(path.join(root,config.baseline),'utf8'),builtHtml=fs.readFileSync(path.join(root,'dist',config.offlineFile),'utf8');
const reference=readBundle(refHtml),built=readBundle(builtHtml),records=[];
const contract=JSON.parse(fs.readFileSync(path.join(root,'docs/RELEASE_CONTRACT.json'),'utf8'));
function check(name,ok,details){records.push({name,passed:!!ok,details});console.log(ok?'PASS':'FAIL',name);}
check('Historical reference bytes intact',sha(refHtml)===contract.referenceSha256);
check('Release module identities intact',JSON.stringify(Object.keys(built.modules).sort())===JSON.stringify(Object.keys(contract.modules).sort()));
check('Single compiled runtime script',built.scripts.length===1);
check('UTF-8 declaration remains within the first 1024 bytes',/charset\s*=\s*["']?utf-8/i.test(builtHtml.slice(0,1024)));
for(const [key,expected]of Object.entries(contract.modules)){
 const ref=reference.modules[key],current=built.modules[key];
 check('Approved module: '+key,ref!==undefined&&current!==undefined&&sha(normalize(ref))===expected.referenceNormalizedSha256&&sha(normalize(current))===expected.approvedNormalizedSha256,{reason:expected.reason});
}
check('Styles match approved release',sha(built.css)===contract.cssSha256);
for(const [file,hash]of Object.entries(contract.scientificFiles))check('Frozen scientific input: '+file,sha(fs.readFileSync(path.join(root,file)))===hash);
for(const name of ['index.html','site/index.html'])check('Deploy entry derives from current build: '+name,fs.readFileSync(path.join(root,name),'utf8')===builtHtml);
check('Homepage personal block absent',!/(?:author-info|has-author|author-phone)/.test(builtHtml));
check('Standalone includes original and KaTeX licenses',builtHtml.includes('Scientific Demos contributors')&&builtHtml.includes('Khan Academy')&&builtHtml.includes('permission notice shall be included'));
check('Deploy directory includes KaTeX license',fs.existsSync(path.join(root,'site/licenses/KaTeX-MIT.txt')));
if(config.id==='lab'){
 const imported=await import(pathToFileURL(path.join(root,'dist/js/physics/data.js')).href);
 const raw=JSON.parse(fs.readFileSync(path.join(root,'data/results.json'),'utf8'));
 check('Raw numerical data equals embedded scientific data',JSON.stringify(imported.DATA)===JSON.stringify(raw));
 check('Parameters match data provenance',sha(fs.readFileSync(path.join(root,'parameters.json')))===raw.parameterSha256);
 const parameters=JSON.parse(fs.readFileSync(path.join(root,'parameters.json'),'utf8'));
 check('Parameters equal displayed data parameters',JSON.stringify(parameters)===JSON.stringify(raw.parameters));
}
fs.mkdirSync(path.join(root,'qa'),{recursive:true});fs.writeFileSync(path.join(root,'qa/source-sync.json'),JSON.stringify({referenceSha256:sha(refHtml),builtSha256:sha(builtHtml),moduleCount:Object.keys(built.modules).length,records},null,2));
if(records.some(x=>!x.passed))process.exitCode=1;
