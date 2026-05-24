/**
 * Model-specific hardware registry — Universal AI Laser Commander
 * Phase 1: static profiles; Phase 2: vendor SDK / serial / Ethernet shim.
 */

export const ControllerFamily = {
    CYPCUT: 'cypcut',
    GENERIC_GCODE: 'generic-gcode',
};

/** @type {Record<string, HardwareProfile>} */
export const HARDWARE_PROFILES = {
    'jq-laser-1530': {
        id: 'jq-laser-1530',
        displayName: 'JQLASER 1530',
        vendor: 'JQLASER',
        modelCode: '1530',
        controllerFamily: ControllerFamily.CYPCUT,
        controllerProductName: 'CypCut',
        workAreaMm: { width: 3000, depth: 1500 },
        zStrokeMm: 120,
        recommendedAssistGas: ['N2', 'O2', 'Air'],
        laser: {
            sourceTypesSupported: ['fiber', 'co2'],
            ratedPowerKwOptions: [6, 8, 12],
            defaultRatedPowerKw: 12,
        },
        cadOutputsRecommended: ['DXF', 'PLT', 'ENG'],
        motionNotesMmPerSec: {
            idleTravelSuggestedMax: 120,
            pierceDwellMsTypical: [80, 220],
        },
        integration: {
            phase: 2,
            summaryUz:
                'CypCut odatda DXF/PLT import va ish stoli ustidagi boshqaruv dasturi orqali ishlaydi. To\'g\'ridan-to\'g\'ri mashina boshqaruvi: keyingi bosqichda TCP/USB/SDK ulanishi.',
            handshakeCandidates: ['Vendor SDK', 'Watcher folder (import queue)', 'RS232 shim (agar mavjud)'],
        },
        safetyChecklistUz: [
            'Interlock va kapot sensorlari',
            'Tez bekor tugmasi sinovi',
            'Gaz bosimi va yo\'nalish',
            'Filtr va ventilyatsiya holati',
        ],
    },
    'generic-flatbed-demo': {
        id: 'generic-flatbed-demo',
        displayName: 'Umumiy stol (demo)',
        vendor: 'Generic',
        modelCode: 'LAB-DEMO',
        controllerFamily: ControllerFamily.GENERIC_GCODE,
        controllerProductName: 'GRBL / analog',
        workAreaMm: { width: 320, depth: 220 },
        zStrokeMm: 45,
        recommendedAssistGas: ['Air'],
        laser: {
            sourceTypesSupported: ['diode', 'co2'],
            ratedPowerKwOptions: [0.005, 0.04],
            defaultRatedPowerKw: 0.04,
        },
        cadOutputsRecommended: ['SVG', 'GCODE'],
        motionNotesMmPerSec: {
            idleTravelSuggestedMax: 40,
            pierceDwellMsTypical: [40, 120],
        },
        integration: {
            phase: 2,
            summaryUz: 'Demo profil — rivojlantirish va UI sinovi uchun.',
            handshakeCandidates: ['serial GRBL'],
        },
        safetyChecklistUz: ['Ko\'z himoyasi', 'Yong\'in extinguisher'],
    },
};

/**
 * @typedef {object} HardwareProfile
 * @property {string} id
 * @property {string} displayName
 * @property {string} vendor
 * @property {string} modelCode
 * @property {string} controllerFamily
 * @property {string} controllerProductName
 * @property {{ width: number, depth: number }} workAreaMm
 * @property {number} zStrokeMm
 * @property {string[]} recommendedAssistGas
 * @property {object} laser
 * @property {string[]} cadOutputsRecommended
 * @property {object} motionNotesMmPerSec
 * @property {object} integration
 * @property {string[]} safetyChecklistUz
 */

export function listHardwareProfiles() {
    return Object.values(HARDWARE_PROFILES);
}

export function getHardwareProfile(id) {
    return HARDWARE_PROFILES[id] ?? null;
}
