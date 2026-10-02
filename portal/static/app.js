/**
 * OmniForge Homelab Mission Control Frontend Application
 */

const state = {
  autoScroll: true,
  logWs: null,
  agentWs: null,
  logLines: 0,
};

// -------------------------------------------------------------
// Initialization
// -------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  initTelemetryPolling();
  initLogWebSocket();
  initAgentDispatcher();
  initServiceControls();
  loadAudioGallery();

  document.getElementById("btnRefresh").addEventListener("click", () => {
    fetchTelemetry();
    fetchServices();
    loadAudioGallery();
    showToast("Refreshed homelab data 🔄");
  });

  const scrollBtn = document.getElementById("btnToggleScroll");
  scrollBtn.addEventListener("click", () => {
    state.autoScroll = !state.autoScroll;
    scrollBtn.textContent = `Auto-scroll: ${state.autoScroll ? "ON" : "OFF"}`;
  });

  document.getElementById("btnClearLogs").addEventListener("click", () => {
    document.getElementById("logOutput").textContent = "";
    state.logLines = 0;
  });
});

// -------------------------------------------------------------
// System Telemetry & Metrics
// -------------------------------------------------------------
function initTelemetryPolling() {
  fetchTelemetry();
  fetchServices();
  setInterval(fetchTelemetry, 2500);
  setInterval(fetchServices, 3000);
}

async function fetchTelemetry() {
  try {
    const res = await fetch("/api/system");
    if (!res.ok) throw new Error("Telemetry fetch failed");
    const data = await res.json();

    document.getElementById("hostname").textContent = data.hostname || "Homelab Host";
    document.getElementById("osSub").textContent = data.os || "Linux";

    // CPU
    const cpuPct = data.cpu.percent || 0;
    document.getElementById("cpuValue").textContent = `${cpuPct}%`;
    document.getElementById("cpuSub").textContent = `${data.cpu.cores_logical} cores • load ${data.cpu.load_avg.map(v => v.toFixed(1)).join(", ")}`;
    document.getElementById("cpuBar").style.width = `${Math.min(100, Math.max(0, cpuPct))}%`;

    // RAM
    const ramPct = data.memory.percent || 0;
    document.getElementById("ramValue").textContent = `${ramPct}%`;
    document.getElementById("ramSub").textContent = `${data.memory.used_mb} / ${data.memory.total_mb} MB`;
    document.getElementById("ramBar").style.width = `${Math.min(100, Math.max(0, ramPct))}%`;

    // Disk
    const diskPct = data.disk.percent || 0;
    document.getElementById("diskValue").textContent = `${diskPct}%`;
    document.getElementById("diskSub").textContent = `${data.disk.free_gb} GB free of ${data.disk.total_gb} GB`;
    document.getElementById("diskBar").style.width = `${Math.min(100, Math.max(0, diskPct))}%`;

    // Uptime
    const sec = data.uptime_seconds || 0;
    const days = Math.floor(sec / 86400);
    const hrs = Math.floor((sec % 86400) / 3600);
    const mins = Math.floor((sec % 3600) / 60);
    document.getElementById("uptimeValue").textContent = days > 0 ? `${days}d ${hrs}h ${mins}m` : `${hrs}h ${mins}m`;

    updateConnStatus(true);
  } catch (err) {
    updateConnStatus(false);
  }
}

function updateConnStatus(connected) {
  const label = document.getElementById("connLabel");
  const pill = document.getElementById("connStatus");
  if (connected) {
    label.textContent = "Connected";
    pill.style.color = "var(--accent-emerald)";
  } else {
    label.textContent = "Reconnecting...";
    pill.style.color = "var(--accent-rose)";
  }
}

// -------------------------------------------------------------
// Service Supervision
// -------------------------------------------------------------
async function fetchServices() {
  try {
    const res = await fetch("/api/services");
    if (!res.ok) return;
    const data = await res.json();
    const svc = (data.services || [])[0];
    if (!svc) return;

    const dot = document.getElementById("svcDot");
    const meta = document.getElementById("svcMeta");

    if (svc.active) {
      dot.className = "status-indicator active";
      meta.textContent = `State: ${svc.state.toUpperCase()} • PID: ${svc.pid || "--"} • RAM: ${svc.memory_mb || 0} MB • systemd`;
      document.getElementById("btnStartSvc").style.display = "none";
      document.getElementById("btnStopSvc").style.display = "inline-flex";
    } else {
      dot.className = "status-indicator inactive";
      meta.textContent = `State: ${svc.state.toUpperCase()} • Inactive`;
      document.getElementById("btnStartSvc").style.display = "inline-flex";
      document.getElementById("btnStopSvc").style.display = "none";
    }
  } catch (e) {
    console.error("Failed to query services:", e);
  }
}

function initServiceControls() {
  document.getElementById("btnRestartSvc").addEventListener("click", () => handleServiceAction("restart"));
  document.getElementById("btnStopSvc").addEventListener("click", () => handleServiceAction("stop"));
  document.getElementById("btnStartSvc").addEventListener("click", () => handleServiceAction("start"));
}

async function handleServiceAction(action) {
  showToast(`Executing ${action} on omniforge.service... ⏳`);
  try {
    const res = await fetch(`/api/services/omniforge.service/${action}`, { method: "POST" });
    const data = await res.json();
    if (res.ok) {
      showToast(`omniforge.service ${action} successful! ✅`);
      fetchServices();
    } else {
      showToast(`Error: ${data.detail || data.message}`, true);
    }
  } catch (e) {
    showToast(`Network error triggering ${action}`, true);
  }
}

// -------------------------------------------------------------
// Live WebSocket Log Streaming
// -------------------------------------------------------------
function initLogWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/logs/omniforge.service`;

  state.logWs = new WebSocket(wsUrl);
  const logElem = document.getElementById("logOutput");

  state.logWs.onopen = () => {
    logElem.textContent = "[System] Live journalctl WebSocket log stream connected.\n";
  };

  state.logWs.onmessage = (event) => {
    state.logLines++;
    if (state.logLines > 800) {
      logElem.textContent = logElem.textContent.substring(logElem.textContent.indexOf("\n") + 1);
    }
    logElem.appendChild(document.createTextNode(event.data + "\n"));
    if (state.autoScroll) {
      logElem.scrollTop = logElem.scrollHeight;
    }
  };

  state.logWs.onclose = () => {
    setTimeout(initLogWebSocket, 3000);
  };
}

// -------------------------------------------------------------
// Cross-Device Agent Session Management
// -------------------------------------------------------------
async function fetchAgentSession() {
  try {
    const res = await fetch("/api/agent/session");
    if (!res.ok) return;
    const data = await res.json();
    state.conversationId = data.conversation_id;
    state.history = data.history || [];

    updateSessionUI();
    renderChatThread();
  } catch (e) {
    console.error("Failed to fetch agent session:", e);
  }
}

function updateSessionUI() {
  const statusElem = document.getElementById("sessionStatus");
  const turnsElem = document.getElementById("turnsBadge");
  const dotElem = document.getElementById("sessionDot");

  const turnCount = state.history.length;
  if (turnsElem) {
    turnsElem.textContent = `${turnCount} turn${turnCount === 1 ? "" : "s"}`;
  }

  if (state.conversationId) {
    const shortId = state.conversationId.substring(0, 8);
    if (statusElem) statusElem.textContent = `Session: ${shortId}...`;
    if (dotElem) {
      dotElem.style.background = "var(--accent-emerald)";
      dotElem.style.boxShadow = "0 0 6px var(--accent-emerald)";
    }
  } else {
    if (statusElem) statusElem.textContent = "Fresh Session";
    if (dotElem) {
      dotElem.style.background = "var(--accent-cyan)";
      dotElem.style.boxShadow = "0 0 6px var(--accent-cyan)";
    }
  }
}

function renderChatThread() {
  const container = document.getElementById("chatMessages");
  const emptyHint = document.getElementById("chatEmptyHint");
  if (!container) return;

  if (!state.history || state.history.length === 0) {
    if (emptyHint) emptyHint.style.display = "block";
    container.innerHTML = "";
    return;
  }

  if (emptyHint) emptyHint.style.display = "none";
  container.innerHTML = state.history.map(turn => {
    const timeStr = turn.timestamp ? new Date(turn.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "";
    const modelTag = turn.model ? turn.model.replace("gemini-", "").replace("claude-", "") : "agent";
    const durTag = turn.duration_seconds ? ` • ${turn.duration_seconds}s` : "";

    return `
      <div class="chat-turn">
        <div class="chat-bubble-user">
          <div class="chat-meta">
            <span class="chat-meta-left">👤 You</span>
            <span>${timeStr}</span>
          </div>
          <div>${escapeHtml(turn.prompt)}</div>
        </div>
        <div class="chat-bubble-agent">
          <div class="chat-meta">
            <span class="chat-meta-left">🤖 Antigravity (${modelTag}${durTag})</span>
            <span>${timeStr}</span>
          </div>
          <div>${escapeHtml(turn.response || "(No text response recorded)")}</div>
        </div>
      </div>
    `;
  }).join("");

  const threadWrapper = document.getElementById("chatThreadContainer");
  if (threadWrapper) {
    threadWrapper.scrollTop = threadWrapper.scrollHeight;
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

async function handleNewSession() {
  showToast("Clearing agent session... ⏳");
  try {
    const res = await fetch("/api/agent/session/new", { method: "POST" });
    if (res.ok) {
      state.conversationId = null;
      state.history = [];
      updateSessionUI();
      renderChatThread();
      const output = document.getElementById("agentStreamOutput");
      if (output) output.textContent = "";
      const streamPanel = document.getElementById("agentStreamPanel");
      if (streamPanel) streamPanel.style.display = "none";
      showToast("Started fresh agent session ✨");
    }
  } catch (e) {
    showToast("Failed to reset session", true);
  }
}

// -------------------------------------------------------------
// Antigravity CLI Agent Dispatcher
// -------------------------------------------------------------
function initAgentDispatcher() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/agent`;

  const input = document.getElementById("agentPromptInput");
  const btn = document.getElementById("btnDispatchAgent");
  const output = document.getElementById("agentStreamOutput");
  const streamPanel = document.getElementById("agentStreamPanel");
  const btnHideStream = document.getElementById("btnHideStream");

  if (btnHideStream && streamPanel) {
    btnHideStream.addEventListener("click", () => {
      const isHidden = streamPanel.style.display === "none";
      streamPanel.style.display = isHidden ? "block" : "none";
      btnHideStream.textContent = isHidden ? "Minimize" : "Show Stream";
    });
  }

  const btnNew = document.getElementById("btnNewSession");
  if (btnNew) btnNew.addEventListener("click", handleNewSession);

  const btnSync = document.getElementById("btnSyncSession");
  if (btnSync) {
    btnSync.addEventListener("click", () => {
      fetchAgentSession();
      showToast("Session synced across devices 🔄");
    });
  }

  // Load initial session on load
  fetchAgentSession();

  function connectAgentWs() {
    state.agentWs = new WebSocket(wsUrl);
    state.agentWs.onmessage = (event) => {
      const data = event.data;
      if (data === "[[AGENT_RUN_COMPLETE]]") {
        btn.disabled = false;
        btn.textContent = "🚀 Dispatch";
        fetchAgentSession();
        return;
      }
      if (
        data.startsWith("🚀") ||
        data.startsWith("⚙️") ||
        data.startsWith("📄") ||
        data.startsWith("⚡") ||
        data.startsWith("🏁") ||
        data.startsWith("💬") ||
        data.startsWith("❌") ||
        data.startsWith("💭")
      ) {
        output.appendChild(document.createTextNode(data + "\n"));
      } else {
        output.appendChild(document.createTextNode(data));
      }
      output.scrollTop = output.scrollHeight;
    };
    state.agentWs.onclose = () => {
      setTimeout(connectAgentWs, 3000);
    };
  }
  connectAgentWs();

  function sendPrompt(promptText) {
    if (!promptText || !state.agentWs || state.agentWs.readyState !== WebSocket.OPEN) {
      showToast("Agent WebSocket is connecting... please wait", true);
      return;
    }
    const modelSelect = document.getElementById("agentModelSelect");
    const selectedModel = modelSelect ? modelSelect.value : "gemini-3.8-flash-medium";
    const effort = selectedModel.includes("flash") ? "low" : "high";

    if (streamPanel) streamPanel.style.display = "block";
    if (btnHideStream) btnHideStream.textContent = "Minimize";
    output.textContent = "";
    btn.disabled = true;
    btn.textContent = "⏳ Executing...";
    input.value = "";
    showToast(`Dispatched to Antigravity (${selectedModel.split("-")[2] || "fast"}) 🧠`);

    state.agentWs.send(JSON.stringify({
      prompt: promptText,
      model: selectedModel,
      effort: effort,
      continue_session: true,
      conversation_id: state.conversationId
    }));
  }

  btn.addEventListener("click", () => {
    sendPrompt(input.value.trim());
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      sendPrompt(input.value.trim());
    }
  });

  document.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      sendPrompt(chip.dataset.prompt);
    });
  });
}

// -------------------------------------------------------------
// Generated Audio & Media Gallery
// -------------------------------------------------------------
async function loadAudioGallery() {
  const container = document.getElementById("audioGallery");
  try {
    const res = await fetch("/api/assets");
    if (!res.ok) throw new Error("Failed to load assets");
    const data = await res.json();
    const assets = (data.assets || []).filter(a => a.type === "audio");

    if (!assets.length) {
      container.innerHTML = `<div class="gallery-empty">No generated bedtime stories found in output/ yet.</div>`;
      return;
    }

    container.innerHTML = assets.map(a => `
      <div class="audio-card">
        <div class="audio-header">
          <span class="audio-title" title="${a.filename}">🎧 ${a.filename}</span>
          <span class="audio-date">${a.size_kb} KB • ${a.modified_str}</span>
        </div>
        <audio controls preload="none">
          <source src="${a.url}" type="audio/mpeg">
          Your browser does not support the audio element.
        </audio>
      </div>
    `).join("");
  } catch (err) {
    container.innerHTML = `<div class="gallery-empty">Error loading audio assets.</div>`;
  }
}

// -------------------------------------------------------------
// UI Toast Notifications
// -------------------------------------------------------------
function showToast(msg, isError = false) {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = "toast";
  if (isError) toast.style.borderColor = "var(--accent-rose)";
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
