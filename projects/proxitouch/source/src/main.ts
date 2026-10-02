import {Renderer} from './engine/renderer.js';
import {CameraState} from './engine/camera.js';
import {clamp} from './engine/math.js';
import {AmbientClock,AMBIENT_SCENES} from './app/ambient.js';
import {deriveState,ModelState} from './app/state.js';
import {SCENES,scenePatch} from './scenes/definitions.js';
import {WorldManager,Frame} from './worlds/WorldManager.js';
import {HUD,HUDState} from './ui/HUD.js';
interface Animation{from:number;to:number;start:number;duration:number;}
export const finitePhase=(phase:number,fallback=1)=>Number.isFinite(phase)?clamp(phase):fallback;
export class ProxiTouchApp {
 loopDirection=1;

 /** Synchronized from the uploaded final presentation; loops are interruptible. */
 startPresentationLoop(reset=false){
   clearTimeout(this.autoTimer);
   if(this.capture||this.explore||this.def.duration<=0){this.animation=undefined;this.draw();if(this.fullAuto&&!this.capture&&!this.explore)this.scheduleAdvance();return;}
   if(reset||this.phase>=.99999)this.phase=0;
   this.loopDirection=1;
   this.animation={from:this.phase,to:1,start:performance.now(),duration:Math.max(1,this.def.duration*1000*Math.max(.001,1-this.phase))};
   this.dirty=true;this.draw();
 }

private toggleExploreBase(force?:boolean){const enter=force??!this.explore;if(enter===this.explore)return;this.stop();this.hud.closeModals();const scroll=!enter?(this.saved?.bodyScroll||0):0;if(enter){this.saved={index:this.index,phase:this.phase,notes:this.notes,bodyScroll:this.hud.body.scrollTop};this.depth=this.state.depth;this.explore=true;this.view=this.def.part==='I'?(this.def.world==='micro'?'micro':['edl','interfaces'].includes(this.def.world)?'nano':'field'):'device';}else{if(this.saved){this.index=this.saved.index;this.phase=this.saved.phase;this.notes=this.saved.notes;}this.explore=false;this.saved=undefined;}this.exploreCamera=undefined;this.draw();if(!enter){this.hud.body.scrollTop=scroll;document.querySelector<HTMLCanvasElement>('#stage')!.focus({preventScroll:true});}}

 ambient=new AmbientClock();captureAmbient=0;
 renderer:Renderer;worlds:WorldManager;hud:HUD;index=0;phase=1;animation?:Animation;state!:ModelState;frame!:Frame;
 explore=false;view='device';depth=-.4;exploreCamera?:CameraState;saved?:{index:number;phase:number;notes:boolean;bodyScroll:number};notes=true;capture=false;auto=false;autoStart=0;fullAuto=false;autoTimer=0;dirty=true;
 history:{scene:string;phase:number;time:number}[]=[];errors:string[]=[];renderTimes:number[]=[];frameIntervals:number[]=[];lastStamp=0;
 constructor(){
  const canvas=document.querySelector<HTMLCanvasElement>('#stage')!;canvas.tabIndex=-1;this.renderer=new Renderer(canvas);this.worlds=new WorldManager();
  this.hud=new HUD(document.querySelector('#app')!,{next:()=>this.next(),previous:()=>this.previous(),explore:()=>this.toggleExplore(),view:v=>this.setView(v),depth:d=>this.setDepth(d),go:id=>this.goTo(id,0,true),quality:q=>this.setQuality(q),auto:()=>this.toggleAuto(),notes:()=>{this.notes=!this.notes;this.draw();},reset:()=>this.restart()});
  const query=new URLSearchParams(location.search),id=query.get('scene');if(id){const n=SCENES.findIndex(s=>s.id===id);if(n>=0)this.index=n;}this.phase=finitePhase(Number(query.get('phase')||1));this.capture=query.has('capture');
  addEventListener('resize',()=>this.draw());addEventListener('keydown',e=>this.key(e));addEventListener('error',e=>this.errors.push(e.message));addEventListener('unhandledrejection',e=>this.errors.push(String(e.reason)));
  let drag:{x:number;y:number}|undefined;
  canvas.addEventListener('pointerdown',e=>{if(!this.explore)return;drag={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag||!this.explore)return;this.frame.camera.orbit(-(e.clientX-drag.x)*.004,-(e.clientY-drag.y)*.004);this.exploreCamera=structuredClone(this.frame.camera.state);drag={x:e.clientX,y:e.clientY};this.draw();});
  canvas.addEventListener('pointerup',()=>drag=undefined);canvas.addEventListener('pointercancel',()=>drag=undefined);
  canvas.addEventListener('wheel',e=>{if(!this.explore)return;e.preventDefault();this.frame.camera.zoom(e.deltaY*.0009);this.exploreCamera=structuredClone(this.frame.camera.state);this.draw();},{passive:false});
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();this.hud.message('\u56fe\u5f62\u4e0a\u4e0b\u6587\u4e22\u5931\uff0c\u8bf7\u5237\u65b0\u540e\u4f7f\u7528 SAFE \u753b\u8d28\u3002');});
  this.draw();this.record();requestAnimationFrame(t=>this.tick(t));
 }
 get def(){return SCENES[this.index];}
 record(){this.history.push({scene:this.def.id,phase:this.phase,time:performance.now()});if(this.history.length>256)this.history.splice(0,this.history.length-256);}
 ui():HUDState{return{explore:this.explore,view:this.view,playing:!!this.animation,capture:this.capture,notes:this.notes,quality:this.renderer.quality,auto:this.auto,fullAuto:this.fullAuto,sceneIndex:this.index};}
 draw(){
  const begin=performance.now();let patch=scenePatch(this.def,this.phase);
  if(this.explore)patch={...patch,depth:this.depth,field:this.view==='exploded'?0:1,bias:1,interfaces:2,explosion:this.view==='exploded'?1:0,morph:1,approach:clamp((this.depth+1)/1.1),mux:0};
  this.state=deriveState(this.def.id,patch,this.phase,this.phase*this.def.duration,this.ambient.sample(this.def.id,performance.now(),this.capture,this.captureAmbient,this.explore));
  const ui=this.ui();this.hud.prepare(this.def,this.state,ui);this.renderer.resize(innerWidth,innerHeight);
  this.frame=this.worlds.get(this.def,this.state,this.explore?this.view:undefined,this.exploreCamera);
  this.renderer.frame(this.frame.root,this.frame.camera,this.frame.other);this.hud.update(this.def,this.state,ui,this.frame);this.dirty=false;
  this.renderTimes.push(performance.now()-begin);if(this.renderTimes.length>180)this.renderTimes.shift();
 }
 
 /** Synchronized from the uploaded final presentation; loops are interruptible. */
 tick(stamp:number){
   if(!this.capture&&!this.explore&&AMBIENT_SCENES.has(this.def.id))this.dirty=true;
   if(this.animation){
     const a=this.animation,t=clamp((stamp-a.start)/a.duration);
     this.phase=a.from+(a.to-a.from)*t;
     if(t>=1){
       this.phase=a.to;this.record();
       if(this.fullAuto){
         if(a.to>=.99999){this.animation=undefined;this.scheduleAdvance();}
         else this.animation={from:0,to:1,start:stamp,duration:Math.max(1,this.def.duration*1000)};
       }else if(!this.capture&&!this.explore&&this.def.duration>0){
         const to=a.to>=.99999?0:1;
         this.loopDirection=to>this.phase?1:-1;
         this.animation={from:this.phase,to,start:stamp,duration:Math.max(1,this.def.duration*1000)};
       }else this.animation=undefined;
     }
     this.dirty=true;
   }
   if(this.explore&&this.auto){
     this.depth=-Math.cos((stamp-this.autoStart)/11000*Math.PI*2);this.dirty=true;
   }
   if(this.dirty){
     if(this.lastStamp)this.frameIntervals.push(stamp-this.lastStamp);
     if(this.frameIntervals.length>180)this.frameIntervals.shift();
     this.lastStamp=stamp;this.draw();
   }else this.lastStamp=0;
   requestAnimationFrame(t=>this.tick(t));
 }

 scheduleAdvance(){clearTimeout(this.autoTimer);this.autoTimer=window.setTimeout(()=>{if(this.fullAuto&&!this.capture&&!this.explore)this.next(false);},1000);}
 
 /** Synchronized from the uploaded final presentation; loops are interruptible. */
 animate(){
   if(this.def.duration<=0){this.phase=1;this.animation=undefined;this.record();this.draw();return;}
   if(this.capture||this.explore){this.animation=undefined;this.draw();return;}
   this.loopDirection=1;
   this.animation={from:this.phase,to:1,start:performance.now(),duration:Math.max(1,this.def.duration*1000*Math.max(.001,1-this.phase))};
   this.dirty=true;this.draw();
 }

 finish(){this.animation=undefined;this.phase=1;this.record();this.draw();if(this.fullAuto)this.scheduleAdvance();}
 
 /** Synchronized from the uploaded final presentation; loops are interruptible. */
 next(manual=true){
   if(this.explore)return;
   if(manual){this.fullAuto=false;clearTimeout(this.autoTimer);}
   this.animation=undefined;
   const scenes=SCENES;
   if(this.index<scenes.length-1){
     this.index++;this.phase=0;this.loopDirection=1;this.ambient.reset();this.record();
     if(!this.capture)this.startPresentationLoop(false);else this.draw();
   }else{
     this.fullAuto=false;
     if(!this.capture&&this.def.duration>0)this.startPresentationLoop(true);else this.draw();
   }
 }

 
 /** Synchronized from the uploaded final presentation; loops are interruptible. */
 previous(){
   if(this.explore)return;
   this.fullAuto=false;clearTimeout(this.autoTimer);this.animation=undefined;
   if(this.index>0)this.index--;
   this.phase=0;this.loopDirection=1;this.ambient.reset();this.record();
   if(!this.capture&&this.def.duration>0)this.startPresentationLoop(false);else this.draw();
 }

 
 /** Synchronized from the uploaded final presentation; loops are interruptible. */
 goTo(id:string,phase=1,play=false){
   const i=SCENES.findIndex(s=>s.id===id);if(i<0)throw Error('Unknown scene '+id);
   this.stop();this.explore=false;this.saved=undefined;this.exploreCamera=undefined;this.index=i;this.ambient.reset();
   phase=finitePhase(phase);
   this.phase=this.capture?phase:(this.def.duration>0?(phase>=.99999?0:phase):phase);
   this.loopDirection=1;this.record();
   if(!this.capture&&this.def.duration>0)this.startPresentationLoop(false);else this.draw();
 }

 seek(phase:number){if(!Number.isFinite(phase))return;this.stop();this.phase=clamp(phase);this.draw();}
 
 /** Synchronized from the uploaded final presentation; loops are interruptible. */
 restart(){
   this.stop();this.ambient.reset();
   if(this.explore){this.depth=-.4;this.exploreCamera=undefined;this.draw();return;}
   this.phase=0;this.loopDirection=1;
   if(!this.capture&&this.def.duration>0)this.startPresentationLoop(false);else this.draw();
 }

 
 /** Synchronized from the uploaded final presentation; loops are interruptible. */
 toggleExplore(force?:boolean){
   const was=this.explore;this.toggleExploreBase(force);
   if(was&&!this.explore&&!this.capture&&this.def.duration>0)this.startPresentationLoop(false);
 }

 setView(v:string){if(!['device','field','micro','nano','signal','exploded'].includes(v))return;if(!this.explore)this.toggleExplore(true);this.view=v;this.exploreCamera=undefined;this.draw();}
 setDepth(d:number){if(!Number.isFinite(d))return;if(!this.explore)this.toggleExplore(true);this.depth=clamp(d,-1,1);this.auto=false;this.draw();}
 toggleAuto(){if(!this.explore)return;this.auto=!this.auto;this.autoStart=performance.now()-Math.acos(-this.depth)/Math.PI/2*11000;this.dirty=true;this.draw();}
 setQuality(q:string){if(!['high','medium','safe'].includes(q))return;this.renderer.quality=q;this.draw();}
 setCaptureMode(v=true){if(v)this.stop();this.capture=v;this.draw();}
 setAmbientTime(seconds:number){if(!Number.isFinite(seconds))return;this.captureAmbient=Math.max(0,seconds);this.draw();}
 stop(){this.animation=undefined;this.auto=false;this.fullAuto=false;clearTimeout(this.autoTimer);}
 
 /** Synchronized from the uploaded final presentation; loops are interruptible. */
 playAll(){
   if(this.capture)return;
   if(this.explore)this.toggleExplore(false);
   this.fullAuto=true;clearTimeout(this.autoTimer);this.animation=undefined;
   if(this.def.duration<=0){this.draw();this.scheduleAdvance();return;}
   if(this.phase>=.99999)this.phase=0;
   this.loopDirection=1;
   this.animation={from:this.phase,to:1,start:performance.now(),duration:Math.max(1,this.def.duration*1000*Math.max(.001,1-this.phase))};
   this.dirty=true;this.draw();
 }

 key(e:KeyboardEvent){if(e.repeat||e.ctrlKey||e.metaKey||e.altKey)return;const el=e.target as HTMLElement|null;if(e.key!=='Escape'&&el&&(el.isContentEditable||el.closest?.('input,select,textarea,button,a[href],[contenteditable],[role=button],[role=textbox],[role=slider]')))return;
  const k=e.key.toLowerCase();if([' ','arrowright','arrowleft','home','end','escape','pageup','pagedown'].includes(k))e.preventDefault();
  if([' ','arrowright','pagedown'].includes(k))this.next();else if(['arrowleft','pageup'].includes(k))this.previous();else if(k==='home')this.goTo('S00');else if(k==='end')this.goTo('S22');else if(k==='r')this.restart();else if(k==='e')this.toggleExplore();else if(k==='t'){this.notes=!this.notes;this.draw();}else if(k==='g')this.hud.toggleMenu();else if(k==='escape'){this.hud.closeModals();if(this.explore)this.toggleExplore(false);}else if(k==='p'&&!this.explore){if(this.fullAuto){this.fullAuto=false;clearTimeout(this.autoTimer);}else this.playAll();}else if(k==='a'&&this.explore)this.toggleAuto();else if(this.explore&&['v','f','m','n','s','x'].includes(k))this.setView(({v:'device',f:'field',m:'micro',n:'nano',s:'signal',x:'exploded'} as Record<string,string>)[k]);
 }
 snapshot(){return{scene:this.def.id,index:this.index,phase:this.phase,model:structuredClone(this.state),camera:structuredClone(this.frame.camera.state),mode:this.explore?'explore':'presentation',view:this.view,notes:this.notes,quality:this.renderer.quality,playing:!!this.animation};}
 diagnostics(){const median=(xs:number[])=>{const a=[...xs].sort((a,b)=>a-b);return a.length?a[Math.floor(a.length/2)]:0;};return{...this.renderer.diagnostics(),...this.hud.diagnostics(),scene:this.def.id,phase:this.phase,mode:this.explore?'explore':'presentation',world:this.frame.world,ambient:{scene:this.ambient.scene,seconds:this.state.ambientTime,capture:this.capture,active:!this.explore&&AMBIENT_SCENES.has(this.def.id)},subjectBounds:this.frame.subjectBounds,rafMedianMs:median(this.frameIntervals),cpuRenderMedianMs:median(this.renderTimes),errors:[...this.errors,...this.renderer.error],ready:true,sceneCount:SCENES.length,model:this.state.interaction,geometry:this.worlds.diagnostics()};}
}
if(typeof document!=='undefined')try{const app=new ProxiTouchApp();Object.assign(window,{__PT:{ready:true,app,scenes:SCENES.map(s=>({id:s.id,beats:s.beats.length,duration:s.duration,world:s.world})),goTo:(id:string,phase=1)=>app.goTo(id,phase),seek:(p:number)=>app.seek(p),next:()=>app.next(),previous:()=>app.previous(),restart:()=>app.restart(),explore:(force?:boolean)=>app.toggleExplore(force),view:(v:string)=>app.setView(v),setDepth:(v:number)=>app.setDepth(v),quality:(q:string)=>app.setQuality(q),captureMode:(v=true)=>app.setCaptureMode(v),ambientTime:(seconds:number)=>app.setAmbientTime(seconds),snapshot:()=>app.snapshot(),diagnostics:()=>app.diagnostics(),render:()=>app.draw(),flush:()=>app.renderer.gl.finish(),stop:()=>app.stop(),playAll:()=>app.playAll(),version:'3.0.0',repeatAnimationPatch:true,repeatAnimationMode:'finite scenes: A-B-A ping-pong; native ambient scenes unchanged; manual Next interrupts'}});if(!app.capture&&!app.explore&&app.def.duration>0)app.startPresentationLoop(true);}
catch(e){document.querySelector('#app')!.innerHTML='<div class="error-screen"><h1>WebGL2</h1><p>'+String(e)+'</p></div>';console.error(e);}
