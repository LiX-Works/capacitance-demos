import {Node,Mesh,InstancedMesh,Material,metals,mesh,fieldMaterial} from '../engine/scene.js';
import {box,cylinder,plane,TubeGeometry,sphere,Geometry} from '../engine/geometry.js';
import {Vec3,clamp,mix,hex} from '../engine/math.js';
import {P,SCALE,point,topPoint,ModelState,fieldNodes,bracket,decodeU16,sectionWidth,analytic} from '../physics/model.js';
export interface Annotation{title:string;detail?:string;point:Vec3;offset?:[number,number];}
const line=(root:Node,paths:Vec3[][],mat:Material,r=.010)=>{const n=paths.length,k=paths[0].length,g=new TubeGeometry(n,k,5);g.update(paths,r);const m=mesh(root,g,mat);m.castShadow=false;return m;};
function segment(a:Vec3,b:Vec3,count=2){return Array.from({length:count},(_,i)=>a.map((v,k)=>mix(v,b[k],i/(count-1)))as Vec3)}
export class Experiment extends Node{
 lower:Mesh;upper:Mesh;hinge:Node;axis:Mesh;dielectric:Mesh;field:Mesh[]=[];fieldGeometries:TubeGeometry[]=[];plane:InstancedMesh;marker:Mesh;microElements:InstancedMesh;boundaryMarkers:InstancedMesh;dimensions:Node;last='';fieldKey='';visibleWidth=sectionWidth;mapsCache='';localMap=false;dimensionMeshes:Mesh[]=[];
 constructor(){super();this.name='shared-SI-geometry';const L=P.length_m,t=P.electrode_thickness_m,D=P.initial_clear_gap_m;
 this.lower=mesh(this,box(L*SCALE,t*SCALE,P.width_m*SCALE),metals.silver.clone({roughness:.42}),point(L/2,-t/2));
 this.hinge=this.add(new Node());this.hinge.position=point(-P.hinge_offset_m,D/2);this.hinge.name='fixed-pivot';
 this.upper=mesh(this.hinge,this.lower.geometry,metals.blue.clone({roughness:.40}),point(L/2+P.hinge_offset_m,D/2+t/2));
 this.axis=mesh(this,cylinder(.00004*SCALE,sectionWidth*SCALE*1.15,.00001*SCALE,16),new Material(0x8ea7b5,{roughness:.8,opacity:.4}),point(-P.hinge_offset_m,D/2),[Math.PI/2,0,0]);this.axis.castShadow=false;
 const mat=P.dielectric;this.dielectric=mesh(this,box((mat.x_end_m-mat.x_start_m)*SCALE,mat.thickness_m*SCALE,P.width_m*SCALE),new Material(0x73aeb0,{roughness:.6,opacity:.72,softness:.16}),point((mat.x_start_m+mat.x_end_m)/2,mat.y_bottom_m+mat.thickness_m/2));
 this.marker=mesh(this,sphere(.030,14,10),new Material(0xd6a954,{roughness:.6}),point(-P.hinge_offset_m,D/2,sectionWidth/2+.0005));this.marker.castShadow=false;
 for(let i=0;i<3;i++){const g=new TubeGeometry(8,88,5);this.fieldGeometries.push(g);const f=mesh(this,g,fieldMaterial().clone({opacity:i===1?.90:.35,emission:.08}));f.castShadow=false;this.field.push(f);}
 const gx=141,gy=101;
 const dataQuad=new Geometry([-.5,-.5,0,0,0,1,0,0,.5,-.5,0,0,0,1,1,0,.5,.5,0,0,0,1,1,1,-.5,.5,0,0,0,1,0,1],[0,1,2,0,2,3]);this.plane=this.add(new InstancedMesh(dataQuad,new Material(0xffffff,{patterned:3,opacity:.97,roughness:1}),gx*gy));this.plane.castShadow=false;this.plane.receiveShadow=false;
 this.microElements=this.add(new InstancedMesh(box(1,1,1),new Material(0xd4a753,{roughness:.75,opacity:.24}),14));this.microElements.castShadow=false;
 this.boundaryMarkers=this.add(new InstancedMesh(sphere(.010,8,6),new Material(0xc59a4b,{roughness:.7,emission:.04}),256));this.boundaryMarkers.castShadow=false;
 this.dimensions=this.add(new Node());
 // Four reusable dimension segments cover the largest annotation set.
 for(let i=0;i<4;i++){const m=line(this.dimensions,[segment([0,0,0],[0,0,0])],new Material(0x7892a5,{roughness:1,opacity:.72}),.006);m.visible=false;this.dimensionMeshes.push(m);}
 }
 set(s:ModelState,scene:string){const key=[s.theta,s.er,s.fullWidth,s.field,scene,s.stage].join(',');if(key===this.last)return;this.last=key;
 const width=s.fullWidth?P.width_m:sectionWidth;this.visibleWidth=width;this.lower.scale[2]=this.upper.scale[2]=this.dielectric.scale[2]=width/P.width_m;this.hinge.rotation[2]=s.theta*Math.PI/180;
 this.axis.scale[1]=width/sectionWidth;this.axis.visible=scene==='02';this.marker.visible=scene==='02';this.marker.position=point(-P.hinge_offset_m,P.initial_clear_gap_m/2,width/2+.0005);
 this.dielectric.visible=s.er>1;this.dielectric.material.opacity=s.field==='lines'?.70:.48;
 const fl=fieldNodes(s.theta,s.er);const useField=s.field==='lines';this.field.forEach(m=>m.visible=useField);
 const fieldKey=[s.theta,s.er,width].join(',');if(useField&&fieldKey!==this.fieldKey){this.fieldKey=fieldKey;for(let slice=0;slice<3;slice++){const paths:Vec3[][]=[];for(let jj=0;jj<8;jj++){const j=jj===7?9:jj;
 const path:Vec3[]=[];let stopped:Vec3|undefined;for(let k=0;k<88;k++){const a=fl.a.paths_m[j][k],b=fl.b.paths_m[j][k];let x=mix(a[0],b[0],fl.t),y=mix(a[1],b[1],fl.t);
 // Only a declared finite display window is shown; no artificial field attraction.
 if(stopped){path.push([...stopped]);continue;}const p=point(x,y,(slice-1)*width*.43);path.push(p);if(Math.abs(x)>.035||y>.032)stopped=p;
 }paths.push(path)}this.fieldGeometries[slice].update(paths,slice===1?.010:.0075)}}
 this.localMap=scene==='09'&&![1.5,2,3,6,8].includes(s.er);this.plane.visible=s.field==='potential'||s.field==='strength';if(this.plane.visible)this.updateMap(s,fl);
 this.boundaryMarkers.visible=scene==='05';if(this.boundaryMarkers.visible){for(let i=0;i<128;i++){const x=P.length_m*(2-Math.cos(Math.PI*i/128)-Math.cos(Math.PI*(i+1)/128))/4;this.boundaryMarkers.set(i,point(x,0,width/2+.00002));this.boundaryMarkers.set(i+128,topPoint(x,P.initial_clear_gap_m,width/2+.00002,s.theta));}}
 this.dimensions.visible=scene==='02'||scene==='03'||scene==='08';if(this.dimensions.visible)this.updateDimensions(s,scene);
 this.microElements.visible=scene==='03'||scene==='08';if(this.microElements.visible){const a=analytic(s.theta,s.er);for(let i=0;i<14;i++){const x=(i+.5)/14*a.W,h=a.h0+(a.h1-a.h0)*(i+.5)/14;this.microElements.set(i,point(x,h/2,width*.10),[0,0,0],[Math.max(.00001,a.W/14*.8)*SCALE,h*SCALE,width*.48*SCALE]);}}
 }
 updateMap(s:ModelState,fl:ReturnType<typeof fieldNodes>){const key=[s.theta,s.er,s.field,this.visibleWidth,this.localMap].join(',');if(key===this.mapsCache)return;this.mapsCache=key;const grid=this.localMap?DATA.localFieldGrid:DATA_GRID();if(this.localMap){const q=bracket(s.theta),ls=DATA.localFields[String(s.er)];fl={a:ls[q.i],b:ls[q.j],t:q.t,exact:q.exact};}this.plane.count=grid.nx*grid.ny;const [x0,x1,y0,y1]=grid.box_m,dx=(x1-x0)/(grid.nx-1),dy=(y1-y0)/(grid.ny-1);const keyName=s.field==='potential'?'potential_u16':'field_log_u16',a=decodeU16(fl.a[keyName]),b=decodeU16(fl.b[keyName]);
 for(let j=0;j<grid.ny;j++)for(let i=0;i<grid.nx;i++){const k=j*grid.nx+i,u=a[k],v=b[k],missing=u===65535||v===65535;let q=mix(u,v,fl.t)/65534;let c:Vec3;if(s.field==='potential'){const t=Math.abs(q-.5)*2;c=q>=.5?[mix(.94,.79,t),mix(.96,.51,t),mix(.98,.16,t)]:[mix(.94,.15,t),mix(.96,.40,t),mix(.98,.65,t)];}else{const logE=-2+q*7,t=clamp((logE-1.5)/2);c=[mix(.96,.02,t),mix(.98,.29,t),mix(.99,.55,t)];}this.plane.set(k,point(x0+i*dx,y0+j*dy,s.fullWidth?0:this.visibleWidth/2+.000025),[0,0,0],[dx*SCALE*1.01,dy*SCALE*1.01,1],c,missing?0:1);}
 }
 updateDimensions(s:ModelState,scene:string){const w=this.visibleWidth/2+.0011,z=w;const D=P.initial_clear_gap_m,del=P.hinge_offset_m,L=P.length_m;const paths:Vec3[][]=[];const add=(a:Vec3,b:Vec3)=>paths.push(segment(a,b));
 if(scene==='02'){add(point(0,-.00085,z),point(L,-.00085,z));add(point(-del,-.0014,z),point(0,-.0014,z));add(point(L+.001,0,z),point(L+.001,D,z));if(s.theta>179.9)add(point(-2*del,-.00055,z),point(0,-.00055,z));}
 else{const a=analytic(s.theta,s.er);add(point(0,a.h0,z),point(0,0,z));add(point(a.W,a.h1,z),point(a.W,0,z));}
 this.dimensionMeshes.forEach((m,i)=>{m.visible=i<paths.length;if(m.visible)(m.geometry as TubeGeometry).update([paths[i]],.006)});
 }
 annotations(s:ModelState,scene:string):Annotation[]{const L=P.length_m,D=P.initial_clear_gap_m,del=P.hinge_offset_m,z=this.visibleWidth/2+.001;const a:Annotation[]=[];
 if(scene==='02'){a.push({title:'H：固定转轴',detail:`(${(-del*1000).toFixed(2)}, ${(D*500).toFixed(2)}) mm`,point:point(-del,D/2,z),offset:[-115,-50]},{title:`L = ${(L*1000).toFixed(2)} mm`,point:point(L/2,0,z),offset:[0,65]});if(s.theta>175)a.push({title:`g = 2δ = ${(del*2000).toFixed(2)} mm`,point:point(-del,0,z),offset:[-140,48]});else a.push({title:`δ = ${(del*1000).toFixed(2)} mm`,point:point(-del/2,-.0013,z),offset:[-90,70]});if(s.theta<10)a.push({title:`D = ${(D*1000).toFixed(2)} mm`,point:point(L+.001,D/2,z),offset:[70,-20]});}
 else if(scene==='03'||scene==='08'){const v=analytic(s.theta,s.er);a.push({title:'h₀',point:point(0,v.h0/2,z),offset:[-55,-35]},{title:'h(x) = h₀ + x tanθ',point:point(v.W*.62,(v.h0+(v.h1-v.h0)*.62)/2,z),offset:[70,-25]});if(scene==='08')a.push({title:'空气 + 介质 + 空气',detail:'电气厚度 h − t(1 − 1/εr)',point:point(.011,.00034,z),offset:[25,90]});}
 else{a.push({title:'旋转电极',detail:`θ = ${s.theta.toFixed(s.theta%1?1:0)}°`,point:topPoint(L*.65,D+P.electrode_thickness_m,z,s.theta),offset:[-80,-55]},{title:'固定电极',point:point(L*.7,0,z),offset:[45,45]});}
 if(s.er>1&&![ '08'].includes(scene))a.push({title:`介质 εr = ${s.er}`,detail:`t = ${(P.dielectric.thickness_m*1000).toFixed(3)} mm`,point:point(.010,.000525,z),offset:[-110,58]});return a;
 }
 bounds(s:ModelState):Vec3[]{const z=this.visibleWidth/2,L=P.length_m,D=P.initial_clear_gap_m;const pts:Vec3[]=[];for(const x of[0,L])for(const zz of[-z,z]){pts.push(point(x,0,zz));pts.push(topPoint(x,D,zz,s.theta));}if(s.field==='lines'){const f=fieldNodes(s.theta,s.er);for(const i of[0,1,2,3,4,5,6,9])for(let k=0;k<88;k+=4){const a=f.a.paths_m[i][k],b=f.b.paths_m[i][k];for(const zz of[-this.visibleWidth*.43,this.visibleWidth*.43])pts.push(point(mix(a[0],b[0],f.t),mix(a[1],b[1],f.t),zz))}}if(this.plane.visible){const grid=this.localMap?DATA.localFieldGrid:DATA.fieldGrid;for(const x of grid.box_m.slice(0,2))for(const y of grid.box_m.slice(2,4))pts.push(point(x,y,s.fullWidth?0:this.visibleWidth/2+.000025));}if(this.dimensions.visible){pts.push(point(-P.hinge_offset_m,-.0014,z+.0011),point(L+.001,-.0014,z+.0011));}return pts;}
}
import {DATA} from '../physics/data.js';
function DATA_GRID(){return DATA.fieldGrid}
