// ==================== NAVIGATION ULTRA SIMPLE ====================
let currentStep = 1;
const TOTAL_STEPS = 6; // Nombre total de pages

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
  if (nextBtn) nextBtn.disabled = (step === TOTAL_STEPS);
  
  // Barre de progression
  const progressFill = document.getElementById('progress-fill');
  if (progressFill) {
    progressFill.style.width = ((step / TOTAL_STEPS) * 100) + '%';
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
  if (currentStep < TOTAL_STEPS) {
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

  // Pas de champs multi maintenant, tous les champs sont simples
    for (const [key, value] of formData.entries()) {
    data[key] = value || "";
  }

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
  
  // Tous les champs texte, textarea, number, select
  Object.keys(data).forEach(function(key) {
    const el = form.elements.namedItem(key);
    if (el) {
      if (el.type === 'radio') {
        const radio = form.querySelector('input[name="' + key + '"][value="' + data[key] + '"]');
        if (radio) radio.checked = true;
      } else if (el.type === 'checkbox') {
        el.checked = data[key] === el.value;
      } else {
        el.value = data[key] || "";
      }
    }
  });
}

  let saveTimer = null;
  function scheduleSave() {
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(save, 450);
}

// ==================== SCORING (DÉSACTIVÉ TEMPORAIREMENT) ====================
  /*function computeScores() {
    const data = serializeForm();

    // Gains (20 pts)
    let tc = 0;
    const q19TempsMap = {
      '< 30 min': 2,
      '30 min – 2 h': 5,
      '2 h – 1 jour': 8,
      '> 1 jour': 10,
      'Difficile à estimer': 5
    };
    tc += q19TempsMap[data.q19_temps] || 0;
    
    if (data.q19_cout && Number(data.q19_cout) > 0) {
      const cout = Number(data.q19_cout);
      if (cout >= 50000) tc += 10;
      else if (cout >= 20000) tc += 7;
      else if (cout >= 10000) tc += 5;
      else if (cout >= 5000) tc += 3;
      else tc += 1;
    }
    
    const q21 = Array.isArray(data.q21) ? data.q21 : [];
    tc += Math.min(3, q21.length);
    tc = Math.min(10, tc);

    const q18 = Array.isArray(data.q18) ? data.q18 : [];
    const impact = Math.min(10, q18.length * 2);
    const gains = Math.min(20, tc + impact);

    // Irritants (20 pts)
    const irrQ16 = Number(data.q16 || 3);
    const irrQ16Pts = Math.round((irrQ16 / 5) * 10);
    
    let vol = 0;
    const q11Map = { 'Occasionnelle / ad hoc': 1, 'Trimestrielle': 3, 'Mensuelle': 5, 'Hebdomadaire': 8, 'Quotidienne': 10 };
    vol += q11Map[data.q11] || 0;
    const q12Map = { '1–10': 1, '11–50': 3, '51–200': 5, '201–1000': 8, '1000+': 10 };
    vol = Math.round((vol + (q12Map[data.q12] || 0)) / 2);
    const q13Map = { '< 10 min': 2, '10–30 min': 4, '30–60 min': 6, '1–2 h': 8, '+2 h': 10 };
    vol = Math.round((vol + (q13Map[data.q13] || 0)) / 2);
    const q14Map = { '1': 2, '2–5': 4, '6–20': 6, '21–50': 8, '50+': 10 };
    vol = Math.round((vol + (q14Map[data.q14] || 0)) / 2);
    const q15Map = { '1–10': 2, '11–50': 4, '51–200': 6, '201–1000': 8, '1000+': 10 };
    vol = Math.round((vol + (q15Map[data.q15] || 0)) / 2);
    vol = Math.min(10, vol);
    const irritants = Math.min(20, irrQ16Pts + vol);

    // Faisabilité (20 pts)
    const q17 = Array.isArray(data.q17) ? data.q17 : [];
    let feat = 0;
    ['Basé sur des règles claires','Données structurées (fichiers, BDD)','Process stable (peu de changements)','Outils avec API disponibles','Peu d\'exceptions / cas particuliers','Validation humaine possible en bout'].forEach(function(item) {
      if (q17.indexOf(item) !== -1) feat += 2;
    });
    feat = Math.min(10, feat);

    const q8 = Array.isArray(data.q8) ? data.q8 : [];
    let simp = 0;
    if (q8.indexOf('Productivité / efficacité') !== -1) simp += 3;
    if (q8.indexOf('Qualité / fiabilité') !== -1) simp += 2;
    if (q8.indexOf('Coût') !== -1) simp += 3;
    if (q8.indexOf('Conformité / risques') !== -1) simp += 2;
    simp = Math.min(10, simp);
    const faisabilite = Math.min(20, feat + simp);

    const global = Math.round(gains * 2 + irritants * 1.5 + faisabilite * 1.5);

    return {
      gains: { total: gains, tc: tc, impact: impact },
      irritants: { total: irritants, irrQ12: irrQ16Pts, vol: vol },
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
  }*/

  /*function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  function setBar(id, pct) {
    const el = document.getElementById(id);
  if (el) el.style.width = Math.max(0, Math.min(100, pct)) + '%';
}*/

// ==================== UTILS ====================
function escapeHtml(s) {
    return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ==================== RÉCAPITULATIF ====================
  function renderRecap() {
  const recapEl = document.getElementById('recap-content');
    if (!recapEl) return;
  
    const d = serializeForm();
  
  const html = `
    <div class="recap-section">
      <h3>👤 Persona</h3>
      <div class="recap-item">
        <div class="recap-label">Q1. Nom</div>
        <div class="recap-value">${escapeHtml(d.q1 || '—')}</div>
      </div>
      <div class="recap-item">
        <div class="recap-label">Q2. Prénom</div>
        <div class="recap-value">${escapeHtml(d.q2 || '—')}</div>
      </div>
      <div class="recap-item">
        <div class="recap-label">Q3. Rôle / Fonction</div>
        <div class="recap-value">${escapeHtml(d.q3 || '—')}</div>
      </div>
      <div class="recap-item">
        <div class="recap-label">Q4. Département</div>
        <div class="recap-value">${escapeHtml(d.q4 || '—')}</div>
      </div>
    </div>

    <div class="recap-section">
      <h3>💡 Contexte & Besoin</h3>
      <div class="recap-item">
        <div class="recap-label">Q5. Brief utilisateur</div>
        <div class="recap-value">${escapeHtml(d.q5 || '—').replace(/\n/g, '<br>')}</div>
      </div>
      <div class="recap-item">
        <div class="recap-label">Q6. Exécution actuelle de la tâche</div>
        <div class="recap-value">${escapeHtml(d.q6 || '—').replace(/\n/g, '<br>')}</div>
      </div>
    </div>

    <div class="recap-section">
      <h3>📊 Volumétrie & Impact</h3>
      <div class="recap-item">
        <div class="recap-label">Q7. Fréquence du besoin</div>
        <div class="recap-value">${escapeHtml(d.q7 || '—')}</div>
      </div>
      <div class="recap-item">
        <div class="recap-label">Q8. Nombre d'exécutions à chaque occurrence</div>
        <div class="recap-value">${escapeHtml(d.q8 || '—')}</div>
      </div>
      <div class="recap-item">
        <div class="recap-label">Q9. Temps d'exécution unitaire</div>
        <div class="recap-value">${escapeHtml(d.q9 || '—')}</div>
      </div>
      <div class="recap-item">
        <div class="recap-label">Q10. Nombre de personnes exécutantes</div>
        <div class="recap-value">${escapeHtml(d.q10 || '—')}</div>
      </div>
      <div class="recap-item">
        <div class="recap-label">Q11. Niveau d'irritant / urgence</div>
        <div class="recap-value">${escapeHtml(d.q11 || '3')}/5</div>
      </div>
      <div class="recap-item">
        <div class="recap-label">Q11a. Pourquoi irritant</div>
        <div class="recap-value">${escapeHtml(d.q11a || '—')}</div>
      </div>
      <div class="recap-item">
        <div class="recap-label">Q11b. Pourquoi urgent</div>
        <div class="recap-value">${escapeHtml(d.q11b || '—')}</div>
      </div>
    </div>

    <div class="recap-section">
      <h3>🔧 Nature de la tâche</h3>
      <div class="recap-item">
        <div class="recap-label">Q12. Éléments sources de la tâche</div>
        <div class="recap-value">${escapeHtml(d.q12 || '—').replace(/\n/g, '<br>')}</div>
      </div>
      <div class="recap-item">
        <div class="recap-label">Q13. Action manuelle ?</div>
        <div class="recap-value">${escapeHtml(d.q13 || '—')}</div>
      </div>
      <div class="recap-item">
        <div class="recap-label">Q13a. Exemple d'action manuelle</div>
        <div class="recap-value">${escapeHtml(d.q13a || '—')}</div>
      </div>
      <div class="recap-item">
        <div class="recap-label">Q14. Règles simples et stables ?</div>
        <div class="recap-value">${escapeHtml(d.q14 || '—')}</div>
      </div>
      <div class="recap-item">
        <div class="recap-label">Q14a. Exemple règle/cas complexe</div>
        <div class="recap-value">${escapeHtml(d.q14a || '—')}</div>
      </div>
      <div class="recap-item">
        <div class="recap-label">Q15. Complexité organisationnelle</div>
        <div class="recap-value">${escapeHtml(d.q15 || '—')}</div>
      </div>
      <div class="recap-item">
        <div class="recap-label">Q16. Outils nécessaires</div>
        <div class="recap-value">${escapeHtml(d.q16 || '—')}</div>
      </div>
    </div>
  `;
  
  recapEl.innerHTML = html;
}

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', function() {
  console.log('=== SCRIPT PRÊT ===');
  
  const form = document.getElementById("process-form");
  if (!form) {
    console.error('FORM NON TROUVÉ');
    return;
  }
  
  // Analyse IA
  const analyzeBtn = document.getElementById('analyze-btn');
  const aiAnalysisOutput = document.getElementById('ai-analysis-output');
  
  if (analyzeBtn && aiAnalysisOutput) {
    analyzeBtn.addEventListener('click', async function() {
      analyzeBtn.disabled = true;
      analyzeBtn.textContent = '⏳ Analyse en cours...';
      aiAnalysisOutput.innerHTML = '<p style="color: #6c757d; text-align: center; padding: 20px;">Analyse IA en cours, veuillez patienter...</p>';
      
      try {
        const formData = serializeForm();
        
        const response = await fetch('http://localhost:5050/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ form_data: formData })
        });
        
        if (!response.ok) {
          throw new Error('HTTP ' + response.status);
        }
        
        const result = await response.json();
        displayAnalysisResult(result);
        
    } catch (e) {
        aiAnalysisOutput.innerHTML = '<p style="color: #dc3545; padding: 10px; background: #f8d7da; border-radius: 8px;">❌ Erreur: ' + e.message + '<br>Vérifiez que le backend est lancé (uvicorn main:app --port 5050)</p>';
      } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyser le formulaire';
      }
    });
  }
  
  function displayAnalysisResult(result) {
    const output = aiAnalysisOutput;
    if (!output) return;
    
    const html = `
      <div class="analysis-result">
        <div class="analysis-section">
          <h4>📝 User Story</h4>
          <div class="user-story-box">
            <div class="user-story-content">${result.user_story.html}</div>
            <p class="word-count">${result.user_story.word_count} mots</p>
          </div>
        </div>
        
        <div class="analysis-section">
          <h4>📊 Schéma d'exécution</h4>
          <pre class="ascii-diagram">${escapeHtml(result.execution_schema.ascii_diagram)}</pre>
          <div class="steps-list">
            <strong>Étapes :</strong>
            <ol>
              ${result.execution_schema.steps.map(s => '<li>' + escapeHtml(s.description) + '</li>').join('')}
            </ol>
          </div>
        </div>
        
        <div class="analysis-section">
          <h4>🔧 Éléments sources analysés</h4>
          <div class="elements-grid">
            ${result.elements_sources.types.map(el => 
              '<div class="element-badge"><span class="badge-cat">' + escapeHtml(el.category) + '</span> ' + escapeHtml(el.description) + '</div>'
            ).join('')}
          </div>
          <p><strong>Types de sources :</strong> ${result.elements_sources.count} | <strong>Complexité :</strong> <span class="complexity-${result.elements_sources.complexity_level.toLowerCase()}">${escapeHtml(result.elements_sources.complexity_level)}</span></p>
        </div>
        
        <div class="analysis-section">
          <h4>🎯 Scoring</h4>
          <div class="scoring-simple">
            <div class="scoring-row">
              <span>Impact Business</span>
              <span class="level-badge level-${result.scoring.impact_business_level.toLowerCase()}">${result.scoring.impact_business_level}</span>
            </div>
            <div class="scoring-row">
              <span>Faisabilité Technique</span>
              <span class="level-badge level-${result.scoring.faisabilite_technique_level.toLowerCase()}">${result.scoring.faisabilite_technique_level}</span>
            </div>
            <div class="scoring-row">
              <span>Urgence</span>
              <span class="level-badge level-${result.scoring.urgence_level.toLowerCase()}">${result.scoring.urgence_level}</span>
            </div>
            <div class="scoring-total-row">
              <span>Score Total</span>
              <span class="scoring-total-value" title="${escapeHtml(result.scoring.formula)}">${result.scoring.total}/100</span>
            </div>
          </div>
        </div>
        
        <div class="analysis-section">
          <h4>⚖️ Argumentaire Pro / Con</h4>
          <div class="pro-con-grid">
            <div class="pro-section">
              <h5 class="pro-title">✅ Arguments POUR</h5>
              ${result.pro_con.pros.map(pro => 
                '<div class="pro-con-item pro-item">' +
                '<div class="pro-con-argument">' + escapeHtml(pro.argument) + '</div>' +
                '<div class="pro-con-weight weight-' + pro.weight.toLowerCase() + '">' + escapeHtml(pro.weight) + '</div>' +
                '</div>'
              ).join('')}
            </div>
            <div class="con-section">
              <h5 class="con-title">⚠️ Arguments CONTRE / Risques</h5>
              ${result.pro_con.cons.map(con => 
                '<div class="pro-con-item con-item">' +
                '<div class="pro-con-argument">' + escapeHtml(con.argument) + '</div>' +
                '<div class="pro-con-weight weight-' + con.weight.toLowerCase() + '">' + escapeHtml(con.weight) + '</div>' +
                '</div>'
              ).join('')}
            </div>
          </div>
        </div>
        
        <div class="analysis-section">
          <h4>🚀 Plan de Delivery suggéré</h4>
          <div class="delivery-time">
            <strong>Temps total estimé :</strong> <span class="dev-time-badge">${escapeHtml(result.delivery.dev_time)}</span>
          </div>
          
          <div class="phases-simple">
            ${result.delivery.phases.map(phase => 
              '<div class="phase-simple-item">' +
              '<div class="phase-simple-header">' +
              '<span class="phase-simple-number">' + phase.phase + '</span>' +
              '<span class="phase-simple-name">' + escapeHtml(phase.name) + '</span>' +
              '<span class="phase-simple-duration">' + escapeHtml(phase.duration) + '</span>' +
              '</div>' +
              '<div class="phase-simple-actions">' + escapeHtml(phase.actions) + '</div>' +
              '<div class="phase-simple-difficulty">⚡ ' + escapeHtml(phase.main_difficulty) + '</div>' +
              '</div>'
            ).join('')}
          </div>
        </div>
        
        <div class="analysis-section">
          <h4>💡 En attendant l'automatisation...</h4>
          <p class="hint" style="margin: 4px 0 12px;">Actions que l'utilisateur peut mettre en place dès maintenant pour améliorer sa situation.</p>
          <div class="quick-wins-list-single">
            ${result.delivery.quick_wins.map(qw => 
              '<div class="quick-win-item">' +
              '<div class="qw-action">💡 ' + escapeHtml(qw.action) + '</div>' +
              '<div class="qw-impact">→ ' + escapeHtml(qw.impact) + '</div>' +
              '</div>'
            ).join('')}
          </div>
        </div>
      </div>
    `;
    
    output.innerHTML = html;
  }
  
  // Auto-save
  form.addEventListener("input", scheduleSave);
  form.addEventListener("change", scheduleSave);
  form.addEventListener("input", renderRecap);
  form.addEventListener("change", renderRecap);
  
  // Load saved data
  load();
  
  // Go to first step
  window.goToStep(1);
  
  // Initial recap
  renderRecap();
  
  console.log('=== TOUT EST PRÊT ===');
});

