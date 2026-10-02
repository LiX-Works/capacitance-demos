import { Node, Mesh, InstancedMesh, Material, metals, mesh, gelMaterial, fieldMaterial, contactMaterial } from '../engine/scene.js';
import { cylinder, ring, sector, roundedBox, sphere, TubeGeometry } from '../engine/geometry.js';
import { Vec3, clamp, mix, smooth, hex } from '../engine/math.js';
import { MicroAssembly } from './Dome.js';
import { makeConductor } from './FringeField.js';
import { interaction } from '../physics/interaction.js';
import { haloFieldSample } from '../physics/haloField.js';
export class LegacyDevice extends Node {
    substrate: Node;
    halo: Node;
    core: MicroAssembly;
    guard: Mesh;
    field: Mesh;
    fieldGeometry: TubeGeometry;
    conductor: Node;
    vias: Node;
    last = '';
    constructor() {
        super();
        this.substrate = this.add(new Node());
        mesh(this.substrate, cylinder(3.6, .30, .09, 112), metals.dark, [0, 0, 0]);
        mesh(this.substrate, ring(3.40, 3.57, .045, 112), metals.silver, [0, .175, 0]);
        mesh(this.substrate, cylinder(3.43, .075, .018, 112), new Material(0xc6d1d7, { roughness: .64 }), [0, .172, 0]);
        mesh(this.substrate, ring(3.56, 3.60, .022, 112), metals.blue, [0, .04, 0]);
        const connector = this.substrate.add(new Node());
        connector.rotation[1] = -.25;
        mesh(connector, roundedBox(1.12, .075, 2.0, .10), metals.dark, [0, -.04, 4.25]);
        for (let i = 0; i < 4; i++)
            mesh(connector, roundedBox(.13, .016, .72, .01), new Material(0xba9e6f, { metalness: .74, roughness: .45 }), [-.33 + i * .22, .006, 4.75]);
        mesh(connector, roundedBox(1.04, .08, .15, .025), metals.silver, [0, -.055, 4.35]);
        this.halo = this.add(new Node());
        mesh(this.halo, ring(3.28, 3.42, .055, 112), metals.blue, [0, .265, 0]);
        mesh(this.halo, ring(2.55, 2.70, .055, 112), metals.silver, [0, .265, 0]);
        const n = 32;
        const tx = this.halo.add(new InstancedMesh(sector(2.78, 3.33, Math.PI / n * .49, .058, 5), metals.blue, n)), rx = this.halo.add(new InstancedMesh(sector(2.64, 3.17, Math.PI / n * .49, .058, 5), metals.silver, n));
        for (let i = 0; i < n; i++) {
            tx.set(i, [0, .265, 0], [0, i / n * Math.PI * 2, 0]);
            rx.set(i, [0, .265, 0], [0, (i + .5) / n * Math.PI * 2, 0]);
        }
        this.guard = mesh(this, ring(1.83, 2.39, .065, 112), new Material(0xc0d0d7, { roughness: .72, softness: .1 }), [0, .245, 0]);
        mesh(this, ring(2.39, 2.415, .031, 112), new Material(0x7193a8, { roughness: .7 }), [0, .265, 0]);
        mesh(this, ring(1.80, 1.83, .038, 112), new Material(0x728f9f, { roughness: .7 }), [0, .27, 0]);
        this.core = this.add(new MicroAssembly());
        this.core.position = [0, .315, 0];
        this.core.scale = [.52, .52, .52];
        this.vias = this.add(new Node());
        for (const [a, r] of [[2.5, 2.63], [2.72, 3.35]]) {
            mesh(this.vias, cylinder(.058, .023, .006, 20), metals.dark, [Math.cos(a) * r, .31, Math.sin(a) * r]);
            mesh(this.vias, ring(.023, .048, .015, 20), new Material(0xb49b70, { metalness: .6 }), [Math.cos(a) * r, .328, Math.sin(a) * r]);
        }
        for (const a of [.785, 2.356, 3.927, 5.498]) {
            const x = Math.cos(a) * 3.47, z = Math.sin(a) * 3.47;
            mesh(this.substrate, cylinder(.064, .017, .006, 24), metals.silver, [x, .224, z]);
            mesh(this.substrate, roundedBox(.059, .01, .012, .002), metals.dark, [x, .235, z], [0, a, 0]);
        }
        this.fieldGeometry = new TubeGeometry(48, 56, 5);
        this.field = mesh(this, this.fieldGeometry, fieldMaterial().clone({ opacity: .65 }));
        this.field.castShadow = false;
        this.conductor = this.add(makeConductor());
        this.conductor.scale = [2.3, .65, 2.3];
        this.conductor.visible = false;
        this.set(-1, 0, 0);
    }
    set(depth: number, explosion = 0, field = 0, emphasis = 'all', time = 0) {
        const key = [depth, explosion, field, emphasis].join(',');
        if (key === this.last)
            return;
        this.last = key;
        const state = interaction(depth);
        this.core.set(depth, explosion, true);
        this.substrate.position[1] = 0;
        this.halo.position[1] = explosion * .12;
        this.guard.position[1] = .245 + explosion * .12;
        this.guard.material.color = emphasis === 'guard' ? hex(0x87bac9) : hex(0xc0d0d7);
        this.guard.material.opacity = emphasis === 'core' ? .26 : 1;
        this.halo.visible = emphasis !== 'core-only';
        this.core.visible = emphasis !== 'halo-only';
        this.field.visible = field > 0;
        this.field.material.opacity = field * .65;
        this.conductor.visible = depth > -.93 && explosion < .15 && emphasis !== 'none';
        this.conductor.traverse(n => { if (n instanceof Mesh)
            n.material.opacity = smooth(clamp((depth + .93) / .10)); });
        const coverTop = this.core.position[1] + (this.core.planeY + .195) * .52;
        this.conductor.position = [0, coverTop + state.externalGap, 0];
        const numerical = haloFieldSample(this.conductor.position[1], this.conductor.visible);
        const paths: Vec3[][] = [];
        // Rotate an actual axisymmetric Laplace section around the annular buses.
        // Endpoints lie on real Tx/Rx buses or on the grounded explanatory probe.
        // Individual fingers / Core cross-talk are deliberately NOT claimed solved.
        for (let plane = 0; plane < 12; plane++) {
            const theta = plane / 12 * Math.PI * 2 + .08, c = Math.cos(theta), sn = Math.sin(theta);
            for (let line = 0; line < 4; line++) {
                const points: Vec3[] = [];
                for (let k = 0; k < 56; k++) {
                    const a = numerical.a.paths[line][k], b = numerical.b.paths[line][k], radius = mix(a[0], b[0], numerical.t), y = mix(a[1], b[1], numerical.t) + explosion * .12;
                    points.push([radius * c, y, radius * sn]);
                }
                paths.push(points);
            }
        }
        this.fieldGeometry.update(paths, .0105);
    }
}
