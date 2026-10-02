import { Node, Mesh, InstancedMesh, Material, metals, mesh, fieldMaterial } from '../engine/scene.js';
import { Geometry, roundedBox, TubeGeometry, cylinder, box } from '../engine/geometry.js';
import { Vec3, clamp, mix } from '../engine/math.js';
export interface CapState {
    gap: number;
    overlap: number;
    dielectric: number;
    partition: number;
    field: number;
    charges: number;
}
export class Capacitor extends Node {
    top: Mesh;
    bottom: Mesh;
    slab: Mesh;
    areas: Mesh[] = [];
    dielectrics: Mesh[] = [];
    field: Mesh;
    fieldGeometry: TubeGeometry;
    charges: Node;
    positive: InstancedMesh;
    negative: InstancedMesh;
    readonly chargeColumns=10;readonly chargeRows=7;
    last = '';
    width = 4.8;
    depth = 3.2;
    constructor() {
        super();
        this.bottom = mesh(this, roundedBox(this.width, .24, this.depth, .075), metals.silver);
        this.top = mesh(this, this.bottom.geometry, metals.silver.clone(), [0, 1.94, 0]);
        this.slab = mesh(this, roundedBox(4.6, 1, 3, .07), new Material(0x91c4cb, { roughness: .68, opacity: .62, softness: .65 }));
        this.areas = [mesh(this, roundedBox(1, .009, 3, .001), new Material(0x6bb2c7, { roughness: .8, opacity: .58 }), [0, .126, 0]), mesh(this, roundedBox(1, .009, 3, .001), new Material(0x69b9c9, { roughness: .8, opacity: .6 }))];
        for (const color of [0x71afbe, 0xc6b283])
            this.dielectrics.push(mesh(this, roundedBox(1, 1, 3.05, .055), new Material(color, { roughness: .68, opacity: .60, softness: .48 })));
        this.fieldGeometry = new TubeGeometry(24, 40, 5);
        this.field = mesh(this, this.fieldGeometry, fieldMaterial());
        this.field.castShadow = false;
        this.charges = this.add(new Node());
        const gm=box(.145,.022,.028),pos=new Material(0xc8872b,{roughness:.65,emission:.12}),neg=new Material(0x245d87,{roughness:.65,emission:.08});
        const count=this.chargeColumns*this.chargeRows;
        this.positive=this.charges.add(new InstancedMesh(gm,pos,count*2));
        this.negative=this.charges.add(new InstancedMesh(gm,neg,count));
        this.positive.castShadow=this.negative.castShadow=false;
        this.positive.receiveShadow=this.negative.receiveShadow=false;
        for(let z=0;z<this.chargeRows;z++)for(let x=0;x<this.chargeColumns;x++){
            const i=z*this.chargeColumns+x,px=-2.04+x*4.08/(this.chargeColumns-1),pz=-1.26+z*2.52/(this.chargeRows-1);
            this.negative.set(i,[px,.17,pz]);
            this.positive.set(i*2,[px,.245,pz]);
            this.positive.set(i*2+1,[px,.245,pz],[0,0,Math.PI/2]);
        }
        this.set({ gap: 1.7, overlap: 1, dielectric: 0, partition: 0, field: 1, charges: 1 });
    }
    set(s: CapState) {
        const key = JSON.stringify(s);
        if (key === this.last)
            return;
        this.last = key;
        const shift = (1 - s.overlap) * this.width;
        this.top.position = [shift, s.gap + .24, 0];
        this.slab.visible = s.dielectric > 0 && s.partition === 0;
        this.slab.position = [mix(5.1, 0, s.dielectric), s.gap / 2 + .12, 0];
        this.slab.scale = [1, s.gap * .91, 1];
        this.field.material.opacity = s.field * .7;
        this.field.visible = s.field > 0;
        const overlapWidth = this.width - shift, overlapCenter = shift / 2;
        this.areas.forEach((m, i) => { m.visible = s.overlap < .99; m.scale[0] = overlapWidth; m.position = [overlapCenter, i === 0 ? .126 : s.gap + .114, 0]; });
        this.dielectrics.forEach((m, i) => { m.visible = s.partition > 0; if (s.partition === 1) {
            m.position = [(i === 0 ? -1 : 1) * this.width * .245, s.gap / 2 + .12, 0];
            m.scale = [this.width * .477, s.gap * .94, 1];
        }
        else {
            m.position = [0, .12 + s.gap * (i === 0 ? .25 : .75), 0];
            m.scale = [this.width * .96, s.gap * .465, 1];
        } });
        const paths: Vec3[][] = [];
        for (let j = 0; j < 4; j++)
            for (let i = 0; i < 6; i++) {
                const x = shift - this.width / 2 + (i + .5) / 6 * overlapWidth, z = -1.18 + j * .785, p: Vec3[] = [];
                for (let k = 0; k < 40; k++)
                    p.push([x, .132 + (s.gap - .02) * k / 39, z]);
                paths.push(p);
            }
        this.fieldGeometry.update(paths, .0105);
        this.charges.visible=s.charges>0;
        this.positive.position=[shift,s.gap+.24,0];
        this.positive.material.opacity=this.negative.material.opacity=clamp(s.charges);

    }
}
