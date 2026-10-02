import { Vec3, Mat4, identity, compose, multiply, hex } from './math.js';
import { Geometry } from './geometry.js';
export class Material {
    color: Vec3;
    metalness = .0;
    roughness = .5;
    opacity = 1;
    emission = 0;
    softness = 0;
    patterned = 0;
    doubleSide = true;
    constructor(color: number | Vec3 = 0x8298ac, options: Partial<Material> = {}) { this.color = typeof color === 'number' ? hex(color) : color; Object.assign(this, options); }
    clone(options: Partial<Material> = {}) { return new Material([...this.color], { ...this, ...options }); }
}
export class Node {
    position: Vec3 = [0, 0, 0];
    rotation: Vec3 = [0, 0, 0];
    scale: Vec3 = [1, 1, 1];
    visible = true;
    name = '';
    world: Mat4 = identity();
    local: Mat4 = identity();
    children: Node[] = [];
    parent?: Node;
    add<T extends Node>(node: T): T { node.parent = this; this.children.push(node); return node; }
    update(parent?: Mat4) { compose(this.position, this.rotation, this.scale, this.local); if (parent)
        multiply(parent, this.local, this.world);
    else
        this.world.set(this.local); for (const n of this.children)
        n.update(this.world); }
    traverse(fn: (n: Node) => void) { if (!this.visible)
        return; fn(this); this.children.forEach(n => n.traverse(fn)); }
}
export class Mesh extends Node {
    castShadow = true;
    receiveShadow = true;
    constructor(public geometry: Geometry, public material: Material) { super(); }
}
export class InstancedMesh extends Mesh {
    matrices: Float32Array;
    normals: Float32Array;
    colors: Float32Array;
    instanceVersion = 0;
    constructor(g: Geometry, m: Material, public count: number) { super(g, m); this.matrices = new Float32Array(count * 16); this.normals = new Float32Array(count * 9); this.colors = new Float32Array(count * 4); for (let i = 0; i < count; i++)
        this.set(i, [0, 0, 0], [0, 0, 0], [1, 1, 1]); }
    set(i: number, p: Vec3, r: Vec3 = [0, 0, 0], s: Vec3 = [1, 1, 1], c: Vec3 = [1, 1, 1], alpha = 1) { const matrix = compose(p, r, s); this.matrices.set(matrix, i * 16); for (let col = 0; col < 3; col++)
        for (let row = 0; row < 3; row++)
            this.normals[i * 9 + col * 3 + row] = matrix[col * 4 + row] / Math.max(1e-12, s[col] * s[col]); this.colors.set([...c, alpha], i * 4); this.instanceVersion++; }
}
export const metals = { silver: new Material(0x879cac, { metalness: .82, roughness: .32, patterned: 1 }), dark: new Material(0x344f67, { metalness: .72, roughness: .4 }), blue: new Material(0x537e9e, { metalness: .7, roughness: .37 }), pale: new Material(0xc5d4dc, { metalness: .62, roughness: .4 }) };
export const gelMaterial = () => new Material(0x70b9c0, { metalness: .02, roughness: .56, opacity: .72, softness: .24 });
export const fieldMaterial = () => new Material(0x387fae, { roughness: .8, emission: .16, opacity: .85 });
export const contactMaterial = () => new Material(0xc78b36, { metalness: .03, roughness: .56, emission: .02 });
export function mesh(root: Node, g: Geometry, m: Material, p: Vec3 = [0, 0, 0], r: Vec3 = [0, 0, 0], s: Vec3 = [1, 1, 1]) { const o = root.add(new Mesh(g, m)); o.position = p; o.rotation = r; o.scale = s; return o; }
