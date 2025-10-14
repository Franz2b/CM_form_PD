(function () {
  const STORAGE_KEY = "cm_form_pd_v1";

  const form = document.getElementById("process-form");
  const saveIndicator = document.getElementById("save-indicator");
  const exportBtn = document.getElementById("export-json");
  const resetBtn = document.getElementById("reset-form");
  const coachLink = document.getElementById("coach-link");
  const q12 = document.getElementById("q12");
  const q12Output = document.getElementById("q12-output");
  const wizardSteps = Array.from(document.querySelectorAll('.wizard-step'));
  const sections = Array.from(document.querySelectorAll('.step-section'));
  const prevBtn = document.getElementById('prev-step');
  const nextBtn = document.getElementById('next-step');
  const gotoScoreBtn = document.getElementById('goto-score');
  const progressFill = document.getElementById('progress-fill');
  const recapEl = document.getElementById('recap-content');
  const aiSynthBtn = document.getElementById('ai-synthese-btn');
  const aiDeliveryBtn = document.getElementById('ai-delivery-btn');
  const aiOut = document.getElementById('ai-synthese-output');
  const aiDeliveryOut = document.getElementById('ai-delivery-output');
  const aiBackendUrl = document.getElementById('ai-backend-url');
  const aiApiKey = document.getElementById('ai-api-key');
  const aiSaveSettings = document.getElementById('ai-save-settings');

  if (!form) return;

  // Reflect range value
  if (q12 && q12Output) {
    q12.addEventListener("input", () => {
      q12Output.textContent = q12.value;
    });
  }

  // Manage "Autre" controls visibility state for q4/q14/q17
  function syncOtherControl(checkbox) {
    const controlsId = checkbox.getAttribute("data-controls");
    if (!controlsId) return;
    const controlled = document.getElementById(controlsId);
    if (!controlled) return;
    const isChecked = checkbox.checked;
    controlled.disabled = !isChecked;
    controlled.style.opacity = isChecked ? "1" : ".6";
  }

  function initOtherControls() {
    const others = form.querySelectorAll('input[type="checkbox"][data-controls]');
    others.forEach((el) => {
      syncOtherControl(el);
      el.addEventListener("change", () => syncOtherControl(el));
    });
  }

  // Serialize form to a structured object
  function serializeForm() {
    const data = {};
    const formData = new FormData(form);

    // Initialize arrays for multi-select questions
    const multi = new Set(["q4", "q13", "q14", "q16", "q17"]);
    multi.forEach((k) => (data[k] = []));

    for (const [key, value] of formData.entries()) {
      if (multi.has(key)) {
        data[key].push(value);
      } else if (key === "q4_autre" || key === "q14_autre" || key === "q17_autre") {
        // tie "autre" text inputs to their checkbox set only if non-empty
        if (value && String(value).trim().length > 0) {
          const parentKey = key.split("_")[0];
          if (!Array.isArray(data[parentKey])) data[parentKey] = [];
          data[parentKey].push(`Autre: ${String(value).trim()}`);
        }
      } else if (key === "q15_cout") {
        data[key] = value === "" ? null : Number(value);
      } else {
        data[key] = value;
      }
    }

    // Ensure required contact fields included even if empty (for consistent JSON)
    ["q18", "q19", "q20", "q21"].forEach((k) => {
      if (!(k in data)) data[k] = "";
    });

    // Irritant slider explicit number
    if (!("q12" in data)) data.q12 = Number(q12?.value ?? 3);
    else data.q12 = Number(data.q12);

    return data;
  }

  function save() {
    const data = serializeForm();
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        savedAt: new Date().toISOString(),
        data
      }));
      const ts = new Date();
      updateSaveIndicator(ts);
    } catch (e) {
      // noop
    }
  }

  function load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (!parsed || !parsed.data) return;
      populateForm(parsed.data);
      if (parsed.savedAt) updateSaveIndicator(new Date(parsed.savedAt));
    } catch (e) {
      // noop
    }
  }

  function clearStorage() {
    try { localStorage.removeItem(STORAGE_KEY); } catch (e) {}
  }

  function populateForm(data) {
    // Text / textarea / number
    [
      "q1","q2","q3","q5","q6","q15_cout","q18","q19","q20","q21"
    ].forEach((id) => {
      const el = form.elements.namedItem(id);
      if (el && "value" in el) el.value = data[id] ?? "";
    });

    // Slider
    if (typeof data.q12 !== "undefined") {
      q12.value = String(data.q12);
      q12.dispatchEvent(new Event("input"));
    }

    // Radio groups
    ["q7","q8","q9","q10","q11","q15"].forEach((name) => {
      const value = data[name];
      if (!value) return;
      const input = form.querySelector(`input[name="${name}"][value="${cssEscape(value)}"]`);
      if (input) input.checked = true;
    });

    // Checkbox groups
    ["q4","q13","q14","q16","q17"].forEach((name) => {
      const values = Array.isArray(data[name]) ? data[name] : [];
      const inputs = form.querySelectorAll(`input[name="${name}"]`);
      inputs.forEach((input) => {
        input.checked = values.includes(input.value);
      });
      // hydrate "Autre" free text if provided as "Autre: x"
      const other = values.find((v) => typeof v === "string" && v.startsWith("Autre:"));
      const otherInput = form.querySelector(`#${name}-autre`);
      if (other && otherInput) {
        const txt = other.replace(/^Autre:\s*/, "");
        const ctrl = form.querySelector(`input[name="${name}"][value="Autre"]`);
        if (ctrl) ctrl.checked = true;
        otherInput.value = txt;
      }
    });

    // sync disabled state for other controls
    initOtherControls();
  }

  function cssEscape(str) {
    return String(str).replace(/"/g, '\\"');
  }

  function updateSaveIndicator(ts) {
    if (!saveIndicator) return;
    const d = ts instanceof Date ? ts : new Date(ts);
    const formatted = d.toLocaleString(undefined, {
      year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit"
    });
    saveIndicator.textContent = `Dernière sauvegarde : ${formatted}`;
  }

  // Debounced auto-save
  let saveTimer = null;
  function scheduleSave() {
    if (saveTimer) window.clearTimeout(saveTimer);
    saveTimer = window.setTimeout(save, 450);
  }

  function bindAutosave() {
    form.addEventListener("input", scheduleSave);
    form.addEventListener("change", scheduleSave);
  }

  // Wizard navigation
  let currentStep = 1; // 1..5
  function setStep(step) {
    currentStep = Math.max(1, Math.min(5, step));
    sections.forEach((sec) => {
      const isActive = Number(sec.getAttribute('data-step')) === currentStep;
      sec.classList.toggle('is-active', isActive);
    });
    wizardSteps.forEach((btn) => {
      const stepNum = Number(btn.getAttribute('data-step'));
      btn.setAttribute('aria-selected', String(stepNum === currentStep));
    });
    prevBtn.disabled = currentStep === 1;
    nextBtn.disabled = currentStep === 5;
    const pct = (currentStep / 5) * 100;
    if (progressFill) progressFill.style.width = `${pct}%`;
  }

  function bindWizard() {
    wizardSteps.forEach((btn) => {
      btn.addEventListener('click', () => setStep(Number(btn.getAttribute('data-step'))));
    });
    prevBtn.addEventListener('click', () => setStep(currentStep - 1));
    nextBtn.addEventListener('click', () => setStep(currentStep + 1));
    gotoScoreBtn.addEventListener('click', () => setStep(5));
  }

  // Scoring
  function computeScores() {
    const data = serializeForm();

    // 1) Gains (20)
    // Temps/Coûts (Q15–Q17) → 10 pts
    let tc = 0;
    // Q15 mapping
    const q15 = data.q15;
    const q15Map = {
      '< 30 min par exécution': 2,
      '30 min – 2 h': 5,
      '2 h – 1 jour': 8,
      '> 1 jour': 10,
      'Difficile à estimer': 5
    };
    tc += q15Map[q15] || 0;
    // Q17 presence boosts (each checked adds 1 up to +3)
    const q17 = Array.isArray(data.q17) ? data.q17 : [];
    tc += Math.min(3, q17.length);
    tc = Math.min(10, tc);

    // Impact (Q14) → 10 pts (each item 2 pts, max 10)
    const q14 = Array.isArray(data.q14) ? data.q14 : [];
    const impact = Math.min(10, q14.length * 2);
    const gains = Math.min(20, tc + impact);

    // 2) Irritants & Urgence (20)
    // Irritant Q12 (1..5) → scale to 10
    const irrQ12 = Number(data.q12 || 0);
    const irrQ12Pts = Math.round((irrQ12 / 5) * 10);

    // Volumétrie Q7–Q11 → 10 pts
    let vol = 0;
    const q7Map = { 'Occasionnelle / ad hoc': 1, 'Trimestrielle': 3, 'Mensuelle': 5, 'Hebdomadaire': 8, 'Quotidienne': 10 };
    vol += q7Map[data.q7] || 0;
    const q8Map = { '1–10': 1, '11–50': 3, '51–200': 5, '201–1000': 8, '1000+': 10 };
    vol = Math.round((vol + (q8Map[data.q8] || 0)) / 2);
    const q9Map = { '< 10 min': 2, '10–30 min': 4, '30–60 min': 6, '1–2 h': 8, '+2 h': 10 };
    vol = Math.round((vol + (q9Map[data.q9] || 0)) / 2);
    const q10Map = { '1': 2, '2–5': 4, '6–20': 6, '21–50': 8, '50+': 10 };
    vol = Math.round((vol + (q10Map[data.q10] || 0)) / 2);
    const q11Map = { '1–10': 2, '11–50': 4, '51–200': 6, '201–1000': 8, '1000+': 10 };
    vol = Math.round((vol + (q11Map[data.q11] || 0)) / 2);
    vol = Math.min(10, vol);
    const irritants = Math.min(20, irrQ12Pts + vol);

    // 3) Faisabilité (20)
    // Caractéristiques Q13: points positifs si règles claires, données structurées, etc.
    const q13 = Array.isArray(data.q13) ? data.q13 : [];
    const positives = ['Basé sur des règles claires','Données structurées'];
    const helpers = ['Répétitif','Chronophage','Faible valeur ajoutée','Saisie manuelle'];
    let feat = 0;
    feat += positives.filter(v => q13.includes(v)).length * 4; // 0..8
    feat += Math.min(2, helpers.filter(v => q13.includes(v)).length); // +0..2 -> max 10
    feat = Math.min(10, feat);

    // Simplicité perçue (indirects): moins d’outils, process bien défini approximé
    // Heuristique simple: si Multi-outils absent + Fort besoin de coordination absent → +6
    // sinon +2; si Saisie manuelle absente + Données structurées présente → +2
    let simp = 0;
    const has = (v) => q13.includes(v);
    if (!has('Multi-outils') && !has('Fort besoin de coordination inter-équipes')) simp += 6; else simp += 2;
    if (!has('Saisie manuelle') && has('Données structurées')) simp += 2;
    // Bonus si Q4 contient Productivité/Efficacité ou Qualité/Fiabilité (objectif clair)
    const q4 = Array.isArray(data.q4) ? data.q4 : [];
    if (q4.includes('Productivité / efficacité') || q4.includes('Qualité / fiabilité')) simp += 2;
    simp = Math.min(10, simp);
    const faisabilite = Math.min(20, feat + simp);

    // 4) Global (100) – pondération: Gains 40%, Irritants 30%, Faisabilité 30
    const global = Math.round(gains * 2 + irritants * 1.5 + faisabilite * 1.5); // 20*2 + 20*1.5 + 20*1.5 = 100

    return {
      gains: { total: gains, tc, impact },
      irritants: { total: irritants, irrQ12: irrQ12Pts, vol },
      faisabilite: { total: faisabilite, feat, simp },
      global
    };
  }

  function renderScores() {
    const s = computeScores();
    setText('score-gains-tc', `${s.gains.tc}/10`);
    setText('score-gains-impact', `${s.gains.impact}/10`);
    setText('score-gains', `${s.gains.total}/20`);
    setBar('bar-gains-tc', s.gains.tc * 10);
    setBar('bar-gains-impact', s.gains.impact * 10);

    setText('score-irr-q12', `${s.irritants.irrQ12}/10`);
    setText('score-irr-vol', `${s.irritants.vol}/10`);
    setText('score-irritants', `${s.irritants.total}/20`);
    setBar('bar-irr-q12', s.irritants.irrQ12 * 10);
    setBar('bar-irr-vol', s.irritants.vol * 10);

    setText('score-fais-feat', `${s.faisabilite.feat}/10`);
    setText('score-fais-simp', `${s.faisabilite.simp}/10`);
    setText('score-faisabilite', `${s.faisabilite.total}/20`);
    setBar('bar-fais-feat', s.faisabilite.feat * 10);
    setBar('bar-fais-simp', s.faisabilite.simp * 10);

    setText('score-global', `${s.global}/100`);
    setBar('bar-global', s.global);
    const cat = s.global >= 70 ? '🟢 Quick win' : s.global >= 45 ? '🟡 À challenger' : '🔴 Long shot';
    setText('score-category', cat);
  }

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }
  function setBar(id, pct) {
    const el = document.getElementById(id);
    if (el) el.style.width = `${Math.max(0, Math.min(100, pct))}%`;
  }

  function exportJson() {
    const data = serializeForm();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const fileBase = data.q1 ? `${slugify(data.q1)}` : "process";
    a.href = url;
    a.download = `${fileBase}_diagnostic.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  function slugify(s) {
    return String(s)
      .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
      .toLowerCase().replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)+/g, "");
  }

  function resetForm() {
    if (!confirm("Réinitialiser le formulaire ? Les données locales seront effacées.")) return;
    form.reset();
    clearStorage();
    initOtherControls();
    if (q12) q12.dispatchEvent(new Event("input"));
    updateSaveIndicator("jamais");
  }

  function initCoachLink() {
    // Remplacez par votre canal de support préféré
    coachLink.addEventListener("click", (e) => {
      e.preventDefault();
      const subject = encodeURIComponent("Besoin d'aide – Diagnostic Process");
      const body = encodeURIComponent("Bonjour,\n\nJ'aurais besoin d'un coup de main sur le formulaire de diagnostic process.\n\nContexte: ...\n\nMerci !");
      window.location.href = `mailto:coach-ia@exemple.com?subject=${subject}&body=${body}`;
    });
  }

  // Init
  initOtherControls();
  bindAutosave();
  load();
  bindWizard();
  setStep(1);
  renderScores();
  exportBtn.addEventListener("click", exportJson);
  resetBtn.addEventListener("click", resetForm);
  initCoachLink();
  // Recompute scores on any change
  form.addEventListener('input', renderScores);
  form.addEventListener('change', renderScores);

  // ---------- Récap dynamique ----------
  function renderRecap() {
    if (!recapEl) return;
    const d = serializeForm();
    const recap = [
      { title: 'Processus', items: [
        ['Nom du processus', d.q1 || '—'],
        ['Objectif', d.q2 || '—'],
        ['Étapes clés', (d.q3 || '—')]
      ]},
      { title: 'Volumétrie', items: [
        ['Fréquence', d.q7 || '—'],
        ['Exécutions typiques', d.q8 || '—'],
        ['Durée moyenne', d.q9 || '—'],
        ['# Personnes', d.q10 || '—'],
        ['# GO concernés', d.q11 || '—'],
        ['Irritant (1–5)', String(d.q12 ?? '—')]
      ]},
      { title: 'Caractéristiques & Impact', items: [
        ['Caractéristiques', (d.q13 || []).join(', ') || '—'],
        ['Type d’impact', (d.q14 || []).join(', ') || '—'],
        ['Temps/Coût économisé', d.q15 || '—'],
        ['Coût (€)', (d.q15_cout ?? '—')]
      ]},
      { title: 'Contact', items: [
        ['Nom', d.q18 || '—'],
        ['Poste', d.q19 || '—'],
        ['Département', d.q20 || '—'],
        ['E‑mail', d.q21 || '—']
      ]}
    ];
    recapEl.innerHTML = recap.map(block => `
      <div class="recap-item">
        <h4>${escapeHtml(block.title)}</h4>
        <ul>
          ${block.items.map(([k,v]) => `<li><strong>${escapeHtml(k)}:</strong> ${escapeHtml(String(v))}</li>`).join('')}
        </ul>
      </div>
    `).join('');
  }

  function escapeHtml(s) {
    return String(s)
      .replaceAll('&','&amp;')
      .replaceAll('<','&lt;')
      .replaceAll('>','&gt;')
      .replaceAll('"','&quot;')
      .replaceAll("'",'&#039;');
  }

  renderRecap();
  form.addEventListener('input', renderRecap);
  form.addEventListener('change', renderRecap);

  // ---------- IA: paramètres ----------
  const AI_SETTINGS_KEY = 'cm_form_pd_ai_settings_v1';
  function loadAiSettings() {
    try {
      const raw = localStorage.getItem(AI_SETTINGS_KEY);
      if (!raw) return;
      const { backendUrl } = JSON.parse(raw);
      if (backendUrl && aiBackendUrl) aiBackendUrl.value = backendUrl;
    } catch {}
  }
  function saveAiSettings() {
    try {
      const backendUrl = aiBackendUrl?.value || '';
      localStorage.setItem(AI_SETTINGS_KEY, JSON.stringify({ backendUrl }));
    } catch {}
  }
  loadAiSettings();
  aiSaveSettings?.addEventListener('click', saveAiSettings);
  // Prefill default URL if empty
  if (aiBackendUrl && !aiBackendUrl.value) {
    aiBackendUrl.value = 'http://localhost:5050/ai';
  }

  // ---------- IA: prompts ----------
  function buildContextPrompt() {
    const d = serializeForm();
    const s = computeScores();
    return `Contexte formulaire de diagnostic process:\n` +
      `- Nom du processus: ${d.q1 || '-'}\n` +
      `- Objectif: ${d.q2 || '-'}\n` +
      `- Etapes cles: ${d.q3 || '-'}\n` +
      `- Enjeux: ${(d.q4||[]).join(', ') || '-'}\n` +
      `- Outils: ${d.q5 || '-'}\n` +
      `- Parties prenantes: ${d.q6 || '-'}\n` +
      `- Frequence: ${d.q7 || '-'} / Volumetrie: ${d.q8 || '-'} / Duree: ${d.q9 || '-'} / Personnes: ${d.q10 || '-'} / GO: ${d.q11 || '-'}\n` +
      `- Irritant: ${d.q12 || '-'} / Caractéristiques: ${(d.q13||[]).join(', ') || '-'}\n` +
      `- Impact attendu: ${(d.q14||[]).join(', ') || '-'}\n` +
      `- Temps/Coût economise: ${d.q15 || '-'} / Cout(€): ${d.q15_cout ?? '-'}\n` +
      `Scores: Gains ${s.gains.total}/20, Irritants ${s.irritants.total}/20, Faisabilite ${s.faisabilite.total}/20, Global ${s.global}/100.`;
  }

  function synthesePrompt() {
    return `Tu es un consultant en optimisation de processus. Produis une synthèse CLAIRE au FORMAT HTML sémantique (h3, h4, p, ul/li). Structure attendue :\n` +
      `- <h3>Résumé</h3> + <p>…</p>\n` +
      `- <h3>Irritants</h3> + <ul><li>…</li></ul>\n` +
      `- <h3>Opportunités & gains</h3> + <ul><li>…</li></ul>\n` +
      `- <h3>Risques/contraintes</h3> + <ul><li>…</li></ul>\n` +
      `- <h3>Recommandation Go/No-Go</h3> + <p>…</p>\n\n` +
      buildContextPrompt();
  }

  function deliveryPrompt() {
    return `A partir du contexte, génère au FORMAT HTML un seul bloc fusionné contenant :\n` +
      `- <h3>User Story</h3> + <p>En tant que …, je veux … afin de …</p>\n` +
      `- <h3>Staffing</h3> + <ul><li>Profil — charge (S/M/L)</li></ul>\n` +
      `- <h3>Roadmap</h3> + <ol><li>Semaine N: …</li></ol> (4-6 étapes)\n\n` +
      buildContextPrompt();
  }

  // ---------- IA: appels ----------
  async function callAiApi(kind) {
    const backendUrl = aiBackendUrl?.value?.trim();
    const apiKey = aiApiKey?.value?.trim();
    const prompt = kind === 'synthese' ? synthesePrompt() : deliveryPrompt();

    // Si un proxy backend est fourni, on l'utilise (recommandé)
    if (backendUrl) {
      try {
        const res = await fetch(backendUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        return data.text || JSON.stringify(data);
      } catch (e) {
        return `Erreur backend IA: ${String(e)}`;
      }
    }

    // Fallback (non recommandé): appel direct OpenAI côté navigateur si clé fournie
    if (apiKey) {
      try {
        const res = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
          },
          body: JSON.stringify({
            model: 'gpt-4o-mini',
            messages: [
              { role: 'system', content: 'Tu es un assistant expert en design de processus et delivery produit.' },
              { role: 'user', content: prompt }
            ],
            temperature: 0.2,
            max_tokens: 800
          })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        return data.choices?.[0]?.message?.content?.trim() || 'Réponse vide.';
      } catch (e) {
        return `Erreur OpenAI: ${String(e)}`;
      }
    }

    return 'Aucun backend IA configuré. Renseignez un proxy backend ou une clé (non recommandé).';
  }

  aiSynthBtn?.addEventListener('click', async () => {
    aiOut.innerHTML = '⏳ Génération en cours…';
    const text = await callAiApi('synthese');
    aiOut.innerHTML = sanitizeHtml(text);
  });
  aiDeliveryBtn?.addEventListener('click', async () => {
    aiDeliveryOut.innerHTML = '⏳ Génération en cours…';
    const text = await callAiApi('delivery');
    aiDeliveryOut.innerHTML = sanitizeHtml(text);
  });

  // Sanitizer minimal pour autoriser h3/h4/p/ul/ol/li/b/strong/em
  function sanitizeHtml(input) {
    try {
      const allowed = new Set(['H3','H4','P','UL','OL','LI','B','STRONG','EM']);
      const tmp = document.createElement('div');
      tmp.innerHTML = input;
      const walker = document.createTreeWalker(tmp, NodeFilter.SHOW_ELEMENT, null);
      const toRemove = [];
      while (walker.nextNode()) {
        const el = walker.currentNode;
        if (!allowed.has(el.tagName)) toRemove.push(el);
        // remove attributes
        [...el.attributes].forEach(attr => el.removeAttribute(attr.name));
      }
      toRemove.forEach(el => el.replaceWith(...el.childNodes));
      return tmp.innerHTML;
    } catch {
      return input;
    }
  }
})();


