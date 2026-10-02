import { Vec3, normalize, cross, sub } from './math.js';
export class Geometry {
    version = 0;
    data: Float32Array;
    indices: Uint32Array;
    constructor(vertices: number[] | Float32Array, indices: number[] | Uint32Array) { this.data = new Float32Array(vertices); this.indices = new Uint32Array(indices); }
    touch() { this.version++; }
}
export function parametric(nu: number, nv: number, fn: (u: number, v: number) => {
    p: Vec3;
    n: Vec3;
}): Geometry {
    const data: number[] = [], indices: number[] = [];
    for (let j = 0; j <= nv; j++)
        for (let i = 0; i <= nu; i++) {
            const u = i / nu, v = j / nv, { p, n } = fn(u, v);
            data.push(...p, ...n, u, v);
        }
    const tri = (a: number, b: number, c: number) => { const p = (i: number) => [data[i * 8], data[i * 8 + 1], data[i * 8 + 2]] as Vec3; const normal = cross(sub(p(b), p(a)), sub(p(c), p(a))); const dot = normal.reduce((v, n, k) => v + n * (data[a * 8 + 3 + k] + data[b * 8 + 3 + k] + data[c * 8 + 3 + k]), 0); if (dot < 0)
        indices.push(a, c, b);
    else
        indices.push(a, b, c); };
    for (let j = 0; j < nv; j++)
        for (let i = 0; i < nu; i++) {
            const a = j * (nu + 1) + i, b = a + 1, c = a + nu + 1, d = c + 1;
            tri(a, c, b);
            tri(b, c, d);
        }
    return new Geometry(data, indices);
}
export function sphere(r = 1, nu = 28, nv = 18): Geometry { return parametric(nu, nv, (u, v) => { const t = u * Math.PI * 2, p = v * Math.PI, n: Vec3 = [Math.sin(p) * Math.cos(t), Math.cos(p), Math.sin(p) * Math.sin(t)]; return { p: [n[0] * r, n[1] * r, n[2] * r], n }; }); }
export function lathe(profile: [
    number,
    number
][], segments = 80): Geometry {
    const data: number[] = [], ind: number[] = [];
    for (let j = 0; j < profile.length; j++) {
        const a = profile[Math.max(0, j - 1)], b = profile[Math.min(profile.length - 1, j + 1)], n = normalize([b[1] - a[1], a[0] - b[0], 0]);
        for (let i = 0; i <= segments; i++) {
            const t = i / segments * Math.PI * 2, c = Math.cos(t), s = Math.sin(t);
            data.push(profile[j][0] * c, profile[j][1], profile[j][0] * s, n[0] * c, n[1], n[0] * s, i / segments, j / (profile.length - 1));
        }
    }
    for (let j = 0; j < profile.length - 1; j++)
        for (let i = 0; i < segments; i++) {
            const a = j * (segments + 1) + i, b = a + 1, c = a + segments + 1, d = c + 1;
            ind.push(a, c, b, b, c, d);
        }
    return new Geometry(data, ind);
}
export function cylinder(r: number, h: number, bevel = .04, segments = 80): Geometry { const b = Math.min(bevel, h * .3, r * .2); return lathe([[0, -h / 2], [r - b, -h / 2], [r, -h / 2 + b], [r, h / 2 - b], [r - b, h / 2], [0, h / 2]], segments); }
export function ring(inner: number, outer: number, h = .05, segments = 100): Geometry { const b = Math.min(.018, h * .25); return lathe([[inner + b, -h / 2], [outer - b, -h / 2], [outer, -h / 2 + b], [outer, h / 2 - b], [outer - b, h / 2], [inner + b, h / 2], [inner, h / 2 - b], [inner, -h / 2 + b], [inner + b, -h / 2]], segments); }
export function sector(inner: number, outer: number, angle: number, h: number, n = 8): Geometry {
    const d: number[] = [], ix: number[] = [];
    const v = (p: Vec3, n: Vec3) => { d.push(...p, ...n, 0, 0); return d.length / 8 - 1; };
    for (let i = 0; i < n; i++) {
        const a = -angle / 2 + angle * i / n, b = -angle / 2 + angle * (i + 1) / n;
        for (const side of [-1, 1]) {
            const q = [v([inner * Math.cos(a), side * h / 2, inner * Math.sin(a)], [0, side, 0]), v([outer * Math.cos(a), side * h / 2, outer * Math.sin(a)], [0, side, 0]), v([outer * Math.cos(b), side * h / 2, outer * Math.sin(b)], [0, side, 0]), v([inner * Math.cos(b), side * h / 2, inner * Math.sin(b)], [0, side, 0])];
            if (side > 0)
                ix.push(q[0], q[3], q[1], q[1], q[3], q[2]);
            else
                ix.push(q[0], q[1], q[3], q[1], q[2], q[3]);
        }
    }
    const edges: [
        [
            number,
            number
        ],
        [
            number,
            number
        ]
    ][] = [];
    for (let i = 0; i < n; i++) {
        const a = -angle / 2 + angle * i / n, b = -angle / 2 + angle * (i + 1) / n;
        edges.push([[outer * Math.cos(a), outer * Math.sin(a)], [outer * Math.cos(b), outer * Math.sin(b)]], [[inner * Math.cos(b), inner * Math.sin(b)], [inner * Math.cos(a), inner * Math.sin(a)]]);
    }
    for (const a of [-angle / 2, angle / 2]) {
        const p: [
            number,
            number
        ] = [inner * Math.cos(a), inner * Math.sin(a)], q: [
            number,
            number
        ] = [outer * Math.cos(a), outer * Math.sin(a)];
        edges.push(a < 0 ? [p, q] : [q, p]);
    }
    for (const [a, b] of edges) {
        const n = normalize([b[1] - a[1], 0, a[0] - b[0]]), k = d.length / 8;
        v([a[0], -h / 2, a[1]], n);
        v([b[0], -h / 2, b[1]], n);
        v([a[0], h / 2, a[1]], n);
        v([b[0], h / 2, b[1]], n);
        ix.push(k, k + 2, k + 1, k + 1, k + 2, k + 3);
    }
    return new Geometry(d, ix);
}
export function roundedBox(w: number, h: number, d: number, r = .13, segments = 9): Geometry {
    const data: number[] = [], ix: number[] = [];
    const seg = Math.max(2, segments);
    // Cube-sphere rounding, explicit bevel samples avoid excessively subdividing flat faces.
    const dims = [w, h, d];
    for (let axis = 0; axis < 3; axis++)
        for (const sign of [-1, 1]) {
            const aa = (axis + 1) % 3, bb = (axis + 2) % 3;
            const b = Math.min(r, w * .45, h * .45, d * .45);
            const samples = (len: number) => { const q = [-len / 2]; for (let i = 1; i < seg; i++)
                q.push(-len / 2 + b * i / (seg - 1)); q.push(len / 2 - b); for (let i = 1; i < seg; i++)
                q.push(len / 2 - b + b * i / (seg - 1)); return q; };
            const xs = samples(dims[aa]), ys = samples(dims[bb]), base = data.length / 8;
            for (let j = 0; j < ys.length; j++)
                for (let i = 0; i < xs.length; i++) {
                    const p: Vec3 = [0, 0, 0];
                    p[axis] = sign * dims[axis] / 2;
                    p[aa] = xs[i];
                    p[bb] = ys[j];
                    const c = p.map((v, k) => Math.max(-dims[k] / 2 + b, Math.min(dims[k] / 2 - b, v))) as Vec3;
                    const n = normalize(sub(p, c));
                    data.push(c[0] + n[0] * b, c[1] + n[1] * b, c[2] + n[2] * b, ...n, i / (xs.length - 1), j / (ys.length - 1));
                }
            for (let j = 0; j < ys.length - 1; j++)
                for (let i = 0; i < xs.length - 1; i++) {
                    const a = base + j * xs.length + i, b = a + 1, c = a + xs.length, d = c + 1;
                    if (sign > 0)
                        ix.push(a, b, c, b, d, c);
                    else
                        ix.push(a, c, b, b, c, d);
                }
        }
    return new Geometry(data, ix);
}
export function plane(size = 80): Geometry { return new Geometry([-size, 0, -size, 0, 1, 0, 0, 0, -size, 0, size, 0, 1, 0, 0, 1, size, 0, size, 0, 1, 0, 1, 1, size, 0, -size, 0, 1, 0, 1, 0], [0, 1, 2, 0, 2, 3]); }
export class TubeGeometry extends Geometry {
    constructor(public count: number, public steps = 64, public sides = 5) { const idx: number[] = []; for (let l = 0; l < count; l++)
        for (let j = 0; j < steps - 1; j++)
            for (let k = 0; k < sides; k++) {
                const a = (l * steps + j) * sides + k, b = (l * steps + j) * sides + (k + 1) % sides, c = a + sides, d = b + sides;
                idx.push(a, b, c, b, d, c);
            } super(new Float32Array(count * steps * sides * 8), idx); }
    update(paths: Vec3[][], radius = .012) { for (let l = 0; l < this.count; l++) {
        const path = paths[l] || paths[0];
        for (let j = 0; j < this.steps; j++) {
            const p = path[Math.min(j, path.length - 1)], a = path[Math.max(0, j - 1)], b = path[Math.min(path.length - 1, j + 1)], t = normalize(sub(b, a));
            let n = normalize(cross(t, [0, 0, 1]));
            if (Math.hypot(...n) < .2)
                n = normalize(cross(t, [0, 1, 0]));
            const bin = cross(t, n);
            for (let k = 0; k < this.sides; k++) {
                const ang = k / this.sides * Math.PI * 2, co = Math.cos(ang), si = Math.sin(ang), nx = n[0] * co + bin[0] * si, ny = n[1] * co + bin[1] * si, nz = n[2] * co + bin[2] * si, o = ((l * this.steps + j) * this.sides + k) * 8;
                this.data[o] = p[0] + nx * radius;
                this.data[o + 1] = p[1] + ny * radius;
                this.data[o + 2] = p[2] + nz * radius;
                this.data[o + 3] = nx;
                this.data[o + 4] = ny;
                this.data[o + 5] = nz;
                this.data[o + 6] = j / (this.steps - 1);
                this.data[o + 7] = l / this.count;
            }
        }
    } this.touch(); }
}
export function box(w: number, h: number, d: number): Geometry { const data: number[] = [], idx: number[] = []; const dims = [w, h, d]; for (let axis = 0; axis < 3; axis++)
    for (const sign of [-1, 1]) {
        const a = (axis + 1) % 3, b = (axis + 2) % 3, base = data.length / 8;
        for (const [u, v] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
            const p: Vec3 = [0, 0, 0], n: Vec3 = [0, 0, 0];
            p[axis] = sign * dims[axis] / 2;
            p[a] = u * dims[a] / 2;
            p[b] = v * dims[b] / 2;
            n[axis] = sign;
            data.push(...p, ...n, (u + 1) / 2, (v + 1) / 2);
        }
        if (sign > 0)
            idx.push(base, base + 1, base + 2, base + 1, base + 3, base + 2);
        else
            idx.push(base, base + 2, base + 1, base + 1, base + 2, base + 3);
    } return new Geometry(data, idx); }
