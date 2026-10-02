import {DATA} from '../physics/data.js';
import {sample,analytic,ModelState} from '../physics/model.js';
import {Scene} from '../scenes/definitions.js';
const pf=(v:number)=>v*1e12;
export class Chart{
 root:HTMLElement;log=false;last='';
 constructor(parent:HTMLElement){this.root=document.createElement('section');this.root.className='chart';parent.append(this.root);}
 update(scene:Scene,s:ModelState){const key=[scene.id,s.theta,s.er,this.log].join('|');if(key===this.last)return;this.last=key;const kind=scene.chart;this.root.classList.toggle('hidden',kind==='none');if(kind==='none')return;
 const W=1450,H=235,l=65,r=1405,top=35,bottom=194;
 const erPlot=kind==='er',xmax=erPlot?8:180,x=(v:number)=>l+(v/(xmax))*(r-l);
 const current=sample(s.theta,s.er),currentRows=DATA.curves[String(s.er===1?1:4)];
 const plotted=erPlot?DATA.er_scan:[...DATA.curves['1'],...(kind==='dielectric'||s.er!==1?DATA.curves['4']:[])];
 const maxValue=Math.max(pf(current.C_F),...plotted.map((v:any)=>pf(v.C_F)),...(kind==='validation'?DATA.checks3d.rows.map((v:any)=>pf(v.C3D_F)):[]));
 const ymax=Math.max(erPlot?40:kind==='dielectric'?34:28,Math.ceil(maxValue/5)*5),log=this.log&&!erPlot;
 const y=(v:number)=>bottom-(log?Math.log10(Math.max(.8,v)/.8)/Math.log10(40/.8):v/ymax)*(bottom-top);
 const ticks=log?[1,2,5,10,20,40]:Array.from({length:Math.floor(ymax/(ymax>30?10:5))+1},(_,i)=>i*(ymax>30?10:5));
 let svg=`<svg viewBox="0 0 ${W} ${H}" aria-label="${erPlot?'介电常数':'展开角'}与绝对电容"><defs><clipPath id="plot-clip"><rect x="${l}" y="${top-8}" width="${r-l}" height="${bottom-top+9}"/></clipPath></defs>`;
 for(const t of ticks)svg+=`<path class="grid" d="M${l},${y(t)}H${r}"/><text x="${l-14}" y="${y(t)+5}" text-anchor="end">${t}</text>`;
 const xticks=erPlot?[1,2,4,6,8]:[0,30,60,90,120,150,180];for(const t of xticks)svg+=`<path class="tick" d="M${x(t)},${bottom}v5"/><text x="${x(t)}" y="${bottom+26}" text-anchor="middle">${t}${erPlot?'':'°'}</text>`;
 svg+=`<text class="axis-label" x="${l}" y="17">C / pF${log?'（对数）':''}</text><text x="${r}" y="${bottom+26}" text-anchor="end" class="axis-extra">${erPlot?'εr':'θ'}</text><g clip-path="url(#plot-clip)">`;
 const path=(pts:{x:number,y:number|null}[],cls:string)=>{let d='',started=false;for(const p of pts){if(p.y===null||!Number.isFinite(p.y)){started=false;continue}d+=`${started?'L':'M'}${x(p.x).toFixed(2)},${y(p.y).toFixed(2)} `;started=true;}return `<path class="trace ${cls}" d="${d}"/>`;};
 let legend='<i class="air"></i>空气 · 二维数值';
 if(erPlot){const rows=DATA.er_scan;svg+=path(rows.map((v:any)=>({x:v.er,y:pf(v.C_F)})),'diel');svg+=path(rows.map((v:any)=>({x:v.er,y:pf(v.analytic.strip_F)})),'approx');for(const row of rows)svg+=`<circle class="node diel-dot" cx="${x(row.er)}" cy="${y(pf(row.C_F))}" r="4.5"/>`;legend='<i class="diel"></i>数值节点 <i class="approx"></i>局部串联近似';
 }else{
  svg+=path(DATA.curves['1'].map((v:any)=>({x:v.theta_deg,y:pf(v.C_F)})),'air');
  if(kind==='dielectric'||s.er!==1){svg+=path(DATA.curves['4'].map((v:any)=>({x:v.theta_deg,y:pf(v.C_F)})),'diel');legend+=' <i class="diel"></i>εr = 4 · 二维数值';}
  if(kind==='dielectric'){svg+=path(currentRows.map((v:any)=>({x:v.theta_deg,y:v.analytic.strip_F===null?null:pf(v.analytic.strip_F)})),'approx');legend+=` <i class="approx"></i>局部近似 · εr = ${s.er}`;}
  if(kind==='models'){svg+=path(currentRows.map((v:any)=>({x:v.theta_deg,y:v.analytic.strip_F===null?null:pf(v.analytic.strip_F)})),'approx');svg+=path(DATA.curves['1'].map((v:any)=>({x:v.theta_deg,y:v.analytic.wedge_F===null?null:pf(v.analytic.wedge_F)})),'sector');legend+=` <i class="approx"></i>局部条带 · εr = ${s.er} <i class="sector"></i>映射扇区候选${s.er!==1?' · 空气':''}`;}
  if(kind==='validation'){for(const row of DATA.checks3d.rows.filter((v:any)=>v.nl===14)){const xx=x(row.theta_deg),yy=y(pf(row.C3D_F));svg+=`<path class="check3d" d="M${xx},${yy-6}l6,6 -6,6 -6,-6Z"/>`;}legend+=' <i class="check3d"></i>有限宽度 3D 检查点 · 空气';}
 }
 const v=current,xx=x(erPlot?s.er:s.theta),yy=y(pf(v.C_F));svg+=`<path class="cursor" d="M${xx},${top-2}V${bottom}"/><circle class="marker" cx="${xx}" cy="${yy}" r="5.5"/>`;
 svg+='</g></svg>';
 const an=analytic(s.theta,s.er),error=an.C===null?'此角度不适用':((an.C/v.C_F-1)*100).toFixed(1)+'%';
 const sub=kind==='models'||kind==='dielectric'?`当前局部近似偏差 ${error}`:kind==='validation'?'3D 只有三个检查点，未求解整条 3D 曲线':erPlot?'每个实心点是独立求解，连线仅引导阅读':'实线连接计算节点；非节点角度使用线性插值';
 this.root.innerHTML=`<div class="chart-heading"><div class="legend">${legend}</div><span>${sub}</span></div>${svg}`;
 }
}
