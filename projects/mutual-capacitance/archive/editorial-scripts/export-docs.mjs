import fs from 'node:fs';import path from 'node:path';import {SCENES} from '../../dist/js/scenes/definitions.js';
const root=path.resolve(import.meta.dirname,'../..');fs.mkdirSync(path.join(root,'docs'),{recursive:true});fs.writeFileSync(path.join(root,'docs/SCENE_MANIFEST.json'),JSON.stringify(SCENES,null,2));
fs.writeFileSync(path.join(root,'docs/SCENE_COPY.md'),'# Capacitance Lab - scene copy\n\n'+SCENES.map(s=>'## '+s.id+' / '+s.title+'\n\n'+s.body+'\n\n```tex\n'+s.formula+'\n```\n\n'+s.meaning+'\n').join('\n---\n\n'));
console.log('Exported',SCENES.length,'scene definitions and copy.');
