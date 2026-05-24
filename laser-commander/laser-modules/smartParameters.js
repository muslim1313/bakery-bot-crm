/**
 * Heuristic “AI” kesish tavsiyasi — haqiqiy modeldan oldingi placeholder.
 * Output keyingi bosqichda to‘g‘ridan-to‘g‘ri G-code / CypCut parametrlariga map qilinadi.
 */

import { MATERIAL_LIBRARY } from './materialKnowledge.js';

/**
 * @param {object} ctx
 * @param {string} ctx.materialId
 * @param {number} ctx.thicknessMm
 * @param {number} ctx.laserRatedPowerKw
 * @param {{ width: number, depth: number }} ctx.workAreaMm
 */
export function recommendCutParameters(ctx) {
    const mat = MATERIAL_LIBRARY[ctx.materialId];
    const t = Math.max(0.1, Number(ctx.thicknessMm) || 1);
    const kw = Math.max(0.5, Number(ctx.laserRatedPowerKw) || 6);

    const baseSpeed = (420 / t) * Math.pow(kw / 6, 0.55);
    const cutSpeedMmS = clamp(Math.round(baseSpeed * 10) / 10, 2, 120);

    const basePower = 65 + t * 8 + (kw > 8 ? 6 : 0);
    const powerPercent = clamp(Math.round(basePower), 35, 98);

    const pierceMs = clamp(Math.round(120 + t * 45), 60, 800);

    const focusMm =
        Math.round((mat?.focusOffsetMmPerMmThickness ?? -0.06) * t * 10) / 10;

    return {
        cutSpeedMmS,
        powerPercent,
        pierceTimeMs: pierceMs,
        focusOffsetMm: focusMm,
        gasSuggestionUz: mat?.category === 'metal' ? 'N2 (yoki qalin po\'latda O2 strategiyasi)' : 'Air / minimal assist',
        rationaleUz: [
            `Quvvat bazisi: ${kw} kW nominal.`,
            `Qalinlik ${t} mm uchun tezlik va quvvat muvozanati (ademo formulasi).`,
            mat?.notesUz ?? '',
        ].filter(Boolean),
        disclaimerUz:
            'Bu qiymatlar sinovdan oldin ishchi namuna ustida tekshirilishi shart. Phase 2: real-time PID va kapillar sensor.',
    };
}

function clamp(v, lo, hi) {
    return Math.min(hi, Math.max(lo, v));
}
