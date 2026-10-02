import {DATA} from './data.js';
import {Vec3,clamp,mix} from '../engine/math.js';
export const P=DATA.parameters;
export const SCALE=150; // one isotropic metre-to-render-unit mapping; never changes the physics.
export const sectionWidth=.028; // a declared visual clipping window, not a different physical b.
export type FieldMode='lines'|'potential'|'strength'|'off';
export interface ModelState {theta:number;er:number;phase:number;fullWidth:boolean;field:FieldMode;explore:boolean;section:boolean;stage:number;}
export function point(x:number,y:number,z=0):Vec3{return[x*SCALE,y*SCALE,z*SCALE]}
export function topPoint(x:number,y=P.initial_clear_gap_m,z=0,theta=0):Vec3{const q=theta*Math.PI/180,c=Math.cos(q),s=Math.sin(q),hx=-P.hinge_offset_m,hy=P.initial_clear_gap_m/2;return [(hx+(x-hx)*c-(y-hy)*s)*SCALE,(hy+(x-hx)*s+(y-hy)*c)*SCALE,z*SCALE]}
export function topSI(x:number,y:number,theta:number):[number,number]{const p=topPoint(x,y,0,theta);return[p[0]/SCALE,p[1]/SCALE]}
export function analytic(theta:number,er=1){const q=theta*Math.PI/180,L=P.length_m,D=P.initial_clear_gap_m,d=P.hinge_offset_m,eps=P.epsilon0_F_per_m*P.air_relative_permittivity,b=P.width_m;
 if(theta>=89.999)return {C:null as number|null,air:null as number|null,wedge:null as number|null,dual:null as number|null,W:0,h0:0,h1:0,logGap:0};
 const slope=Math.tan(q),W=Math.max(0,Math.min(L,-d+(L+d)*Math.cos(q)-D/2*Math.sin(q))),h0=D/2*(1+1/Math.cos(q))+d*slope,h1=h0+W*slope;
 if(W<=0)return{C:null,air:null,wedge:null,dual:null,W,h0,h1,logGap:0};
 const integral=(a:number,z:number,o=0)=>Math.abs(slope)<1e-9?(z-a)/(h0-o):Math.log1p((z-a)*slope/(h0+a*slope-o))/slope;
 const air=integral(0,W);let area=air;
 if(er!==1){const m=P.dielectric,a=Math.max(0,m.x_start_m),z=Math.min(W,m.x_end_m);if(z>a)area+=integral(a,z,m.thickness_m*(1-1/er))-integral(a,z);}
 const wedge=theta<1e-7?air:air*slope/q;
 return{C:eps*b*area,air:eps*b*air,wedge:eps*b*wedge,dual:eps*b*wedge*(1+q/(2*Math.PI-q)),W,h0,h1,logGap:W/air};
}
export function wedgeValue(){const w=P.wedge,a=w.angle_deg*Math.PI/180,e=P.epsilon0_F_per_m*P.air_relative_permittivity;return {C:e*P.width_m*Math.log(w.outer_radius_m/w.inner_radius_m)/a,Einner:P.voltage_difference_V/(a*w.inner_radius_m),Eouter:P.voltage_difference_V/(a*w.outer_radius_m)}}
export function bracket(theta:number){const a:number[]=DATA.angles;let hi=a.findIndex(v=>v>=theta);if(hi<=0)return{i:0,j:0,t:0,exact:true};const lo=hi-1;if(Math.abs(a[hi]-theta)<1e-8)return{i:hi,j:hi,t:0,exact:true};return{i:lo,j:hi,t:(theta-a[lo])/(a[hi]-a[lo]),exact:false}}
export function curve(er:number){return DATA.curves[String(er===1?1:4)] as any[]}
export function sample(theta:number,er:number){
 if(theta===0&&![1,4].includes(er)){const row=DATA.er_scan.find((v:any)=>v.er===er);if(row)return{...row,exact:true,interpolated:false,bracket:[0,0]};}
 const b=bracket(theta),list=curve(er),a=list[b.i],z=list[b.j];const C=mix(a.C_F,z.C_F,b.t),Cprime=mix(a.Cprime_F_per_m,z.Cprime_F_per_m,b.t),base=list[0].C_F;
 return{theta_deg:theta,er,C_F:C,Cprime_F_per_m:Cprime,normalized:C/base,panels:a.panels,exact:b.exact,interpolated:!b.exact,bracket:[a.theta_deg,z.theta_deg],residual:Math.max(a.residual,z.residual)};
}
export function fieldNodes(theta:number,er:number){if(theta===0&&DATA.erFields[String(er)]){const a=DATA.erFields[String(er)];return{a,b:a,t:0,exact:true}}const q=bracket(theta),ls=DATA.fields[String(er===1?1:4)];return{a:ls[q.i],b:ls[q.j],t:q.t,exact:q.exact}}
const decoded=new Map<string,Uint16Array>();
export function decodeU16(s:string){let a=decoded.get(s);if(a)return a;const raw=atob(s);const bytes=Uint8Array.from(raw,c=>c.charCodeAt(0));a=new Uint16Array(bytes.buffer);decoded.set(s,a);return a;}
export function materialColor(er:number):Vec3{return er===1?[.72,.83,.88]:[.44,.69,.65]}
