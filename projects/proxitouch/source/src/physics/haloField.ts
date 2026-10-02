import { haloFieldData as data } from './haloFieldData.js';
import { clamp, mix } from '../engine/math.js';
/** A representative axisymmetric annular-bus field, not a finger-resolved device solve. */
export function haloFieldSample(bottom: number, objectVisible: boolean) {
    if (!objectVisible)
        return { a: data.baseline, b: data.baseline, t: 0 };
    const states = data.states;
    if (bottom > states[0].bottom!) {
        return { a: data.baseline, b: states[0], t: clamp((7 - bottom) / (7 - states[0].bottom!)) };
    }
    const v = clamp((states[0].bottom! - bottom) / (states[0].bottom! - states.at(-1)!.bottom!)) * (states.length - 1), i = Math.min(states.length - 2, Math.floor(v));
    return { a: states[i], b: states[i + 1], t: v - i };
}
