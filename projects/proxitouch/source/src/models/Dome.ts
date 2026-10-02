import { Node, Mesh, InstancedMesh, Material, metals, mesh, gelMaterial, contactMaterial } from '../engine/scene.js';
import { Geometry, lathe, cylinder, ring, roundedBox, TubeGeometry } from '../engine/geometry.js';
import { Vec3, clamp, mix, normalize } from '../engine/math.js';
import { interaction, domeContact } from '../physics/interaction.js';
export class DeformableDome extends Geometry {
    radius: number;
    height: number;
    contactRadius = 0;
    planeHeight = 0;
    last = -100;
    segments = 56;
    rings = 35;
    constructor(radius = .70, height = .96) { super(new Float32Array((35 + 2) * (56 + 1) * 8), new Uint32Array()); this.radius = radius; this.height = height; const idx: number[] = []; for (let j = 0; j < 36; j++)
        for (let i = 0; i < 56; i++) {
            const a = j * 57 + i, b = a + 1, c = a + 57, d = c + 1;
            idx.push(a, c, b, b, c, d);
        } this.indices = new Uint32Array(idx); this.deform(0); }
    deform(indent: number) {
        if (Math.abs(indent - this.last) < 1e-6)
            return;
        this.last = indent;
        indent = clamp(indent, 0, this.height * .60);
        const plane = this.height - indent;
        const a = indent > 0 ? this.radius * Math.sqrt(clamp(1 - (plane / this.height) ** 2)) : 0;
        this.contactRadius = a;
        this.planeHeight = plane;
        const R = this.radius + indent * .10;
        const profile: [
            number,
            number
        ][] = [[0, 0], [R, 0]];
        for (let j = 1; j <= this.rings; j++) {
            const t = 1 - j / this.rings;
            const r = R * t;
            let y: number;
            if (r <= a)
                y = plane;
            else {
                const v = (r - a) / (R - a);
                y = plane * Math.sqrt(Math.max(0, 1 - v * v));
            }
            profile.push([r, y]);
        }
        if (a > 0) {
            const edge = profile.findIndex((p, i) => i > 1 && p[0] <= a);
            if (edge > 1)
                profile[edge] = [a, plane];
        }
        for (let j = 0; j < profile.length; j++) {
            const before = profile[Math.max(j - 1, 0)], after = profile[Math.min(j + 1, profile.length - 1)];
            let normal = normalize([after[1] - before[1], before[0] - after[0], 0]);
            if (j === 0)
                normal = [0, -1, 0];
            if (j === profile.length - 1)
                normal = [0, 1, 0];
            for (let i = 0; i <= this.segments; i++) {
                const th = i / this.segments * Math.PI * 2, c = Math.cos(th), s = Math.sin(th), k = (j * (this.segments + 1) + i) * 8;
                this.data.set([profile[j][0] * c, profile[j][1], profile[j][0] * s, normal[0] * c, normal[1], normal[0] * s, i / this.segments, j / (profile.length - 1)], k);
            }
        }
        this.touch();
    }
}
/** A true thin, rounded-square membrane. The rim stays fixed while its centre bends. */
export class FlexibleFilm extends Geometry {
 original:Float32Array;amount=-1;half:number;thickness:number;faceSigns:number[]=[];
 constructor(width=6.24,thickness=.07){
  const d:number[]=[],ix:number[]=[],signs:number[]=[];const h=width/2,n=28,r=.25;
  const point=(x:number,z:number):[number,number]=>{const cx=clamp(x,-h+r,h-r),cz=clamp(z,-h+r,h-r),dx=x-cx,dz=z-cz,len=Math.hypot(dx,dz);return len>r?[cx+dx*r/len,cz+dz*r/len]:[x,z];};
  for(const sign of [1,-1]){
   const base=d.length/8;
   for(let j=0;j<=n;j++)for(let i=0;i<=n;i++){const [x,z]=point(-h+2*h*i/n,-h+2*h*j/n);d.push(x,sign*thickness/2,z,0,sign,0,i/n,j/n);signs.push(sign);}
   for(let j=0;j<n;j++)for(let i=0;i<n;i++){const a=base+j*(n+1)+i,b=a+1,c=a+n+1,e=c+1;if(sign>0)ix.push(a,c,b,b,c,e);else ix.push(a,b,c,b,e,c);}
  }
  const rim:[number,number][]=[];
  for(let side=0;side<4;side++)for(let k=0;k<32;k++){const a=side*Math.PI/2+k/31*Math.PI/2;rim.push([(h-r)*Math.sign(Math.cos(a)||1)+r*Math.cos(a),(h-r)*Math.sign(Math.sin(a)||1)+r*Math.sin(a)]);}
  // Rounded perimeter uses quadrant centres, with straight edges between arcs.
  rim.length=0;
  for(let side=0;side<4;side++){const cx=[h-r,-h+r,-h+r,h-r][side],cz=[h-r,h-r,-h+r,-h+r][side];for(let k=0;k<=10;k++){const a=side*Math.PI/2+k/10*Math.PI/2;rim.push([cx+r*Math.cos(a),cz+r*Math.sin(a)]);}}
  const base=d.length/8;
  for(let i=0;i<=rim.length;i++){const [x,z]=rim[i%rim.length],next=rim[(i+1)%rim.length],prev=rim[(i+rim.length-1)%rim.length],normal=normalize([next[1]-prev[1],0,prev[0]-next[0]]);for(const s of [-1,1]){d.push(x,s*thickness/2,z,...normal,i/rim.length,(s+1)/2);signs.push(0);}}
  for(let i=0;i<rim.length;i++){const a=base+i*2;ix.push(a,a+1,a+2,a+1,a+3,a+2);}
  super(d,ix);this.original=new Float32Array(d);this.half=h;this.thickness=thickness;this.faceSigns=signs;this.bend(0);
 }
 weight(x:number,z:number){const a=Math.max(Math.abs(x),Math.abs(z));const t=clamp((a-2.43)/(this.half-2.43));return 1-t*t*(3-2*t);}
 bend(amount:number){if(Math.abs(amount-this.amount)<1e-7)return;this.amount=amount;
  for(let k=0,i=0;k<this.data.length;k+=8,i++){const x=this.original[k],z=this.original[k+2];this.data[k+1]=this.original[k+1]-amount*this.weight(x,z);const sign=this.faceSigns[i];if(sign){const dx=-amount*(this.weight(x+.002,z)-this.weight(x-.002,z))/.004,dz=-amount*(this.weight(x,z+.002)-this.weight(x,z-.002))/.004,n=normalize([-dx,1,-dz]);this.data[k+3]=n[0]*sign;this.data[k+4]=n[1]*sign;this.data[k+5]=n[2]*sign;}}
  this.touch();
 }
}
export class MicroAssembly extends Node {
 bottom:Mesh;base:Mesh;electrodeFilm:Mesh;coverFilm:Mesh;domeGroup:Node;electrode:Node;cover:Node;
 domes:Mesh[]=[];patches:Mesh[]=[];geometries:DeformableDome[]=[];planeY=1.52;area=0;last='';deflection=0;
 electrodeGeometry:FlexibleFilm;coverGeometry:FlexibleFilm;surfaceGuides:TubeGeometry;
 constructor(){
  super();this.name='shared-EC-ionogel-EB-stack';
  this.bottom=mesh(this,roundedBox(6.44,.18,6.44,.075,5),metals.silver.clone(),[0,0,0]);this.bottom.name='EB';
  this.base=mesh(this,roundedBox(6.08,.28,6.08,.12,5),gelMaterial().clone({opacity:.78}),[0,.24,0]);
  this.domeGroup=this.add(new Node());
  const pmat=contactMaterial();
  const positions:Vec3[]=[[0,.38,0]];for(let z=-1;z<=1;z++)for(let x=-1;x<=1;x++)if(x||z)positions.push([x*1.7,.38,z*1.7]);
  positions.forEach((p,i)=>{const g=new DeformableDome(.7,i===0?.96:.91);this.geometries.push(g);this.domes.push(mesh(this.domeGroup,g,gelMaterial().clone({opacity:.9}),p));const patch=mesh(this.domeGroup,cylinder(1,.012,.002,48),pmat.clone(),[p[0],1.34,p[2]]);patch.castShadow=false;patch.scale=[.001,1,.001];this.patches.push(patch);});
  this.electrode=this.add(new Node());this.electrode.name='EC-shared-physical-node';
  this.electrodeGeometry=new FlexibleFilm();this.electrodeFilm=mesh(this.electrode,this.electrodeGeometry,new Material(0x9dbac7,{metalness:.50,roughness:.43,opacity:.28,softness:.08}));
  for(let i=0;i<4;i++)mesh(this.electrode,roundedBox(6.14,.075,.066,.025,4),metals.pale.clone({opacity:.82}),[i%2?3.08:0,0,i%2?0:(i===0?3.08:-3.08)],[0,i%2?Math.PI/2:0,0]);
  // Correct the two lateral rim positions independently.
  this.electrode.children[2].position[0]=3.08;this.electrode.children[4].position[0]=-3.08;
  this.surfaceGuides=new TubeGeometry(2,40,5);const guide=mesh(this.electrode,this.surfaceGuides,new Material(0x7397ac,{metalness:.35,roughness:.6,opacity:.65}));guide.castShadow=false;
  this.cover=this.add(new Node());this.coverGeometry=new FlexibleFilm(6.48,.10);
  this.coverFilm=mesh(this.cover,this.coverGeometry,new Material(0xc5d9df,{roughness:.65,opacity:.095,softness:.35}));
  this.set(-1);
 }
 set(depth:number,explosion=0,showCover=true){
  const key=[depth,explosion,showCover].join(',');if(this.last===key)return;this.last=key;
  const m=interaction(depth),load=m.contact?.004+m.pressure*.996:0,indent=.35*Math.pow(load,2/3);
  this.deflection=.18*m.membraneClosure+indent;this.planeY=1.52-this.deflection;this.area=0;
  this.geometries.forEach((g,i)=>{const delta=Math.max(0,indent-(i===0?0:.05));g.deform(delta);const p=this.patches[i];p.visible=delta>0;p.position[1]=.38+g.planeHeight+.006;p.scale=[Math.max(.001,g.contactRadius),1,Math.max(.001,g.contactRadius)];this.area+=Math.PI*g.contactRadius*g.contactRadius;});
  this.electrode.position[1]=1.555+explosion*1.8;this.electrodeGeometry.bend(this.deflection);
  this.cover.position[1]=1.665+explosion*3;this.coverGeometry.bend(this.deflection);this.cover.visible=showCover;
  this.electrodeFilm.material.opacity=mix(.42,.82,clamp(explosion));
  const lines:Vec3[][]=[];for(const z of [-2.48,2.48]){const line:Vec3[]=[];for(let i=0;i<40;i++){const x=-3.09+i/39*6.18;line.push([x,.038-this.deflection*this.electrodeGeometry.weight(x,z),z]);}lines.push(line);}this.surfaceGuides.update(lines,.009);this.coverFilm.material.opacity=mix(.095,.3,clamp(explosion));
  this.domeGroup.position[1]=explosion*.8;this.base.position[1]=.24+explosion*.8;this.bottom.position[1]=-explosion*.12;
 }
}
