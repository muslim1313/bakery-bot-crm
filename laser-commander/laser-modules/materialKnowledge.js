/**
 * Material kutubxonasi — kesish parametrlarining boshlang‘ich qiymatlari.
 * Phase 2: haqiqiy AI/model inference bilan almashtiriladi.
 */

/** @type {Record<string, MaterialEntry>} */
export const MATERIAL_LIBRARY = {
    'steel-mild': {
        id: 'steel-mild',
        labelUz: 'Po\'lat (yarnimoq)',
        category: 'metal',
        thicknessMmCommon: [1, 2, 3, 4, 6, 8, 10],
        focusOffsetMmPerMmThickness: -0.08,
        notesUz: 'Yuqori akslantirish; N2 bilan po\'latda sifat yaxshilanadi.',
    },
    'ss304': {
        id: 'ss304',
        labelUz: 'Zanglamas po\'lat 304',
        category: 'metal',
        thicknessMmCommon: [0.8, 1, 1.5, 2, 3],
        focusOffsetMmPerMmThickness: -0.06,
        notesUz: 'N2 yoki qalin kesimda aralash gaz strategiyasi.',
    },
    'al5052': {
        id: 'al5052',
        labelUz: 'Alyuminiy 5052',
        category: 'metal',
        thicknessMmCommon: [1, 2, 3, 4, 5],
        focusOffsetMmPerMmThickness: -0.05,
        notesUz: 'Yuqori akslantirish; qalin kesimda quvvat ko\'payadi.',
    },
    'mdf': {
        id: 'mdf',
        labelUz: 'MDF',
        category: 'organic',
        thicknessMmCommon: [3, 6, 9, 12],
        focusOffsetMmPerMmThickness: -0.03,
        notesUz: 'CO2 / fiber mosligi mashinaga bog\'liq — profilni tekshiring.',
    },
    'acrylic': {
        id: 'acrylic',
        labelUz: 'Akril',
        category: 'organic',
        thicknessMmCommon: [2, 3, 5, 8, 10],
        focusOffsetMmPerMmThickness: -0.04,
        notesUz: 'Flame polishing uchun tezlik va havoni muvozanatlash.',
    },
};

export function listMaterials() {
    return Object.values(MATERIAL_LIBRARY);
}
