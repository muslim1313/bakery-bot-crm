/**
 * Client-side session state — keyingi bosqichda server/API bilan sinxronlanadi.
 */

import { getHardwareProfile } from './hardwareProfiles.js';

const STORAGE_KEY = 'laser_commander_state_v1';

const defaultState = () => ({
    selectedHardwareId: 'jq-laser-1530',
    materialId: 'steel-mild',
    thicknessMm: 3,
    laserPowerKw: 12,
    referenceLengthMm: '',
    referencePx: '',
    lastAnalysis: null,
});

export function loadState() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return defaultState();
        return { ...defaultState(), ...JSON.parse(raw) };
    } catch {
        return defaultState();
    }
}

export function saveState(partial) {
    const cur = loadState();
    const next = { ...cur, ...partial };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    return next;
}

export function activeHardware(state) {
    return getHardwareProfile(state.selectedHardwareId);
}
