/**
 * Object → CAD masshtablash konveyeri — arxitektura (Phase 1 stub).
 * Phase 2: OpenCV/contour, SAM/AUTOSEG, vectorization (Potrace/Clipper), DXF writer.
 */

export const PipelineStep = {
    UPLOAD: 'upload',
    PREPROCESS: 'preprocess',
    CONTOUR_DETECT: 'contour_detect',
    SCALE_CALIBRATE: 'scale_calibrate',
    VECTORIZE: 'vectorize',
    DXF_EXPORT: 'dxf_export',
};

export function describePipelineStepsUz() {
    return [
        { key: PipelineStep.UPLOAD, title: 'Yuklash', detail: 'Eskiz yoki detal fotosi (RAW).' },
        { key: PipelineStep.PREPROCESS, title: 'Oldi ishlov', detail: 'Perspektiva, noise, kontrast.' },
        { key: PipelineStep.CONTOUR_DETECT, title: 'Kontur', detail: 'Chegarani aniqlash + morfologiya.' },
        {
            key: PipelineStep.SCALE_CALIBRATE,
            title: 'Masshtab kalibratsiyasi',
            detail: 'Ma\'lum uzunlik (qoida / qalqon) yoki referens ob\'ekt.',
        },
        { key: PipelineStep.VECTORIZE, title: 'Vektorlash', detail: 'Bezier/polyline soddalashtirish.' },
        { key: PipelineStep.DXF_EXPORT, title: 'DXF chiqish', detail: 'Layerlar: Cut / Mark / Etch.' },
    ];
}

/**
 * @param {File|null} file
 * @param {object} calibration
 * @param {number|null} calibration.referenceLengthMm — ma’lum fizik uzunlik
 * @param {number|null} calibration.referencePx — suratdagi piksel uzunligi
 */
export async function analyzePartImageStub(file, calibration = {}) {
    await delay(400);

    const refMm = Number(calibration.referenceLengthMm);
    const refPx = Number(calibration.referencePx);
    let mmPerPx = null;
    if (refMm > 0 && refPx > 0) mmPerPx = refMm / refPx;

    const baseSteps = file
        ? [PipelineStep.UPLOAD, PipelineStep.PREPROCESS, PipelineStep.CONTOUR_DETECT]
        : [PipelineStep.UPLOAD];
    if (mmPerPx) baseSteps.push(PipelineStep.SCALE_CALIBRATE);

    return {
        ok: !!file,
        fileName: file?.name ?? '(bo\'sh)',
        mmPerPx,
        boundingBoxMm:
            mmPerPx && file
                ? {
                      width: Math.round(180 * mmPerPx * 10) / 10,
                      height: Math.round(120 * mmPerPx * 10) / 10,
                  }
                : null,
        contourConfidence: file ? 0.42 : 0,
        nextPhaseUz:
            'Backend: GPU inference + DXF encoder ulanishi. Hozircha UI oqimi va kalibratsiya kontrakti.',
        stepsCompleted: baseSteps,
    };
}

function delay(ms) {
    return new Promise((r) => setTimeout(r, ms));
}
