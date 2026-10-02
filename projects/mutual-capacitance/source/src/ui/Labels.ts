import {CameraRig} from '../engine/camera.js';
import {Annotation} from '../models/Experiment.js';
import {clamp} from '../engine/math.js';
export class Labels{
 root:HTMLElement;overlap=0;out=0;constructor(parent:HTMLElement){this.root=document.createElement('div');this.root.className='labels';parent.append(this.root)}
 update(items:Annotation[],camera:CameraRig,rect:DOMRect){this.root.innerHTML='<svg class="leaders"></svg>';const svg=this.root.querySelector('svg')!;svg.setAttribute('viewBox',`0 0 ${innerWidth} ${innerHeight}`);const used:DOMRect[]=[];this.overlap=0;this.out=0;
 const overlap=(a:{left:number,right:number,top:number,bottom:number},b:DOMRect)=>Math.max(0,Math.min(a.right,b.right)-Math.max(a.left,b.left))*Math.max(0,Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top));
 for(const l of items.slice(0,4)){const p=camera.project(l.point,innerWidth,innerHeight);if(!p.valid)continue;const el=document.createElement('div');el.className='world-label';const b=document.createElement('strong');b.textContent=l.title;el.append(b);if(l.detail){const d=document.createElement('small');d.textContent=l.detail;el.append(d)}this.root.append(el);const w=el.offsetWidth,h=el.offsetHeight,ox=(l.offset?.[0]||65)*innerWidth/1920,oy=(l.offset?.[1]||-35)*innerHeight/1080;
 const cand=[[ox,oy],[-w-35,oy],[ox,oy+80],[-w-35,oy+65],[ox,-70],[-w-30,-90]];let best={x:0,y:0,score:Infinity};for(const [dx,dy]of cand){const x=clamp(p.x+dx,rect.left+10,rect.right-w-8),y=clamp(p.y+dy,rect.top+10,rect.bottom-h-10);let score=Math.hypot(x-(p.x+ox),y-(p.y+oy));for(const u of used)score+=overlap({left:x,right:x+w,top:y,bottom:y+h},u)*80;if(score<best.score)best={x,y,score}}
 el.style.left=best.x+'px';el.style.top=best.y+'px';const r=el.getBoundingClientRect();for(const u of used)if(overlap(r,u)>2)this.overlap++;used.push(r);if(r.left<0||r.right>innerWidth||r.top<0||r.bottom>innerHeight)this.out++;
 const endx=p.x<r.left?r.left:p.x>r.right?r.right:clamp(p.x,r.left+5,r.right-5),endy=clamp(p.y,r.top+5,r.bottom-5);
 if(p.x>rect.left&&p.x<rect.right&&p.y>rect.top&&p.y<rect.bottom)svg.insertAdjacentHTML('beforeend',`<line x1="${p.x}" y1="${p.y}" x2="${endx}" y2="${endy}"/><circle cx="${p.x}" cy="${p.y}" r="2.1"/>`);
 }
 }
}
