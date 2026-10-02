/** State regressions exercise the typed runtime without WebGL or a browser. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import ts from 'typescript';

const source=path.resolve(import.meta.dirname,'../src'),cache=new Map();
function load(file){
 file=path.resolve(file).replace(/\.js$/,'.ts');
 if(cache.has(file))return cache.get(file).exports;
 const module={exports:{}};cache.set(file,module);
 const compiled=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.CommonJS}}).outputText;
 vm.runInThisContext(`(function(require,module,exports){${compiled}\n})`,{filename:file})(id=>load(path.resolve(path.dirname(file),id)),module,module.exports);
 return module.exports;
}
const {ProxiTouchApp,finitePhase}=load(path.join(source,'main.ts'));
const {SCENES}=load(path.join(source,'scenes/definitions.ts'));
const {AmbientClock,AMBIENT_SCENES}=load(path.join(source,'app/ambient.ts'));
const {HUD}=load(path.join(source,'ui/HUD.ts'));
const originals={window:globalThis.window,requestAnimationFrame:globalThis.requestAnimationFrame,clearTimeout:globalThis.clearTimeout};
let timerId=0;const timers=new Map();
globalThis.window={setTimeout:fn=>{timers.set(++timerId,fn);return timerId;}};
globalThis.clearTimeout=id=>timers.delete(id);
globalThis.requestAnimationFrame=()=>0;
function app(id='S00'){
 const a=Object.assign(Object.create(ProxiTouchApp.prototype),{index:SCENES.findIndex(s=>s.id===id),phase:0,loopDirection:1,capture:false,captureAmbient:0,explore:false,auto:false,fullAuto:false,autoTimer:0,history:[],ambient:new AmbientClock(),dirty:false,lastStamp:0,frameIntervals:[],draws:0,notes:true});
 a.draw=()=>{a.draws++;a.dirty=false;};
 a.toggleExplore=force=>{a.explore=force??!a.explore;};
 return a;
}
function advanceTimer(a){const fn=timers.get(a.autoTimer);assert(fn,'Autoplay dwell timer exists');timers.delete(a.autoTimer);fn();}
const records=[];
function check(name,fn){fn();records.push(name);console.log('PASS',name);}
try{
 check('Autoplay crosses every finite and zero-duration scene and stops at the ending',()=>{
  const a=app();a.playAll();let steps=0;
  while(a.fullAuto&&steps++<100){if(a.animation)a.tick(a.animation.start+a.animation.duration+1);else advanceTimer(a);}
  assert.equal(a.fullAuto,false);assert.equal(a.def.id,'S22');assert(steps<100);
  for(const id of ['S05','S07','S18'])assert(a.history.some(h=>h.scene===id));
 });
 check('Manual Next interrupts once and cancels a pending autoplay dwell',()=>{
  const a=app('S04');a.fullAuto=true;a.next(false);assert.equal(a.def.id,'S05');assert(timers.has(a.autoTimer));
  a.next();assert.equal(a.def.id,'S06');assert.equal(a.fullAuto,false);assert(!timers.has(a.autoTimer));
 });
 check('Finite presentation scenes still follow A-B-A ping-pong',()=>{
  const a=app('S04');assert(a.def.duration>0);a.startPresentationLoop();a.tick(a.animation.start+a.animation.duration+1);
  assert.equal(a.phase,1);assert.equal(a.animation.to,0);a.tick(a.animation.start+a.animation.duration+1);
  assert.equal(a.phase,0);assert.equal(a.animation.to,1);
 });
 check('Ambient ownership, captured time and explore pause remain independent of phase',()=>{
  assert.deepEqual([...AMBIENT_SCENES],['S05','S07','S18']);const c=new AmbientClock();
  assert.equal(c.sample('S05',1000),0);assert.equal(c.sample('S05',2000),1);
  assert.equal(c.sample('S05',3000,true,4),4);assert.equal(c.sample('S05',4000,false,0,true),0);
  assert.equal(c.sample('S05',5000),1);assert.equal(c.sample('S04',6000),0);
 });
 check('Invalid query and public phase/depth/time inputs never poison state',()=>{
  assert.equal(finitePhase(Number('invalid')),1);assert.equal(finitePhase(Infinity),1);assert.equal(finitePhase(-2),0);assert.equal(finitePhase(2),1);
  const a=app('S04');a.capture=true;a.goTo('S04',NaN);assert.equal(a.phase,1);
  a.phase=.4;a.seek(NaN);a.seek(Infinity);assert.equal(a.phase,.4);a.seek(3);assert.equal(a.phase,1);
  a.depth=.3;a.setDepth(NaN);a.setDepth(Infinity);assert.equal(a.depth,.3);assert.equal(a.explore,false);
  a.setDepth(2);assert.equal(a.depth,1);a.setDepth(-2);assert.equal(a.depth,-1);
  a.captureAmbient=2;a.setAmbientTime(NaN);a.setAmbientTime(Infinity);assert.equal(a.captureAmbient,2);a.setAmbientTime(-4);assert.equal(a.captureAmbient,0);
 });
 check('Capture cancels existing animation and autoplay and remains stable across ticks',()=>{
  const a=app('S04');a.playAll();a.scheduleAdvance();a.auto=true;a.setCaptureMode(true);
  assert.equal(a.animation,undefined);assert.equal(a.fullAuto,false);assert.equal(a.auto,false);assert(!timers.has(a.autoTimer));
  const phase=a.phase;a.tick(performance.now()+100000);a.playAll();assert.equal(a.phase,phase);assert.equal(a.animation,undefined);assert.equal(a.fullAuto,false);
 });
 check('Native focused controls keep their keys and editable content keeps global shortcuts',()=>{
  const a=app('S04');let next=0,escaped=0;a.next=()=>next++;a.hud={closeModals:()=>escaped++};
  function key(k,selector=null,editable=false){let prevented=false;a.key({key:k,target:{isContentEditable:editable,closest:()=>selector},preventDefault:()=>prevented=true});return prevented;}
  assert.equal(key(' ','button'),false);assert.equal(key('ArrowRight','input'),false);assert.equal(key('r','textarea'),false);assert.equal(key('e',null,true),false);assert.equal(next,0);
  assert.equal(key(' '),true);assert.equal(next,1);assert.equal(key('Escape','input'),true);assert.equal(escaped,1);
 });
 check('Navigation hint and accessible button label agree with one-step interruption',()=>{
  const nodes=new Map();const node=()=>({textContent:'',attributes:{},classList:{toggle(){},remove(){}},setAttribute(k,v){this.attributes[k]=v;}});
  const root={dataset:{},classList:{toggle(){}},querySelector:k=>{if(!nodes.has(k))nodes.set(k,node());return nodes.get(k);},querySelectorAll:()=>[]};
  const h=Object.assign(Object.create(HUD.prototype),{root,last:'S04,false,device',body:node(),panel:node(),plots:{update(){}}});
  h.prepare(SCENES.find(s=>s.id==='S04'),{phase:.2},{explore:false,view:'device',notes:true,capture:false,playing:true,sceneIndex:4});
  assert.equal(root.querySelector('#next-button').textContent,'下一页 →');assert.equal(root.querySelector('#next-button').attributes['aria-label'],'中断当前动画并进入下一页');assert.equal(root.querySelector('.navigation-hint').textContent,'→ 中断当前动画并翻页');
 });
 check('Presentation history retains only the latest 256 entries',()=>{
  const a=app();for(let i=0;i<300;i++){a.phase=i/300;a.record();}assert.equal(a.history.length,256);assert.equal(a.history[0].phase,44/300);assert.equal(a.history.at(-1).phase,299/300);
 });
 console.log(`${records.length} ProxiTouch regressions passed.`);
}finally{
 for(const [key,value] of Object.entries(originals)){if(value===undefined)delete globalThis[key];else globalThis[key]=value;}
}

