import { interaction, Interaction } from '../physics/interaction.js';
export type WorldKind='macro'|'micro'|'nano'|'device'|'application';
export interface ModelState {
 scene:string;phase:number;gap:number;overlap:number;dielectric:number;partition:number;
 field:number;charges:number;morph:number;approach:number;bias:number;interfaces:number;
 scale:number;depth:number;pressure:number;explosion:number;arrayCount:number;
 haloEmphasis:number;coreEmphasis:number;guardEmphasis:number;time:number;ambientTime:number;
 merge:number;scan:number;mux:number;highlight:number;curvature:number;interaction:Interaction;
}
export const defaultState:ModelState={scene:'S00',phase:0,gap:1.7,overlap:1,dielectric:0,partition:0,field:1,charges:1,morph:0,approach:0,bias:0,interfaces:1,scale:0,depth:-1,pressure:0,explosion:0,arrayCount:1,haloEmphasis:1,coreEmphasis:1,guardEmphasis:0,time:0,ambientTime:0,merge:1,scan:0,mux:0,highlight:0,curvature:0,interaction:interaction(-1)};
export type StatePatch=Partial<Omit<ModelState,'interaction'|'scene'>>;
export function deriveState(scene:string,patch:StatePatch,phase:number,time=0,ambientTime=0):ModelState{const state={...defaultState,...patch,scene,phase,time,ambientTime};state.interaction=interaction(state.depth);state.pressure=state.interaction.pressure;return state;}
