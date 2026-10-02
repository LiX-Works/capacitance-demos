import { Vec3, Mat4, perspective, lookAt, multiply, transform, clamp, vlerp } from './math.js';
export interface CameraState {
    position: Vec3;
    target: Vec3;
    fov: number;
    offset?: number;
}
export class CameraRig {
    state: CameraState = { position: [9, 7.5, 12], target: [0, 1, 0], fov: 34, offset: 0 };
    aspect = 16 / 9;
    view: Mat4 = lookAt(this.state.position, this.state.target);
    projection: Mat4 = perspective(34, 16 / 9);
    vp: Mat4 = multiply(this.projection, this.view);
    update() { this.view = lookAt(this.state.position, this.state.target); this.projection = perspective(this.state.fov, this.aspect); this.projection[8] = this.state.offset || 0; this.vp = multiply(this.projection, this.view); }
    set(a: CameraState, b?: CameraState, t = 0) { this.state = b ? { position: vlerp(a.position, b.position, t), target: vlerp(a.target, b.target, t), fov: a.fov + (b.fov - a.fov) * t, offset: (a.offset || 0) + ((b.offset || 0) - (a.offset || 0)) * t } : structuredClone(a); this.update(); }
    project(p: Vec3, w: number, h: number) { const q = transform(this.vp, p); return { x: (q[0] * .5 + .5) * w, y: (-.5 * q[1] + .5) * h, depth: q[2], valid: q[2] > -1 && q[2] < 1 }; }
    orbit(dx: number, dy: number) { const p = this.state.position, t = this.state.target, v = [p[0] - t[0], p[1] - t[1], p[2] - t[2]], r = Math.hypot(...v); let th = Math.atan2(v[0], v[2]) + dx, ph = Math.acos(v[1] / r) + dy; ph = clamp(ph, .15, Math.PI * .48); this.state.position = [t[0] + r * Math.sin(ph) * Math.sin(th), t[1] + r * Math.cos(ph), t[2] + r * Math.sin(ph) * Math.cos(th)]; this.update(); }
    zoom(delta: number) { const t = this.state.target, p = this.state.position, f = clamp(Math.exp(delta), .75, 1.25); this.state.position = [t[0] + (p[0] - t[0]) * f, t[1] + (p[1] - t[1]) * f, t[2] + (p[2] - t[2]) * f]; this.update(); }
}
