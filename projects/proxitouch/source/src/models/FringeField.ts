import { Node, Mesh, InstancedMesh, Material, metals, mesh, fieldMaterial } from '../engine/scene.js';
import { roundedBox, lathe, sphere, TubeGeometry, cylinder } from '../engine/geometry.js';
import { Vec3, clamp, mix, smooth } from '../engine/math.js';
import { revisionFieldData as data } from '../physics/revisionFieldData.js';
type FieldState={paths:number[][][];coupling:number};
export function fieldSample(approach:number) {
 const d=mix(6.0,.28,clamp(approach)),list=data.approach;
 if(d>=list[0].distance!)return {a:data.morph.at(-1)!,b:list[0],t:clamp((6-d)/(6-list[0].distance!)),distance:d};
 const x=clamp((list[0].distance!-d)/(list[0].distance!-list.at(-1)!.distance!))*(list.length-1),i=Math.min(list.length-2,Math.floor(x));
 return {a:list[i],b:list[i+1],t:x-i,distance:d};
}
export function mutualSignal(approach:number){const {a,b,t}=fieldSample(approach);return Math.abs(mix(a.coupling,b.coupling,t)/data.metadata.baselineCouplingArbitrary-1);}
export function makeConductor(){
 const p:[number,number][]=[[0,0],[.20,.035],[.39,.14],[.54,.31],[.615,.49],[.63,.63],[.63,2.35],[.61,2.55],[.52,2.76],[.33,2.92],[0,3]];
 const g=new Node();g.name='approaching-equivalent-target';
 mesh(g,lathe(p,56),new Material(0xc3c8c7,{metalness:0,roughness:.74,softness:.28,opacity:.91}));return g;
}
export class FringeField extends Node {
 tx:Mesh;rx:Mesh;pivot:Node;hinge:Mesh;conductor:Node;curves:Mesh[]=[];geometries:TubeGeometry[]=[];particles:InstancedMesh;
 paths:Vec3[][]=[];last='';signal=0;distance=6;directPathCount=30;targetCoupledPathCount=6;
 constructor(){
  super();const geom=roundedBox(3.4,.20,3.15,.065);
  this.tx=mesh(this,geom,metals.blue.clone(),[-1.85,.15,0]);this.tx.name='Tx';
  this.pivot=this.add(new Node());this.pivot.position=[0,1,0];this.pivot.name='fixed-book-spine';
  this.rx=mesh(this.pivot,geom,metals.silver.clone(),[-1.85,.85,0]);this.rx.name='Rx';
  // A finite-gap capacitor needs an offset spine to end coplanar after a pure half-turn.
  // The entire upper leaf/spine rotates about a fixed edge axis; no translational track.
  const spine=mesh(this.pivot,roundedBox(.10,.89,3.05,.03,4),new Material(0xc9d8df,{roughness:1,opacity:0}),[-.08,.40,0]);spine.castShadow=spine.receiveShadow=false;
  this.hinge=mesh(this,cylinder(.065,3.28,.015,32),new Material(0xcbd6dd,{opacity:.012,roughness:1,metalness:0,emission:0}),[0,1,0],[Math.PI/2,0,0]);this.hinge.castShadow=this.hinge.receiveShadow=false;
  this.conductor=this.add(makeConductor());
  for(let i=0;i<3;i++){const geo=new TubeGeometry(12,56,5);this.geometries.push(geo);const m=mesh(this,geo,fieldMaterial().clone({opacity:i===1?.88:.50}));m.castShadow=false;this.curves.push(m);}
  this.particles=this.add(new InstancedMesh(sphere(.033,10,7),new Material(0x639aba,{roughness:.7,emission:.18}),16));this.particles.castShadow=false;this.particles.name='ambient-field-flow';
  this.set(0,0,1,0);
 }
 set(morph:number,approach:number,intensity=1,time=0,targetAlways=false,ambientFlow=false){
  const q=clamp(morph),key=[q,approach,intensity,targetAlways].join(',');
  if(key!==this.last){
   this.last=key;this.pivot.rotation[2]=-Math.PI*q;this.hinge.visible=q<.999;this.pivot.children[1].visible=false;
   let a:FieldState,b:FieldState,t:number;
   if(approach>0&&q>.999){const sample=fieldSample(approach);a=sample.a;b=sample.b;t=sample.t;this.distance=sample.distance;}
   else{const x=q*(data.morph.length-1),i=Math.min(data.morph.length-2,Math.floor(x));a=data.morph[i];b=data.morph[i+1];t=x-i;this.distance=6;}
   this.signal=mutualSignal(approach);this.conductor.visible=targetAlways||approach>.015;
   this.conductor.position=[0,.25+this.distance,0];
   this.conductor.traverse(n=>{if(n instanceof Mesh)n.material.opacity=targetAlways?.88:.91*smooth(clamp((approach-.015)/.08));});
   this.paths=[];const baseline=data.morph.at(-1)!;
   for(let slice=0;slice<3;slice++){
    const paths:Vec3[][]=[];
    for(let l=0;l<12;l++){
     const affected=approach>0&&slice===1&&l>=3&&l<9;
     const points:Vec3[]=[];
     for(let k=0;k<56;k++){
      const useBase=approach>0&&!affected;const ap=useBase?baseline.paths[l][k]:a.paths[l][k],bp=useBase?ap:b.paths[l][k];
      let x=mix(ap[0],bp[0],t),y=mix(ap[1],bp[1],t);
      // Finite-width target: off-centre sections remain directly coupled and bend mildly.
      if(useBase)y+=.12*approach*Math.sin(k/55*Math.PI)**2;
      let z=(slice-1)*1.08;
      if(useBase&&slice===1){const bottom=.25+this.distance,top=bottom+3,gate=smooth(clamp((y-bottom+.25)/.45))*smooth(clamp((top+.25-y)/.45));z=(l<3?-1:1)*1.10*Math.exp(-((x/.85)**2))*gate;}
      points.push([x,y,z]);
     }
     paths.push(points);this.paths.push(points);
    }
    this.geometries[slice].update(paths,slice===1?.014:.011);
    this.curves[slice].visible=intensity>0;this.curves[slice].material.opacity=intensity*(slice===1?.84:.53);
   }
  }
  this.particles.visible=q>.98&&intensity>0&&approach<.01;
  // Spread across depth slices and low / middle / highest arcs, with staggered phases.
  this.particles.count=ambientFlow?16:8;
  const tracks=[0,13,26,3,16,29,6,19,32,9,22,35,12,25,4,18];
  for(let i=0;i<this.particles.count;i++){const path=this.paths[ambientFlow?tracks[i]:12+i+2];if(!path)continue;
   if(!ambientFlow){this.particles.set(i,path[Math.floor(((i*.117+time*.07)%1)*55)]);continue;}
   const q=((i*.381966+time*(.072+(i%3)*.006))%1)*55,k=Math.floor(q),f=q-k;
   const a=path[k],b=path[Math.min(55,k+1)];this.particles.set(i,a.map((v,j)=>mix(v,b[j],f)) as Vec3,[0,0,0],[1.21,1.21,1.21]);
  }
 }
 diagnostics(){return {hinge:[...this.pivot.position],angle:this.pivot.rotation[2],directPaths:this.directPathCount,targetAffectedPaths:this.targetCoupledPathCount,flowIndicators:this.particles.count,indicatorMeaning:'coupling-path guide; not free air charge transport',hingeOpacity:this.hinge.material.opacity,solver:data.metadata.model};}
}
