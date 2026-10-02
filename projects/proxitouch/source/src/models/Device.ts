import { Node, Mesh, Material, metals, mesh, fieldMaterial } from '../engine/scene.js';
import { roundedBox, TubeGeometry } from '../engine/geometry.js';
import { Vec3, clamp, mix, hex } from '../engine/math.js';
import { MicroAssembly } from './Dome.js';
import { makeConductor } from './FringeField.js';
import { interaction } from '../physics/interaction.js';
import { revisionFieldData as data } from '../physics/revisionFieldData.js';
/** Revision 2 actual shared-electrode pixel. No annular independent Tx/Rx Halo. */
export class Device extends Node {
 substrate:Node;eh:Node;halo:Node;core:MicroAssembly;guard:Node;field:Mesh;fieldGeometry:TubeGeometry;conductor:Node;
 rails:Mesh[]=[];readout:Mesh;readoutGeometry:TubeGeometry;last='';paths:Vec3[][]=[];activeWindow='HC';
 readonly channelNodes:{HC:Node[];CB:Node[]};
 constructor(){
  super();this.name='ProxiTouch-shared-square-pixel';
  this.substrate=this.add(new Node());
  mesh(this.substrate,roundedBox(7.0,.28,7.0,.12,6),new Material(0xbccbd3,{roughness:.65,metalness:.08}));
  mesh(this.substrate,roundedBox(6.77,.065,6.77,.025,4),new Material(0xd1dce1,{roughness:.72}),[0,.17,0]);
  const supportMat=new Material(0xc2d5dc,{roughness:.74,opacity:.45,softness:.15});
  this.eh=this.add(new Node());this.eh.name='EH-four-addressable-boundaries';this.halo=this.eh;
  for(let side=0;side<4;side++){
   const r:Vec3=[0,side%2?Math.PI/2:0,0],p:Vec3=side%2?[side===1?3.15:-3.15,1.204,0]:[0,1.204,side===0?3.15:-3.15];
   this.rails.push(mesh(this.eh,roundedBox(6.05,.11,.39,.035,5),metals.blue.clone(),p,r));
   mesh(this.substrate,roundedBox(6.02,.87,.37,.035,3),supportMat.clone(),[p[0],.695,p[2]],r);
  }
  this.guard=this.add(new Node());this.guard.name='dielectric-separation';
  for(let side=0;side<4;side++)mesh(this.guard,roundedBox(4.43,.36,.17,.035,3),new Material(0xd0dde1,{roughness:.8,opacity:.65}),side%2?[side===1?2.14:-2.14,.40,0]:[0,.40,side===0?2.14:-2.14],[0,side%2?Math.PI/2:0,0]);
  this.core=this.add(new MicroAssembly());this.core.position=[0,.24,0];this.core.scale=[.62,.62,.62];
  this.channelNodes={HC:[this.eh,this.core.electrode],CB:[this.core.electrode,this.core.bottom]};
  mesh(this.substrate,roundedBox(1.35,.075,1.44,.07,4),new Material(0x536f80,{roughness:.67,metalness:.12}),[0,-.04,3.98]);
  for(let i=0;i<3;i++)mesh(this.substrate,roundedBox(.22,.014,.67,.006,3),new Material(0xb49b70,{metalness:.68,roughness:.48}),[(i-1)*.36,.006,4.24]);
  this.fieldGeometry=new TubeGeometry(48,56,5);this.field=mesh(this,this.fieldGeometry,fieldMaterial().clone({opacity:.68}));this.field.castShadow=false;
  this.readoutGeometry=new TubeGeometry(3,24,5);this.readout=mesh(this,this.readoutGeometry,new Material(0xbc8b41,{roughness:.65,opacity:.8,emission:.06}));this.readout.castShadow=false;
  this.conductor=this.add(makeConductor());this.conductor.scale=[2.1,.65,2.1];
  this.set(-1,0,.7,'hero');
 }
 set(depth:number,explosion=0,field=0,mode='hero',time=0){
  const key=[depth,explosion,field,mode].join(',');if(key===this.last)return;this.last=key;
  this.core.electrodeFilm.material.emission=this.core.bottom.material.emission=0;this.rails.forEach(r=>r.material.emission=0);
  const m=interaction(depth);this.core.set(depth,explosion,true);
  this.eh.position[1]=explosion*.16;this.guard.position[1]=explosion*.12;
  const cb=mode==='muxCB'||mode==='pressure',hc=mode==='muxHC'||mode==='hc';this.activeWindow=cb?'CB':'HC';
  const ec=this.core.electrodeFilm.material;
  ec.color=hex(cb?0xc0b599:hc?0x8cbbc9:0x9ebac6);ec.opacity=explosion>.1?mix(.30,.80,clamp(explosion)):['touch','pressure','signals','field'].includes(mode)?.25:hc?.54:.48;
  this.core.bottom.material.color=hex(cb?0xb8a779:0x879cac);this.core.bottom.material.opacity=hc?.38:1;
  this.rails.forEach(r=>{r.material.color=hex(cb?0x8dabbc:0x537e9e);r.material.opacity=mode==='pressure'?.60:mode==='muxCB'?.50:1;});
  this.field.visible=field>0&&mode!=='muxCB';this.field.material.opacity=field*.68;
  this.conductor.visible=['hc','touch','pressure','signals','field'].includes(mode)&&explosion<.15;
  const coverTop=.24+(this.core.planeY+.195)*.62;this.conductor.position=[0,coverTop+m.externalGap,0];
  this.conductor.traverse(n=>{if(n instanceof Mesh)n.material.opacity=['touch','pressure','signals'].includes(mode)?.57:.88;});
  const list=data.square,baseline=list[0];let a=baseline,b=baseline,t=0;
  if(this.conductor.visible){const d=this.conductor.position[1];const states=list.slice(1);if(d>=states[0].distance!){a=baseline;b=states[0];t=clamp((6.2-d)/(6.2-states[0].distance!));}else{const q=clamp((states[0].distance!-d)/(states[0].distance!-states.at(-1)!.distance!))*(states.length-1),i=Math.min(states.length-2,Math.floor(q));a=states[i];b=states[i+1];t=q-i;}}
  const paths:Vec3[][]=[];const ecTop=.24+(this.core.planeY+.07+explosion*1.8)*.62;
  for(let side=0;side<4;side++)for(let slice=0;slice<3;slice++)for(let line=0;line<4;line++){
   const affected=this.conductor.visible&&slice===1&&line>=2,points:Vec3[]=[];
   for(let k=0;k<56;k++){
    const aa=(affected?a:baseline).paths[line][k],bb=(affected?b:baseline).paths[line][k];let x=mix(aa[0],bb[0],t),y=mix(aa[1],bb[1],t);
    const receiver=!affected||((t<.5?a:b).ends[line]==='receiver');
    if(receiver)y+=(ecTop-1.244)*Math.pow(k/55,3);
    y+=explosion*.16*(1-k/55);const z=(slice-1)*1.24;
    points.push(side===0?[x,y,z]:side===1?[z,y,x]:side===2?[-x,y,z]:[z,y,-x]);
   }paths.push(points);
  }
  this.paths=paths;this.fieldGeometry.update(paths,.0115);
  this.readout.visible=mode==='muxCB';const rpaths:Vec3[][]=[];
  for(let i=0;i<3;i++){const p:Vec3[]=[];for(let k=0;k<24;k++)p.push([(i-1)*.78,mix(ecTop-.05,.24-explosion*.12*.62,k/23),.65]);rpaths.push(p);}this.readoutGeometry.update(rpaths,.019);
 }
 emphasizeMultiplex(cb:number){
  const color=(a:number,b:number,t:number)=>hex(a).map((v,k)=>mix(v,hex(b)[k],t)) as Vec3;
  this.activeWindow=cb>.5?'CB':'HC';
  this.rails.forEach(r=>{r.material.color=color(0x397ea2,0xa5b9c5,cb);r.material.opacity=mix(1,.42,cb);r.material.emission=.13*(1-cb);});
  this.core.electrodeFilm.material.color=color(0x78b2ca,0xc2a668,cb);
  this.core.electrodeFilm.material.opacity=.60;this.core.electrodeFilm.material.emission=.13;
  this.core.bottom.material.color=color(0xa4b6c1,0xc29a54,cb);this.core.bottom.material.opacity=mix(.38,1,cb);this.core.bottom.material.emission=.14*cb;
  this.field.visible=true;this.field.material.opacity=mix(.78,.16,cb);
  this.readout.visible=true;this.readout.material.opacity=.88*cb;
 }
 emphasizeShared(amount:number){this.core.electrodeFilm.material.emission=.14*amount;}

 diagnostics(){return {architecture:'EH-EC-EB',shape:'segmented-square',sharedEC:this.channelNodes.HC[1]===this.channelNodes.CB[0],EHsegments:4,centralDomes:this.core.domes.length,directFieldPaths:40,targetAffectedPaths:8,activeWindow:this.activeWindow,contactArea:this.core.area,membraneDeflection:this.core.deflection,ECbounds:'central only',EBbounds:'central only; not full-pixel ground plane'};}
}
