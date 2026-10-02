import './r2_models.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import { SCENES,scenePatch,sceneCamera } from '../../dist/js/scenes/definitions.js';
import { COPY } from '../../dist/js/scenes/copy.js';
import { AmbientClock,AMBIENT_SCENES,compositeWeights,multiplexWeight,MUX_DWELL_SECONDS } from '../../dist/js/app/ambient.js';
import { Capacitor } from '../../dist/js/models/Capacitor.js';
import { FringeField } from '../../dist/js/models/FringeField.js';
import { IonicVolume } from '../../dist/js/models/IonicVolume.js';
import { Device } from '../../dist/js/models/Device.js';
import { SharedArray } from '../../dist/js/models/SharedArray.js';
import {multiply,transform} from '../../dist/js/engine/math.js';
import { ApplicationHero } from '../../dist/js/models/ApplicationHero.js';
const tests=[];function test(name,fn){fn();tests.push({name,passed:true});console.log('PASS R3',name);}
const near=(a,b,t=1e-6)=>assert.ok(Math.abs(a-b)<t,`${a} != ${b}`);
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const baseline=JSON.parse(fs.readFileSync('../docs/r3/R2_BASELINE.json','utf8'));
test('Only final-patch copy pages differ from the approved R2/R3 baseline',()=>{for(let i=0;i<22;i++){if([10,11].includes(i))continue;const id='S'+String(i).padStart(2,'0');assert.equal(hash(COPY[id].title+'\n'+COPY[id].body),baseline.copy[id]);}});
test('Low-level renderer patch changes only per-instance alpha',()=>{assert.equal(hash(fs.readFileSync('src/engine/renderer.ts','utf8').replace('float alpha=uOpacity*vColor.a;','float alpha=uOpacity;')),baseline.files['src/engine/renderer.ts']);});
test('Original geometry, camera, microstructure, field data and plots are unchanged',()=>{for(const name of baseline.lockedFiles)assert.equal(hash(fs.readFileSync(name)),baseline.files[name],name);});
const cap=new Capacitor();
test('70 pluses and 70 minuses cover a 10 by 7 grid with margins',()=>{assert.equal(cap.positive.count,140);assert.equal(cap.negative.count,70);const xs=new Set(),zs=new Set();for(let i=0;i<70;i++){xs.add(cap.negative.matrices[i*16+12]);zs.add(cap.negative.matrices[i*16+14]);}assert.equal(xs.size,10);assert.equal(zs.size,7);assert.ok(Math.max(...xs)<2.4&&Math.min(...xs)>-2.4);assert.ok(Math.max(...zs)<1.6&&Math.min(...zs)>-1.6);});
test('Upper pluses stand clear of the top surface for every S02 state',()=>{for(let i=0;i<=60;i++){const s=scenePatch(SCENES[2],i/60);cap.set({...s,partition:0,field:1,charges:1});const top=cap.top.position[1]+.12;const lowest=cap.positive.position[1]+.245-.145/2;assert.ok(lowest>top+.02);assert.equal(cap.charges.visible,true);}assert.equal(cap.positive.castShadow,false);});
test('S03/S04 each retain two nodes and double duration',()=>{assert.equal(SCENES[3].duration,1.8);assert.equal(SCENES[4].duration,2.6);assert.equal(SCENES[3].beats.length,2);assert.equal(SCENES[4].beats.length,2);for(const i of [3,4]){const a=sceneCamera(SCENES[i],0),b=sceneCamera(SCENES[i],1);const yaw=c=>Math.atan2(c.position[0]-c.target[0],c.position[2]-c.target[2]);assert.ok(Math.abs(yaw(a)-yaw(b))>Math.PI/6);}});
test('Ambient pages are explicit and do not create extra main animations',()=>{assert.deepEqual([...AMBIENT_SCENES],['S05','S07','S18']);assert.equal(SCENES[5].duration,0);assert.equal(SCENES[18].duration,0);});
test('Ambient clock advances, freezes for capture, and pauses on Explore',()=>{const c=new AmbientClock();near(c.sample('S07',1000),0);near(c.sample('S07',2500),1.5);near(c.sample('S07',9000,true,3.2),3.2);near(c.sample('S07',19000,false,0,true),0);near(c.sample('S07',25000),1.5);near(c.sample('S07',26000),2.5);near(c.sample('S08',30000),0);near(c.sample('S07',33000),0);});
test('Composite cycles neutral -> region i -> layer j -> heterogeneous materials -> neutral',()=>{const a=compositeWeights(0),b=compositeWeights(2.2),c=compositeWeights(4.4),d=compositeWeights(6.8),e=compositeWeights(9.59);near(a.region,0);assert.ok(b.region>.95&&b.layer<.1);assert.ok(c.layer>.9);assert.ok(d.material>.9);assert.ok(e.region<.02&&e.layer<.02&&e.material<.02);for(let t=0;t<9.5;t+=.1){const x=compositeWeights(t),y=compositeWeights(t+9.6);near(x.region,y.region);near(x.layer,y.layer);near(x.material,y.material);}});
const fringe=new FringeField();
test('Hinge remains a fixed kinematic pivot but is optically invisible',()=>{for(let p=0;p<=1;p+=.05){fringe.set(p,0);assert.deepEqual(fringe.pivot.position,[0,1,0]);assert.ok(fringe.hinge.material.opacity<=.03);assert.equal(fringe.hinge.castShadow,false);assert.equal(fringe.hinge.receiveShadow,false);assert.equal(fringe.pivot.children[1].visible,false);}});
test('S07 flow spans all height families; other pages keep R2 eight indicators',()=>{fringe.set(1,0,1,0,false,true);assert.equal(fringe.particles.count,16);let max=0,min=9;for(let t=0;t<15;t+=.1){fringe.set(1,0,1,t,false,true);for(let i=0;i<16;i++){max=Math.max(max,fringe.particles.matrices[i*16+13]);min=Math.min(min,fringe.particles.matrices[i*16+13]);}}assert.ok(max>3.95);assert.ok(min<.5);fringe.set(1,0,1,0);assert.equal(fringe.particles.count,8);});
const ionic=new IonicVolume();
test('S10 is a finite main animation, not an ambient page',()=>{assert.equal(AMBIENT_SCENES.has('S10'),false);assert.ok(SCENES[10].duration>0);assert.equal(SCENES[10].beats.length,3);assert.ok(COPY.S10.body.includes('两侧 EDL 不发生明显重叠'));assert.ok(COPY.S10.body.includes('C\\not\\propto'));assert.ok(!COPY.S10.body.includes('C_{\\mathrm{bottom}}\\gg C_{\\mathrm{top}}'));});
test('S10 compression shortens macro gap while keeping local EDL thickness fixed',()=>{ionic.set(1,true,1,0,1,0,0);const top0=ionic.top.position[1],it0=ionic.interfaceTop.position[1],ib0=ionic.interfaceBottom.position[1];ionic.set(1,true,1,0,1,0,1);assert.ok(top0-ionic.top.position[1]>.95);near(it0-ionic.interfaceTop.position[1],top0-ionic.top.position[1]);near(ionic.interfaceBottom.position[1],ib0);near(ionic.interfaceTop.scale[1],1);near(ionic.interfaceBottom.scale[1],1);});
test('S10 screening emphasizes both interfaces and de-emphasizes bulk ions',()=>{ionic.set(1,true,1,0,1,0,0);ionic.setScreening(1);assert.ok(ionic.interfaceTop.material.emission>.35&&ionic.interfaceBottom.material.emission>.35);assert.ok(ionic.negative.colors[3]>.9);assert.ok(ionic.negative.colors[60*4+3]<.25);});
test('S11 uses generic microstructure language and omits repeated gap explanation',()=>{assert.ok(COPY.S11.body.includes('微结构'));assert.ok(!COPY.S11.body.includes('离子凝胶微穹顶'));assert.ok(!COPY.S11.body.includes('d\\downarrow'));});
test('No LegacyDevice import or object in the presentation world manager',()=>{const src=fs.readFileSync('src/worlds/WorldManager.ts','utf8');assert.ok(!src.includes('new LegacyDevice'));assert.ok(!src.includes('legacyWorld'));assert.ok(src.includes("world=this.deviceWorld;this.activate(world,this.device);this.device.set(-1,0,s.field,'hero')"));near(scenePatch(SCENES[13],0).field,.6);assert.deepEqual(SCENES[12].camera.at(-1),SCENES[13].camera[0]);});
test('Mux nominal dwell is 2.5 times R2 and has exactly two windows',()=>{near(MUX_DWELL_SECONDS/(3.6/9),2.5);near(multiplexWeight(.5),0);near(multiplexWeight(1.5),1);for(let t=0;t<2;t+=.02)near(multiplexWeight(t),multiplexWeight(t+2));const ui=fs.readFileSync('src/ui/HUD.ts','utf8');assert.ok(ui.includes('<b>HC</b><b>CB</b><small>'));});
const dev=new Device();
test('Mux changes emphasis smoothly without moving shared EC or field geometry',()=>{dev.set(.35,.38,.8,'multiplex');const geom=dev.fieldGeometry.version;const node=dev.channelNodes.HC[1];let last=1;for(let i=0;i<=40;i++){dev.emphasizeMultiplex(i/40);assert.equal(node,dev.channelNodes.CB[0]);assert.equal(dev.fieldGeometry.version,geom);assert.ok(dev.rails[0].material.opacity<=last+1e-8);last=dev.rails[0].material.opacity;}assert.equal(dev.activeWindow,'CB');assert.ok(dev.readout.material.opacity>.8);});
const array=new SharedArray();
test('During the four-pixel merge, outer borders never move',()=>{array.set(4,-1,0,0);const m=Array.from(array.independent.matrices);const outer=[];for(let i=0;i<16;i++){const x=m[i*16+12],z=m[i*16+14];if(Math.abs(x)>2.99||Math.abs(z)>2.99)outer.push(i);}assert.equal(outer.length,8);for(let step=0;step<=100;step++){array.set(4,-1,step/100,0);for(const i of outer)for(const j of [0,1,2,4,5,6,8,9,10,12,13,14])near(array.independent.matrices[i*16+j],m[i*16+j]);}});
test('Interior duplicate rails approach the midline monotonically',()=>{let distance=10;for(let t=0;t<=1.001;t+=.01){array.set(4,-1,t,0);const x=Math.abs(array.independent.matrices[1*16+12]);assert.ok(x<=distance+1e-7);distance=x;}assert.ok(distance<1e-6);});
test('Merge and 4-to-16 expansion have a resolved stable plateau',()=>{for(let i=0;i<=100;i++){const p=i/100,s=scenePatch(SCENES[20],p);if(p>=.34&&p<=.71)near(s.arrayCount,4);if(p>.71)near(s.merge,1);}near(scenePatch(SCENES[20],.66).merge,1);assert.ok((.71-.61)*SCENES[20].duration>=.7);});
const app=new ApplicationHero();
test('Application has two 10x16 skins, distinct ECs and nonduplicated shared boundaries',()=>{assert.equal(app.leftSkin.ec.count,160);assert.equal(app.rightSkin.ec.count,160);assert.equal(app.leftSkin.eh.count,346);assert.equal(app.rightSkin.eh.count,346);assert.notEqual(app.leftSkin.ec,app.rightSkin.ec);assert.equal(app.diagnostics().wholeGridShorted,false);});
test('Grasp is monotonic; first touch is local; pressure region expands; egg stays intact',()=>{let last=9;const egg=hash(new Uint8Array(app.egg.geometry.data.buffer));for(let t=-1;t<=.851;t+=.025){app.set(t);assert.ok(app.spread<=last+1e-9);last=app.spread;assert.equal(hash(new Uint8Array(app.egg.geometry.data.buffer)),egg);}app.set(-.01);assert.equal(app.leftSkin.contacts,0);app.set(.03);assert.ok(app.leftSkin.contacts>0&&app.leftSkin.contacts<=4);app.set(.85);assert.ok(app.leftSkin.contacts>12&&app.leftSkin.contacts<80);assert.equal(app.diagnostics().eggIntact,true);});
test('Ending keeps a static stopped grip after phase .92',()=>{const a=scenePatch(SCENES[22],.92),b=scenePatch(SCENES[22],1);near(a.depth,b.depth);assert.ok(!COPY.S22.body.includes('boxed'));assert.ok(COPY.S22.body.includes('Approach'));});
test('Dense EC and EH vertices do not penetrate the analytic intact egg envelope',()=>{
 assert.deepEqual(app.egg.scale,[1,1,.91]);let worst=2;
 for(let step=0;step<=20;step++){app.set(step/20*.85);app.update();
  for(const skin of [app.leftSkin,app.rightSkin])for(const name of ['ec','eh']){
   const m=skin[name];for(let i=0;i<m.count;i++){const matrix=multiply(m.world,m.matrices.subarray(i*16,i*16+16));
    for(let j=0;j<m.geometry.data.length;j+=8){const [x,y,z]=transform(matrix,Array.from(m.geometry.data.subarray(j,j+3))),h=(y-3.1)/1.95;if(Math.abs(h)>=1)continue;const r=1.39*Math.sqrt(1-h*h)*(1-.16*h),q=Math.hypot(x/r,z/(r*.91));worst=Math.min(worst,q);}
   }
  }
 }
 assert.ok(worst>=.999,`minimum normalized radius ${worst}`);
});
const prior=JSON.parse(fs.readFileSync('../qa/model-tests.json','utf8'));
fs.writeFileSync('../qa/r3-model-tests.json',JSON.stringify({sourceSha256:hash(fs.readFileSync('../dist/ProxiTouch-offline.html')),testCount:prior.testCount+tests.length,inheritedR2:prior.tests,revision3:tests,scope:'Software, geometry and timing consistency only; not empirical sensor validation'},null,2));
console.log('TOTAL',prior.testCount+tests.length);
