import {Node,Mesh,InstancedMesh,Material,metals,mesh,fieldMaterial} from '../engine/scene.js';
import {roundedBox,TubeGeometry,sphere} from '../engine/geometry.js';
import {Vec3,hex,clamp,mix,rng} from '../engine/math.js';
import {compositeWeights} from '../app/ambient.js';
export class CompositeCapacitor extends Node {
 blocks:Mesh[]=[];speckles:InstancedMesh[]=[];last='';weights={region:0,layer:0,material:0};
 constructor(){super();mesh(this,roundedBox(5.6,.22,3.7,.075),metals.silver,[0,0,0]);mesh(this,roundedBox(5.6,.22,3.7,.075),metals.silver,[0,2.30,0]);
  // Four dielectric volumes: full-height left/right branches, with only the centre branch split along the field direction.
  this.blocks.push(mesh(this,roundedBox(1.70,1.99,3.42,.055,5),new Material(0xb4c7cf,{roughness:.62,opacity:.62,softness:.2}),[-1.77,1.17,0]));
  this.blocks.push(mesh(this,roundedBox(1.70,.98,3.42,.055,5),new Material(0xb4c7cf,{roughness:.62,opacity:.62,softness:.2}),[0,.665,0]));
  this.blocks.push(mesh(this,roundedBox(1.70,.98,3.42,.055,5),new Material(0xb4c7cf,{roughness:.62,opacity:.62,softness:.2}),[0,1.675,0]));
  this.blocks.push(mesh(this,roundedBox(1.70,1.99,3.42,.055,5),new Material(0xb4c7cf,{roughness:.62,opacity:.62,softness:.2}),[1.77,1.17,0]));
  // Fixed-seed, low-contrast inclusions make the heterogeneous-material stage deterministic rather than noisy or fluid-like.
  const random=rng(51005),dotGeo=sphere(.052,10,7);
  for(const [x,color] of [[-1.77,0x77b88f],[1.77,0xd89a9f]] as [number,number][]){
   const dots=this.add(new InstancedMesh(dotGeo,new Material(color,{roughness:.8,opacity:0,emission:.015}),28));dots.castShadow=false;
   for(let i=0;i<28;i++)dots.set(i,[x+(random()-.5)*1.35,.25+random()*1.80,(random()-.5)*2.85],[0,0,0],[.65+random()*.8,.65+random()*.8,.65+random()*.8]);
   this.speckles.push(dots);
  }
  const g=new TubeGeometry(15,24,5),f=mesh(this,g,fieldMaterial().clone({opacity:.6}));f.castShadow=false;const paths:Vec3[][]=[];
  for(let i=0;i<3;i++)for(let z=0;z<5;z++){const p:Vec3[]=[];for(let k=0;k<24;k++)p.push([(i-1)*1.77,.12+k/23*2.07,-1.35+z*.675]);paths.push(p);}g.update(paths,.012);
 }
 set(highlight:number){this.emphasize(highlight>=1?1:0,highlight>=2?1:0,highlight>=3?1:0);}
 setAmbient(seconds:number){const w=compositeWeights(seconds);this.emphasize(w.region,w.layer,w.material);}
 emphasize(region:number,layer:number,material:number){const key=[region,layer,material].map(x=>x.toFixed(3)).join(',');if(key===this.last)return;this.last=key;this.weights={region,layer,material};
  const base=hex(0xb7c7ce),cyan=hex(0x238fac),gold=hex(0xdca13b),green=hex(0x91c4a3),pink=hex(0xdca4ab);
  this.blocks.forEach((b,i)=>{
   const centre=i===1||i===2,upper=i===2;
   let c=base;
   if(centre)c=c.map((v,k)=>mix(v,cyan[k],region)) as Vec3;
   if(upper)c=c.map((v,k)=>mix(v,gold[k],layer)) as Vec3;
   if(i===0)c=c.map((v,k)=>mix(v,green[k],material)) as Vec3;
   if(i===3)c=c.map((v,k)=>mix(v,pink[k],material)) as Vec3;
   b.material.color=c;
   const active=Math.max(centre?region:0,upper?layer:0,(i===0||i===3)?material:0);
   const dim=Math.max(region,layer,material)*(1-active);
   b.material.opacity=mix(.60,.86,active)-.20*dim;
   b.material.emission=.10*(centre?region:0)+.12*(upper?layer:0)+.055*((i===0||i===3)?material:0);
  });
  this.speckles.forEach(s=>{s.material.opacity=.22*clamp(material);s.material.emission=.02+.03*clamp(material);});
 }
}
