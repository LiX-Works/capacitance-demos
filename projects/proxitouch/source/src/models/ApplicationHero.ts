import {Node,Mesh,InstancedMesh,Material,metals,mesh} from '../engine/scene.js';
import {roundedBox,box,parametric,lathe,cylinder,ring} from '../engine/geometry.js';
import {Vec3,Mat4,clamp,mix,smooth,normalize,hex,transform,compose} from '../engine/math.js';

const EGG_Y=3.10,EGG_RY=1.95;
function eggRadius(y:number){const h=(y-EGG_Y)/EGG_RY;return Math.abs(h)>=1?0:1.39*Math.sqrt(1-h*h)*(1-.16*h);}
/** Dense rendering LOD: one independent EC per cell, one instance per shared EH edge.
 * No invisible 320-fold replication of the nine-dome explanatory macro model.
 * The warm surface response is illustrative, not calibrated pressure or control.
 */
class DenseSkin extends Node {
 readonly nx=10;readonly nz=16;readonly pitch=.28;
 film:Mesh;gel:InstancedMesh;ec:InstancedMesh;eh:InstancedMesh;
 contacts=0;maxIndent=0;minimumClearance=0;last='';
 private matrix!:Mat4;private inward:Vec3=[1,0,0];private near=0;
 constructor(){
  super();this.name='10x16-shared-EH-independent-EC-skin';
  this.film=mesh(this,parametric(20,32,(u,v)=>({p:[(u-.5)*2.90,.012,(v-.5)*4.58],n:[0,1,0]})),new Material(0xc1d2d9,{roughness:.76,opacity:.19,softness:.15}));
  this.film.castShadow=false;
  this.gel=this.add(new InstancedMesh(roundedBox(.229,.034,.229,.009,2),new Material(0x87b7bf,{roughness:.69,softness:.2,opacity:.23}),160));
  this.ec=this.add(new InstancedMesh(roundedBox(.207,.024,.207,.008,2),new Material(0xffffff,{metalness:.52,roughness:.44}),160));
  this.eh=this.add(new InstancedMesh(box(this.pitch-.014,.023,.016),new Material(0xffffff,{metalness:.65,roughness:.43}),346));
  this.gel.castShadow=this.ec.castShadow=this.eh.castShadow=false;
 }
 rest(u:number){return .065+.018*u*u;}
 configure(matrix:Mat4){this.matrix=matrix;const a=transform(matrix,[0,0,0]),b=transform(matrix,[0,1,0]);this.inward=normalize(b.map((v,k)=>v-a[k]) as Vec3);}
 clearance(u:number,v:number){
  const p=transform(this.matrix,[u,0,v]),r=eggRadius(p[1]);if(r<.001)return 9;
  const rz=r*.91,n=this.inward;
  const A=(n[0]/r)**2+(n[2]/rz)**2,B=2*(p[0]*n[0]/(r*r)+p[2]*n[2]/(rz*rz)),C=(p[0]/r)**2+(p[2]/rz)**2-1,disc=B*B-4*A*C;
  return disc<0?9:(-B-Math.sqrt(disc))/(2*A);
 }
 minGap(){let min=9;for(let j=0;j<this.nz;j++)for(let i=0;i<this.nx;i++){const u=(i-4.5)*this.pitch,v=(j-7.5)*this.pitch;min=Math.min(min,this.clearance(u,v)-this.rest(u)-.066);}return min;}
 height(u:number,v:number){return Math.min(this.rest(u),this.clearance(u,v)-.067);}
 rotationAt(u:number,v:number):Vec3 {const du=(this.height(u+.006,v)-this.height(u-.006,v))/.012,dv=(this.height(u,v+.006)-this.height(u,v-.006))/.012;return[-Math.atan(dv),0,Math.atan(du)];}
 /** Conservative finite-cell contact envelope. The centre-only tangent can cut the
  * egg at the edge of a cell crossing the contact front; sample its rigid corners. */
 safeHeight(u:number,v:number,rotation:Vec3,offset:number,extents:Vec3){
  const R=compose([0,0,0],rotation,[1,1,1]);let h=this.height(u,v);
  for(const x of [-extents[0],0,extents[0]])for(const z of [-extents[2],0,extents[2]])for(const y of [-extents[1],extents[1]]){
   const d=transform(R,[x,y,z]);h=Math.min(h,this.clearance(u+d[0],v+d[2])-offset-d[1]-.004);
  }return h;
 }
 response(u:number,v:number){
  const gap=this.clearance(u,v)-this.rest(u)-.066,indent=Math.max(0,-gap),near=this.near*Math.exp(-((u+.06)**2/2.8+(v-.20)**2/4.4));
  const warm=indent>1e-5?(.94+.06*Math.sqrt(clamp(indent/.105)))*smooth(clamp(indent/.00022)):0;
  return {near,indent,warm};
 }
 set(matrix:Mat4,depth:number){
  this.configure(matrix);this.near=smooth(clamp((depth+1)/.95));this.contacts=0;this.maxIndent=0;this.minimumClearance=this.minGap();
  const neutral=hex(0xa9c2cc),blue=hex(0x438fbc),warm=hex(0xffb940),warmCentre=hex(0xe59129);
  for(let j=0;j<this.nz;j++)for(let i=0;i<this.nx;i++){
   const u=(i-4.5)*this.pitch,v=(j-7.5)*this.pitch,k=j*this.nx+i,r=this.response(u,v),rotation=this.rotationAt(u,v),h=this.safeHeight(u,v,rotation,.045,[.1035,.012,.1035]);
   if(r.indent>1e-5)this.contacts++;this.maxIndent=Math.max(this.maxIndent,r.indent);
   const target=warm.map((x,n)=>mix(x,warmCentre[n],clamp(r.indent/.105))) as Vec3;
   const c=neutral.map((x,n)=>mix(mix(x,blue[n],r.near*.94),target[n],r.warm)) as Vec3;
   this.gel.set(k,[u,h+.009,v],rotation);
   this.ec.set(k,[u,h+.045,v],rotation,[1,1,1],c);
  }
  let k=0;const railBase=hex(0x60869b),railBlue=hex(0x367eaa);
  for(let axis=0;axis<2;axis++)for(let line=0;line<=(axis?this.nx:this.nz);line++)for(let segment=0;segment<(axis?this.nz:this.nx);segment++){
   const u=axis?(line-this.nx/2)*this.pitch:(segment-(this.nx-1)/2)*this.pitch;
   const v=axis?(segment-(this.nz-1)/2)*this.pitch:(line-this.nz/2)*this.pitch;
   const h=this.height(u,v),r=this.response(u,v),color=railBase.map((x,n)=>mix(x,railBlue[n],r.near*.85)) as Vec3;
   // Small isolated short edges, with a real junction gap: not one permanently shorted grid.
   const rot=this.rotationAt(u,v),rotation:Vec3=axis?[rot[0],Math.PI/2,0]:[0,0,rot[2]],safe=this.safeHeight(u,v,rotation,.043,[(this.pitch-.014)/2,.0115,.008]);
   this.eh.set(k++,[u,safe+.043,v],rotation,[1,1,1],color);
  }
  const g=this.film.geometry;for(let k=0;k<g.data.length;k+=8){const u=(g.data[k+6]-.5)*2.90,v=(g.data[k+7]-.5)*4.58,du=(this.height(u+.006,v)-this.height(u-.006,v))/.012,dv=(this.height(u,v+.006)-this.height(u,v-.006))/.012;g.data[k]=u;g.data[k+1]=this.height(u,v)-.025;g.data[k+2]=v;g.data.set(normalize([-du,1,-dv]),k+3);}g.touch();
 }
}

export class ApplicationHero extends Node {
 left:Node;right:Node;leftSkin:DenseSkin;rightSkin:DenseSkin;egg:Mesh;
 spread=3;contactSpread=2;last=NaN;stage='approach';readonly pixelsPerJaw=160;
 constructor(){
  super();this.name='ProxiTouch-concept-egg-grasp';
  // Reuses R1 gripper material / mechanical vocabulary with the R2 electrode architecture.
  mesh(this,roundedBox(6.90,.62,3.14,.18,5),metals.silver,[0,.02,-.25]);
  mesh(this,roundedBox(6.48,.10,2.72,.05,3),metals.blue,[0,.375,-.25]);
  mesh(this,roundedBox(5.95,.13,.20,.04,3),metals.dark,[0,.485,.82]);
  mesh(this,roundedBox(5.95,.13,.20,.04,3),metals.dark,[0,.485,-1.22]);
  mesh(this,cylinder(.78,1.02,.10,40),metals.silver,[0,.04,-2.10],[Math.PI/2,0,0]);
  mesh(this,ring(.43,.65,.08,36),metals.blue,[0,.04,-2.65],[Math.PI/2,0,0]);
  // A small staging support avoids an unexplained floating egg before first touch.
  // The demonstration does not lift the egg or claim a closed-loop grasp.
  mesh(this,cylinder(.13,.70,.025,24),metals.silver,[0,.77,0]);
  mesh(this,cylinder(.27,.055,.012,32),new Material(0xcbd7dc,{roughness:.78,softness:.1}),[0,1.13,0]);
  this.left=this.add(new Node());this.right=this.add(new Node());
  for(const [i,jaw] of [this.left,this.right].entries()){
   const sign=i===0?1:-1;
   mesh(jaw,roundedBox(.88,.38,2.85,.10,4),metals.silver,[0,.62,0]);
   mesh(jaw,roundedBox(.26,4.75,.22,.055,4),metals.silver,[-sign*.10,3.12,-1.36]);
   mesh(jaw,roundedBox(.26,4.75,.22,.055,4),metals.silver,[-sign*.10,3.12,1.36]);
   mesh(jaw,roundedBox(.58,.23,2.95,.07,4),metals.silver,[-sign*.06,5.49,0]);
   mesh(jaw,roundedBox(.36,.10,2.61,.032,3),metals.blue,[sign*.05,5.32,0]);
   for(const z of [-1.35,1.35])for(const y of [1.01,5.18])mesh(jaw,cylinder(.071,.018,.005,12),metals.dark,[sign*.16,y,z],[0,0,Math.PI/2]);
  }
  this.leftSkin=this.left.add(new DenseSkin());this.leftSkin.position=[.22,3.05,0];this.leftSkin.rotation=[Math.PI/2,0,-Math.PI/2];
  this.rightSkin=this.right.add(new DenseSkin());this.rightSkin.position=[-.22,3.05,0];this.rightSkin.rotation=[Math.PI/2,0,Math.PI/2];
  const profile:[number,number][]=[];for(let i=0;i<=64;i++){const y=EGG_Y-EGG_RY+i/64*EGG_RY*2;profile.push([eggRadius(y),y]);}
  this.egg=mesh(this,lathe(profile,72),new Material(0xe2d0b2,{roughness:.69,softness:.08,metalness:0}));this.egg.name='intact-rigid-egg-concept';this.egg.scale=[1,1,.91];
  // Calibrate a geometric first-contact point, not a guessed screen distance.
  let lo=1.4,hi=3.5;for(let i=0;i<30;i++){const c=(lo+hi)/2;this.place(c);this.update();this.leftSkin.configure(this.leftSkin.world);if(this.leftSkin.minGap()>0)hi=c;else lo=c;}this.contactSpread=(lo+hi)/2;
  this.set(-1);
 }
 place(spread:number){this.spread=spread;this.left.position=[-spread,0,0];this.right.position=[spread,0,0];}
 set(depth:number){
  if(depth===this.last)return;this.last=depth;
  const opening=.96*(1-smooth(clamp(depth+1))),compression=.12*smooth(clamp(depth));
  this.place(this.contactSpread+opening-compression);this.update();
  this.leftSkin.set(this.leftSkin.world,depth);this.rightSkin.set(this.rightSkin.world,depth);
  this.stage=this.leftSkin.contacts===0?'approach':depth<.12?'touch':'pressure';
 }
 diagnostics(){return{kind:'concept-only; not a measured or closed-loop grip',gridPerJaw:[10,16],independentECs:320,sharedEHsegments:692,pixelsPerJaw:160,contacts:[this.leftSkin.contacts,this.rightSkin.contacts],maxIndent:this.leftSkin.maxIndent,spread:this.spread,firstContactSpread:this.contactSpread,stage:this.stage,eggRigid:true,eggIntact:true,wholeGridShorted:false};}
}
