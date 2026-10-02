import assert from 'node:assert/strict';
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import ts from '../node_modules/typescript/lib/typescript.js';

const source=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const output=await mkdtemp(path.join(tmpdir(),'mutual-model-regressions-'));
try{
 const program=ts.createProgram(['main.ts','models/Experiment.ts','ui/Chart.ts'].map(name=>path.join(source,'src',name)),{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.NodeNext,moduleResolution:ts.ModuleResolutionKind.NodeNext,rootDir:path.join(source,'src'),outDir:output,strict:true,skipLibCheck:true});
 const diagnostics=ts.getPreEmitDiagnostics(program);
 assert.equal(diagnostics.length,0,ts.formatDiagnosticsWithColorAndContext(diagnostics,{getCanonicalFileName:x=>x,getCurrentDirectory:()=>source,getNewLine:()=> '\n'}));
 assert.equal(program.emit().emitSkipped,false);
 await writeFile(path.join(output,'package.json'),' {"type":"module"}');
 const load=name=>import(pathToFileURL(path.join(output,name)).href);
 const {Application}=await load('main.js'),{Experiment}=await load('models/Experiment.js'),{Chart}=await load('ui/Chart.js');
 const {SCENES,stateFor}=await load('scenes/definitions.js'),{analytic}=await load('physics/model.js');
 globalThis.requestAnimationFrame=()=>0;
 const makeApp=(id='06')=>{
  const app=Object.create(Application.prototype);
  Object.assign(app,{index:SCENES.findIndex(s=>s.id===id),phase:.35,animation:undefined,explore:false,fieldCycleIndex:2,fieldCycleModes:['lines','potential','strength'],overrideField:'strength',overrideEr:1,fullWidth:false,auto:false,history:[],frameTimes:[],lastFrame:0,dirty:true,camera:{state:{position:[7,4,10],target:[.2,1,0],fov:34,offset:0}},hud:{close(){}}});
  app.draw=function(){this.state=this.derive();this.dirty=false;};app.draw();return app;
 };
 for(const playing of [false,true])for(const auto of [false,true]){
  const app=makeApp();app.auto=auto;if(playing)app.animate();
  const camera=structuredClone(app.camera.state);app.toggleExplore(true);
  assert.equal(app.animation,undefined);assert.equal(app.auto,false);
  app.setField('lines');app.overrideEr=4;app.fullWidth=true;app.manualCamera={...camera,position:[99,4,10]};app.overrideTheta=140;
  app.toggleExplore(false);
  assert.equal(app.explore,false);assert.equal(app.fieldCycleIndex,2);assert.equal(app.overrideField,'strength');assert.equal(app.overrideEr,1);assert.equal(app.fullWidth,false);assert.equal(app.phase,.35);assert.equal(app.auto,auto);assert.equal(!!app.animation,playing);assert.deepEqual(app.manualCamera,camera);assert.equal(app.overrideTheta,undefined);
 }
 const ended=makeApp();ended.phase=1;ended.auto=true;let scheduled=0;ended.schedule=()=>scheduled++;ended.toggleExplore(true);ended.toggleExplore(false);assert.equal(scheduled,1);
 const timerApp=makeApp();timerApp.timer=setTimeout(()=>assert.fail('exploration should cancel pending next-page timer'),10000);timerApp.toggleExplore(true);assert.equal(timerApp.timer,undefined);
 const previousFromExplore=makeApp('01');previousFromExplore.auto=true;previousFromExplore.animate();previousFromExplore.toggleExplore(true);previousFromExplore.previous();assert.equal(previousFromExplore.auto,false);assert.equal(previousFromExplore.phase,0);
 const cycling=makeApp();cycling.resetFieldCycle();for(const mode of ['lines','potential','strength','lines']){assert.equal(cycling.overrideField,mode);cycling.advanceFieldCycle();}
 for(const id of ['04','09']){const app=makeApp(id);const before=app.overrideField;app.advanceFieldCycle();assert.equal(app.overrideField,before);}
 const controls=makeApp();let pauses=0,prevented=0;controls.togglePause=()=>pauses++;
 for(const selector of ['button','input','a','contenteditable'])controls.key({key:' ',target:{closest:()=>selector},preventDefault:()=>prevented++});
 assert.equal(pauses,0);assert.equal(prevented,0);
 controls.key({key:' ',target:{closest:()=>null},preventDefault:()=>prevented++});assert.equal(pauses,1);assert.equal(prevented,1);
 controls.key({key:' ',ctrlKey:true,target:{closest:()=>null},preventDefault:()=>assert.fail('modified shortcut intercepted')});assert.equal(pauses,1);
 const captureApp=makeApp();captureApp.auto=true;captureApp.animate();captureApp.timer=setTimeout(()=>assert.fail('capture must cancel pending navigation'),10000);
 const captureBefore=captureApp.snapshot();captureApp.setCapture(true);assert.equal(captureApp.animation,undefined);assert.equal(captureApp.timer,undefined);assert.equal(captureApp.auto,false);
 captureApp.animate();captureApp.schedule();captureApp.autoplay();captureApp.togglePause();captureApp.tick(performance.now()+60000);
 assert.equal(captureApp.snapshot().phase,captureBefore.phase);assert.deepEqual(captureApp.snapshot().state,captureBefore.state);assert.equal(captureApp.snapshot().playing,false);assert.equal(captureApp.timer,undefined);assert.equal(captureApp.auto,false);
 captureApp.setCapture(false);assert.equal(captureApp.animation,undefined,'leaving capture does not silently restart');captureApp.animate();assert.ok(captureApp.animation,'normal animation resumes when requested');captureApp.stop();assert.equal(captureApp.animation,undefined);
 const invalidApp=makeApp();invalidApp.animate();const invalidBefore=invalidApp.snapshot(),invalidAnimation=invalidApp.animation;
 for(const value of [NaN,Infinity,-Infinity])for(const call of [()=>invalidApp.go('01',value,true),()=>invalidApp.seek(value),()=>invalidApp.setTheta(value)]){assert.throws(call,RangeError);assert.deepEqual(invalidApp.snapshot(),invalidBefore);assert.equal(invalidApp.animation,invalidAnimation);}
 invalidApp.seek(-2);assert.equal(invalidApp.phase,0);invalidApp.seek(3);assert.equal(invalidApp.phase,1);invalidApp.go('01',2);assert.equal(invalidApp.phase,1);invalidApp.setTheta(200);assert.equal(invalidApp.overrideTheta,180);
 const frames=makeApp();frames.phase=.4;frames.animate();const start=frames.animation.start,duration=frames.scene.duration*1000;
 frames.tick(start+duration*.1);assert.ok(Math.abs(frames.phase-.5)<1e-10,'resume keeps the original phase speed');
 frames.animation=undefined;for(let i=1;i<=600;i++){frames.dirty=true;frames.tick(i*16);frames.record();}
 assert.equal(frames.frameTimes.length,180);assert.equal(frames.history.length,256);
 const experiment=new Experiment(),pool=experiment.dimensionMeshes.map(m=>m.geometry);
 for(let i=0;i<500;i++){experiment.visibleWidth=.028;experiment.updateDimensions({...stateFor(SCENES[1],0),theta:i%2?180:0},i%3?'02':'03');}
 assert.equal(experiment.dimensions.children.length,4);assert.deepEqual(experiment.dimensionMeshes.map(m=>m.geometry),pool);
 assert.equal(experiment.dimensionMeshes.filter(m=>m.visible).length,4);
 experiment.updateDimensions(stateFor(SCENES[2],0),'03');assert.equal(experiment.dimensionMeshes.filter(m=>m.visible).length,2);
 const chart=Object.create(Chart.prototype);chart.root={classList:{toggle(){}},innerHTML:''};chart.log=false;chart.last='';
 const scene=SCENES.find(s=>s.id==='06'),state={...stateFor(scene,0),theta:0,er:4};chart.update(scene,state);
 const marker=Number(chart.root.innerHTML.match(/class="marker"[^>]*cy="([^"]+)"/)[1]);
 assert.ok(marker>=35&&marker<=194,'er=4 current marker stays inside the chart');
 assert.match(chart.root.innerHTML,/class="trace diel"/);assert.match(chart.root.innerHTML,/εr = 4 · 二维数值/);
 const firstDielectricY=Number(chart.root.innerHTML.match(/class="trace diel" d="M65\.00,([\d.]+)/)[1]);assert.ok(Math.abs(marker-firstDielectricY)<.01,'current marker lies on the matching material curve');
 const models=SCENES.find(s=>s.id==='03');chart.update(models,{...state,er:4});
 const approxY=Number(chart.root.innerHTML.match(/class="trace approx" d="M65\.00,([\d.]+)/)[1]);assert.ok(Math.abs(approxY-(194-analytic(0,4).C*1e12/30*159))<.01,'local approximation uses the selected dielectric');
 chart.update(models,{...state,er:1});assert.match(chart.root.innerHTML,/局部条带 · εr = 1/);
 console.log('Mutual model regressions passed: exploration, native keys, repeat modes, resumed playback, bounded diagnostics, reusable dimension geometry, material chart, stable capture, finite API inputs.');
}finally{await rm(output,{recursive:true,force:true});}
