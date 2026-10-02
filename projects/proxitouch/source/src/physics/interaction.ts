import { clamp, smooth, mix } from '../engine/math.js';
/** A normalized teaching coordinate, never a calibrated distance or pressure. */
export interface Interaction {
    depth: number;
    externalGap: number;
    membraneClosure: number;
    pressure: number;
    contact: boolean;
    contactRadius: number;
    area: number;
    areaNormalized: number;
    hc: number;
    cb: number;
    halo: number;
    core: number;
    coreRelativeCapacitance: number;
    haloDominance: number;
    coreDominance: number;
    stage: 'far' | 'approach' | 'touch' | 'pressure';
}
export function domeContact(pressure: number, height = .96, radius = .70, planeOffset = 0) {
    const load = clamp(pressure), indent = .35 * Math.pow(load, 2 / 3) + planeOffset;
    const plane = Math.max(.25, height - indent);
    const a = indent <= 0 ? 0 : radius * Math.sqrt(clamp(1 - (plane / height) ** 2));
    return { plane, a, indent: Math.max(0, indent), area: Math.PI * a * a };
}
export function interaction(depth: number): Interaction {
    depth = clamp(depth, -1, 1);
    const p = clamp(depth);
    // The outside first touches the protective cover at -0.08. The air gap closes
    // mechanically over the next interval. The upper electrode/gel interface forms
    // at 0. A small resolved preload makes the onset visible, not an ideal point.
    const externalGap = Math.max(0, (-depth - .08) * 4.6);
    const membraneClosure = smooth(clamp((depth + .08) / .08));
    const residualAirGap = .18 * (1 - membraneClosure);
    const resolvedIndent = membraneClosure === 1 ? .35 * Math.pow(clamp(.004 + p * .996), 2 / 3) : 0;
    const contact = residualAirGap < 1e-9 && resolvedIndent > 0, load = contact ? clamp(.004 + p * .996) : 0;
    const central = domeContact(load), ring = domeContact(load, .91, .70, -.05);
    const area = central.area + 8 * ring.area;
    const max = domeContact(1).area + 8 * domeContact(1, .91, .70, -.05).area;
    const areaNormalized = clamp(area / max);
    const approach = smooth(clamp((depth + 1) / 1.08));
    const hc = .88 * Math.pow(approach, 1.65) + .055 * smooth(p);
    const parasitic = .025 * hc;
    const core = parasitic + .975 * areaNormalized;
    const coreRelativeCapacitance = 1 + 4.8 * core;
    const coreDominance = .08 + .92 * smooth(clamp((depth + .08) / .55));
    const haloDominance = 1 - .60 * smooth(clamp((depth + .06) / .6));
    return { depth, externalGap, membraneClosure, pressure: p, contact, contactRadius: central.a, area, areaNormalized, hc, cb: core, halo: hc, core, coreRelativeCapacitance, haloDominance, coreDominance, stage: depth < -.7 ? 'far' : depth < 0 ? 'approach' : depth < .12 ? 'touch' : 'pressure' };
}
