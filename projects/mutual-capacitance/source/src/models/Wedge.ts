import {Node,Mesh,Material,metals,mesh} from '../engine/scene.js';
import {box,TubeGeometry,Geometry} from '../engine/geometry.js';
import {Vec3} from '../engine/math.js';
import {P,SCALE,point,sectionWidth} from '../physics/model.js';
import type {Annotation} from './Experiment.js';
export class Wedge extends Node{
 arcs:Mesh;rays:Mesh;boundaries:Mesh;
 constructor(){super();const w=P.wedge,r0=w.inner_radius_m,r1=w.outer_radius_m,alpha=w.angle_deg*Math.PI/180,th=P.electrode_thickness_m;
 const plate=new Geometry([r0*SCALE,0,-sectionWidth*SCALE/2,0,1,0,0,0,r1*SCALE,0,-sectionWidth*SCALE/2,0,1,0,1,0,r1*SCALE,0,sectionWidth*SCALE/2,0,1,0,1,1,r0*SCALE,0,sectionWidth*SCALE/2,0,1,0,0,1],[0,2,1,0,3,2]);for(const t of[0,alpha]){const n=this.add(new Node());n.rotation[2]=t;mesh(n,plate,t?metals.blue.clone():metals.silver.clone());}
 const paths:Vec3[][]=[];for(const z of[-sectionWidth*.28,0,sectionWidth*.28])for(let i=0;i<7;i++){const r=r0+(r1-r0)*i/6;paths.push(Array.from({length:65},(_,j)=>{const t=alpha*j/64;return point(r*Math.cos(t),r*Math.sin(t),z)}));}
 const g=new TubeGeometry(paths.length,65,5);g.update(paths,.011);this.arcs=mesh(this,g,new Material(0x387fae,{roughness:.8,opacity:.85,emission:.07}));this.arcs.castShadow=false;
 const ep:Vec3[][]=[];for(let i=1;i<5;i++){const t=alpha*i/5;ep.push(Array.from({length:32},(_,j)=>{const r=r0+(r1-r0)*j/31;return point(r*Math.cos(t),r*Math.sin(t),0)}));}const eg=new TubeGeometry(ep.length,32,4);eg.update(ep,.007);this.rays=mesh(this,eg,new Material(0xb18c58,{roughness:1,opacity:.58}));this.rays.castShadow=false;
 const bounds:Vec3[][]=[];for(const r of[r0,r1])for(const z of[-sectionWidth/2,sectionWidth/2])bounds.push(Array.from({length:65},(_,j)=>point(r*Math.cos(alpha*j/64),r*Math.sin(alpha*j/64),z)));const bg=new TubeGeometry(4,65,4);bg.update(bounds,.007);this.boundaries=mesh(this,bg,new Material(0x7c939f,{opacity:.36,roughness:1}));this.boundaries.castShadow=false;
 }
 set(phase:number){this.arcs.material.opacity=.32+.53*Math.min(1,phase*2);this.rays.material.opacity=.25+.33*Math.max(0,(phase-.3)/.7);}
 annotations():Annotation[]{const w=P.wedge;return[{title:'弯曲的电场线',detail:'同心圆弧；|E| ∝ 1/r',point:point(.018,.010,sectionWidth/2),offset:[40,-65]},{title:'等势线',detail:'径向直线',point:point(.017,.006,0),offset:[60,60]},{title:'绝缘径向边界',detail:'r₀ = 5 mm，r₁ = 30 mm',point:point(.028,.009,sectionWidth/2),offset:[75,20]}]}
 bounds(){const w=P.wedge,a=w.angle_deg*Math.PI/180;const p:Vec3[]=[];for(const r of[w.inner_radius_m,w.outer_radius_m])for(const t of[0,a])for(const z of[-sectionWidth/2,sectionWidth/2])p.push(point(r*Math.cos(t),r*Math.sin(t),z));return p;}
}
