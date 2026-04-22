/* Mnemosyne Dashboard — Core utilities */

// ── State ──
let currentTab = 'guided';
let currentRole = 'employee';
let currentStep = -1; // -1 = start screen
let empSource = 'internal';
let atkSource = 'email';
let atkAttempts = 0, atkBlocked = 0, atkSucceeded = 0;
let stepData = {}; // stores API responses per step
let statsInterval, memInterval;

// ── API helper ──
async function api(url, opts = {}) {
  try {
    const r = await fetch(url, {
      method: opts.method || 'GET',
      headers: opts.body ? {'Content-Type': 'application/json'} : {},
      body: opts.body ? JSON.stringify(opts.body) : undefined
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
  } catch (e) {
    throw e;
  }
}

// ── Tab switching ──
function switchTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));
  document.getElementById(tab).classList.add('active');
  document.getElementById('tab-' + tab).classList.add('active');
  if (tab === 'playground') { refreshMemories(); startPlaygroundPolling(); }
  else { stopPlaygroundPolling(); }
}

// ── Stats polling ──
function refreshStats() {
  api('/api/stats').then(d => {
    document.getElementById('stat-stored').textContent = d.total_stored || 0;
    document.getElementById('stat-blocked').textContent = d.total_blocked || 0;
  }).catch(() => {});
}

function startPlaygroundPolling() {
  stopPlaygroundPolling();
  memInterval = setInterval(() => {
    refreshMemories();
    refreshEventFeed();
  }, 3000);
}
function stopPlaygroundPolling() { if (memInterval) clearInterval(memInterval); }

// ── Role switching ──
function switchRole(role) {
  currentRole = role;
  document.getElementById('role-employee').className = 'role-card' + (role === 'employee' ? ' active-employee' : '');
  document.getElementById('role-attacker').className = 'role-card' + (role === 'attacker' ? ' active-attacker' : '');
  document.getElementById('employee-view').classList.toggle('hidden', role !== 'employee');
  document.getElementById('attacker-view').classList.toggle('hidden', role !== 'attacker');
  if (role === 'employee') refreshMemories();
}

// ── Source buttons ──
function setSource(btn, prefix) {
  const parent = btn.parentElement;
  parent.querySelectorAll('.source-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  if (prefix === 'emp') empSource = btn.dataset.src;
  else atkSource = btn.dataset.src;
}

// ── Attack tab switching ──
function switchAtkTab(tab) {
  document.querySelectorAll('.atk-tab').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('atk-custom').classList.toggle('hidden', tab !== 'custom');
  document.getElementById('atk-prebuilt').classList.toggle('hidden', tab !== 'prebuilt');
}

// ── Helpers ──
function showError(containerId, msg) {
  document.getElementById(containerId).innerHTML = `<div class="error-card">❌ ${msg}</div>`;
}

function setBtnLoading(btnId, loading, text) {
  const btn = document.getElementById(btnId);
  btn.disabled = loading;
  btn.innerHTML = loading ? `<span class="spinner"></span> ${text || 'Working...'}` : (text || btn.textContent);
}

function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── Start stats polling ──
statsInterval = setInterval(refreshStats, 3000);
refreshStats();
