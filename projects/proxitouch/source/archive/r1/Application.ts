import { Node, Mesh, InstancedMesh, Material, metals, mesh, gelMaterial, contactMaterial, fieldMaterial } from '../engine/scene.js';
import { parametric, cylinder, ring, roundedBox, sphere, TubeGeometry } from '../engine/geometry.js';
import { Vec3, clamp, mix, smooth, normalize, hex } from '../engine/math.js';
import { interaction } from '../physics/interaction.js';
export class SensorArray extends Node {
    sheet: Mesh;
    rim: InstancedMesh;
    halo: InstancedMesh;
    core: InstancedMesh;
    contact: InstancedMesh;
    last = '';
    activeCount = 1;
    countLabel = '1 PIXEL';
    constructor() { super(); this.sheet = mesh(this, parametric(32, 8, (u, v) => { const x = (u - .5) * 10, z = (v - .5) * 9.8, y = -.2 + .026 * x * x; return { p: [x, y, z], n: normalize([-.052 * x, 1, 0]) }; }), new Material(0xc4d6dd, { roughness: .7, metalness: .12 })); this.rim = this.add(new InstancedMesh(cylinder(1, .14, .04, 28), metals.silver, 64)); this.halo = this.add(new InstancedMesh(ring(.72, .93, .06, 28), metals.blue, 64)); this.core = this.add(new InstancedMesh(cylinder(.47, .21, .08, 28), gelMaterial().clone({ opacity: 1 }), 64)); this.contact = this.add(new InstancedMesh(cylinder(.23, .013, .003, 24), contactMaterial(), 64)); this.set(1, .3); }
    set(count: number, depth = .3) {
        const key = count + ',' + depth;
        if (key === this.last)
            return;
        this.last = key;
        const c = clamp(count, 1, 64), level = Math.log(c) / Math.log(4), l = Math.min(2, Math.floor(level)), t = clamp(level - l), u = smooth(t), parentCount = 4 ** l, childCount = parentCount * 4;
        const np = 2 ** l, nc = np * 2, pitch = (n: number) => mix(3.25, 1.12, (n - 1) / 7), pp = pitch(np), pc = pitch(nc), radius = mix(pp, pc, u) * .40;
        const coord = (index: number, levels: number) => { let x = 0, z = 0; for (let k = 0; k < levels; k++) {
            const d = Math.floor(index / 4 ** k) % 4;
            x = x * 2 + (d & 1);
            z = z * 2 + (d >> 1);
        } return [x, z]; };
        const extent = mix(Math.max(3.3, np * pp), Math.max(3.3, nc * pc), u);
        this.sheet.scale = [1, 1, 1];
        const sheet = this.sheet.geometry;
        for (let k = 0; k < sheet.data.length; k += 8) {
            const x = (sheet.data[k + 6] - .5) * extent, z = (sheet.data[k + 7] - .5) * extent, n = normalize([-.052 * x, 1, 0]);
            sheet.data[k] = x;
            sheet.data[k + 1] = -.2 + .026 * x * x;
            sheet.data[k + 2] = z;
            sheet.data[k + 3] = n[0];
            sheet.data[k + 4] = n[1];
            sheet.data[k + 5] = n[2];
        }
        sheet.touch();
        this.activeCount = t < .005 ? parentCount : childCount;
        const shown = u < .02 ? parentCount : u > .98 ? childCount : 0;
        this.countLabel = shown ? `${shown} ${shown === 1 ? 'PIXEL' : 'PIXELS'}` : `${parentCount} \u2192 ${childCount} PIXELS`;
        const state = interaction(depth);
        this.rim.count = this.halo.count = this.core.count = this.contact.count = this.activeCount;
        this.contact.visible = state.contact;
        for (let i = 0; i < 64; i++) {
            const alive = i < parentCount ? 1 : i < childCount ? u : 0, a = coord(i % parentCount, l), b = coord(i, l + 1);
            const x = mix((a[0] - (np - 1) / 2) * pp, (b[0] - (nc - 1) / 2) * pc, u), z = mix((a[1] - (np - 1) / 2) * pp, (b[1] - (nc - 1) / 2) * pc, u), y = -.2 + .026 * x * x;
            const rot: Vec3 = [0, 0, Math.atan(.052 * x)], scale: Vec3 = [radius * alive, radius * alive, radius * alive], distance = Math.hypot(x, z), local = clamp(state.areaNormalized * (1.25 - distance * .09)), cool = hex(0x9ecbd0), warm = hex(0xddb570);
            const at = (h: number): Vec3 => [x - Math.sin(rot[2]) * h, y + Math.cos(rot[2]) * h, z];
            this.rim.set(i, at(.14 * radius + .05), rot, scale);
            this.halo.set(i, at(.22 * radius + .05), rot, scale);
            this.core.set(i, at(.28 * radius + .05), rot, scale, cool.map((v, k) => mix(v, warm[k], local)) as Vec3);
            this.contact.set(i, at(.393 * radius + .05), rot, [radius * alive * Math.sqrt(local), radius * alive, radius * alive * Math.sqrt(local)]);
        }
    }
}
export class SkinPatch extends Node {
    sheet: Mesh;
    rim: InstancedMesh;
    halo: InstancedMesh;
    core: InstancedMesh;
    patch: InstancedMesh;
    lastKey = '';
    constructor() { super(); this.sheet = mesh(this, parametric(12, 22, (u, v) => { const x = (u - .5) * 1.76, z = (v - .5) * 3.75, y = .06 + .08 * x * x; return { p: [x, y, z], n: normalize([-.16 * x, 1, 0]) }; }), new Material(0x8faab9, { metalness: .17, roughness: .72 })); this.rim = this.add(new InstancedMesh(cylinder(.172, .035, .009, 20), metals.silver, 32)); this.halo = this.add(new InstancedMesh(ring(.115, .154, .018, 20), metals.blue, 32)); this.core = this.add(new InstancedMesh(cylinder(.077, .033, .010, 20), new Material(0xffffff, { roughness: .60, softness: .35 }), 32)); this.patch = this.add(new InstancedMesh(cylinder(.071, .004, .001, 20), contactMaterial(), 32)); this.set(-1); }
    set(depth: number, spread = 2.08) {
        const key = depth + ',' + spread;
        if (key === this.lastKey)
            return;
        this.lastKey = key;
        const state = interaction(depth);
        for (let j = 0; j < 8; j++)
            for (let i = 0; i < 4; i++) {
                const x = (i - 1.5) * .425, z = (j - 3.5) * .45, rest = .06 + .08 * x * x;
                const section = 1 - ((-z - .25) / 1.86) ** 2 - (x / 1.4) ** 2, xr = 1.48 * Math.sqrt(Math.max(0, section));
                const available = spread - .475 - xr;
                const indentation = state.contact ? Math.max(0, rest + .0735 - available) : 0, y = rest - indentation;
                const rot: Vec3 = [0, 0, -Math.atan(.16 * x)], k = j * 4 + i, local = indentation > 0 ? clamp(.08 + state.areaNormalized * .92) * clamp(indentation / .035) : 0;
                const c = hex(0x9ac7ce), w = hex(0xdea04e);
                this.rim.set(k, [x, y + .018, z], rot);
                this.halo.set(k, [x, y + .044, z], rot);
                this.core.set(k, [x, y + .057, z], rot, [1, 1, 1], c.map((v, n) => mix(v, w[n], local)) as Vec3);
                this.patch.set(k, [x, y + .076, z], rot, [Math.sqrt(local), 1, Math.sqrt(local)]);
            }
        // Compliant skin bends away from the rigid target instead of intersecting it.
        const height = (x: number, z: number) => { const rest = .06 + .08 * x * x, section = 1 - ((-z - .25) / 1.86) ** 2 - (x / 1.4) ** 2, xr = 1.48 * Math.sqrt(Math.max(0, section)); return rest - (state.contact ? Math.max(0, rest + .0735 - (spread - .475 - xr)) : 0); };
        const g = this.sheet.geometry;
        for (let k = 0; k < g.data.length; k += 8) {
            const x = g.data[k], z = g.data[k + 2], y = height(x, z), dx = (height(x + .002, z) - height(x - .002, z)) / .004, dz = (height(x, z + .002) - height(x, z - .002)) / .004, n = normalize([-dx, 1, -dz]);
            g.data[k + 1] = y;
            g.data[k + 3] = n[0];
            g.data[k + 4] = n[1];
            g.data[k + 5] = n[2];
        }
        g.touch();
    }
}
export class RoboticGripper extends Node {
    left: Node;
    right: Node;
    leftSkin: SkinPatch;
    rightSkin: SkinPatch;
    target: Node;
    field: Mesh;
    fieldGeometry: TubeGeometry;
    last = -2;
    constructor() {
        super();
        mesh(this, roundedBox(6.25, .70, 3.05, .20), metals.dark, [0, -.1, -.35]);
        mesh(this, roundedBox(5.75, .11, 2.65, .12), metals.silver, [0, .302, -.35]);
        mesh(this, cylinder(1.24, 1.4, .15, 64), metals.silver, [0, -.12, -2.25], [Math.PI / 2, 0, 0]);
        mesh(this, ring(.93, 1.13, .08, 64), metals.blue, [0, -.12, -2.98], [Math.PI / 2, 0, 0]);
        this.left = this.add(new Node());
        this.right = this.add(new Node());
        const sides = [this.left, this.right];
        for (const [i, side] of sides.entries()) {
            mesh(side, cylinder(.55, 2.18, .08, 64), metals.blue, [0, .55, 0], [Math.PI / 2, 0, 0]);
            mesh(side, ring(.21, .40, .042, 48), metals.silver, [0, .55, 1.11], [Math.PI / 2, 0, 0]);
            mesh(side, cylinder(.16, .06, .01, 32), metals.dark, [0, .55, 1.15], [Math.PI / 2, 0, 0]);
            mesh(side, roundedBox(.86, 3.8, 1.93, .22), metals.silver, [0, 2.25, 0]);
            mesh(side, roundedBox(.70, .23, 1.77, .1), metals.dark, [0, 4.13, 0]);
            const cover = mesh(side, roundedBox(.12, 3.1, 1.7, .055), new Material(0xc5d7dd, { roughness: .76 }), [i === 0 ? .44 : -.44, 2.37, 0]);
        }
        this.leftSkin = this.left.add(new SkinPatch());
        this.leftSkin.position = [.475, 2.3, 0];
        this.leftSkin.rotation = [Math.PI / 2, 0, -Math.PI / 2];
        this.rightSkin = this.right.add(new SkinPatch());
        this.rightSkin.position = [-.475, 2.3, 0];
        this.rightSkin.rotation = [Math.PI / 2, 0, Math.PI / 2];
        this.target = this.add(new Node());
        const egg = mesh(this.target, sphere(1, 48, 32), new Material(0xd7c9b2, { roughness: .73, softness: .22 }), [0, 2.55, 0], [0, 0, 0], [1.48, 1.86, 1.4]);
        mesh(this.target, ring(.65, .68, .014, 64), new Material(0xb3a58d, { roughness: .8 }), [0, 3.9, 0]);
        this.fieldGeometry = new TubeGeometry(12, 40, 5);
        this.field = mesh(this, this.fieldGeometry, fieldMaterial().clone({ opacity: .42 }));
        this.field.castShadow = false;
        this.set(-.6);
    }
    set(depth: number) {
        if (depth === this.last)
            return;
        this.last = depth;
        const s = interaction(depth), closing = clamp((depth + 1) / 1.0), opening = 1 - closing;
        const spread = 2.08 + .70 * opening - .04 * s.pressure;
        this.left.position = [-spread, 0, 0];
        this.right.position = [spread, 0, 0];
        this.left.rotation[2] = .20 * opening;
        this.right.rotation[2] = -.20 * opening;
        this.leftSkin.set(depth, spread);
        this.rightSkin.set(depth, spread);
        const paths: Vec3[][] = [];
        for (let side = 0; side < 2; side++)
            for (let i = 0; i < 6; i++) {
                const sign = side === 0 ? -1 : 1, z = (i - 2.5) * .40;
                const path: Vec3[] = [];
                for (let k = 0; k < 40; k++) {
                    const t = k / 39, y = 1.2 + t * 2.4, x = sign * (spread - .56 + Math.sin(t * Math.PI) * (-.4 - .3 * s.halo));
                    path.push([x, y, z]);
                }
                paths.push(path);
            }
        this.fieldGeometry.update(paths, .012);
        this.field.material.opacity = .45 * (1 - s.pressure * .6);
        this.field.visible = depth < .4;
    }
}
