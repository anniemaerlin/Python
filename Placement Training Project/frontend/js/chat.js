/**
 * PP.PRICING — PriceIQ AI Chat Assistant
 * Full-featured chatbot: uses backend /api/v1/chat/message for responses,
 * falls back to client-side KB when backend is unavailable.
 */

(function () {
  'use strict';

  const API_BASE = 'http://localhost:8000/api/v1';

  /* ════════════════════════════════════════════════════════
     Client-side knowledge base (offline fallback)
     ════════════════════════════════════════════════════════ */
  const KB = {
    greet: [
      'Hello! I\'m <strong>PriceIQ</strong>, your AI pricing assistant. I can help you with:\n\n• Price predictions & optimization\n• Demand forecasting\n• Competitor analysis\n• Customer segmentation\n• Revenue simulation\n\nWhat would you like to explore?',
      'Hi there! I\'m <strong>PriceIQ</strong> — powered by XGBoost & Random Forest ML models. Ask me anything about pricing strategy, market intelligence, or demand trends!'
    ],
    help: '<strong>I can help you with:</strong>\n\n• <code>predict price</code> — AI price recommendation\n• <code>forecast demand</code> — Demand trend analysis\n• <code>analyze competitors</code> — Market positioning\n• <code>segment customer</code> — Classify a customer\n• <code>simulate revenue</code> — Revenue impact calculator\n• <code>what is dynamic pricing?</code> — Learn concepts\n• <code>pricing tips</code> — Best practices\n\nOr just ask me anything in plain English!',
    about: '<strong>PP.PRICING</strong> is an enterprise-grade AI Dynamic Pricing Engine using XGBoost & Random Forest ML models, real-time competitor monitoring, demand forecasting, and customer segmentation.',
    dynamic_pricing: '<strong>Dynamic Pricing</strong> adjusts prices in real-time based on demand, competition, inventory, and conversion rate. Our ML models analyze all these signals to recommend the optimal price.',
    tips: '<strong>Pricing Best Practices:</strong>\n\n• Monitor competitors daily\n• Use demand forecasting for peak periods\n• VIP customers: 5% discount; Budget-Conscious: 15%\n• Low inventory = time to increase price\n• Confidence score above 85% = act immediately',
    segments: '<strong>Customer Segments:</strong>\n\n• VIP — High LTV, 5% discount, 95% retention\n• Regular — Consistent buyers, 3% discount\n• Budget-Conscious — Price-sensitive, 15% discount\n• Inactive — Re-engage with 20% offer\n• New — Welcome discount 10%',
    unknown: [
      'Hmm, I\'m not sure about that specific topic. Try asking me about price prediction, demand forecasting, competitor analysis, or customer segmentation.',
      'I\'m specialized in pricing intelligence. Type <code>help</code> to see all available commands!'
    ]
  };

  /* ════════════════════════════════════════════════════════
     Client-side intent detection (offline fallback only)
     ════════════════════════════════════════════════════════ */
  function detectIntentOffline(msg) {
    const m = msg.toLowerCase();
    if (/hello|hi |hey |good morning|good afternoon|greet/.test(m)) return 'greet';
    if (/help|what can|what do|commands|features/.test(m)) return 'help';
    if (/about|what is pp|what is this|who are you/.test(m)) return 'about';
    if (/dynamic pricing|how does pricing work|price strategy/.test(m)) return 'dynamic_pricing';
    if (/tip|best practice|advice|recommend/.test(m)) return 'tips';
    if (/segment|vip|regular|budget|inactive|new customer/.test(m)) return 'segments';
    return 'unknown';
  }

  function getOfflineResponse(msg) {
    const intent = detectIntentOffline(msg);
    const val = KB[intent];
    if (Array.isArray(val)) return val[Math.floor(Math.random() * val.length)];
    return val || KB.unknown[Math.floor(Math.random() * KB.unknown.length)];
  }

  /* ════════════════════════════════════════════════════════
     Backend API call
     ════════════════════════════════════════════════════════ */
  async function fetchBackendResponse(message) {
    const res = await fetch(`${API_BASE}/chat/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: 'web_chat' }),
      signal: AbortSignal.timeout(8000)
    });
    if (!res.ok) throw new Error(`API ${res.status}`);
    const data = await res.json();
    return data.reply || '';
  }

  /* ════════════════════════════════════════════════════════
     Markdown renderer
     ════════════════════════════════════════════════════════ */
  function renderMarkdown(text) {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/^• (.+)$/gm, '<li>$1</li>')
      .replace(/(<li>.*<\/li>(\n|$))+/gs, m => `<ul>${m}</ul>`)
      .replace(/\n{2,}/g, '<br><br>')
      .replace(/\n/g, '<br>');
  }

  /* ════════════════════════════════════════════════════════
     UI helpers
     ════════════════════════════════════════════════════════ */
  function timeStr() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function addMessage(text, role) {
    const msgs   = document.getElementById('chat-messages');
    const typing = document.getElementById('chat-typing');
    const div    = document.createElement('div');
    div.className = 'chat-msg ' + role;

    const icon = role === 'ai' ? 'fa-robot' : 'fa-user';
    const html = renderMarkdown(text);

    div.innerHTML = `
      <div class="chat-msg-avatar"><i class="fa-solid ${icon}"></i></div>
      <div class="chat-msg-body">
        <div class="chat-bubble">${html}</div>
        <span class="chat-msg-time">${timeStr()}</span>
      </div>`;

    msgs.insertBefore(div, typing);
    msgs.scrollTop = msgs.scrollHeight;
    return div;
  }

  function setTyping(show) {
    const el = document.getElementById('chat-typing');
    if (el) el.classList.toggle('visible', show);
    const msgs = document.getElementById('chat-messages');
    if (msgs) msgs.scrollTop = msgs.scrollHeight;
  }

  /* ════════════════════════════════════════════════════════
     Send message
     ════════════════════════════════════════════════════════ */
  async function sendMessage(text) {
    const input   = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send');
    const msg     = (text || input.value.trim());
    if (!msg) return;

    input.value = '';
    input.style.height = 'auto';

    addMessage(msg, 'user');
    setTyping(true);
    sendBtn.disabled = true;

    // Realistic delay 0.6–1.4s
    const delay = 600 + Math.random() * 800;
    await new Promise(r => setTimeout(r, delay));

    try {
      let reply;
      try {
        reply = await fetchBackendResponse(msg);
      } catch {
        // Backend unavailable — use offline fallback
        reply = getOfflineResponse(msg);
      }
      setTyping(false);
      addMessage(reply, 'ai');
    } catch (e) {
      setTyping(false);
      addMessage('Sorry, something went wrong. Please try again!', 'ai');
    }

    sendBtn.disabled = false;
    input.focus();
  }

  /* ════════════════════════════════════════════════════════
     Build DOM — injects FAB + chat window into any page
     ════════════════════════════════════════════════════════ */
  function buildChat() {
    // Avoid double-init
    if (document.getElementById('chat-fab')) return;

    /* ── Floating Action Button ── */
    const fab = document.createElement('button');
    fab.id = 'chat-fab';
    fab.setAttribute('aria-label', 'Open PriceIQ Chat');
    fab.innerHTML = `<i class="fa-solid fa-robot"></i><span id="chat-notif"></span>`;
    document.body.appendChild(fab);

    /* ── Chat Window ── */
    const win = document.createElement('div');
    win.id = 'chat-window';
    win.setAttribute('role', 'dialog');
    win.setAttribute('aria-label', 'PriceIQ AI Pricing Assistant');
    win.innerHTML = `
      <!-- ── Header ── -->
      <div class="chat-header">
        <div class="chat-header-avatar"><i class="fa-solid fa-robot"></i></div>
        <div class="chat-header-info">
          <div class="chat-header-name">PriceIQ Assistant</div>
          <div class="chat-header-status">
            <span class="chat-status-dot"></span>
            <span>Online · ML Models Loaded</span>
          </div>
        </div>
        <div class="chat-header-actions">
          <button class="chat-header-btn" id="chat-clear" title="Clear chat"><i class="fa-solid fa-trash-can"></i></button>
          <button class="chat-header-btn" id="chat-close" title="Close chat"><i class="fa-solid fa-xmark"></i></button>
        </div>
      </div>

      <!-- ── Quick Prompts ── -->
      <div class="chat-quickbar">
        <button class="chat-quick-btn" data-q="predict price">💰 Price Predict</button>
        <button class="chat-quick-btn" data-q="forecast demand">📈 Forecast</button>
        <button class="chat-quick-btn" data-q="analyze competitors">🏪 Competitors</button>
        <button class="chat-quick-btn" data-q="segment customer">👤 Segment</button>
        <button class="chat-quick-btn" data-q="pricing tips">💡 Tips</button>
        <button class="chat-quick-btn" data-q="what is dynamic pricing?">🤖 How it works</button>
        <button class="chat-quick-btn" data-q="explain xgboost">🧠 XGBoost</button>
        <button class="chat-quick-btn" data-q="inventory tips">📦 Inventory</button>
      </div>

      <!-- ── Messages ── -->
      <div id="chat-messages">
        <div id="chat-typing">
          <div class="chat-msg-avatar" style="width:32px;height:32px;border-radius:10px;background:linear-gradient(135deg,rgba(0,242,254,0.15),rgba(127,0,255,0.15));border:1px solid rgba(0,242,254,0.25);display:flex;align-items:center;justify-content:center;color:#00f2fe;font-size:0.85rem;flex-shrink:0;">
            <i class="fa-solid fa-robot"></i>
          </div>
          <div class="typing-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <!-- ── Input ── -->
      <div class="chat-input-area">
        <textarea id="chat-input" placeholder="Ask about pricing, demand, competitors…" rows="1" aria-label="Chat input"></textarea>
        <button id="chat-send" aria-label="Send message"><i class="fa-solid fa-paper-plane"></i></button>
      </div>
      <div class="chat-disclaimer">PriceIQ uses live backend data · Responses may vary</div>
    `;
    document.body.appendChild(win);

    /* ── Events ── */

    // FAB toggle
    fab.addEventListener('click', () => {
      const isOpen = win.classList.toggle('open');
      fab.classList.toggle('open', isOpen);
      document.getElementById('chat-notif').classList.remove('visible');
      if (isOpen) {
        const msgs    = document.getElementById('chat-messages');
        const hasChat = msgs.querySelectorAll('.chat-msg').length > 0;
        if (!hasChat) {
          setTimeout(() => addMessage(KB.greet[0], 'ai'), 300);
        }
        document.getElementById('chat-input').focus();
      }
    });

    // Close button
    document.getElementById('chat-close').addEventListener('click', () => {
      win.classList.remove('open');
      fab.classList.remove('open');
    });

    // Clear button
    document.getElementById('chat-clear').addEventListener('click', () => {
      const msgs   = document.getElementById('chat-messages');
      const typing = document.getElementById('chat-typing');
      msgs.querySelectorAll('.chat-msg').forEach(m => m.remove());
      msgs.appendChild(typing);
      setTimeout(() => addMessage(KB.greet[0], 'ai'), 200);
    });

    // Send button
    document.getElementById('chat-send').addEventListener('click', () => sendMessage());

    // Enter key (Shift+Enter = newline)
    document.getElementById('chat-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    // Auto-resize textarea
    document.getElementById('chat-input').addEventListener('input', function () {
      this.style.height = 'auto';
      this.style.height = Math.min(this.scrollHeight, 100) + 'px';
    });

    // Quick prompt buttons
    win.querySelectorAll('.chat-quick-btn').forEach(btn => {
      btn.addEventListener('click', () => sendMessage(btn.dataset.q));
    });

    // Show notification dot after 5 seconds if chat hasn't been opened
    setTimeout(() => {
      if (!win.classList.contains('open')) {
        document.getElementById('chat-notif').classList.add('visible');
      }
    }, 5000);
  }

  /* ── Init ── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildChat);
  } else {
    buildChat();
  }

})();
