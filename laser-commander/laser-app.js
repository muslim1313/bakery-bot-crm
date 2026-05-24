/**
 * Universal AI Laser Commander — Phase 1 UI shell
 */

import { listHardwareProfiles, getHardwareProfile } from './laser-modules/hardwareProfiles.js';
import { listMaterials } from './laser-modules/materialKnowledge.js';
import { recommendCutParameters } from './laser-modules/smartParameters.js';
import { describePipelineStepsUz, analyzePartImageStub } from './laser-modules/autoScalePipeline.js';
import { loadState, saveState, activeHardware } from './laser-modules/appState.js';

const tg = window.Telegram?.WebApp;
if (tg) {
    tg.ready();
    tg.expand();
}

function $(sel) {
    return document.querySelector(sel);
}

function $$(sel) {
    return [...document.querySelectorAll(sel)];
}

function setView(id) {
    $$('[data-view]').forEach((el) => {
        el.hidden = el.getAttribute('data-view') !== id;
    });
    $$('.lc-nav__btn').forEach((btn) => {
        const active = btn.getAttribute('data-nav') === id;
        btn.classList.toggle('lc-nav__btn--active', active);
        btn.setAttribute('aria-current', active ? 'page' : 'false');
    });
}

function renderHardwareSelect(state) {
    const sel = $('#hardware-select');
    sel.innerHTML = '';
    listHardwareProfiles().forEach((p) => {
        const o = document.createElement('option');
        o.value = p.id;
        o.textContent = `${p.displayName} · ${p.controllerProductName}`;
        sel.appendChild(o);
    });
    sel.value = state.selectedHardwareId;
}

function renderHardwareDetail(state) {
    const p = activeHardware(state);
    const box = $('#hardware-detail');
    if (!p) {
        box.innerHTML = '';
        return;
    }

    box.innerHTML = `
        <header class="lc-card__head">
            <h3>${escapeHtml(p.displayName)}</h3>
            <span class="lc-chip">${escapeHtml(p.controllerProductName)}</span>
        </header>
        <dl class="lc-dl">
            <div><dt>Ish maydoni</dt><dd>${p.workAreaMm.width} × ${p.workAreaMm.depth} mm</dd></div>
            <div><dt>Z hod</dt><dd>${p.zStrokeMm} mm</dd></div>
            <div><dt>Tavsiya CAD</dt><dd>${p.cadOutputsRecommended.join(', ')}</dd></div>
            <div><dt>Gaz</dt><dd>${p.recommendedAssistGas.join(', ')}</dd></div>
            <div><dt>Lazer (nominal)</dt><dd>${p.laser.ratedPowerKwOptions.join(' / ')} kW</dd></div>
        </dl>
        <p class="lc-muted">${escapeHtml(p.integration.summaryUz)}</p>
        <ul class="lc-list">${p.safetyChecklistUz.map((x) => `<li>${escapeHtml(x)}</li>`).join('')}</ul>
        <section class="lc-subpanel">
            <h4>Ulanish strategiyasi (Phase 2)</h4>
            <ul class="lc-list lc-list--compact">${p.integration.handshakeCandidates.map((x) => `<li>${escapeHtml(x)}</li>`).join('')}</ul>
        </section>
    `;
}

function renderMaterialSelect(state) {
    const sel = $('#material-select');
    sel.innerHTML = '';
    listMaterials().forEach((m) => {
        const o = document.createElement('option');
        o.value = m.id;
        o.textContent = m.labelUz;
        sel.appendChild(o);
    });
    sel.value = state.materialId;
    $('#thickness-input').value = state.thicknessMm;
    $('#power-kw-select').innerHTML = '';
    const hw = activeHardware(state);
    const opts = hw?.laser.ratedPowerKwOptions ?? [6];
    opts.forEach((kw) => {
        const o = document.createElement('option');
        o.value = String(kw);
        o.textContent = `${kw} kW`;
        $('#power-kw-select').appendChild(o);
    });
    $('#power-kw-select').value = String(
        state.laserPowerKw ?? hw?.laser.defaultRatedPowerKw ?? opts[0],
    );
}

function refreshSmartParams(state) {
    const hw = activeHardware(state);
    const rec = recommendCutParameters({
        materialId: state.materialId,
        thicknessMm: Number($('#thickness-input').value) || state.thicknessMm,
        laserRatedPowerKw: Number($('#power-kw-select').value),
        workAreaMm: hw.workAreaMm,
    });

    $('#smart-params-body').innerHTML = `
        <div class="lc-metric-grid">
            <div class="lc-metric"><span>Kesish tezligi</span><strong>${rec.cutSpeedMmS} mm/s</strong></div>
            <div class="lc-metric"><span>Lazer quvvati</span><strong>${rec.powerPercent}%</strong></div>
            <div class="lc-metric"><span>Pierce vaqti</span><strong>${rec.pierceTimeMs} ms</strong></div>
            <div class="lc-metric"><span>Fokus offset</span><strong>${rec.focusOffsetMm} mm</strong></div>
        </div>
        <p class="lc-tag">${escapeHtml(rec.gasSuggestionUz)}</p>
        <ul class="lc-list lc-list--compact">${rec.rationaleUz.map((x) => `<li>${escapeHtml(x)}</li>`).join('')}</ul>
        <p class="lc-disclaimer">${escapeHtml(rec.disclaimerUz)}</p>
        <pre class="lc-pre" id="pseudo-gcode">${escapeHtml(generatePseudoGcode(rec, hw))}</pre>
    `;
}

function generatePseudoGcode(rec, hw) {
    const lines = [
        `; Laser Commander — pseudo block (CypCut / post-processor almashadi)`,
        `; Stock: ${hw?.displayName ?? 'unknown'}`,
        `G21 ; mm`,
        `; SPEED_MM_S=${rec.cutSpeedMmS} POWER=${rec.powerPercent}% PIERCE_MS=${rec.pierceTimeMs}`,
        `; FOCUS_OFFSET_MM=${rec.focusOffsetMm}`,
        `; DXF import → toolpath planner → native controller`,
    ];
    return lines.join('\n');
}

function renderPipelineOverview() {
    const steps = describePipelineStepsUz();
    const ul = $('#pipeline-overview');
    ul.innerHTML = steps
        .map(
            (s) =>
                `<li data-step="${s.key}"><strong>${escapeHtml(s.title)}</strong><span>${escapeHtml(s.detail)}</span></li>`,
        )
        .join('');
}

function highlightPipeline(completedKeys) {
    const setDone = new Set(completedKeys);
    $$('#pipeline-overview li').forEach((li) => {
        const k = li.getAttribute('data-step');
        li.classList.toggle('lc-step--done', setDone.has(k));
    });
}

async function runObjectAnalysis(state) {
    const input = $('#part-photo-input');
    const file = input.files?.[0] ?? null;
    const calibration = {
        referenceLengthMm: $('#ref-mm').value,
        referencePx: $('#ref-px').value,
    };

    const result = await analyzePartImageStub(file, calibration);
    $('#object-cad-status').textContent = result.ok
        ? `Tahlil (stub): ${result.fileName}`
        : 'Fayl tanlang yoki kalibratsiya kiriting.';

    $('#object-cad-detail').innerHTML = `
        <p class="lc-muted">${escapeHtml(result.nextPhaseUz)}</p>
        ${
            result.boundingBoxMm
                ? `<p><strong>Taxminiy o\'lcham:</strong> ${result.boundingBoxMm.width} × ${result.boundingBoxMm.height} mm</p>`
                : ''
        }
        ${
            result.mmPerPx != null
                ? `<p><strong>mm/px:</strong> ${result.mmPerPx.toFixed(4)}</p>`
                : ''
        }
    `;

    highlightPipeline(result.stepsCompleted);

    const nextState = saveState({
        referenceLengthMm: calibration.referenceLengthMm,
        referencePx: calibration.referencePx,
        lastAnalysis: result,
    });
    return nextState;
}

function escapeHtml(s) {
    return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function bindNav() {
    $$('.lc-nav__btn').forEach((btn) => {
        btn.addEventListener('click', () => setView(btn.getAttribute('data-nav')));
    });
}

function bindEquipment(state) {
    $('#hardware-select').addEventListener('change', (e) => {
        const next = saveState({ selectedHardwareId: e.target.value });
        renderHardwareDetail(next);
        renderMaterialSelect(next);
        refreshSmartParams(next);
    });
}

function bindMaterials(state) {
    $('#material-select').addEventListener('change', (e) => {
        saveState({ materialId: e.target.value });
        refreshSmartParams(loadState());
    });
    $('#thickness-input').addEventListener('change', () => {
        saveState({ thicknessMm: Number($('#thickness-input').value) || 1 });
        refreshSmartParams(loadState());
    });
    $('#power-kw-select').addEventListener('change', () => {
        saveState({ laserPowerKw: Number($('#power-kw-select').value) });
        refreshSmartParams(loadState());
    });
    $('#btn-refresh-ai-params').addEventListener('click', () => refreshSmartParams(loadState()));
}

function bindObjectCad() {
    $('#btn-run-analysis').addEventListener('click', async () => {
        await runObjectAnalysis(loadState());
    });
}

document.addEventListener('DOMContentLoaded', () => {
    let state = loadState();

    if (!getHardwareProfile(state.selectedHardwareId)) {
        state = saveState({ selectedHardwareId: 'jq-laser-1530' });
    }

    bindNav();
    bindEquipment(state);
    bindMaterials(state);
    bindObjectCad();

    renderHardwareSelect(state);
    renderHardwareDetail(state);
    renderMaterialSelect(state);
    refreshSmartParams(state);
    renderPipelineOverview();
    highlightPipeline([]);

    setTimeout(() => {
        const loader = $('#loader');
        if (loader) {
            loader.style.opacity = '0';
            setTimeout(() => loader.classList.add('hidden'), 400);
        }
    }, 500);

    document.documentElement.classList.remove('lc-loading');
});
