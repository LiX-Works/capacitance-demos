import {clamp,smooth} from '../engine/math.js';
/** Only these presentation pages own an ambient loop. No scene phase is mutated. */
export const AMBIENT_SCENES=new Set(['S05','S07','S18']);
export class AmbientClock {
 scene='';seconds=0;private last=0;private running=false;
 sample(scene:string,now:number,capture=false,captureSeconds=0,explore=false):number {
  if(scene!==this.scene){this.scene=scene;this.seconds=0;this.running=false;}
  const active=AMBIENT_SCENES.has(scene)&&!explore;
  if(active&&!capture&&this.running)this.seconds+=Math.max(0,(now-this.last)/1000);
  this.last=now;this.running=active&&!capture;
  return active?(capture?captureSeconds:this.seconds):0;
 }
 reset(){this.seconds=0;this.running=false;}
}
const ramp=(x:number,a:number,b:number)=>smooth(clamp((x-a)/(b-a)));
/** S05: default -> horizontal region i -> vertical layer j -> heterogeneous materials -> default. */
export function compositeWeights(seconds:number){
 const p=((seconds%9.6)+9.6)%9.6/9.6;
 const region=ramp(p,.10,.20)*(1-ramp(p,.82,.94));
 const layer=ramp(p,.34,.44)*(1-ramp(p,.82,.94));
 const material=ramp(p,.58,.68)*(1-ramp(p,.86,.97));
 return {phase:p,region,layer,material};
}
/** R2 nominal dwell = 3.6/9 = 0.4 s. R3 dwell = 1 s (40% switching speed). */
export const MUX_DWELL_SECONDS=1;
export function multiplexWeight(seconds:number){
 const p=((seconds%2)+2)%2;
 return p<1?ramp(p,.76,1):1-ramp(p,1.76,2);
}
