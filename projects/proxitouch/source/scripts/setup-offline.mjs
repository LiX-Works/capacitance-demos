/** Cross-platform extraction of the included archive of the locally available TypeScript package.
 * No npm registry, shell tar, global package, or network access is needed.
 */
import fs from 'node:fs';
import path from 'node:path';
import {gunzipSync} from 'node:zlib';
const root=path.resolve(import.meta.dirname,'..');
const destination=path.join(root,'node_modules','typescript');
if(fs.existsSync(path.join(destination,'lib','typescript.js'))){console.log('Local TypeScript compiler is ready.');process.exit(0)}
const archive=path.resolve(root,'../tools/typescript-5.8.3.tgz');
if(!fs.existsSync(archive))throw Error('Missing offline compiler archive: '+archive);
const tar=gunzipSync(fs.readFileSync(archive));
const text=(b,a,z)=>b.subarray(a,z).toString('utf8').replace(/\0.*$/s,'');
let files=0;
for(let offset=0;offset+512<=tar.length;){
 const h=tar.subarray(offset,offset+512);if(h.every(x=>x===0))break;
 const name=text(h,0,100),prefix=text(h,345,500),type=text(h,156,157)||'0';
 const size=parseInt(text(h,124,136).trim(),8)||0;
 if(!Number.isSafeInteger(size)||size<0||size>64000000)throw Error('Invalid archive entry size');
 const full=(prefix?prefix+'/':'')+name;
 // Python tarfile may emit POSIX extended metadata; contents need no metadata.
 if(type==='0'||type==='5'){
  if(!full.startsWith('package/')){offset+=512+Math.ceil(size/512)*512;continue}
  const relative=full.slice(8);
  if(relative.split('/').includes('..')||path.isAbsolute(relative))throw Error('Unsafe archive path');
  const target=path.resolve(destination,relative);
  if(!target.startsWith(destination+path.sep)&&target!==destination)throw Error('Unsafe archive target');
  if(type==='5')fs.mkdirSync(target,{recursive:true});
  else{fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,tar.subarray(offset+512,offset+512+size));files++}
 }
 offset+=512+Math.ceil(size/512)*512;
}
if(!fs.existsSync(path.join(destination,'lib','typescript.js')))throw Error('Compiler extraction failed');
console.log('Installed offline TypeScript 5.8.3 ('+files+' files).');
