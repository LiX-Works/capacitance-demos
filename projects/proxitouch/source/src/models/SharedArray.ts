import {Node,Mesh,InstancedMesh,Material,mesh,metals} from '../engine/scene.js';
import {roundedBox,parametric} from '../engine/geometry.js';
import {Vec3,clamp,mix,smooth,normalize,hex} from '../engine/math.js';
import {interaction} from '../physics/interaction.js';
import {makeConductor} from './FringeField.js';
const coord=(index:number,level:number):[number,number]=>{let x=0,z=0;for(let k=0;k<level;k++){const d=Math.floor(index/4**k)%4;x=x*2+(d&1);z=z*2+(d>>1);}return[x,z];};
export class SharedArray extends Node {
 sheet:Mesh;support:InstancedMesh;bottom:InstancedMesh;gel:InstancedMesh;ec:InstancedMesh;independent:InstancedMesh;boundaries:InstancedMesh;target:Node;
 activeCount=1;edgeCount=4;selected=0;selectedEdges:number[]=[];edgeOwners:number[][]=[];last='';centres:Vec3[]=[];phaseMerge=0;
 constructor(){
  super();this.name='shared-addressable-boundary-array';
  this.sheet=mesh(this,parametric(32,16,(u,v)=>({p:[(u-.5)*9,-.20,(v-.5)*9],n:[0,1,0]})),new Material(0xbacdd6,{metalness:.08,roughness:.73}));
  this.support=this.add(new InstancedMesh(roundedBox(1,.13,1,.035,3),new Material(0xd0dbe1,{roughness:.75}),16));
  this.bottom=this.add(new InstancedMesh(roundedBox(1,.06,1,.023,3),metals.silver.clone(),16));
  this.gel=this.add(new InstancedMesh(roundedBox(1,.13,1,.035,3),new Material(0x8ebdc5,{roughness:.66,softness:.3,opacity:.78}),16));
  this.ec=this.add(new InstancedMesh(roundedBox(1,.075,1,.025,3),new Material(0xffffff,{metalness:.65,roughness:.42}),16));
  const rail=roundedBox(1,.073,.11,.024,3),mat=new Material(0xffffff,{metalness:.72,roughness:.39});
  this.independent=this.add(new InstancedMesh(rail,mat.clone(),64));this.boundaries=this.add(new InstancedMesh(rail,mat.clone(),40));
  this.independent.castShadow=this.boundaries.castShadow=false;
  this.target=this.add(makeConductor());this.target.scale=[2.1,.65,2.1];this.set(1,-1,0,0,0,false);
 }
 set(count:number,depth=-1,merge=1,scan=0,curvature=0,showTarget=false){
  const key=[count,depth,merge,scan,curvature,showTarget].join(',');if(key===this.last)return;this.last=key;this.phaseMerge=merge;this.independent.castShadow=this.boundaries.castShadow=showTarget;
  const level=clamp(Math.log(clamp(count,1,16))/Math.log(4),0,2),l=Math.min(1,Math.floor(level)),u=smooth(level-l),np=2**l,nc=np*2,parents=np*np;
  const pp=np===1?4.6:3.0,pc=nc===2?3.0:2.20,pitch=mix(pp,pc,u),extent=mix(np*pp,nc*pc,u);
  this.activeCount=u<.001?parents:nc*nc;const gridN=u<.001?np:nc;const gridLevel=Math.log2(gridN);this.selected=Math.min(this.activeCount-1,Math.floor(scan));
  const chosen=coord(this.selected,gridLevel);this.centres=[];
  const state=interaction(depth),height=(x:number,z:number)=>.014*curvature*x*x;
  const response=(x:number,z:number)=>{const r2=(x+1.1)**2+(z+1.1)**2;return {near:smooth(clamp((depth+1)/.95))*Math.exp(-r2/14),pressure:state.areaNormalized*Math.exp(-r2/3.0)};};
  for(let i=0;i<16;i++){
   const alive=i<parents?1:i<this.activeCount?u:0,a=coord(i%parents,l),b=coord(i,l+1),x=mix((a[0]-(np-1)/2)*pp,(b[0]-(nc-1)/2)*pc,u),z=mix((a[1]-(np-1)/2)*pp,(b[1]-(nc-1)/2)*pc,u),y=height(x,z),r=response(x,z),local=showTarget||curvature>0?r.pressure:0;
   this.centres.push([x,y+.33-.075*local,z]);const rotation:Vec3=[0,0,Math.atan(.028*curvature*x)],at=(h:number):Vec3=>[x,y+h,z];
   const baseScale:Vec3=[pitch*.94*alive,1,pitch*.94*alive],centralScale:Vec3=[pitch*.62*alive,1,pitch*.62*alive];
   this.support.set(i,at(-.08),rotation,baseScale);
   this.bottom.set(i,at(.025),rotation,[pitch*.65*alive,1,pitch*.65*alive]);
   this.gel.set(i,at(.14),rotation,[pitch*.60*alive,1,pitch*.60*alive]);
   let color=hex(i===this.selected&&merge>.95?0x83b1c5:0xb2c8d2);
   if(showTarget||curvature>0){const c=hex(0xb8cdd5),blue=hex(0x669fba),gold=hex(0xd2aa62);color=c.map((v,k)=>mix(mix(v,blue[k],r.near*.8),gold[k],local)) as Vec3;}
   this.ec.set(i,at(.292-.075*local),rotation,centralScale,color);
   const positionInGrid=coord(i,Math.log2(gridN));
   const fade=smooth(clamp((merge-.56)/.44));
   const len=pitch-.16;
   for(let side=0;side<4;side++){
    const outer=side===0?positionInGrid[1]===gridN-1:side===2?positionInGrid[1]===0:side===1?positionInGrid[0]===gridN-1:positionInGrid[0]===0;
    const sep=outer?.5:mix(.435,.5,smooth(clamp(merge/.82)));
    const ox=side%2?(side===1?1:-1)*pitch*sep:0,oz=side%2?0:(side===0?1:-1)*pitch*sep;
    this.independent.set(i*4+side,[x+ox,height(x+ox,z+oz)+.292,z+oz],[0,side%2?Math.PI/2:0,0],[len*alive,1,alive],hex(0x668ca4),1-fade);
   }
  }
  this.support.count=this.bottom.count=this.gel.count=this.ec.count=this.activeCount;this.independent.count=this.activeCount*4;this.independent.visible=merge<.999;
  this.boundaries.visible=merge>.56;this.edgeOwners=[];this.selectedEdges=[];let k=0;
  const n=gridN,p=n===np?pp:pc;
  const indexAt=(x:number,z:number)=>{for(let a=0;a<n*n;a++){const c=coord(a,gridLevel);if(c[0]===x&&c[1]===z)return a;}return-1;};
  const add=(vertical:boolean,j:number,row:number)=>{
   let across=(j-n/2)*p,along=(row-(n-1)/2)*p,len=p-.16,alpha=1;
   if(n===nc&&u<.999){const srcAcross=(j%2===0?(j/2-np/2)*pp:(Math.floor(j/2)-(np-1)/2)*pp),srcAlong=(Math.floor(row/2)-(np-1)/2)*pp+(row%2?1:-1)*(pp-.16)*.25;across=mix(srcAcross,across,u);along=mix(srcAlong,along,u);len=mix((pp-.16)*.5,len,u);alpha=j%2?u:1;}
   const x=vertical?across:along,z=vertical?along:across,owners=vertical?[indexAt(j-1,row),indexAt(j,row)]:[indexAt(row,j-1),indexAt(row,j)];
   const active=this.selected>=0&&owners.includes(this.selected)&&merge>.98;this.edgeOwners.push(owners.filter(o=>o>=0));if(active)this.selectedEdges.push(k);
   const tilt=vertical?0:Math.atan(.028*curvature*x);
   this.boundaries.set(k++,[x,height(x,z)+.292,z],[0,vertical?Math.PI/2:0,tilt],[len,1,1],hex(active?0x34769e:0x7693a8),alpha*smooth(clamp((merge-.56)/.44)));
  };
  for(let j=0;j<=n;j++)for(let row=0;row<n;row++)add(true,j,row);
  for(let j=0;j<=n;j++)for(let row=0;row<n;row++)add(false,j,row);
  this.boundaries.count=k;this.edgeCount=k;
  const g=this.sheet.geometry;for(let i=0;i<g.data.length;i+=8){const x=(g.data[i+6]-.5)*(extent+.22),z=(g.data[i+7]-.5)*(extent+.22),normal=normalize([-.028*curvature*x,1,0]);g.data[i]=x;g.data[i+1]=height(x,z)-.18;g.data[i+2]=z;g.data.set(normal,i+3);}g.touch();
  this.target.visible=showTarget;const yc=height(-1.1,-1.1)+.334-.075*state.areaNormalized;this.target.position=[-1.1,yc+state.externalGap,-1.1];
  this.target.traverse(n=>{if(n instanceof Mesh)n.material.opacity=mix(.80,.38,smooth(clamp(depth/.18)));});
 }
 diagnostics(){return {pixels:this.activeCount,uniqueBoundarySegments:this.edgeCount,expectedFinalSegments:40,selectedEC:this.selected,selectedEdges:this.selectedEdges,selectedEdgeCount:this.selectedEdges.length,sharedEdges:this.edgeOwners.filter(x=>x.length===2).length,independentFramesVisible:this.independent.visible,merge:this.phaseMerge,junctionGap:.16,wholeGridShorted:false};}
}
