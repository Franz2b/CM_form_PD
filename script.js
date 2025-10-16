// ==================== NAVIGATION ULTRA SIMPLE ====================
let currentStep = 1;

window.goToStep = function(step) {
  console.log('>>> GO TO STEP:', step);
  currentStep = step;
  
  // Masquer toutes les sections
  const sections = document.querySelectorAll('.step-section');
  sections.forEach(function(sec) {
    sec.classList.remove('is-active');
    sec.style.display = 'none';
  });
  
  // Afficher la section courante
  const activeSection = document.querySelector('.step-section[data-step="' + step + '"]');
  if (activeSection) {
    activeSection.classList.add('is-active');
    activeSection.style.display = 'block';
    console.log('>>> Section ' + step + ' affichée');
  } else {
    console.error('>>> SECTION NON TROUVÉE:', step);
  }
  
  // Mettre à jour les boutons wizard
  const wizardBtns = document.querySelectorAll('.wizard-step');
  wizardBtns.forEach(function(btn) {
    const btnStep = Number(btn.getAttribute('data-step'));
    if (btnStep === step) {
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
    } else {
      btn.classList.remove('active');
      btn.setAttribute('aria-selected', 'false');
    }
  });
  
  // Désactiver/activer prev/next
  const prevBtn = document.getElementById('prev-step');
  const nextBtn = document.getElementById('next-step');
  if (prevBtn) prevBtn.disabled = (step === 1);
  if (nextBtn) nextBtn.disabled = (step === 5);
  
  // Barre de progression
  const progressFill = document.getElementById('progress-fill');
  if (progressFill) {
    progressFill.style.width = ((step / 5) * 100) + '%';
  }
};

window.goPrev = function() {
  console.log('>>> PREV');
  if (currentStep > 1) {
    window.goToStep(currentStep - 1);
  }
};

window.goNext = function() {
  console.log('>>> NEXT');
  if (currentStep < 5) {
    window.goToStep(currentStep + 1);
  }
};

// ==================== AUTO-SAVE ====================
const STORAGE_KEY = "cm_form_pd_v1";

  function serializeForm() {
  const form = document.getElementById("process-form");
  if (!form) return {};
  
    const data = {};
    const formData = new FormData(form);
  const multi = ["q4", "q13", "q14", "q16", "q17"];

  multi.forEach(function(k) { data[k] = []; });

    for (const [key, value] of formData.entries()) {
    if (multi.indexOf(key) !== -1) {
        data[key].push(value);
      } else if (key === "q4_autre" || key === "q14_autre" || key === "q17_autre") {
      if (value && String(value).trim()) {
          const parentKey = key.split("_")[0];
          if (!Array.isArray(data[parentKey])) data[parentKey] = [];
        data[parentKey].push("Autre: " + String(value).trim());
        }
      } else if (key === "q15_cout") {
        data[key] = value === "" ? null : Number(value);
      } else {
      data[key] = value || "";
    }
  }

  const q12 = document.getElementById("q12");
  data.q12 = q12 ? Number(q12.value) : 3;

    return data;
  }

  function save() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        savedAt: new Date().toISOString(),
      data: serializeForm()
    }));
  } catch (e) {}
  }

  function load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (!parsed || !parsed.data) return;
      populateForm(parsed.data);
  } catch (e) {}
  }

  function populateForm(data) {
  const form = document.getElementById("process-form");
  if (!form) return;
  
  ["q1","q2","q3","q5","q6","q15_cout","q18","q19","q20","q21","user_story","validation_notes"].forEach(function(id) {
      const el = form.elements.namedItem(id);
    if (el) el.value = data[id] || "";
    });

  ["q12","q7","q8","q9","q10","q11","q15_temps"].forEach(function(name) {
      if (!data[name]) return;
      const input = form.querySelector('input[name="' + name + '"][value="' + data[name] + '"]');
      if (input) input.checked = true;
    });

  ["q4","q13","q14","q16","q17"].forEach(function(name) {
      const values = Array.isArray(data[name]) ? data[name] : [];
    const inputs = form.querySelectorAll('input[name="' + name + '"]');
    inputs.forEach(function(input) {
      input.checked = values.indexOf(input.value) !== -1;
    });
  });
}

  let saveTimer = null;
  function scheduleSave() {
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(save, 450);
}

// ==================== SCORING ====================
  function computeScores() {
    const data = serializeForm();

  // Gains
    let tc = 0;
  const q15TempsMap = {
    '< 30 min': 2,
      '30 min – 2 h': 5,
      '2 h – 1 jour': 8,
      '> 1 jour': 10,
      'Difficile à estimer': 5
    };
  tc += q15TempsMap[data.q15_temps] || 0;
  
  if (data.q15_cout && Number(data.q15_cout) > 0) {
    const cout = Number(data.q15_cout);
    if (cout >= 50000) tc += 10;
    else if (cout >= 20000) tc += 7;
    else if (cout >= 10000) tc += 5;
    else if (cout >= 5000) tc += 3;
    else tc += 1;
  }
  
    const q17 = Array.isArray(data.q17) ? data.q17 : [];
    tc += Math.min(3, q17.length);
    tc = Math.min(10, tc);

    const q14 = Array.isArray(data.q14) ? data.q14 : [];
    const impact = Math.min(10, q14.length * 2);
    const gains = Math.min(20, tc + impact);

  // Irritants
  const irrQ12Pts = Math.round((Number(data.q12 || 0) / 5) * 10);
  
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

  // Faisabilité
    const q13 = Array.isArray(data.q13) ? data.q13 : [];
    let feat = 0;
  ['Basé sur des règles claires','Données structurées (fichiers, BDD)','Process stable (peu de changements)','Outils avec API disponibles','Peu d\'exceptions / cas particuliers','Validation humaine possible en bout'].forEach(function(item) {
    if (q13.indexOf(item) !== -1) feat += 2;
  });
    feat = Math.min(10, feat);

  const q4 = Array.isArray(data.q4) ? data.q4 : [];
    let simp = 0;
  if (q4.indexOf('Productivité / efficacité') !== -1) simp += 3;
  if (q4.indexOf('Qualité / fiabilité') !== -1) simp += 2;
  if (q4.indexOf('Coût') !== -1) simp += 3;
  if (q4.indexOf('Conformité / risques') !== -1) simp += 2;
    simp = Math.min(10, simp);
    const faisabilite = Math.min(20, feat + simp);

  const global = Math.round(gains * 2 + irritants * 1.5 + faisabilite * 1.5);

    return {
    gains: { total: gains, tc: tc, impact: impact },
    irritants: { total: irritants, irrQ12: irrQ12Pts, vol: vol },
    faisabilite: { total: faisabilite, feat: feat, simp: simp },
    global: global
    };
  }

  function renderScores() {
    const s = computeScores();
  
  setText('score-gains-tc', s.gains.tc + '/10');
  setText('score-gains-impact', s.gains.impact + '/10');
  setText('score-gains', s.gains.total + '/20');
    setBar('bar-gains-tc', s.gains.tc * 10);
    setBar('bar-gains-impact', s.gains.impact * 10);

  setText('score-irr-q12', s.irritants.irrQ12 + '/10');
  setText('score-irr-vol', s.irritants.vol + '/10');
  setText('score-irritants', s.irritants.total + '/20');
    setBar('bar-irr-q12', s.irritants.irrQ12 * 10);
    setBar('bar-irr-vol', s.irritants.vol * 10);

  setText('score-fais-feat', s.faisabilite.feat + '/10');
  setText('score-fais-simp', s.faisabilite.simp + '/10');
  setText('score-faisabilite', s.faisabilite.total + '/20');
    setBar('bar-fais-feat', s.faisabilite.feat * 10);
    setBar('bar-fais-simp', s.faisabilite.simp * 10);

  setText('score-global', s.global + '/100');
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
  if (el) el.style.width = Math.max(0, Math.min(100, pct)) + '%';
}

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', function() {
  console.log('=== SCRIPT PRÊT ===');
  
  const form = document.getElementById("process-form");
  if (!form) {
    console.error('FORM NON TROUVÉ');
    return;
  }
  
  // Autre controls
  const otherCheckboxes = form.querySelectorAll('input[type="checkbox"][data-controls]');
  otherCheckboxes.forEach(function(checkbox) {
    const controlsId = checkbox.getAttribute("data-controls");
    const controlled = document.getElementById(controlsId);
    
    function update() {
      if (controlled) {
        controlled.disabled = !checkbox.checked;
        controlled.style.opacity = checkbox.checked ? "1" : ".6";
      }
    }
    
    update();
    checkbox.addEventListener("change", update);
  });
  
  // Auto-save
  form.addEventListener("input", scheduleSave);
  form.addEventListener("change", scheduleSave);
  form.addEventListener("input", renderScores);
  form.addEventListener("change", renderScores);
  
  // Load saved data
  load();
  
  // Go to first step
  window.goToStep(1);
  
  // Initial scores
  renderScores();
  
  console.log('=== TOUT EST PRÊT ===');
});
