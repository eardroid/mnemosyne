/* Mnemosyne Dashboard — Live Playground */

// ── Employee: Store Memory ──
async function employeeStore() {
  const content = document.getElementById('emp-memory').value.trim();
  if (!content) return;
  setBtnLoading('emp-store-btn', true, 'Storing...');
  try {
    const r = await api('/api/inject', {method:'POST', body:{content, source: empSource}});
    let html;
    if (r.status === 'STORED') {
      html = `<div class="card card-green" style="margin-top:12px"><strong>✓ Memory stored successfully</strong><br>Source: ${empSource} | Trust level: ${r.trust?.toUpperCase()}<br><span style="color:var(--dim)">Alex will now use this in future responses.</span></div>`;
    } else {
      const matched = (r.patterns_checked||[]).filter(p=>p.matched).map(p=>p.pattern).join(', ');
      html = `<div class="card card-yellow" style="margin-top:12px"><strong>⚠ Memory flagged</strong><br>Patterns matched: ${matched}<br>Trust: ${r.trust}</div>`;
    }
    html += `<div class="explain-panel" style="margin-top:8px"><h4>💡 What just happened?</h4><p>${r.status==='STORED' ? 'The memory passed all security checks and was stored in Alex\'s long-term memory via Mem0.' : 'Mnemosyne detected suspicious patterns and blocked this memory from being stored.'}</p></div>`;
    document.getElementById('emp-result').innerHTML = html;
    document.getElementById('emp-memory').value = '';
    refreshMemories();
  } catch(e) { showError('emp-result', e.message); }
  setBtnLoading('emp-store-btn', false, 'Store Memory');
}

// ── Employee: Ask Alex ──
async function employeeAsk() {
  const q = document.getElementById('emp-question').value.trim();
  if (!q) return;
  setBtnLoading('emp-ask-btn', true, 'Asking...');
  try {
    const r = await api('/api/ask', {method:'POST', body:{question: q}});
    document.getElementById('emp-answer').innerHTML = `<div class="card card-blue" style="margin-top:12px"><strong>Alex says:</strong> ${r.answer}<br><span style="color:var(--dim)">Memories used: ${r.memories_used}</span><details style="margin-top:8px"><summary style="color:var(--blue);cursor:pointer;font-size:.85rem">Show context sent to LLM</summary><pre style="background:#111;padding:8px;border-radius:4px;font-size:.8rem;color:var(--dim);margin-top:4px;white-space:pre-wrap">${r.context_preview || 'N/A'}</pre></details></div>`;
  } catch(e) { showError('emp-answer', e.message); }
  setBtnLoading('emp-ask-btn', false, 'Ask');
}

// ── Refresh memories list ──
async function refreshMemories() {
  try {
    const mems = await api('/api/memories');
    const el = document.getElementById('memory-list');
    if (!mems || mems.length === 0) { el.innerHTML = '<p style="color:var(--dim)">No memories stored yet.</p>'; return; }
    el.innerHTML = mems.map(m => {
      const preview = (m.memory || '').substring(0, 80);
      return `<div class="mem-item"><span class="badge badge-green" style="margin-right:8px">stored</span>${preview}${m.memory?.length > 80 ? '...' : ''}</div>`;
    }).join('');
  } catch(e) { /* silent */ }
}

// ── Refresh event feed ──
async function refreshEventFeed() {
  try {
    const rows = await api('/api/recent');
    const el = document.getElementById('event-feed');
    if (!el) return;
    el.innerHTML = (rows || []).slice(0, 10).map(r => {
      const cls = r.status === 'BLOCKED' ? 'blocked' : 'stored';
      const preview = (r.content || '').substring(0, 50);
      return `<div class="event-card ${cls}"><span class="badge ${r.status==='BLOCKED'?'badge-red':'badge-green'}" style="margin-right:6px">${r.status}</span><span style="color:var(--dim);margin-right:6px">${(r.timestamp||'').substring(11,19)}</span><span style="color:var(--dim);margin-right:6px">${r.source}</span>${r.flags_found ? `<span style="color:var(--yellow);font-size:.8rem">[${r.flags_found}]</span>` : ''}<br><span style="color:var(--dim);font-size:.82rem">${preview}...</span></div>`;
    }).join('');
  } catch(e) { /* silent */ }
}

// ── Attacker: Pattern scan animation ──
async function showPatternScan(container, result) {
  const pats = result.patterns_checked || [];
  let html = `
    <div style="margin:16px 0">
      <h4 style="color:var(--dim);margin-bottom:8px">Layer 1 — Pattern scan</h4>
      <div class="progress-bar"><div class="progress-fill" id="atk-progress" style="width:0%"></div></div>
      <div id="atk-patterns"></div>
    </div>`;
  container.innerHTML = html;

  const patContainer = document.getElementById('atk-patterns');
  const progBar = document.getElementById('atk-progress');

  for (let i = 0; i < pats.length; i++) {
    progBar.style.width = ((i + 1) / pats.length * 100) + '%';
    const row = document.createElement('div');
    row.className = 'pattern-row ' + (pats[i].matched ? 'hit' : 'miss');
    row.innerHTML = `<span class="icon">${pats[i].matched ? '⚡' : '✓'}</span><span>Checking: "${pats[i].pattern}"</span><span style="margin-left:auto">${pats[i].matched ? 'HIT' : 'MISS'}</span>`;
    patContainer.appendChild(row);
    await delay(100);
  }

  await delay(400);

  // Layer 2
  container.innerHTML += `
    <div style="margin:16px 0; border-top: 1px solid #333; padding-top: 16px;">
      <h4 style="color:var(--dim);margin-bottom:8px">Layer 2 — AI semantic analysis</h4>
      <div id="layer2-spinner" style="color:var(--blue)"><span class="spinner"></span> Sending to Groq for intent analysis...</div>
      <div id="layer2-result" class="hidden"></div>
    </div>`;

  await delay(800); // Simulate network wait for animation effect since backend already ran it

  document.getElementById('layer2-spinner').classList.add('hidden');
  const l2 = document.getElementById('layer2-result');
  l2.classList.remove('hidden');
  const sem = result.semantic || {};
  l2.innerHTML = `
    <div class="card" style="font-size:0.9rem">
      <div><strong>Attack detected:</strong> <span style="color:${sem.is_attack?'var(--red)':'var(--green)'}">${sem.is_attack ? 'YES' : 'NO'}</span></div>
      <div><strong>Confidence:</strong> ${(sem.confidence * 100).toFixed(0)}%</div>
      <div><strong>Attack type:</strong> ${sem.attack_type || 'none'}</div>
      <div style="margin-top:4px"><strong>AI reasoning:</strong> <span style="color:var(--dim)">${sem.reasoning || 'N/A'}</span></div>
    </div>
  `;

  await delay(400);

  // Trust evaluation
  let trustHtml = `<div class="card card-yellow" style="margin-top:12px"><strong>Trust evaluation:</strong> Source: ${result.trust === 'low' ? 'email/ticket/external' : result.trust} → Trust Level: <strong>${(result.trust||'').toUpperCase()}</strong><br><span style="color:var(--dim);font-size:.85rem">email/ticket/external = LOW trust</span></div>`;
  container.innerHTML += trustHtml;
  await delay(400);

  // Verdict
  if (result.status === 'BLOCKED') {
    container.innerHTML += `<div class="verdict verdict-blocked">⛔ INJECTION BLOCKED</div><div style="text-align:center"><p>Mnemosyne intercepted this attack.</p><p style="color:var(--red);margin-top:4px"><strong>Caught by:</strong> ${result.caught_by || 'Unknown'}</p><p style="color:var(--dim);margin-top:8px">memory.add() was NOT called. Alex never saw this message.<br>Ledger entry written: BLOCKED</p></div>`;
    atkBlocked++;
  } else {
    container.innerHTML += `<div class="verdict verdict-stored">⚠ INJECTION SUCCEEDED</div><div style="text-align:center"><p style="color:var(--yellow)">Memory was stored — Alex is now vulnerable.</p></div>`;
    atkSucceeded++;
  }
  atkAttempts++;
  document.getElementById('atk-attempts').textContent = atkAttempts;
  document.getElementById('atk-blocked').textContent = atkBlocked;
  document.getElementById('atk-succeeded').textContent = atkSucceeded;

  // Explain panel
  container.innerHTML += `<div class="explain-panel" style="margin-top:16px"><h4>💡 What just happened?</h4><p>${result.status === 'BLOCKED' ? 'Mnemosyne intercepted the injection attempt. It detected dangerous patterns in the content and combined with the low-trust source, blocked it before it could reach the agent\'s memory.' : 'The injected content did not match any known danger patterns. This shows the limitation of pattern-based detection — novel attacks may slip through.'}</p></div>`;

  // Explain button
  container.innerHTML += `<button class="btn btn-ghost btn-sm" style="margin-top:8px" onclick="explainAttack(this,'${result.status==='BLOCKED'?'blocked':'stored'}')">🤖 Explain this attack</button><div id="explain-result"></div>`;

  refreshEventFeed();
}

// ── Attacker: Inject custom ──
async function attackerInject() {
  const content = document.getElementById('atk-content').value.trim();
  if (!content) return;
  setBtnLoading('atk-inject-btn', true, 'Injecting...');
  try {
    const r = await api('/api/inject', {method:'POST', body:{content, source: atkSource}});
    await showPatternScan(document.getElementById('atk-result'), r);
  } catch(e) { showError('atk-result', e.message); }
  setBtnLoading('atk-inject-btn', false, 'Inject');
}

// ── Attacker: Pre-built attacks ──
async function firePrebuilt(idx) {
  const content = PREBUILT_ATTACKS[idx];
  document.querySelectorAll('.prebuilt-btn').forEach(b => b.disabled = true);
  try {
    const r = await api('/api/inject', {method:'POST', body:{content, source: 'email'}});
    await showPatternScan(document.getElementById('atk-result'), r);
  } catch(e) { showError('atk-result', e.message); }
  document.querySelectorAll('.prebuilt-btn').forEach(b => b.disabled = false);
}

// ── Explain attack ──
async function explainAttack(btn, status) {
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Asking Groq...';
  try {
    const desc = status === 'blocked'
      ? 'An attacker tried to inject a false memory into an AI agent via an email. Mnemosyne detected danger patterns (payment rerouting language) and a low-trust source, and blocked the memory write. The agent never received the poisoned data.'
      : 'An attacker injected a memory that bypassed pattern detection. No known danger patterns were found, so the memory was stored. This shows the limits of string-matching defense.';
    const r = await api('/api/explain', {method:'POST', body:{last_operation: desc}});
    document.getElementById('explain-result').innerHTML = `<div class="card card-purple" style="margin-top:8px"><strong>🤖 Mnemosyne explains:</strong><br>${r.explanation}</div>`;
  } catch(e) { document.getElementById('explain-result').innerHTML = `<div class="error-card">${e.message}</div>`; }
  btn.disabled = false;
  btn.textContent = '🤖 Explain this attack';
}

// ── Compare Mode ──
async function runCompare() {
  setBtnLoading('compare-btn', true, 'Running comparison...');
  try {
    const r = await api('/api/compare', {method:'POST'});
    document.getElementById('compare-result').innerHTML = `<div class="compare-grid"><div class="card card-red"><h4 style="color:var(--red)">❌ Without Mnemosyne</h4><p style="margin-top:8px">${r.poisoned_answer}</p></div><div class="card card-green"><h4 style="color:var(--green)">✓ With Mnemosyne</h4><p style="margin-top:8px">${r.clean_answer}</p></div></div>`;
  } catch(e) { showError('compare-result', e.message); }
  setBtnLoading('compare-btn', false, '⚔ Compare Mode');
}

// ── Reset Memory ──
async function resetMemory() {
  if (!confirm('This will wipe all memories. Are you sure?')) return;
  try {
    await api('/api/reset', {method:'POST'});
    refreshMemories();
    refreshStats();
  } catch(e) { alert('Reset failed: ' + e.message); }
}
