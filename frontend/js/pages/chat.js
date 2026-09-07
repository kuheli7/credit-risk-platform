/**
 * CreditLens Unified Chat Store & Controller
 * Powers both the Floating CreditLens AI widget and the main Talk to Data page (?page=talk).
 * Ensures a single shared conversation state, bidirectional synchronization,
 * suggestion chips, session persistence, and full history preservation across views.
 */

(function () {
  const STORAGE_KEY = 'creditlens_conversation_history_v1';
  const SESSION_ID_KEY = 'creditlens_chat_session_id';

  // Canonical suggested questions shared across both surfaces
  const SHARED_SUGGESTIONS = [
    { label: 'Default rate by income', query: 'What is the default rate by income type?' },
    { label: 'Which occupations are riskiest?', query: 'Which occupations are riskiest?' },
    { label: 'External score < 0.3', query: 'Show applicants with external score below 0.3' },
    { label: 'Credit leverage impact', query: 'How does high credit leverage affect default risk?' },
    { label: 'Credit vs annuity by contract', query: 'What is the distribution of credit versus annuity amounts across contract types?' }
  ];

  function getSessionId() {
    let sid = sessionStorage.getItem(SESSION_ID_KEY);
    if (!sid) {
      sid = 'sess_' + Math.random().toString(36).substring(2, 10) + '_' + Date.now();
      sessionStorage.setItem(SESSION_ID_KEY, sid);
    }
    return sid;
  }

  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function formatInsight(text) {
    if (!text) return '';
    return escapeHtml(text).replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  }

  window.copySqlSnippet = function (btn, sqlText) {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(sqlText).then(function () {
        const orig = btn.innerText;
        btn.innerText = 'COPIED!';
        btn.style.color = '#10b981';
        setTimeout(function () {
          btn.innerText = orig;
          btn.style.color = '';
        }, 1600);
      });
    }
  };

  function buildResultChartConfig(msgId, res) {
    if (!res || !res.rows || res.rows.length < 2 || !res.columns || res.columns.length < 2) {
      return null;
    }
    // 1. Identify label column (first text/categorical column)
    let labelCol = null;
    for (const c of res.columns) {
      const isText = res.rows.some(r => typeof r[c] === 'string' && isNaN(Number(r[c])));
      if (isText) {
        labelCol = c;
        break;
      }
    }
    if (!labelCol) labelCol = res.columns[0];

    // 2. Identify primary metric column (numeric)
    let valCol = null;
    const priorities = ['default_rate', 'pct', 'rate', 'avg', 'amount', 'credit', 'total', 'count'];
    for (const p of priorities) {
      const found = res.columns.find(c => c !== labelCol && c.toLowerCase().includes(p));
      if (found) {
        valCol = found;
        break;
      }
    }
    if (!valCol) {
      for (let i = res.columns.length - 1; i >= 0; i--) {
        const c = res.columns[i];
        if (c !== labelCol && res.rows.some(r => !isNaN(parseFloat(r[c])))) {
          valCol = c;
          break;
        }
      }
    }
    if (!valCol) return null;

    const rows = res.rows.slice(0, 10);
    const labels = rows.map(r => String(r[labelCol] != null ? r[labelCol] : 'N/A'));
    const values = rows.map(r => parseFloat(r[valCol]) || 0);
    const canvasId = `talk-chart-${msgId}`;
    const isRate = valCol.toLowerCase().includes('rate') || valCol.toLowerCase().includes('pct');

    return {
      canvasId: canvasId,
      labelCol: labelCol,
      valCol: valCol,
      labels: labels,
      values: values,
      isRate: isRate,
      html: `
        <div class="talk-chart-wrap" style="margin: 14px 0; background: var(--card, #ffffff); border: 1px solid var(--line-strong, rgba(18,32,26,0.12)); border-radius: 4px; padding: 14px 18px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid var(--line, rgba(18,32,26,0.06)); padding-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--green, #5fa83d);"></span>
              <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: var(--navy); text-transform: uppercase;">
                Interactive Auto-Chart: ${escapeHtml(valCol.replace(/_/g, ' ').toUpperCase())}
              </span>
            </div>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 10.5px; color: var(--ink-dim);">
              BY ${escapeHtml(labelCol.replace(/_/g, ' ').toUpperCase())}
            </span>
          </div>
          <div style="position: relative; height: 210px; width: 100%;">
            <canvas id="${canvasId}"></canvas>
          </div>
        </div>
      `
    };
  }

  function renderChartConfigs(configs) {
    if (!window.Chart || !configs || configs.length === 0) return;
    setTimeout(() => {
      configs.forEach(cfg => {
        const canvas = document.getElementById(cfg.canvasId);
        if (!canvas) return;
        if (canvas._chartInstance) canvas._chartInstance.destroy();

        const colors = cfg.values.map(v => {
          if (cfg.isRate) {
            if (v > 20) return 'rgba(184, 92, 62, 0.85)';
            if (v > 8) return 'rgba(217, 154, 60, 0.85)';
            return 'rgba(95, 168, 61, 0.85)';
          }
          return 'rgba(95, 168, 61, 0.85)';
        });

        const borderColors = cfg.values.map(v => {
          if (cfg.isRate) {
            if (v > 20) return '#b85c3e';
            if (v > 8) return '#d99a3c';
            return '#5fa83d';
          }
          return '#3c7a26';
        });

        canvas._chartInstance = new Chart(canvas, {
          type: 'bar',
          data: {
            labels: cfg.labels,
            datasets: [{
              label: cfg.valCol.replace(/_/g, ' ').toUpperCase(),
              data: cfg.values,
              backgroundColor: colors,
              borderColor: borderColors,
              borderWidth: 1,
              borderRadius: 4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                callbacks: {
                  label: function(ctx) {
                    return ' ' + ctx.dataset.label + ': ' + ctx.parsed.y + (cfg.isRate ? '%' : '');
                  }
                }
              }
            },
            scales: {
              x: {
                grid: { display: false },
                ticks: {
                  font: { family: "'JetBrains Mono', monospace", size: 10 },
                  color: '#5c6b63',
                  maxRotation: 30,
                  minRotation: 0
                }
              },
              y: {
                grid: { color: 'rgba(18,32,26,0.06)' },
                ticks: {
                  font: { family: "'JetBrains Mono', monospace", size: 10 },
                  color: '#5c6b63',
                  callback: function(v) {
                    return v + (cfg.isRate ? '%' : '');
                  }
                }
              }
            }
          }
        });
      });
    }, 60);
  }

  const ChatStore = {
    messages: [],
    isSubmitting: false,
    sessionId: getSessionId(),
    suggestions: SHARED_SUGGESTIONS,

    init() {
      // 1. Load persisted messages
      try {
        const saved = sessionStorage.getItem(STORAGE_KEY);
        if (saved) {
          this.messages = JSON.parse(saved);
        } else {
          this.messages = [];
        }
      } catch (err) {
        console.warn('Failed to load chat history from storage:', err);
        this.messages = [];
      }

      // 2. Fetch server samples if available to keep suggestions synchronized
      if (window.api && typeof api.getChatSamples === 'function') {
        api.getChatSamples().then(data => {
          if (data && data.samples && data.samples.length > 0) {
            this.suggestions = data.samples.map(s => {
              const short = s.length > 32 ? s.substring(0, 30) + '...' : s;
              return { label: short, query: s };
            });
            this.renderMainSuggestionsBar();
            // Re-render floating greeting pills if no user message yet
            if (this.messages.length === 0) {
              this.renderFloatingWidget();
            }
          }
        }).catch(err => {
          console.warn('Could not refresh chat samples:', err);
        });
      }

      // 3. Render both surfaces
      this.renderBoth();
      this.renderMainSuggestionsBar();
    },

    save() {
      try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(this.messages));
      } catch (err) {
        console.warn('Failed to save chat history:', err);
      }
    },

    renderBoth() {
      this.renderMainPage();
      this.renderFloatingWidget();
    },

    renderMainSuggestionsBar() {
      const bar = document.getElementById('talk-suggestions-chips');
      if (!bar) return;
      bar.innerHTML = this.suggestions.map(item => `
        <button type="button" class="talk-chip" onclick="window.ChatStore.submitQuestion('${escapeHtml(item.query).replace(/'/g, "\\'")}')">${escapeHtml(item.label)}</button>
      `).join('');
    },

    renderMainPage() {
      const stream = document.getElementById('talk-chat-stream');
      if (!stream) return;

      const welcomeHtml = `
        <div class="talk-msg-bot">
          <div class="talk-msg-bot-head">
            <div class="talk-msg-bot-agent">
              <div class="talk-msg-bot-avatar">C</div>
              <div>
                <div class="talk-msg-bot-name">CreditLens Portfolio Analyst</div>
                <div style="font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--green-dark);">Connected to Home Credit Portfolio DB (307k records)</div>
              </div>
            </div>
            <span class="talk-msg-bot-tag">SYSTEM READY</span>
          </div>
          <div style="font-size: 13.5px; line-height: 1.6; color: var(--navy);">
            Hello! I am your AI credit portfolio analyst. You can ask any question about applicant demographics, default rates, loan types, or external credit bureau scores in plain English. I will translate your question into SQL, query the live database, and summarize the key findings.
          </div>
          <div style="margin-top: 12px; font-size: 12px; color: var(--ink-dim);">
            Click any of the suggested prompts below to explore, or type your own question in the input bar.
          </div>
        </div>
      `;

      if (this.messages.length === 0) {
        stream.innerHTML = welcomeHtml;
        return;
      }

      let html = welcomeHtml;
      const chartConfigs = [];

      this.messages.forEach(msg => {
        if (msg.role === 'user') {
          html += `
            <div class="talk-msg-user">
              <div class="talk-msg-user-meta">
                <span>YOU ASKED</span>
                <span>${escapeHtml(msg.timestamp)}</span>
              </div>
              <div class="talk-msg-user-text">${escapeHtml(msg.text)}</div>
            </div>
          `;
        } else if (msg.role === 'assistant') {
          if (msg.loading) {
            html += `
              <div class="talk-msg-bot">
                <div class="talk-msg-bot-head">
                  <div class="talk-msg-bot-agent">
                    <div class="talk-msg-bot-avatar">C</div>
                    <div>
                      <div class="talk-msg-bot-name">CreditLens Portfolio Analyst</div>
                      <div style="font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--green-dark);">Connected to Home Credit Portfolio DB</div>
                    </div>
                  </div>
                  <span class="talk-msg-bot-tag">QUERYING...</span>
                </div>
                <div class="talk-loading-indicator" style="display:flex; align-items:center; gap:10px; padding:12px 0; color:var(--ink-dim); font-size:13px;">
                  <div class="talk-loading-spinner" style="width:16px; height:16px; border:2px solid var(--green); border-top-color:transparent; border-radius:50%; animation:spin 0.8s linear infinite;"></div>
                  <span>Synthesizing SQL &amp; scanning 307k portfolio records...</span>
                </div>
              </div>
            `;
          } else if (msg.data && msg.data.success) {
            const res = msg.data;
            let chartHtml = '';
            const chartCfg = buildResultChartConfig(msg.id, res);
            if (chartCfg) {
              chartConfigs.push(chartCfg);
              chartHtml = chartCfg.html;
            }

            let tableHtml = '';
            if (res.rows && res.rows.length > 0 && res.columns && res.columns.length > 0) {
              const headerCols = res.columns.map(c => `<th>${escapeHtml(c.replace(/_/g, ' ').toUpperCase())}</th>`).join('');
              const bodyRows = res.rows.slice(0, 10).map(row => {
                const cells = res.columns.map(c => {
                  const val = row[c];
                  const isNum = typeof val === 'number' || (!isNaN(parseFloat(val)) && isFinite(val) && val !== '');
                  return `<td style="${isNum ? "text-align:right; font-family:'JetBrains Mono',monospace;" : ''}">${escapeHtml(val == null ? 'NULL' : String(val))}</td>`;
                }).join('');
                return `<tr>${cells}</tr>`;
              }).join('');

              tableHtml = `
                <div class="talk-table-wrap">
                  <table class="talk-data-table">
                    <thead><tr>${headerCols}</tr></thead>
                    <tbody>${bodyRows}</tbody>
                  </table>
                </div>
                ${res.rows.length > 10 ? `<div style="font-family:'JetBrains Mono',monospace; font-size:10.5px; color:var(--ink-dim); margin-top:6px;">Showing top 10 of ${res.rows.length} records returned</div>` : ''}
              `;
            }

            const escapedSql = escapeHtml(res.sql || '-- No SQL generated');
            const safeSqlForAttr = (res.sql || '').replace(/\\/g, '\\\\').replace(/`/g, '\\`').replace(/\$/g, '\\$');
            const formattedInsight = formatInsight(res.insight || '');

            let followUpsHtml = '';
            if (res.suggested_questions && res.suggested_questions.length > 0) {
              followUpsHtml = `
                <div style="margin-top: 14px; border-top: 1px solid var(--border-subtle, #e2e8f0); padding-top: 10px;">
                  <div style="font-size: 11px; font-weight: 700; color: var(--ink-dim); text-transform: uppercase; margin-bottom: 6px; font-family: 'JetBrains Mono', monospace;">Follow-up exploration</div>
                  <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                    ${res.suggested_questions.map(q => `
                      <button type="button" class="talk-chip" onclick="window.ChatStore.submitQuestion('${escapeHtml(q).replace(/'/g, "\\'")}')">${escapeHtml(q)}</button>
                    `).join('')}
                  </div>
                </div>
              `;
            }

            html += `
              <div class="talk-msg-bot">
                <div class="talk-msg-bot-head">
                  <div class="talk-msg-bot-agent">
                    <div class="talk-msg-bot-avatar">N</div>
                    <div>
                      <div class="talk-msg-bot-name">NeoStats Portfolio Analyst</div>
                      <div style="font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--green-dark);">SQLite Portfolio · Verified Query</div>
                    </div>
                  </div>
                  <span class="talk-msg-bot-tag">${res.row_count !== undefined ? res.row_count + ' ROWS' : 'COMPLETE'}</span>
                </div>

                ${res.insight ? `
                  <div class="talk-insight-card">
                    <div class="talk-insight-title">Executive Takeaway</div>
                    <div class="talk-insight-body">${formattedInsight}</div>
                  </div>
                ` : ''}

                <div class="talk-sql-box">
                  <div class="talk-sql-header">
                    <span>GENERATED SQL</span>
                    <button type="button" class="talk-copy-btn" onclick="copySqlSnippet(this, \`${safeSqlForAttr}\`)">COPY SQL</button>
                  </div>
                  <pre class="talk-sql-code"><code>${escapedSql}</code></pre>
                </div>

                ${chartHtml}
                ${tableHtml}
                ${followUpsHtml}
              </div>
            `;
          } else {
            // Bot Error Response
            const errText = (msg.data && msg.data.error) || 'The system could not parse the natural language query into valid SQL.';
            const attemptedSql = msg.data && msg.data.sql;
            html += `
              <div class="talk-msg-bot">
                <div class="talk-msg-bot-head">
                  <div class="talk-msg-bot-agent">
                    <div class="talk-msg-bot-avatar" style="background:#8b2b2b;">!</div>
                    <div>
                      <div class="talk-msg-bot-name">NeoStats Portfolio Analyst</div>
                      <div style="font-family:'JetBrains Mono',monospace; font-size:10px; color:#c94a4a;">Query Execution Warning</div>
                    </div>
                  </div>
                  <span class="talk-msg-bot-tag" style="background:#ffeded; color:#a12626;">ERROR</span>
                </div>
                <div style="color: #922B21; font-size: 13px; line-height: 1.5; padding: 10px 14px; background: #FDEDEC; border-radius: 4px; border: 1px solid #F5B7B1;">
                  <strong>Unable to complete request:</strong> ${escapeHtml(errText)}
                </div>
                ${attemptedSql ? `
                  <div class="talk-sql-box" style="margin-top:12px;">
                    <div class="talk-sql-header"><span>ATTEMPTED SQL</span></div>
                    <pre class="talk-sql-code"><code>${escapeHtml(attemptedSql)}</code></pre>
                  </div>
                ` : ''}
              </div>
            `;
          }
        }
      });

      stream.innerHTML = html;
      renderChartConfigs(chartConfigs);
      stream.scrollTo({ top: stream.scrollHeight, behavior: 'smooth' });
    },

    renderFloatingWidget() {
      const body = document.getElementById('f-chat-body');
      if (!body) return;

      const hasUserMessages = this.messages.some(m => m.role === 'user');

      // Suggested question chips for floating widget
      let pillsHtml = '';
      if (!hasUserMessages) {
        pillsHtml = `
          <div class="f-quick-pills" id="f-chat-welcome-pills" style="margin-top:10px; display:flex; flex-wrap:wrap; gap:6px;">
            <div style="font-size:11px; font-weight:700; color:#5fa83d; font-family:'JetBrains Mono',monospace; width:100%; margin-bottom:2px; text-transform:uppercase; letter-spacing:0.04em;">Suggested questions</div>
            ${this.suggestions.slice(0, 4).map(item => `
              <button type="button" class="f-pill" onclick="window.ChatStore.submitQuestion('${escapeHtml(item.query).replace(/'/g, "\\'")}')">${escapeHtml(item.label)}</button>
            `).join('')}
          </div>
        `;
      }

      const welcomeGreetingHtml = `
        <div class="f-msg bot">
          <div class="bubble">
            Hello! I am <b>CreditLens AI</b>, your Credit Risk Data Analyst. Ask me anything about portfolio default rates across cohorts, bureau debt volumes, or applicant demographics.
            ${pillsHtml}
          </div>
          <div class="f-msg-time">Just now</div>
        </div>
      `;

      if (this.messages.length === 0) {
        body.innerHTML = welcomeGreetingHtml;
        return;
      }

      let html = welcomeGreetingHtml;

      this.messages.forEach(msg => {
        if (msg.role === 'user') {
          html += `
            <div class="f-msg user">
              <div class="bubble">${escapeHtml(msg.text)}</div>
              <span class="f-msg-time">${escapeHtml(msg.timestamp)}</span>
            </div>
          `;
        } else if (msg.role === 'assistant') {
          if (msg.loading) {
            html += `
              <div class="f-msg bot">
                <div class="bubble">
                  <div style="display:flex; align-items:center; gap:8px; color:var(--ink-dim, #64748b);">
                    <span class="spinner" style="width:14px; height:14px; border:2px solid #5fa83d; border-top-color:transparent; border-radius:50%; animation:spin 0.8s linear infinite;"></span>
                    <span style="font-size:12.5px;">CreditLens AI is querying portfolio records via Groq LLM...</span>
                  </div>
                </div>
                <span class="f-msg-time">${escapeHtml(msg.timestamp)}</span>
              </div>
            `;
          } else if (msg.data && msg.data.success) {
            const res = msg.data;
            let bubbleContent = '';

            // 1. Digestible Executive Takeaway Card
            if (res.insight) {
              bubbleContent += `
                <div class="f-card-summary" style="background:rgba(16,185,129,0.08); border-left:3px solid #10b981; padding:8px 12px; border-radius:0 6px 6px 0; margin-bottom:8px; font-size:12.5px; line-height:1.5;">
                  <b style="color:#10b981; font-size:11px; text-transform:uppercase; letter-spacing:0.04em; display:block; margin-bottom:3px;">Key Takeaway</b>
                  ${formatInsight(res.insight)}
                </div>
              `;
            }

            // 2. Expandable SQL Details
            if (res.sql) {
              bubbleContent += `
                <details class="f-sql-details" style="margin:6px 0; font-size:12px;">
                  <summary style="cursor:pointer; color:#3b82f6; font-weight:600; user-select:none;">View Generated SQL</summary>
                  <pre class="f-sql-pre" style="margin-top:6px; padding:8px 10px; background:#f1f5f9; border-radius:4px; font-family:'JetBrains Mono',monospace; font-size:11px; overflow-x:auto; white-space:pre-wrap; border:1px solid #e2e8f0;"><code>${escapeHtml(res.sql)}</code></pre>
                </details>
              `;
            }

            // 3. Compact Result Table (top 6 rows)
            if (res.rows && res.rows.length > 0 && res.columns) {
              bubbleContent += `
                <div style="font-size:11px; color:var(--ink-dim, #64748b); margin-top:6px; font-weight:600; text-transform:uppercase;">
                  Returned Data (${res.row_count} rows):
                </div>
                <div class="f-table-wrap" style="overflow-x:auto; margin-top:4px; border:1px solid #e2e8f0; border-radius:4px;">
                  <table class="data-table" style="font-size:11px; width:100%; border-collapse:collapse;">
                    <thead>
                      <tr style="background:#f8fafc; border-bottom:1px solid #e2e8f0;">
                        ${res.columns.slice(0, 4).map(c => `<th style="padding:4px 8px; text-align:left;">${escapeHtml(c)}</th>`).join('')}
                      </tr>
                    </thead>
                    <tbody>
                      ${res.rows.slice(0, 6).map(r => `
                        <tr style="border-bottom:1px solid #f1f5f9;">
                          ${res.columns.slice(0, 4).map(c => `<td style="padding:4px 8px;">${escapeHtml(String(r[c] !== null ? r[c] : ''))}</td>`).join('')}
                        </tr>
                      `).join('')}
                    </tbody>
                  </table>
                </div>
              `;
            }

            // 4. Follow-up quick prompt pills
            if (res.suggested_questions && res.suggested_questions.length > 0) {
              bubbleContent += `
                <div style="margin-top:10px; border-top:1px solid #f1f5f9; padding-top:6px;">
                  <div style="font-size:10.5px; color:var(--ink-dim, #64748b); font-weight:700; text-transform:uppercase; margin-bottom:4px;">Follow-up questions</div>
                  <div class="f-quick-pills" style="display:flex; flex-wrap:wrap; gap:5px;">
                    ${res.suggested_questions.slice(0, 3).map(sq => `
                      <button type="button" class="f-pill" onclick="window.ChatStore.submitQuestion('${escapeHtml(sq).replace(/'/g, "\\'")}')">${escapeHtml(sq)}</button>
                    `).join('')}
                  </div>
                </div>
              `;
            }

            html += `
              <div class="f-msg bot">
                <div class="bubble">${bubbleContent}</div>
                <span class="f-msg-time">${escapeHtml(msg.timestamp)}</span>
              </div>
            `;
          } else {
            // Error in floating widget
            const errText = (msg.data && msg.data.error) || 'SQL safety check or model execution issue.';
            html += `
              <div class="f-msg bot">
                <div class="bubble" style="border-left:3px solid #ef4444; background:#fef2f2;">
                  <div style="color:#b91c1c; font-size:12px; font-weight:600;">Unable to complete query</div>
                  <div style="color:#7f1d1d; font-size:12px; margin-top:2px;">${escapeHtml(errText)}</div>
                </div>
                <span class="f-msg-time">${escapeHtml(msg.timestamp)}</span>
              </div>
            `;
          }
        }
      });

      body.innerHTML = html;
      body.scrollTop = body.scrollHeight;
    },

    async submitQuestion(question) {
      if (!question || !question.trim()) return;
      if (this.isSubmitting) return;

      const q = question.trim();
      this.isSubmitting = true;

      // Update UI input fields & buttons
      const talkInput = document.getElementById('talk-chat-input');
      if (talkInput) talkInput.value = '';
      const fInput = document.getElementById('f-chat-input');
      if (fInput) fInput.value = '';

      const talkBtn = document.getElementById('talk-chat-send-btn');
      if (talkBtn) {
        talkBtn.disabled = true;
        talkBtn.style.opacity = '0.6';
      }
      const fBtn = document.getElementById('f-chat-send');
      if (fBtn) fBtn.disabled = true;

      const timeNow = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const userMsgId = 'usr_' + Date.now();
      const botMsgId = 'bot_' + Date.now();

      // 1. Add User Message
      this.messages.push({
        id: userMsgId,
        role: 'user',
        text: q,
        timestamp: timeNow,
        loading: false,
        data: null
      });

      // 2. Add Assistant Loading Placeholder
      this.messages.push({
        id: botMsgId,
        role: 'assistant',
        text: '',
        timestamp: timeNow,
        loading: true,
        data: null
      });

      this.save();
      this.renderBoth();

      try {
        const res = await api.sendChatMessage(q, this.sessionId);
        
        // Find assistant loading bubble and update
        const botMsg = this.messages.find(m => m.id === botMsgId);
        if (botMsg) {
          botMsg.loading = false;
          botMsg.data = res;
          botMsg.timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
      } catch (err) {
        const botMsg = this.messages.find(m => m.id === botMsgId);
        if (botMsg) {
          botMsg.loading = false;
          botMsg.data = {
            success: false,
            error: err.message || 'Connection error with the NeoStats backend.',
            sql: null
          };
          botMsg.timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
      } finally {
        this.isSubmitting = false;
        if (talkBtn) {
          talkBtn.disabled = false;
          talkBtn.style.opacity = '1';
        }
        if (fBtn) fBtn.disabled = false;

        this.save();
        this.renderBoth();
      }
    },

    async clearChat() {
      this.messages = [];
      this.save();
      this.renderBoth();

      if (window.api && typeof api.clearChat === 'function') {
        try {
          await api.clearChat(this.sessionId);
        } catch (err) {
          console.warn('Backend chat clear notice:', err);
        }
      }
    }
  };

  // Expose globally
  window.ChatStore = ChatStore;
  window.submitTalkQuestion = function (q) {
    ChatStore.submitQuestion(q);
  };
  window.sendFloatingQuery = function (q) {
    ChatStore.submitQuestion(q);
  };

  // Auto-init on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ChatStore.init());
  } else {
    ChatStore.init();
  }
})();
