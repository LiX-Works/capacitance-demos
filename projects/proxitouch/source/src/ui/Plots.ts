import {interaction} from '../physics/interaction.js';
import {mutualSignal} from '../models/FringeField.js';
import {ModelState} from '../app/state.js';
const MUTUAL_Y_MAX=Math.max(.01,Math.ceil(Math.max(...Array.from({length:161},(_,i)=>mutualSignal(i/160)))*1.15*100)/100);
export const mutualPlotLimit=()=>MUTUAL_Y_MAX;
export class Plots {
 root:HTMLDivElement;last='';
 constructor(parent:HTMLElement){this.root=document.createElement('div');this.root.className='plot hidden';parent.append(this.root);}
 update(type:'none'|'mutual'|'dual'|'mini',s:ModelState){
  const key=[type,s.depth,s.approach].join(',');if(key===this.last)return;this.last=key;this.root.className='plot '+type+(type==='none'?' hidden':'');if(type==='none')return;
  if(type==='mutual'){
   const X=(t:number)=>34+t*320,Y=(v:number)=>190-v/MUTUAL_Y_MAX*160;
   const path=Array.from({length:81},(_,i)=>{const t=i/80*s.approach;return `${i?'L':'M'}${X(t)},${Y(mutualSignal(t))}`;}).join(' '),signal=mutualSignal(s.approach);
   this.root.innerHTML=`<h3>\u4e92\u7535\u5bb9\u54cd\u5e94</h3><svg viewBox="0 0 380 232" role="img" aria-label="\u5f52\u4e00\u5316\u4e92\u7535\u5bb9\u53d8\u5316"><path class="axis" d="M34,25V190H354 M34,110H354"/><text x="8" y="194">0</text><text x="0" y="34">${MUTUAL_Y_MAX.toFixed(2)}</text><path class="hc trace" d="${path}"/><circle class="hc dot" cx="${X(s.approach)}" cy="${Y(signal)}" r="4.5"/><text x="34" y="220">\u8fdc</text><text x="333" y="220">\u8fd1</text></svg><div class="readout"><span>S<sub>prox</sub></span><b>${signal.toFixed(3)}</b></div><p class="plot-note">\u5f52\u4e00\u5316\u793a\u610f\uff0c\u975e\u5b9e\u6d4b\u66f2\u7ebf\u3002</p>`;return;
  }
  const row=(channel:'hc'|'cb',title:string)=>{
   const X=(d:number)=>34+(d+1)*160,Y=(v:number)=>142-v*114,value=s.interaction[channel];
   const points=Array.from({length:121},(_,i)=>{const d=-1+i/60;return{d,x:X(d),y:Y(interaction(d)[channel])};}),path=(ps:typeof points)=>ps.map((p,i)=>`${i?'L':'M'}${p.x},${p.y}`).join(' ');
   return `<section class="plot-row"><h3><span class="key ${channel}"></span>${title}<b>${value.toFixed(2)}</b></h3><svg viewBox="0 0 380 188" role="img" aria-label="${title}"><rect class="overlap" x="181" y="20" width="56" height="122"/><path class="axis" d="M34,25V142H354 M34,85H354"/><text x="8" y="146">0</text><text x="8" y="32">1</text><path class="future" d="${path(points)}"/><path class="trace ${channel}" d="${path(points.filter(p=>p.d<=s.depth+.012))}"/><path class="cursor" d="M${X(s.depth)},25V145"/><circle class="dot ${channel}" cx="${X(s.depth)}" cy="${Y(value)}" r="4.4"/><text x="34" y="175">\u63a5\u8fd1</text><text x="179" y="175">\u8f7b\u89e6</text><text x="322" y="175">\u538b\u529b</text></svg></section>`;
  };
  this.root.innerHTML=row('hc','\u7a7a\u95f4\u901a\u9053 HC')+row('cb','\u754c\u9762\u901a\u9053 CB')+'<p class="plot-note">\u4e24\u8def\u5206\u522b\u5f52\u4e00\u5316\uff0c\u975e\u5b9e\u6d4b\u66f2\u7ebf\u3002<br>\u9634\u5f71\u533a\uff1a\u8f7b\u89e6\u9644\u8fd1\u53ef\u91cd\u53e0\u7684\u54cd\u5e94\u3002</p>';
 }
}
