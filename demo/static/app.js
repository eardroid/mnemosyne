async function api(path, body) {
  const opts = { method: "GET", headers: { "Content-Type": "application/json" } };
  if (body) { opts.method = "POST"; opts.body = JSON.stringify(body); }
  const res = await fetch(path, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || ("HTTP " + res.status));
  }
  return res.json();
}

function setStatus(r) {
  const cls = r.status === "STORED" ? "stored" : "blocked";
  const labels = (r.matched_labels || []).join(", ") || "-";
  return `
    <div class="row">
      <span class="tag ${cls}">${r.status}</span>
      <span style="color:var(--dim)">trust=${r.trust}</span>
      <span style="color:var(--dim)">score=${r.score.toFixed(2)}</span>
      <div class="explain">matched: ${labels}</div>
      ${r.block_reason ? `<div class="explain" style="color:var(--red)">why: ${r.block_reason}</div>` : ""}
      <div class="explain">"${r.content}"</div>
    </div>`;
}

async function employeeStore() {
  const content = document.getElementById("emp-memory").value.trim();
  if (!content) return alert("Type a memory first.");
  try {
    const r = await api("/api/inject", {
      content, source: document.getElementById("emp-source").value,
    });
    document.getElementById("emp-result").innerHTML = setStatus(r);
    document.getElementById("emp-memory").value = "";
    refresh();
  } catch (e) { alert(e.message); }
}

async function employeeAsk() {
  const q = document.getElementById("emp-question").value.trim();
  if (!q) return alert("Type a question.");
  try {
    const r = await api("/api/ask", { question: q });
    document.getElementById("emp-answer").innerHTML =
      `<div class="explain"><b>Memories used:</b> ${r.memories_used}</div>
       <div class="explain"><b>Context the agent sees:</b><br><code>${r.context}</code></div>`;
  } catch (e) { alert(e.message); }
}

async function attackerInject() {
  const content = document.getElementById("atk-content").value.trim();
  if (!content) return alert("Type an attack first.");
  try {
    const r = await api("/api/inject", {
      content, source: document.getElementById("atk-source").value,
    });
    document.getElementById("atk-result").innerHTML = setStatus(r);
    refresh();
  } catch (e) { alert(e.message); }
}

async function refresh() {
  try {
    const stats = await api("/api/stats");
    document.getElementById("st-total").textContent = stats.total;
    document.getElementById("st-stored").textContent = stats.stored;
    document.getElementById("st-blocked").textContent = stats.blocked;

    const rows = await api("/api/recent");
    document.getElementById("event-feed").innerHTML = rows.map(r => {
      const cls = r.status === "STORED" ? "stored" : "blocked";
      const prev = (r.content || "").slice(0, 60);
      return `<div class="row">
        <span class="tag ${cls}">${r.status}</span>
        <span style="color:var(--dim)">${r.source} · ${r.trust_level}</span>
        <div class="explain">${prev}</div>
      </div>`;
    }).join("") || `<div class="explain">No events yet.</div>`;
  } catch (e) { }
}

async function resetAll() {
  if (!confirm("Wipe all memories and the ledger?")) return;
  try { await api("/api/reset", {}); refresh(); }
  catch (e) { alert(e.message); }
}

refresh();
setInterval(refresh, 3000);
