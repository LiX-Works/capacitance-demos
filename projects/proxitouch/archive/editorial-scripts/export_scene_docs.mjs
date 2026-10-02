/** Export R3 scoped copy and internal interpolation states. */
import fs from 'node:fs';
import path from 'node:path';
import {SCENES,scenePatch} from '../../dist/js/scenes/definitions.js';
import {deriveState} from '../../dist/js/app/state.js';
const root=path.resolve(import.meta.dirname,'../..');
fs.mkdirSync(path.join(root,'docs'),{recursive:true});
let copy='# ProxiTouch R3 / approved audience copy\n\nS00-S21 imported from revision specification 01; S22 uses the explicit R3 override. Animation directions are not audience copy. Internal keyframes do not add navigation steps.\n\n';
const states=[];
for(const scene of SCENES){
 copy+=`## ${scene.id} / ${scene.title}\n\n${scene.body}\n\n`;
 scene.beats.forEach((keyframe,index)=>{const phase=keyframe.at;states.push({scene:scene.id,keyframe:index,phase,state:deriveState(scene.id,scenePatch(scene,phase),phase,phase*scene.duration)});});
}
fs.writeFileSync(path.join(root,'docs/AUDIENCE_COPY.md'),copy);
fs.writeFileSync(path.join(root,'docs/SCENE_MANIFEST.json'),JSON.stringify(SCENES,null,2));
fs.writeFileSync(path.join(root,'docs/INTERNAL_STATES.json'),JSON.stringify(states,null,2));
console.log('Exported',SCENES.length,'R3 pages;',states.length,'internal state anchors.');
