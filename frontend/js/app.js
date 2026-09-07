/**
 * CreditLens Enterprise Risk Intelligence - Application Router & Main Controller
 */

const VIEWS = ['overview', 'eda', 'risk', 'rules', 'chat'];
let activeView = 'overview';

function showHeroView() {
  const hero = document.getElementById('hero-view');
  if (hero) {
    hero.classList.remove('hidden');
  }
}

function hideHeroView() {
  const hero = document.getElementById('hero-view');
  if (hero) {
    hero.classList.add('hidden');
  }
}

function navigateTo(viewId) {
  if (!VIEWS.includes(viewId)) viewId = 'overview';
  activeView = viewId;

  // 1. Update Navigation Links in Sidebar
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.view === viewId);
  });

  // 2. Toggle View Sections
  document.querySelectorAll('.view-section').forEach(el => {
    el.classList.toggle('active', el.id === `${viewId}-view`);
  });

  // 3. Update Header Title
  const titleMap = {
    overview: 'Portfolio Overview & Executive Intelligence',
    eda: 'Exploratory Data Analysis & Strategic Insights',
    risk: 'Applicant Risk Assessment & SHAP Underwriting',
    rules: 'Credit Policy Engine & Auditable Rules',
    chat: 'Talk-to-Data Conversational Analyst'
  };
  const titleEl = document.getElementById('header-title');
  if (titleEl) {
    titleEl.textContent = titleMap[viewId] || 'Risk Intelligence';
  }

  // 4. Initialize Page Specific Data
  if (viewId === 'overview') initOverviewPage();
  if (viewId === 'eda') initEDAPage();
  if (viewId === 'risk') initRiskPage();
  if (viewId === 'rules') initRulesPage(currentRuleFilter || 'all');
  if (viewId === 'chat' || viewId === 'talk') {
    if (window.ChatStore) window.ChatStore.renderMainPage();
  }

  // Scroll to top of content container
  const container = document.getElementById('content-container');
  if (container) container.scrollTop = 0;
}

// Global Event Listeners Setup
document.addEventListener('DOMContentLoaded', () => {
  // 1. Hero Landing Page Navigation
  const exploreBtn = document.getElementById('btn-hero-explore');
  if (exploreBtn) {
    exploreBtn.addEventListener('click', () => {
      hideHeroView();
      navigateTo('overview');
    });
  }

  const launchBtn = document.getElementById('btn-hero-launch');
  if (launchBtn) {
    launchBtn.addEventListener('click', () => {
      hideHeroView();
      navigateTo('overview');
    });
  }

  const orbitCore = document.getElementById('orbit-core-btn');
  if (orbitCore) {
    orbitCore.addEventListener('click', () => {
      hideHeroView();
      navigateTo('risk');
    });
  }

  // Orbit Nodes Click Navigation
  document.querySelectorAll('.orbit-node-interactive').forEach(node => {
    node.addEventListener('click', () => {
      const navTarget = node.dataset.nav || 'overview';
      hideHeroView();
      navigateTo(navTarget);
    });
  });

  // Return to Hero Page from Sidebar
  const returnHeroBtn = document.getElementById('btn-return-hero');
  if (returnHeroBtn) {
    returnHeroBtn.addEventListener('click', (e) => {
      e.preventDefault();
      showHeroView();
    });
  }

  const sidebarBrandBtn = document.getElementById('sidebar-brand-btn');
  if (sidebarBrandBtn) {
    sidebarBrandBtn.addEventListener('click', (e) => {
      e.preventDefault();
      showHeroView();
    });
  }

  // 2. Sidebar Navigation Click Handlers handled by inline switchPage() in index.html
  // app.js does NOT re-register nav clicks to avoid conflict (nav items use data-page, not data-view)

  // 3. Risk Scoring Preset Change
  const presetSelect = document.getElementById('risk-preset-select');
  if (presetSelect) {
    presetSelect.addEventListener('change', (e) => {
      loadRiskPreset(e.target.value);
    });
  }

  // Live slider value display bindings
  bindSlider('input-age', 'val-age', ' yrs');
  bindSlider('input-employed', 'val-employed', ' yrs');
  bindSliderFloat('input-ext2', 'val-ext2');
  bindSliderFloat('input-ext3', 'val-ext3');
  bindSliderPct('input-refused-rate', 'val-refused-rate');

  // Risk Form Submission
  const riskForm = document.getElementById('risk-evaluation-form');
  if (riskForm) {
    riskForm.addEventListener('submit', handleRiskEvaluation);
  }

  // EDA Tab Handlers
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tabTarget = btn.dataset.tab;
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content-panel').forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetPanel = document.getElementById(`tab-${tabTarget}`);
      if (targetPanel) targetPanel.classList.add('active');
    });
  });

  // Decision Rules Filter Buttons
  document.querySelectorAll('.rule-filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const filter = btn.dataset.filter;
      initRulesPage(filter);
    });
  });

  // Chat Form Submission on Dedicated Page
  const chatForm = document.getElementById('chat-form');
  if (chatForm) {
    chatForm.addEventListener('submit', handleChatSubmit);
  }

  // 4. Floating Chatbot Event Listeners
  setupFloatingChat();

  // Initially, Hero page is visible, but prepare the overview page
  initOverviewPage();
});

function bindSlider(sliderId, tagId, unit = '') {
  const el = document.getElementById(sliderId);
  const tag = document.getElementById(tagId);
  if (!el || !tag) return;
  el.addEventListener('input', () => {
    tag.textContent = `${el.value}${unit}`;
  });
}

function bindSliderFloat(sliderId, tagId) {
  const el = document.getElementById(sliderId);
  const tag = document.getElementById(tagId);
  if (!el || !tag) return;
  el.addEventListener('input', () => {
    tag.textContent = parseFloat(el.value).toFixed(2);
  });
}

function bindSliderPct(sliderId, tagId) {
  const el = document.getElementById(sliderId);
  const tag = document.getElementById(tagId);
  if (!el || !tag) return;
  el.addEventListener('input', () => {
    tag.textContent = `${Math.round(parseFloat(el.value) * 100)}%`;
  });
}

/* ==============================================================================
   FLOATING AI ASSISTANT ("AGENT NEO") CONTROLLER
   ============================================================================== */
function setupFloatingChat() {
  const trigger = document.getElementById('floating-chat-trigger');
  const modal = document.getElementById('floating-chat-modal');
  const closeBtn = document.getElementById('f-chat-close-btn');
  const expandBtn = document.getElementById('f-chat-expand-btn');
  const clearBtn = document.getElementById('f-chat-clear-btn');
  const fChatForm = document.getElementById('f-chat-form');

  if (trigger && modal) {
    trigger.addEventListener('click', () => {
      modal.classList.toggle('closed');
      const bubble = document.getElementById('chat-trigger-bubble');
      if (bubble) bubble.style.display = 'none';
      if (!modal.classList.contains('closed')) {
        if (window.ChatStore) window.ChatStore.renderFloatingWidget();
        const input = document.getElementById('f-chat-input');
        if (input) input.focus();
        const body = document.getElementById('f-chat-body');
        if (body) body.scrollTop = body.scrollHeight;
      }
    });
  }

  if (closeBtn && modal) {
    closeBtn.addEventListener('click', () => {
      modal.classList.add('closed');
    });
  }

  if (expandBtn && modal) {
    expandBtn.addEventListener('click', () => {
      modal.classList.add('closed');
      if (typeof hideHero === 'function') hideHero();
      if (typeof switchPage === 'function') {
        switchPage('talk');
        const u = new URL(window.location);
        u.searchParams.set('page', 'talk');
        history.pushState({ page: 'talk' }, '', u);
      }
      if (window.ChatStore) {
        window.ChatStore.renderMainPage();
      }
      setTimeout(() => {
        const stream = document.getElementById('talk-chat-stream');
        if (stream) stream.scrollTo({ top: stream.scrollHeight, behavior: 'smooth' });
      }, 50);
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      if (window.ChatStore) {
        window.ChatStore.clearChat();
      }
    });
  }

  if (fChatForm) {
    fChatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = document.getElementById('f-chat-input');
      if (input && input.value.trim() && window.ChatStore) {
        const q = input.value.trim();
        window.ChatStore.submitQuestion(q);
      }
    });
  }
}

async function handleFloatingChatSubmit(e) {
  if (e) e.preventDefault();
  const input = document.getElementById('f-chat-input');
  const query = input ? input.value.trim() : '';
  if (!query) return;
  if (window.ChatStore) await window.ChatStore.submitQuestion(query);
}

async function sendFloatingQuery(question) {
  if (window.ChatStore) await window.ChatStore.submitQuestion(question);
}
