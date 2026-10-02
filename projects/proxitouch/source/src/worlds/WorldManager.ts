import {Node,Mesh,InstancedMesh,Material,mesh} from '../engine/scene.js';
import {Geometry,plane} from '../engine/geometry.js';
import {CameraRig,CameraState} from '../engine/camera.js';
import {Vec3,Mat4,clamp,mix,smooth,normalize,cross,transform,multiply} from '../engine/math.js';
import {ModelState} from '../app/state.js';
import {SceneDefinition,sceneCamera} from '../scenes/definitions.js';
import {Capacitor} from '../models/Capacitor.js';
import {CompositeCapacitor} from '../models/CompositeCapacitor.js';
import {FringeField} from '../models/FringeField.js';
import {IonicVolume} from '../models/IonicVolume.js';
import {MicroAssembly} from '../models/Dome.js';
import {Device} from '../models/Device.js';
import {ApplicationHero} from '../models/ApplicationHero.js';
import {multiplexWeight} from '../app/ambient.js';
import {SharedArray} from '../models/SharedArray.js';
export interface LabelSpec{title:string;detail?:string;node?:Node;point:Vec3;offset?:[number,number];priority?:number;emphasis?:number;tone?:'blue'|'gold';}
export interface Frame{root:Node;camera:CameraRig;other?:{root:Node;camera:CameraRig;blend:number};labels:LabelSpec[];scale:string;world:string;subjectBounds?:number[];}
class World{
 root=new Node();content=new Node();camera=new CameraRig();
 constructor(){const floor=mesh(this.root,plane(120),new Material(0xe4ebf0,{roughness:.94,patterned:2}),[0,-.33,0]);floor.castShadow=false;this.root.add(this.content);}
}
const cache=new WeakMap<Geometry,{version:number;corners:Vec3[]}>();
function geometryCorners(g:Geometry){let item=cache.get(g);if(item?.version===g.version)return item.corners;
 const lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];for(let i=0;i<g.data.length;i+=8)for(let k=0;k<3;k++){lo[k]=Math.min(lo[k],g.data[i+k]);hi[k]=Math.max(hi[k],g.data[i+k]);}
 const corners:Vec3[]=[];for(const x of [lo[0],hi[0]])for(const y of [lo[1],hi[1]])for(const z of [lo[2],hi[2]])corners.push([x,y,z]);cache.set(g,{version:g.version,corners});return corners;
}
function subjectPoints(root:Node):Vec3[]{root.update(root.parent?.world);const out:Vec3[]=[];root.traverse(n=>{if(!(n instanceof Mesh)||n.material.opacity<.08||n.name==='ambient-field-flow')return;const corners=geometryCorners(n.geometry);
 if(n instanceof InstancedMesh){for(let i=0;i<n.count;i++){if(n.colors[i*4+3]<.08)continue;const matrix=multiply(n.world,n.matrices.subarray(i*16,i*16+16));for(const p of corners)out.push(transform(matrix,p));}}
 else for(const p of corners)out.push(transform(n.world,p));});return out;
}
function fit(source:CameraState,points:Vec3[],rect:DOMRect,margin=.06):CameraState{
 if(!points.length)return source;
 const c=structuredClone(source),r=new CameraRig();r.aspect=innerWidth/innerHeight;
 const left=(rect.left+rect.width*margin)/innerWidth,right=(rect.right-rect.width*margin)/innerWidth,top=(rect.top+rect.height*margin)/innerHeight,bottom=(rect.bottom-rect.height*margin)/innerHeight;
 for(let i=0;i<4;i++){
  r.set(c);let xs=points.map(p=>r.project(p,1,1).x),ys=points.map(p=>r.project(p,1,1).y);
  const factor=clamp(Math.max((Math.max(...xs)-Math.min(...xs))/(right-left),(Math.max(...ys)-Math.min(...ys))/(bottom-top)),.3,4);
  c.position=c.position.map((v,k)=>c.target[k]+(v-c.target[k])*factor) as Vec3;
  r.set(c);xs=points.map(p=>r.project(p,1,1).x);ys=points.map(p=>r.project(p,1,1).y);
  c.offset=(c.offset||0)+Math.min(...xs)+Math.max(...xs)-left-right;
  const distance=Math.hypot(...c.position.map((v,k)=>v-c.target[k])),forward=normalize(c.target.map((v,k)=>v-c.position[k]) as Vec3),rightV=normalize(cross(forward,[0,1,0])),up=normalize(cross(rightV,forward));
  const shift=(top+bottom-Math.min(...ys)-Math.max(...ys))/2*2*distance*Math.tan(c.fov*Math.PI/360);
  c.position=c.position.map((v,k)=>v+up[k]*shift) as Vec3;c.target=c.target.map((v,k)=>v+up[k]*shift) as Vec3;
 }
 return c;
}
export const CLASSIC_POSITIONS:Vec3[]=[[-6.2,0,0],[-.8,0,0],[6.2,0,0]];
export class WorldManager {
 macro=new World();micro=new World();nano=new World();deviceWorld=new World();application=new World();
 cap:Capacitor;fringe:FringeField;composite:CompositeCapacitor;trio:Node;trioCaps:Capacitor[]=[];circuits:Node;parallel:Capacitor;series:Capacitor;
 question:Node;questionField:FringeField;questionMicro:MicroAssembly;macroIonic:IonicVolume;microIonic:IonicVolume;nanoVolume:IonicVolume;microStructure:MicroAssembly;
 device:Device;array:SharedArray;grasp:ApplicationHero;
 constructor(){
  this.cap=this.macro.content.add(new Capacitor());this.fringe=this.macro.content.add(new FringeField());this.composite=this.macro.content.add(new CompositeCapacitor());
  this.trio=this.macro.content.add(new Node());for(let i=0;i<3;i++){const c=this.trio.add(new Capacitor());c.position=[...CLASSIC_POSITIONS[i]];c.scale=[.80,.80,.80];this.trioCaps.push(c);}
  this.circuits=this.macro.content.add(new Node());this.parallel=this.circuits.add(new Capacitor());this.series=this.circuits.add(new Capacitor());this.parallel.position=[-3.2,0,0];this.series.position=[3.2,0,0];
  this.question=this.macro.content.add(new Node());this.questionField=this.question.add(new FringeField());this.questionMicro=this.question.add(new MicroAssembly());this.questionField.scale=[.66,.66,.66];this.questionMicro.scale=[.65,.65,.65];
  this.macroIonic=this.macro.content.add(new IonicVolume(true));this.microIonic=this.micro.content.add(new IonicVolume(true));this.nanoVolume=this.nano.content.add(new IonicVolume());this.microStructure=this.micro.content.add(new MicroAssembly());
  this.device=this.deviceWorld.content.add(new Device());this.array=this.application.content.add(new SharedArray());this.grasp=this.application.content.add(new ApplicationHero());
 }
 activate(w:World,object:Node){w.content.children.forEach(n=>n.visible=n===object);}
 get(def:SceneDefinition,s:ModelState,view?:string,override?:CameraState):Frame{
  let world=this.macro,kind=def.world,labels:LabelSpec[]=[],other:Frame['other'],camera=sceneCamera(def,s.phase),scale='';
  let secondary:World|undefined,blend=0;
  const L=(title:string,node:Node,point:Vec3,offset:[number,number]=[50,25],priority=0,detail?:string)=>labels.push({title,node,point,offset,priority,detail});
  if(view){kind=view==='field'?(def.part==='I'?'fringe':'device-field'):view==='micro'?'micro':view==='nano'?'interfaces':view==='signal'?'signals':view==='exploded'?'structure':'device';camera={position:view==='nano'?[7.2,4.3,11.5]:[8.8,6.3,13],target:[0,.9,0],fov:34,offset:0};}
  const cs={gap:s.gap,overlap:s.overlap,dielectric:s.dielectric,partition:s.partition,field:s.field,charges:s.charges};
  if(kind==='capacitor'){
   this.activate(world,this.cap);this.cap.set(cs);
   if(def.id==='S02'){const stage=s.phase<.33?'d':s.phase<.66?'A':'\u03b5';L(stage,this.cap,stage==='d'?[2.5,s.gap/2+.12,1.4]:stage==='A'?[.8,.15,1.5]:[.3,s.gap/2+.12,1.4],[40,30]);}
   else{L('\u7535\u6781',this.cap.top,[1.8,0,1.3],[55,-25]);if(s.field>.3)L('\u7535\u573a',this.cap,[1.5,s.gap/2,1.35],[65,60]);}
  }else if(kind==='classics'){
   this.activate(world,this.trio);this.trioCaps.forEach((c,i)=>c.set({gap:i===0?.68:1.4,overlap:i===1?.55:1,dielectric:i===2?1:0,partition:0,field:.8,charges:0}));
   ['\u95f4\u8ddd d','\u9762\u79ef A','\u4ecb\u7535\u5e38\u6570 \u03b5'].forEach((x,i)=>L(x,this.trioCaps[i],[0,0,1.75],[-30,55]));
  }else if(kind==='circuits'){
   this.activate(world,this.circuits);this.parallel.set({...cs,gap:1.7,overlap:1,partition:1,field:.8,charges:0});this.series.set({...cs,gap:1.7,overlap:1,partition:2,field:.8,charges:0});
   L('\u9762\u79ef\u5206\u533a\uff1a\u5e76\u8054',this.parallel,[0,.6,1.6],[-20,55]);L('\u6cbf\u573a\u5206\u5c42\uff1a\u4e32\u8054',this.series,[0,.6,1.6],[-20,55]);
  }else if(kind==='composite'){
   this.activate(world,this.composite);this.composite.setAmbient(s.ambientTime);L('\u9762\u79ef\u65b9\u5411\u5206\u533a i',this.composite.blocks[1],[0,0,1.72],[-115,60]);L('\u7535\u573a\u65b9\u5411\u5206\u5c42 j',this.composite.blocks[2],[0,0,1.72],[65,-20]);
  }else if(kind==='fringe'||kind==='cover'){
   this.activate(world,this.fringe);this.fringe.set(kind==='cover'?1:s.morph,view?clamp((s.depth+1)/1.04):s.approach,s.field,def.id==='S07'&&!view?s.ambientTime:s.time,def.id==='S08'||!!view,def.id==='S07'&&!view);
   if(kind!=='cover'){L('Tx',this.fringe.tx,[-1,0,1.55],[-65,45]);L('Rx',this.fringe.rx,[1,0,1.55],[40,45]);if(this.fringe.conductor.visible)L('\u4eba\u4f53\u7b49\u6548\u76ee\u6807',this.fringe.conductor,[.5,1.5,0],[55,-25]);}
  }else if(kind==='edl'){
   const level=clamp(s.scale,0,2);this.activate(this.macro,this.macroIonic);this.activate(this.micro,this.microIonic);this.activate(this.nano,this.nanoVolume);
   this.nanoVolume.resetEmphasis();this.macroIonic.set(0,true,0);this.microIonic.set(0,true,1);this.nanoVolume.set(s.bias,true,1);
   world=level<1?this.macro:this.micro;secondary=level<1?this.micro:this.nano;blend=smooth(level<1?level:level-1);
   if(level>=2){world=this.nano;secondary=undefined;}
   scale=level<.65?'mm \u00b7 \u5b8f\u89c2':level<1.65?'\u03bcm \u00b7 \u5fae\u89c2':'nm \u00b7 \u754c\u9762\u5c3a\u5ea6\u793a\u610f';
   if(s.bias>.15){L('\u4e0a\u754c\u9762 EDL',this.nanoVolume.interfaceTop,[1.5,0,1.35],[45,-30]);L('\u4e0b\u754c\u9762 EDL',this.nanoVolume.interfaceBottom,[1.8,0,1.45],[50,45]);}
  }else if(kind==='interfaces'){
   world=this.nano;this.activate(world,this.nanoVolume);
   if(view){
    const upper=s.interaction.contact?clamp(.12+s.interaction.areaNormalized):0,gap=.65*(1-s.interaction.membraneClosure);
    this.nanoVolume.resetEmphasis();this.nanoVolume.set(1,true,1,0,upper,gap);
    L(upper?'\u53ef\u53d8\u4e0a\u754c\u9762':'\u4e0a\u754c\u9762\u5c1a\u672a\u63a5\u89e6',this.nanoVolume.top,[1.45,-.12,1.2],[50,-30]);L('\u7a33\u5b9a\u4e0b\u754c\u9762',this.nanoVolume.interfaceBottom,[1.8,0,1.45],[45,50]);
   }else{
    const screening=smooth(clamp((s.phase-.10)/.30)),compression=smooth(clamp((s.phase-.55)/.45));
    this.nanoVolume.set(1,true,1,0,1,0,compression);this.nanoVolume.setScreening(screening);
    L('\u4e0a\u90e8 EDL',this.nanoVolume.interfaceTop,[1.45,0,1.2],[50,-30]);L('\u4e0b\u90e8 EDL',this.nanoVolume.interfaceBottom,[1.8,0,1.45],[45,50]);
    if(screening>.12)L('\u4f53\u76f8\u8fd1\u4f3c\u7535\u4e2d\u6027',this.nanoVolume,[0,1.42,1.45],[85,5],1,'\u5b8f\u89c2\u7535\u573a\u88ab\u5c4f\u853d \u00b7 E \u2248 0');
    if(compression>.06)L('d\u2082 < d\u2081',this.nanoVolume,[2.55,1.45,-1.45],[80,20],1,'\u0394C \u2248 0');
   }
  }else if(kind==='micro'){
   world=this.micro;this.activate(world,this.microStructure);this.microStructure.set(s.depth,0,true);
   L(view?'\u67d4\u6027 EC':'\u67d4\u6027\u4e0a\u7535\u6781',this.microStructure.electrode,[2.5,-this.microStructure.deflection,2.5],[55,-45]);
   if(s.interaction.contact)L('\u6709\u6548\u63a5\u89e6\u9762\u79ef A_eff',this.microStructure.patches[s.interaction.pressure>.2?8:0],[0,.012,0],[80,10]);
   else L('\u5fae\u5c0f\u7a7a\u6c14\u9699',this.microStructure,[2.4,1.44,2],[55,20]);
   L(view?'\u79bb\u5b50\u51dd\u80f6\u5fae\u7a79\u9876':'\u5fae\u7ed3\u6784',this.microStructure.domes[6],[0,.4,.3],[-170,60]);
  }else if(kind==='question'){
   this.activate(world,this.question);const q=smooth(clamp(s.phase/.72));this.questionField.position=[mix(-3.4,-1.1,q),0,0];this.questionMicro.position=[mix(3.4,1.1,q),0,0];this.questionField.set(1,0,.8,0);this.questionMicro.set(.55,0,false);
   this.activate(this.deviceWorld,this.device);this.device.set(-1,0,.6,'hero');secondary=this.deviceWorld;blend=smooth(clamp((s.phase-.55)/.45));
   if(s.phase<.55){L('\u7a7a\u95f4\u8fb9\u7f18\u573a',this.questionField,[0,1,1.5],[-50,60]);L('\u63a5\u89e6\u754c\u9762',this.questionMicro,[0,.7,2.5],[0,70]);}
  }else if(kind==='shared'){
   // Presentation never instantiates or renders LegacyDevice. S12 ends on this same world.
   world=this.deviceWorld;this.activate(world,this.device);this.device.set(-1,0,s.field,'hero');this.device.emphasizeShared(smooth(s.phase));
   if(s.phase>.025){L('\u5171\u4eab EC',this.device.core.electrode,[1.5,0,1.5],[40,-30]);L('EH',this.device.eh,[3.15,1.204,0],[35,45]);L('EB',this.device.core.bottom,[2.5,0,2.5],[40,65]);}
  }else if(kind==='grasp'){
   world=this.application;this.activate(world,this.grasp);this.grasp.set(s.depth);
  }else if(['array','surface','ending'].includes(kind)){
   world=this.application;this.activate(world,this.array);this.array.set(s.arrayCount,s.depth,s.merge,kind==='surface'||(kind==='array'&&s.phase<.94)?-1:s.scan,s.curvature,kind==='surface');
   if(kind==='array'&&s.merge>.95&&this.array.selected>=0){const p=this.array.centres[this.array.selected];L('\u9009\u4e2d EC',this.array,p,[45,-40]);const j=this.array.selectedEdges[0];if(j!==undefined){const m=this.array.boundaries.matrices;L('\u5171\u4eab\u8fb9\u754c',this.array,[m[j*16+12],m[j*16+13],m[j*16+14]],[60,55]);}}
   if(kind==='surface')L(s.interaction.contact?'\u5c40\u90e8\u538b\u529b\u5206\u5e03':'\u63a5\u8fd1\u54cd\u5e94\u5206\u5e03',this.array,[-1.1,.36,-1.1],[100,70]);
  }else{
   world=this.deviceWorld;this.activate(world,this.device);
   const modes:Record<string,string>={approach:'hc',touch:'touch',pressure:'pressure',signals:'signals','device-field':'field',structure:'structure',device:'hero'};
   const mode=kind==='multiplex'?'multiplex':(modes[kind]||'hero'),e=view==='exploded'?1:s.explosion;
   this.device.set(s.depth,e,s.field,mode,s.time);if(kind==='multiplex')this.device.emphasizeMultiplex(multiplexWeight(s.ambientTime));
   if(kind==='multiplex'){L('EH',this.device.eh,[3.15,1.204,0],[45,-25]);L('\u5171\u4eab EC',this.device.core.electrode,[2,0,1.5],[35,-35]);L('EB',this.device.core.bottom,[2.5,0,2.5],[50,40]);}
   else if(kind==='structure'){L('EH',this.device.eh,[3.15,1.204,0],[40,25]);L('\u67d4\u6027 EC',this.device.core.electrode,[-2.3,0,2.4],[-150,-35]);L('\u79bb\u5b50\u51dd\u80f6 / \u5fae\u7a79\u9876',this.device.core.domeGroup,[1.7,.6,1.7],[80,20]);L('EB',this.device.core.bottom,[2.5,0,2.5],[40,55]);L(e>.1?'\u7a7a\u6c14\u9699\uff08\u5c55\u5f00\u793a\u610f\uff09':'\u5fae\u5c0f\u7a7a\u6c14\u9699',this.device.core,[2.5,(this.device.core.planeY+1.34)/2+e*1.25,-1.5],[100,-45]);}
   else{L('EH',this.device.eh,[3.15,1.204,1.0],[35,30]);L('EC',this.device.core.electrode,[-2.5,-this.device.core.deflection,2.4],[-80,30]);
    if(s.interaction.contact)L('\u6709\u6548\u63a5\u89e6\u9762\u79ef',this.device.core.patches[s.interaction.pressure>.2?8:0],[0,.01,0],[50,-35]);
   }
  }
  world.root.update();if(secondary)secondary.root.update();
  const zone=document.querySelector<HTMLElement>('#model-zone')?.getBoundingClientRect()||new DOMRect(innerWidth*.36,innerHeight*.16,innerWidth*.60,innerHeight*.73);
  const points=subjectPoints(world.content);if(secondary)points.push(...subjectPoints(secondary.content));
  let fitted=fit(camera,points,zone,.10);
  if(kind==='question'&&secondary){
   const a=fit(camera,subjectPoints(world.content),zone,.10),b=fit(camera,subjectPoints(secondary.content),zone,.10);
   fitted={position:a.position.map((v,k)=>mix(v,b.position[k],blend)) as Vec3,target:a.target.map((v,k)=>mix(v,b.target[k],blend)) as Vec3,fov:mix(a.fov,b.fov,blend),offset:mix(a.offset||0,b.offset||0,blend)};
  }
  // Live highlights never change projection, and do not change the model state clock.
  if(kind==='composite')labels.forEach((l,i)=>{l.emphasis=i?this.composite.weights.layer:this.composite.weights.region;l.tone=i?'gold':'blue';});
  if(kind==='interfaces'&&!view){labels[0].emphasis=labels[1].emphasis=Math.max(.45,smooth(clamp((s.phase-.10)/.30)));labels[0].tone='blue';labels[1].tone='gold';}
  if(kind==='multiplex'){const cb=multiplexWeight(s.ambientTime);labels.forEach((l,i)=>{l.emphasis=i===0?1-cb:i===1?1:cb;l.tone=i===0?'blue':'gold';});}
  // Keep deliberate scale pushes and ending pullbacks after the safety fit.
  const distanceFactor=kind==='ending'?1+s.phase*.13:kind==='edl'?1.08-.04*s.scale:1;
  fitted.position=fitted.position.map((v,k)=>fitted.target[k]+(v-fitted.target[k])*distanceFactor) as Vec3;
  if(override)fitted=override;
  world.camera.aspect=innerWidth/innerHeight;world.camera.set(fitted);
  if(secondary){secondary.camera.aspect=innerWidth/innerHeight;secondary.camera.set(fitted);other={root:secondary.root,camera:secondary.camera,blend};}
  const projected=points.map(p=>world.camera.project(p,innerWidth,innerHeight));
  return {root:world.root,camera:world.camera,other,labels,scale,world:kind,subjectBounds:projected.length?[Math.min(...projected.map(x=>x.x)),Math.min(...projected.map(x=>x.y)),Math.max(...projected.map(x=>x.x)),Math.max(...projected.map(x=>x.y))]:[]};
 }
 diagnostics(){return {device:this.device.diagnostics(),array:this.array.diagnostics(),book:this.fringe.diagnostics(),application:this.grasp.diagnostics(),interfaces:this.nanoVolume.emphasis};}
}
