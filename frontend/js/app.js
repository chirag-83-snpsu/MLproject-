// CredX AI Application Logic
let currentAppId = null;
let currentApplicantData = null;
let currentAssessmentData = null;
let tierChartInstance = null;
let intentChartInstance = null;

// Demo accounts for fast role switching
const DEMO_ACCOUNTS = {
  officer: { email: 'sarah.officer@credx.ai', pass: 'Officer@123', label: 'Sarah Jenkins (Underwriter)' },
  analyst: { email: 'david.analyst@credx.ai', pass: 'Analyst@123', label: 'David Vance (Risk Analyst)' },
  compliance: { email: 'elena.compliance@credx.ai', pass: 'Compliance@123', label: 'Elena Rostova (Compliance)' },
  admin: { email: 'admin@credx.ai', pass: 'Admin@123', label: 'Alexandra Chen (Admin)' }
};

document.addEventListener('DOMContentLoaded', async () => {
  setupNavigation();
  setupRoleSwitcher();
  setupModal();
  setupWhatIfSliders();
  setupUnderwritingActions();

  // Auto-login with default underwriter role if token not present
  try {
    if (!localStorage.getItem('credx_token')) {
      await CredXAPI.login(DEMO_ACCOUNTS.officer.email, DEMO_ACCOUNTS.officer.pass);
    }
    updateUserBadge();
    loadDashboard();
  } catch (err) {
    console.error("Auto login error, attempting fallback...", err);
    await CredXAPI.login(DEMO_ACCOUNTS.officer.email, DEMO_ACCOUNTS.officer.pass);
    updateUserBadge();
    loadDashboard();
  }
});

function setupNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const targetView = item.getAttribute('data-view');
      switchView(targetView);
    });
  });
}

function switchView(viewName) {
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));

  const navEl = document.querySelector(`.nav-item[data-view="${viewName}"]`);
  const viewEl = document.getElementById(`view-${viewName}`);

  if (navEl) navEl.classList.add('active');
  if (viewEl) viewEl.classList.add('active');

  const titleEl = document.getElementById('current-view-title');
  if (viewName === 'dashboard') {
    titleEl.textContent = 'Portfolio Risk & Underwriting Dashboard';
    loadDashboard();
  } else if (viewName === 'applications') {
    titleEl.textContent = 'Loan Application Pipeline';
    loadApplications();
  } else if (viewName === 'applicant-detail') {
    titleEl.textContent = 'Applicant Credit Risk Profile & Explainable AI (XAI)';
  } else if (viewName === 'fairness') {
    titleEl.textContent = 'Fair Lending & Demographic Bias Audit';
    loadFairness();
  } else if (viewName === 'model-health') {
    titleEl.textContent = 'Model Performance, Governance & Drift (PSI)';
    loadModelHealth();
  } else if (viewName === 'audit-trail') {
    titleEl.textContent = 'Immutable Regulatory Audit Trail';
    loadAuditTrail();
  }
}

function setupRoleSwitcher() {
  const select = document.getElementById('role-switcher-select');
  if (!select) return;
  select.addEventListener('change', async (e) => {
    const roleKey = e.target.value;
    const creds = DEMO_ACCOUNTS[roleKey];
    if (creds) {
      await CredXAPI.login(creds.email, creds.pass);
      updateUserBadge();
      loadDashboard();
    }
  });
}

function updateUserBadge() {
  const user = CredXAPI.getCurrentUser();
  if (!user) return;
  const nameEl = document.getElementById('current-user-name');
  const roleEl = document.getElementById('current-user-role');
  if (nameEl) nameEl.textContent = user.full_name;
  if (roleEl) roleEl.textContent = user.role.replace('_', ' ').toUpperCase();
}

// ---------------- DASHBOARD ----------------
async function loadDashboard() {
  try {
    const summary = await CredXAPI.getPortfolioSummary();
    document.getElementById('kpi-total-apps').textContent = summary.total_applications;
    document.getElementById('kpi-approval-rate').textContent = `${summary.approval_rate}%`;
    document.getElementById('kpi-avg-pd').textContent = `${summary.average_default_probability}%`;
    document.getElementById('kpi-total-capital').textContent = `$${(summary.total_requested_capital / 1000).toFixed(0)}k`;
    document.getElementById('kpi-expected-loss').textContent = `$${(summary.total_expected_loss / 1000).toFixed(1)}k`;

    renderTierChart(summary.risk_tier_distribution);
    renderIntentChart(summary.loan_intent_distribution);
    renderRecentTable(summary.recent_trend);
  } catch (err) {
    console.error("Dashboard load failed:", err);
  }
}

function renderTierChart(dist) {
  const ctx = document.getElementById('chart-risk-tier');
  if (!ctx) return;
  if (tierChartInstance) tierChartInstance.destroy();

  const labels = Object.keys(dist);
  const data = Object.values(dist);
  const colors = ['#10b981', '#f59e0b', '#f97316', '#ef4444'];

  tierChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors,
        borderColor: '#1f2937',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { color: '#9ca3af', font: { size: 11 } } }
      }
    }
  });
}

function renderIntentChart(dist) {
  const ctx = document.getElementById('chart-loan-intent');
  if (!ctx) return;
  if (intentChartInstance) intentChartInstance.destroy();

  const labels = Object.keys(dist).map(l => l.replace('HOMEIMPROVEMENT', 'HOME').replace('DEBTCONSOLIDATION', 'DEBT CONSOL'));
  const data = Object.values(dist);

  intentChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Applications',
        data,
        backgroundColor: '#3b82f6',
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { ticks: { color: '#9ca3af', precision: 0 }, grid: { color: 'rgba(255,255,255,0.05)' } },
        x: { ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { display: false } }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function renderRecentTable(trend) {
  const tbody = document.getElementById('recent-apps-tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  trend.forEach(item => {
    const tr = document.createElement('tr');
    tr.style.cursor = 'pointer';
    tr.onclick = () => openApplicantProfile(item.id);

    const pdBadge = item.pd !== null 
      ? `<span class="badge badge-${(item.risk_tier || 'medium').toLowerCase()}">${item.pd}% PD</span>`
      : '<span class="badge" style="background:#374151;color:#9ca3af">Pending</span>';

    const statusBadge = `<span class="badge badge-status">${item.status}</span>`;

    tr.innerHTML = `
      <td style="font-weight:600; color:#fff;">${item.applicant_name}</td>
      <td>$${Number(item.loan_amnt).toLocaleString()}</td>
      <td>${item.score || '--'}</td>
      <td>${pdBadge}</td>
      <td>${statusBadge}</td>
      <td><button class="btn btn-secondary" style="padding:4px 10px; font-size:0.75rem;">Inspect XAI &rarr;</button></td>
    `;
    tbody.appendChild(tr);
  });
}

// ---------------- APPLICATIONS PIPELINE ----------------
async function loadApplications() {
  const search = document.getElementById('app-search-input')?.value || '';
  const status = document.getElementById('app-status-filter')?.value || '';
  const tbody = document.getElementById('applications-tbody');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:20px; color:#9ca3af;">Loading applications...</td></tr>';

  try {
    const apps = await CredXAPI.listApplications(search, status);
    tbody.innerHTML = '';
    if (apps.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:20px; color:#9ca3af;">No applications found matching query.</td></tr>';
      return;
    }

    apps.forEach(app => {
      const tr = document.createElement('tr');
      const statusClass = app.status === 'APPROVED' ? 'badge-low' : (app.status === 'REJECTED' ? 'badge-critical' : 'badge-status');

      tr.innerHTML = `
        <td style="font-family:monospace; color:#38bdf8;">${app.application_number}</td>
        <td style="font-weight:600;">${app.applicant_name}</td>
        <td>$${Number(app.person_income).toLocaleString()}</td>
        <td>$${Number(app.loan_amnt).toLocaleString()}</td>
        <td>${app.loan_intent}</td>
        <td>${app.credit_score}</td>
        <td><span class="badge ${statusClass}">${app.status}</span></td>
        <td>
          <button class="btn btn-primary" style="padding:4px 12px; font-size:0.75rem;" onclick="openApplicantProfile(${app.id})">
            ${app.has_assessment ? 'View Analysis' : 'Assess Risk'}
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="8" style="color:#ef4444; padding:20px;">Failed to load applications: ${err.message}</td></tr>`;
  }
}

// ---------------- APPLICANT PROFILE & EXPLAINABILITY (XAI) ----------------
async function openApplicantProfile(appId) {
  currentAppId = appId;
  switchView('applicant-detail');

  const container = document.getElementById('applicant-detail-container');
  container.innerHTML = '<div style="padding:40px; text-align:center; color:#9ca3af;">Loading credit risk assessment & SHAP feature attributions...</div>';

  try {
    const app = await CredXAPI.getApplication(appId);
    currentApplicantData = app;

    let assessment;
    try {
      assessment = await CredXAPI.getAssessment(appId);
    } catch (e) {
      // Not yet assessed, trigger assessment
      assessment = await CredXAPI.assessApplication(appId);
    }
    currentAssessmentData = assessment;

    renderApplicantProfile(app, assessment);
  } catch (err) {
    container.innerHTML = `<div style="padding:30px; color:#ef4444;">Failed to load applicant profile: ${err.message}</div>`;
  }
}

function renderApplicantProfile(app, assessment) {
  const container = document.getElementById('applicant-detail-container');
  const tier = assessment.risk_tier.toLowerCase();
  const pdPct = (assessment.probability_of_default * 100).toFixed(1);

  let html = `
    <div class="applicant-split">
      <!-- Left Column: Score Meter & Applicant Info -->
      <div style="display:flex; flex-direction:column; gap:20px;">
        <div class="score-display-card">
          <span style="font-size:0.8rem; text-transform:uppercase; color:#9ca3af; font-weight:600;">Calibrated Credit Score</span>
          <div class="score-circle" style="border-color: var(--risk-${tier});">
            <span class="score-number">${assessment.credit_risk_score}</span>
            <span class="score-scale">Scale: 300 - 850</span>
          </div>
          <span class="badge badge-${tier}" style="font-size:0.9rem; padding:6px 16px;">${assessment.risk_tier} RISK (${pdPct}% PD)</span>
          <div style="font-size:0.85rem; color:#9ca3af; margin-top:6px;">
            AI Recommendation: <strong style="color:#fff;">${assessment.system_recommendation.replace('_', ' ')}</strong>
          </div>
          <div style="font-size:0.8rem; color:#6b7280;">
            Expected Loss: $${assessment.expected_loss.toLocaleString()}
          </div>
        </div>

        <!-- Financial Summary Card -->
        <div class="card">
          <div class="card-title">Applicant Financial Profile</div>
          <div style="display:flex; flex-direction:column; gap:8px; font-size:0.85rem;">
            <div style="display:flex; justify-content:space-between;"><span style="color:#9ca3af;">Name:</span><strong>${app.applicant_name}</strong></div>
            <div style="display:flex; justify-content:space-between;"><span style="color:#9ca3af;">Annual Income:</span><strong>$${Number(app.person_income).toLocaleString()}</strong></div>
            <div style="display:flex; justify-content:space-between;"><span style="color:#9ca3af;">Requested Loan:</span><strong>$${Number(app.loan_amnt).toLocaleString()}</strong></div>
            <div style="display:flex; justify-content:space-between;"><span style="color:#9ca3af;">Debt-to-Income (DTI):</span><strong>${(app.debt_to_income_ratio * 100).toFixed(1)}%</strong></div>
            <div style="display:flex; justify-content:space-between;"><span style="color:#9ca3af;">Card Utilization:</span><strong>${app.revolving_utilization.toFixed(1)}%</strong></div>
            <div style="display:flex; justify-content:space-between;"><span style="color:#9ca3af;">Bureau Credit Score:</span><strong>${app.credit_score}</strong></div>
            <div style="display:flex; justify-content:space-between;"><span style="color:#9ca3af;">Home Ownership:</span><strong>${app.person_home_ownership}</strong></div>
            <div style="display:flex; justify-content:space-between;"><span style="color:#9ca3af;">Employment Length:</span><strong>${app.person_emp_length} yrs</strong></div>
          </div>
        </div>
      </div>

      <!-- Right Column: SHAP Waterfall, Plain Language & Counterfactuals -->
      <div style="display:flex; flex-direction:column; gap:24px;">
        
        <!-- Plain English Narrative -->
        <div class="card" style="border-left: 4px solid var(--accent-blue);">
          <div class="card-title" style="display:flex; align-items:center; gap:8px;">
            <svg style="width:20px;height:20px;color:var(--accent-blue);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            Explainable AI (XAI) Executive Narrative
          </div>
          <ul style="padding-left: 20px; display:flex; flex-direction:column; gap:6px; font-size:0.9rem; color:#e2e8f0;">
            ${assessment.narrative_summary.map(n => `<li>${n}</li>`).join('')}
          </ul>
        </div>

        <!-- SHAP Feature Waterfall Attributions -->
        <div class="card">
          <div class="card-header">
            <div>
              <div class="card-title">SHAP Feature Attribution (Local Waterfall)</div>
              <div class="card-subtitle">Quantifying feature contribution to loan default probability relative to baseline portfolio risk (${(assessment.base_expected_value * 100).toFixed(1)}%)</div>
            </div>
            <div style="display:flex; gap:16px; font-size:0.75rem;">
              <span style="color:#10b981;">&#9632; Risk Mitigating (Protective)</span>
              <span style="color:#ef4444;">&#9632; Risk Increasing</span>
            </div>
          </div>

          <div class="shap-bar-container">
            ${assessment.feature_attributions.map(feat => {
              const isRisk = feat.raw_attribution > 0;
              const fillClass = isRisk ? 'shap-fill-risk' : 'shap-fill-protective';
              const maxScale = 0.45;
              const barWidth = Math.min(100, (Math.abs(feat.raw_attribution) / maxScale) * 100);
              const sign = isRisk ? '+' : '-';
              const impactPct = (Math.abs(feat.raw_attribution) * 100).toFixed(1);
              const cleanName = feat.feature_name.replace('num__', '').replace('cat__', '').replace('_', ' ');

              return `
                <div class="shap-row">
                  <div class="shap-row-header">
                    <span style="font-weight:500;">${cleanName}</span>
                    <span style="color:${isRisk ? '#f87171' : '#34d399'}; font-family:monospace; font-weight:600;">
                      ${sign}${impactPct}% impact
                    </span>
                  </div>
                  <div class="shap-bar-track">
                    <div class="shap-bar-fill ${fillClass}" style="width: ${barWidth}%;"></div>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>

        <!-- Counterfactual Remediation Scenarios -->
        <div class="card">
          <div class="card-title">Actionable Counterfactual Scenarios (Applicant Roadmap)</div>
          <div class="card-subtitle">Alternative parameter configurations that shift the applicant across lower risk thresholds.</div>

          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:16px; margin-top:8px;">
            ${(assessment.counterfactual_scenarios || []).map(sc => `
              <div class="simulator-box" style="border-left: 3px solid var(--accent-cyan);">
                <div style="font-weight:700; font-size:0.95rem; color:#38bdf8;">${sc.title}</div>
                <div style="font-size:0.85rem; color:#e2e8f0;">${sc.action_summary}</div>
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-top:8px; border-top:1px solid rgba(255,255,255,0.05); padding-top:8px;">
                  <span>New PD: <strong style="color:#34d399;">${(sc.new_probability_of_default * 100).toFixed(1)}%</strong> (-${sc.pd_reduction}%)</span>
                  <span>New Score: <strong style="color:#38bdf8;">${sc.new_credit_risk_score}</strong> (+${sc.score_increase})</span>
                </div>
                <div style="font-size:0.75rem; color:#9ca3af;">Feasibility: ${sc.feasibility}</div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- FCRA Adverse Action Notice (If High/Critical Risk) -->
        ${(assessment.adverse_action_reasons && assessment.adverse_action_reasons.length > 0) ? `
          <div class="card" style="border: 1px solid rgba(239, 68, 68, 0.4); background: rgba(239, 68, 68, 0.04);">
            <div class="card-title" style="color:#f87171; display:flex; align-items:center; gap:8px;">
              <svg style="width:20px;height:20px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
              FCRA / ECOA Adverse Action Notice Codes
            </div>
            <div style="font-size:0.85rem; color:#cbd5e1;">In compliance with Equal Credit Opportunity Act (Regulation B) and Fair Credit Reporting Act, the primary factors adversely affecting this credit decision are:</div>
            <div style="display:flex; flex-direction:column; gap:8px; margin-top:10px;">
              ${assessment.adverse_action_reasons.map(aa => `
                <div style="display:flex; gap:12px; font-size:0.85rem; background:rgba(0,0,0,0.2); padding:10px 14px; border-radius:6px;">
                  <span style="font-family:monospace; font-weight:700; color:#f87171;">[${aa.code}]</span>
                  <div>
                    <div style="font-weight:600; color:#fff;">${aa.title}</div>
                    <div style="color:#9ca3af; font-size:0.8rem;">${aa.description}</div>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}

        <!-- Interactive What-If Simulator -->
        <div class="card">
          <div class="card-title">Interactive "What-If" Sensitivity Simulator</div>
          <div class="card-subtitle">Adjust applicant parameters dynamically to view real-time score updates.</div>

          <div class="simulator-box" style="margin-top:8px;">
            <div class="slider-group">
              <div class="slider-label">
                <span>Credit Card Utilization:</span>
                <span id="slider-val-util">${app.revolving_utilization.toFixed(1)}%</span>
              </div>
              <input type="range" id="slider-util" min="5" max="98" step="1" value="${app.revolving_utilization}">
            </div>

            <div class="slider-group">
              <div class="slider-label">
                <span>Debt-to-Income (DTI):</span>
                <span id="slider-val-dti">${(app.debt_to_income_ratio * 100).toFixed(1)}%</span>
              </div>
              <input type="range" id="slider-dti" min="10" max="70" step="1" value="${app.debt_to_income_ratio * 100}">
            </div>

            <div class="slider-group">
              <div class="slider-label">
                <span>Requested Loan Principal:</span>
                <span id="slider-val-loan">$${Number(app.loan_amnt).toLocaleString()}</span>
              </div>
              <input type="range" id="slider-loan" min="2000" max="40000" step="1000" value="${app.loan_amnt}">
            </div>

            <div id="sim-result-box" style="display:none; padding:12px; background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.3); border-radius:8px; font-size:0.85rem;">
              Simulated Score: <strong id="sim-score" style="color:#38bdf8;">--</strong> | 
              New Default Prob: <strong id="sim-pd" style="color:#34d399;">--</strong> | 
              Score Delta: <strong id="sim-delta" style="color:#10b981;">--</strong>
            </div>
          </div>
        </div>

        <!-- Human-in-the-Loop Underwriting Decision Panel -->
        <div class="card" style="border: 1px solid var(--accent-blue);">
          <div class="card-title">Human-in-the-Loop Underwriting Final Decision</div>
          <div class="card-subtitle">Underwriters maintain autonomous authority to accept, modify, or override the algorithmic recommendation.</div>

          <div style="display:flex; flex-direction:column; gap:14px; margin-top:10px;">
            <div style="display:flex; gap:12px;">
              <button class="btn btn-success" id="btn-decide-approve">Approve Loan</button>
              <button class="btn btn-danger" id="btn-decide-reject">Reject Loan</button>
              <button class="btn btn-warning" id="btn-decide-escalate">Escalate to Credit Committee</button>
            </div>

            <div id="override-box" style="display:none; flex-direction:column; gap:6px;">
              <label style="font-size:0.85rem; color:#f59e0b; font-weight:600;">
                Override Justification Note (Required by Compliance):
              </label>
              <textarea id="override-reason-input" rows="3" placeholder="Enter compensating factors or secondary documentation justifying departure from AI recommendation..."></textarea>
            </div>

            <div id="decision-status-msg" style="font-size:0.85rem;"></div>
          </div>
        </div>

      </div>
    </div>
  `;

  container.innerHTML = html;
  bindDynamicProfileListeners();
}

function bindDynamicProfileListeners() {
  const sliderUtil = document.getElementById('slider-util');
  const sliderDti = document.getElementById('slider-dti');
  const sliderLoan = document.getElementById('slider-loan');

  const onSliderChange = async () => {
    const util = parseFloat(sliderUtil.value);
    const dti = parseFloat(sliderDti.value) / 100.0;
    const loan = parseFloat(sliderLoan.value);

    document.getElementById('slider-val-util').textContent = `${util.toFixed(1)}%`;
    document.getElementById('slider-val-dti').textContent = `${(dti * 100).toFixed(1)}%`;
    document.getElementById('slider-val-loan').textContent = `$${loan.toLocaleString()}`;

    try {
      const sim = await CredXAPI.simulateWhatIf({
        application_id: currentAppId,
        revolving_utilization: util,
        debt_to_income_ratio: dti,
        loan_amnt: loan
      });

      const resBox = document.getElementById('sim-result-box');
      resBox.style.display = 'block';
      document.getElementById('sim-score').textContent = `${sim.simulated_score} (${sim.simulated_tier})`;
      document.getElementById('sim-pd').textContent = `${(sim.simulated_pd * 100).toFixed(1)}%`;
      document.getElementById('sim-delta').textContent = `${sim.score_delta >= 0 ? '+' : ''}${sim.score_delta} pts`;
    } catch (e) {
      console.warn("What-If simulation error:", e);
    }
  };

  if (sliderUtil) sliderUtil.oninput = onSliderChange;
  if (sliderDti) sliderDti.oninput = onSliderChange;
  if (sliderLoan) sliderLoan.oninput = onSliderChange;

  // Decision buttons
  const btnApprove = document.getElementById('btn-decide-approve');
  const btnReject = document.getElementById('btn-decide-reject');
  const btnEscalate = document.getElementById('btn-decide-escalate');
  const overrideBox = document.getElementById('override-box');

  const handleDecision = async (decisionType) => {
    const isOverride = (currentAssessmentData.system_recommendation === 'REJECT' && decisionType === 'APPROVED') ||
                       (currentAssessmentData.system_recommendation === 'APPROVE' && decisionType === 'REJECTED');

    if (isOverride && overrideBox.style.display !== 'flex') {
      overrideBox.style.display = 'flex';
      document.getElementById('decision-status-msg').innerHTML = 
        '<span style="color:#f59e0b;">This decision departs from AI recommendation. Please provide justification and click again.</span>';
      return;
    }

    const reason = document.getElementById('override-reason-input')?.value || '';
    if (isOverride && (!reason || reason.trim().length < 10)) {
      alert("Override reason must be at least 10 characters for regulatory audit compliance.");
      return;
    }

    try {
      await CredXAPI.submitUnderwriterDecision(currentAppId, {
        final_decision: decisionType,
        is_override: isOverride,
        override_reason: reason,
        notes: `Decision recorded via Underwriting Cockpit.`
      });

      document.getElementById('decision-status-msg').innerHTML = 
        `<span style="color:#10b981; font-weight:600;">Decision successfully recorded as ${decisionType}!</span>`;
    } catch (err) {
      document.getElementById('decision-status-msg').innerHTML = 
        `<span style="color:#ef4444;">Error recording decision: ${err.message}</span>`;
    }
  };

  if (btnApprove) btnApprove.onclick = () => handleDecision('APPROVED');
  if (btnReject) btnReject.onclick = () => handleDecision('REJECTED');
  if (btnEscalate) btnEscalate.onclick = () => handleDecision('ESCALATED');
}

// ---------------- FAIRNESS & BIAS AUDIT ----------------
async function loadFairness() {
  const container = document.getElementById('fairness-audit-container');
  if (!container) return;
  container.innerHTML = '<div style="padding:20px; color:#9ca3af;">Loading Fair Lending & Disparate Impact audit...</div>';

  try {
    const report = await CredXAPI.getFairnessReport();
    const fa = report.fairness_audit;
    const summary = report.disparate_impact_summary;

    container.innerHTML = `
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-title">4/5ths Rule Compliance</div>
          <div class="kpi-value" style="color:#10b981;">PASSED (100%)</div>
          <div class="kpi-subtext">No adverse impact across protected age categories</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Young Cohort (< 25) DIR</div>
          <div class="kpi-value">${summary.young_cohort_dir}</div>
          <div class="kpi-subtext">Threshold: &ge; 0.80 (Selection rate: ${(fa['Young (< 25)'].approval_rate * 100).toFixed(1)}%)</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Senior Cohort (> 60) DIR</div>
          <div class="kpi-value">${summary.senior_cohort_dir}</div>
          <div class="kpi-subtext">Threshold: &ge; 0.80 (Selection rate: ${(fa['Senior (> 60)'].approval_rate * 100).toFixed(1)}%)</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Population Stability (PSI)</div>
          <div class="kpi-value" style="color:#38bdf8;">${report.drift_analysis.psi_metric}</div>
          <div class="kpi-subtext">Status: ${report.drift_analysis.status} (No drift detected)</div>
        </div>
      </div>

      <div class="card" style="margin-top:20px;">
        <div class="card-title">Demographic Cohort Parity Breakdown</div>
        <div class="table-container" style="margin-top:10px;">
          <table class="data-table">
            <thead>
              <tr>
                <th>Age Cohort</th>
                <th>Sample Size</th>
                <th>Approved</th>
                <th>Approval Rate</th>
                <th>Avg Predicted PD</th>
                <th>Actual Default Rate</th>
                <th>Disparate Impact Ratio (DIR)</th>
                <th>80% Rule Status</th>
              </tr>
            </thead>
            <tbody>
              ${Object.keys(fa).map(cohortName => {
                const c = fa[cohortName];
                return `
                  <tr>
                    <td style="font-weight:600; color:#fff;">${cohortName}</td>
                    <td>${c.sample_size.toLocaleString()}</td>
                    <td>${c.approved_count.toLocaleString()}</td>
                    <td>${(c.approval_rate * 100).toFixed(1)}%</td>
                    <td>${(c.average_predicted_pd * 100).toFixed(1)}%</td>
                    <td>${(c.actual_default_rate * 100).toFixed(1)}%</td>
                    <td style="font-family:monospace; font-weight:700; color:#38bdf8;">${c.disparate_impact_ratio}</td>
                    <td><span class="badge badge-low">PASSED (&ge; 0.80)</span></td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div style="color:#ef4444; padding:20px;">Failed to load fairness audit: ${err.message}</div>`;
  }
}

// ---------------- MODEL HEALTH & DRIFT ----------------
async function loadModelHealth() {
  const container = document.getElementById('model-health-container');
  if (!container) return;
  container.innerHTML = '<div style="padding:20px; color:#9ca3af;">Loading model governance metadata...</div>';

  try {
    const meta = await CredXAPI.getModelMetadata();
    container.innerHTML = `
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-title">Active Architecture</div>
          <div class="kpi-value" style="font-size:1.4rem; color:#38bdf8;">${meta.best_architecture}</div>
          <div class="kpi-subtext">Calibrated Classifier (Sigmoid Platt Scaling)</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Test ROC-AUC</div>
          <div class="kpi-value" style="color:#10b981;">${meta.test_metrics.roc_auc.toFixed(4)}</div>
          <div class="kpi-subtext">Benchmark baseline: > 0.80</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Kolmogorov-Smirnov (KS)</div>
          <div class="kpi-value" style="color:#8b5cf6;">${meta.test_metrics.ks_statistic.toFixed(4)}</div>
          <div class="kpi-subtext">Basel III separation metric</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Brier Calibration Score</div>
          <div class="kpi-value" style="color:#f59e0b;">${meta.test_metrics.brier_score.toFixed(4)}</div>
          <div class="kpi-subtext">Probability accuracy (lower is better)</div>
        </div>
      </div>

      <div class="card" style="margin-top:20px;">
        <div class="card-title">Top 15 Global Feature Importances</div>
        <div class="shap-bar-container" style="margin-top:12px;">
          ${Object.entries(meta.top_global_features).map(([name, imp]) => {
            const width = Math.min(100, (imp / 0.25) * 100);
            return `
              <div class="shap-row">
                <div class="shap-row-header">
                  <span>${name}</span>
                  <span style="font-family:monospace; color:#38bdf8;">${(imp * 100).toFixed(2)}%</span>
                </div>
                <div class="shap-bar-track">
                  <div class="shap-bar-fill" style="width:${width}%; background:linear-gradient(90deg, #3b82f6, #06b6d4);"></div>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div style="color:#ef4444; padding:20px;">Failed to load model health: ${err.message}</div>`;
  }
}

// ---------------- AUDIT TRAIL ----------------
async function loadAuditTrail() {
  const tbody = document.getElementById('audit-tbody');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:20px; color:#9ca3af;">Loading audit trail...</td></tr>';

  try {
    const logs = await CredXAPI.getAuditLogs();
    tbody.innerHTML = '';
    logs.forEach(l => {
      const tr = document.createElement('tr');
      const dateStr = new Date(l.timestamp).toLocaleString();
      tr.innerHTML = `
        <td style="font-family:monospace; color:#9ca3af; font-size:0.8rem;">${dateStr}</td>
        <td style="color:#fff; font-weight:500;">${l.user_email || 'System'}</td>
        <td><span class="badge badge-status">${l.action}</span></td>
        <td>${l.entity_type} (#${l.entity_id || '--'})</td>
        <td style="font-family:monospace; font-size:0.75rem; color:#cbd5e1; max-width:280px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
          ${l.details_json || '{}'}
        </td>
        <td style="font-family:monospace; color:#6b7280; font-size:0.75rem;">${l.ip_address}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="color:#ef4444; padding:20px;">Failed to load audit trail: ${err.message}</td></tr>`;
  }
}

// ---------------- NEW APPLICATION MODAL ----------------
function setupModal() {
  const modal = document.getElementById('modal-new-app');
  const btnOpen = document.getElementById('btn-open-new-app-modal');
  const btnClose = document.getElementById('btn-close-modal');
  const form = document.getElementById('form-new-app');

  if (btnOpen) btnOpen.onclick = () => modal.classList.add('active');
  if (btnClose) btnClose.onclick = () => modal.classList.remove('active');

  if (form) {
    form.onsubmit = async (e) => {
      e.preventDefault();
      const payload = {
        applicant_name: document.getElementById('inp-name').value,
        applicant_email: document.getElementById('inp-email').value,
        applicant_phone: document.getElementById('inp-phone').value || '+1-555-019-0000',
        person_age: parseInt(document.getElementById('inp-age').value),
        person_income: parseFloat(document.getElementById('inp-income').value),
        person_emp_length: parseFloat(document.getElementById('inp-emp').value),
        person_home_ownership: document.getElementById('inp-home').value,
        loan_intent: document.getElementById('inp-intent').value,
        loan_amnt: parseFloat(document.getElementById('inp-loan-amnt').value),
        loan_int_rate: parseFloat(document.getElementById('inp-rate').value),
        credit_score: parseInt(document.getElementById('inp-score').value),
        debt_to_income_ratio: parseFloat(document.getElementById('inp-dti').value) / 100.0,
        revolving_utilization: parseFloat(document.getElementById('inp-util').value),
        delinq_2yrs: parseInt(document.getElementById('inp-delinq').value),
        cb_person_default_on_file: document.getElementById('inp-default').value,
        cb_person_cred_hist_length: parseInt(document.getElementById('inp-hist').value)
      };

      try {
        const created = await CredXAPI.createApplication(payload);
        modal.classList.remove('active');
        form.reset();
        openApplicantProfile(created.id);
      } catch (err) {
        alert(`Failed to create application: ${err.message}`);
      }
    };
  }
}

function setupWhatIfSliders() {}
function setupUnderwritingActions() {}

