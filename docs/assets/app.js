/* ============================================================
   CRYPTO PULSE — Frontend App
   ============================================================ */

const DATA_URL = './data.json';

// ─── State ───────────────────────────────────────────────────
let state = {
  allCoins: [],
  currentTab: 'mainstream',
  searchQuery: '',
  sortBy: 'heat',
};

// ─── Tag color mapping ────────────────────────────────────────
const TAG_COLORS = {
  'Layer 2': 'blue', 'DeFi': 'green', 'AI': 'blue',
  'DePIN': 'yellow', 'NFT': 'yellow', 'GameFi': 'blue',
  'PoW': 'yellow', 'ETH生态': 'blue', '支付': 'green',
  '动物币': 'red', 'Meme': 'red', '名人背书': 'yellow',
  '社区驱动': 'green', '文化币': 'red', 'OG': 'yellow',
  'Layer 1': 'green', 'Staking': 'blue', 'Privacy': 'yellow',
};

function getTagClass(tag) {
  return 'tag-' + (TAG_COLORS[tag] || 'green');
}

// ─── Format helpers ───────────────────────────────────────────
function fmtMarketCap(n) {
  if (!n || n === '暂无') return '暂无';
  if (n >= 1e12) return '$' + (n / 1e12).toFixed(2) + 'T';
  if (n >= 1e9)  return '$' + (n / 1e9).toFixed(2) + 'B';
  if (n >= 1e6)  return '$' + (n / 1e6).toFixed(2) + 'M';
  return '$' + n.toLocaleString();
}

function fmtHolders(n) {
  if (!n || n === '暂无') return '暂无';
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K';
  return n.toString();
}

function fmtTrend(pct) {
  if (pct === null || pct === undefined || pct === '暂无') return { text: '暂无', cls: '' };
  const num = parseFloat(pct);
  if (isNaN(num)) return { text: '暂无', cls: '' };
  const sign = num >= 0 ? '+' : '';
  return { text: sign + num.toFixed(1) + '%', cls: num >= 0 ? 'up' : 'down' };
}

function fmtPrice(p) {
  if (!p || p === '暂无') return '暂无';
  const n = parseFloat(p);
  if (isNaN(n)) return '暂无';
  if (n >= 1) return '$' + n.toLocaleString(undefined, { maximumFractionDigits: 2 });
  return '$' + n.toFixed(6);
}

function timeAgo(ts) {
  if (!ts) return '--';
  const d = new Date(ts);
  const diff = Date.now() - d.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return mins + ' 分钟前';
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return hrs + ' 小时前';
  return Math.floor(hrs / 24) + ' 天前';
}

// ─── Render coin card ─────────────────────────────────────────
function renderCard(coin, idx) {
  const trend = fmtTrend(coin.trend_24h_pct);
  const heatWidth = Math.min(100, Math.round((coin.heat_score || 0)));
  const tags = (coin.narrative_tags || []).slice(0, 3);
  const topPost = (coin.top_posts || [])[0];

  const iconHTML = coin.image_url
    ? `<img src="${escHtml(coin.image_url)}" alt="${escHtml(coin.name)}" />`
    : coin.emoji || '🪙';

  const tagsHTML = tags.map(t =>
    `<span class="tag ${getTagClass(t)}">${escHtml(t)}</span>`
  ).join('');

  const postHTML = topPost
    ? `<div class="top-post-preview">${escHtml(topPost.content || '')}</div>
       <div class="top-post-meta">
         <span class="x-icon">𝕏</span>
         <span>@${escHtml(topPost.author || 'unknown')}</span>
         <span>❤ ${fmtNum(topPost.likes)}</span>
         <span>🔁 ${fmtNum(topPost.retweets)}</span>
       </div>`
    : `<div class="top-post-preview" style="color:var(--text-muted)">暂无热门推文数据</div>`;

  return `
<div class="coin-card" data-id="${escHtml(coin.id)}" style="animation-delay:${idx * 0.04}s">
  <div class="card-header">
    <div class="coin-identity">
      <div class="coin-icon">${iconHTML}</div>
      <div class="coin-name-block">
        <div class="coin-name">${escHtml(coin.name)}</div>
        <div class="coin-symbol">${escHtml(coin.symbol)}</div>
      </div>
    </div>
    <div class="coin-trend">
      <div class="trend-pct ${trend.cls}">${trend.text}</div>
      <div class="trend-label">24h提及变化</div>
    </div>
  </div>

  <div class="narrative-tags">${tagsHTML}</div>

  <p class="coin-story">${escHtml(coin.story || '暂无项目描述')}</p>

  <div class="stats-row">
    <div class="stat-item">
      <div class="stat-label">市值</div>
      <div class="stat-value">${fmtMarketCap(coin.market_cap)}</div>
    </div>
    <div class="stat-item">
      <div class="stat-label">价格</div>
      <div class="stat-value">${fmtPrice(coin.price)}</div>
    </div>
    <div class="stat-item">
      <div class="stat-label">持有者</div>
      <div class="stat-value">${fmtHolders(coin.holders)}</div>
    </div>
  </div>

  <div class="heat-row">
    <span class="heat-label">社区热度</span>
    <div class="heat-bar-bg">
      <div class="heat-bar-fill" style="width:${heatWidth}%"></div>
    </div>
    <span class="heat-value">${heatWidth}</span>
  </div>

  ${postHTML}
</div>`;
}

// ─── Render modal detail ──────────────────────────────────────
function renderModal(coin) {
  const trend = fmtTrend(coin.trend_24h_pct);
  const iconHTML = coin.image_url
    ? `<img src="${escHtml(coin.image_url)}" alt="${escHtml(coin.name)}" />`
    : coin.emoji || '🪙';
  const tags = (coin.narrative_tags || []).map(t =>
    `<span class="tag ${getTagClass(t)}">${escHtml(t)}</span>`
  ).join('');

  const postsHTML = (coin.top_posts || []).length
    ? coin.top_posts.slice(0, 5).map(p => `
        <div class="post-item">
          <div class="post-author">@${escHtml(p.author || 'unknown')}</div>
          <div class="post-content">${escHtml(p.content || '')}</div>
          <div class="post-stats">
            <span>❤ ${fmtNum(p.likes)}</span>
            <span>🔁 ${fmtNum(p.retweets)}</span>
            <span>💬 ${fmtNum(p.replies)}</span>
            ${p.url ? `<a href="${escHtml(p.url)}" target="_blank" rel="noopener" class="post-link">查看原文 →</a>` : ''}
          </div>
        </div>`).join('')
    : '<p style="color:var(--text-muted);font-family:var(--font-mono);font-size:13px">暂无帖子数据</p>';

  return `
<div class="modal-coin-header">
  <div class="modal-coin-icon">${iconHTML}</div>
  <div>
    <div class="modal-coin-name">${escHtml(coin.name)}</div>
    <div class="modal-coin-symbol">${escHtml(coin.symbol)} &nbsp;·&nbsp; 创建于 ${escHtml(coin.created_at || '未知')}</div>
    <div style="margin-top:8px">${tags}</div>
  </div>
</div>

<div class="modal-section">
  <div class="modal-section-title">核心数据</div>
  <div class="modal-stats">
    <div class="modal-stat">
      <div class="modal-stat-label">市值</div>
      <div class="modal-stat-value">${fmtMarketCap(coin.market_cap)}</div>
    </div>
    <div class="modal-stat">
      <div class="modal-stat-label">当前价格</div>
      <div class="modal-stat-value">${fmtPrice(coin.price)}</div>
    </div>
    <div class="modal-stat">
      <div class="modal-stat-label">持有者数量</div>
      <div class="modal-stat-value">${fmtHolders(coin.holders)}</div>
    </div>
    <div class="modal-stat">
      <div class="modal-stat-label">24h 提及趋势</div>
      <div class="modal-stat-value" style="color:var(--${trend.cls === 'up' ? 'accent' : (trend.cls === 'down' ? 'red' : 'text-primary')})">${trend.text}</div>
    </div>
    <div class="modal-stat">
      <div class="modal-stat-label">社区热度</div>
      <div class="modal-stat-value">${coin.heat_score || '--'} / 100</div>
    </div>
    <div class="modal-stat">
      <div class="modal-stat-label">24h 提及次数</div>
      <div class="modal-stat-value">${fmtNum(coin.mentions_24h)}</div>
    </div>
  </div>
</div>

<div class="modal-section">
  <div class="modal-section-title">项目故事</div>
  <div class="story-block">${escHtml(coin.story || '暂无项目描述')}</div>
</div>

<div class="modal-section">
  <div class="modal-section-title">X 平台热门帖子</div>
  <div class="posts-list">${postsHTML}</div>
</div>`;
}

// ─── Filter & Sort ────────────────────────────────────────────
function getVisibleCoins() {
  let coins = state.allCoins.filter(c => c.type === state.currentTab);

  if (state.searchQuery) {
    const q = state.searchQuery.toLowerCase();
    coins = coins.filter(c =>
      (c.name || '').toLowerCase().includes(q) ||
      (c.symbol || '').toLowerCase().includes(q) ||
      (c.story || '').toLowerCase().includes(q)
    );
  }

  coins.sort((a, b) => {
    if (state.sortBy === 'heat') return (b.heat_score || 0) - (a.heat_score || 0);
    if (state.sortBy === 'market_cap') return (b.market_cap || 0) - (a.market_cap || 0);
    if (state.sortBy === 'trend') return (parseFloat(b.trend_24h_pct) || 0) - (parseFloat(a.trend_24h_pct) || 0);
    return 0;
  });

  return coins;
}

// ─── Render grid ──────────────────────────────────────────────
function renderGrid() {
  const grid = document.getElementById('coin-grid');
  const coins = getVisibleCoins();

  if (coins.length === 0) {
    grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:60px 0;color:var(--text-muted);font-family:var(--font-mono)">
      <div style="font-size:32px;margin-bottom:12px">⬡</div>
      <div>未找到相关币种</div>
    </div>`;
    return;
  }

  grid.innerHTML = coins.map((c, i) => renderCard(c, i)).join('');

  // Attach click events
  grid.querySelectorAll('.coin-card').forEach(card => {
    card.addEventListener('click', () => {
      const id = card.dataset.id;
      const coin = state.allCoins.find(c => c.id === id);
      if (coin) openModal(coin);
    });
  });
}

// ─── Modal ────────────────────────────────────────────────────
function openModal(coin) {
  document.getElementById('modal-content').innerHTML = renderModal(coin);
  document.getElementById('modal-overlay').classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('modal-overlay').classList.add('hidden');
  document.body.style.overflow = '';
}

// ─── Tab switch ───────────────────────────────────────────────
function switchTab(tab) {
  state.currentTab = tab;
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tab);
  });
  renderGrid();
}

// ─── Update counts ────────────────────────────────────────────
function updateCounts(coins) {
  document.getElementById('mainstream-count').textContent =
    coins.filter(c => c.type === 'mainstream').length;
  document.getElementById('meme-count').textContent =
    coins.filter(c => c.type === 'meme').length;
}

// ─── Load data ────────────────────────────────────────────────
async function loadData() {
  const loadingEl = document.getElementById('loading-state');
  const errorEl   = document.getElementById('error-state');
  const gridEl    = document.getElementById('coin-grid');

  loadingEl.classList.remove('hidden');
  errorEl.classList.add('hidden');
  gridEl.classList.add('hidden');

  try {
    // Add cache-busting query param
    const res = await fetch(DATA_URL + '?t=' + Date.now());
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();

    state.allCoins = data.coins || [];

    // Update timestamp
    if (data.updated_at) {
      document.getElementById('last-update').textContent = timeAgo(data.updated_at);
    }

    updateCounts(state.allCoins);
    loadingEl.classList.add('hidden');
    gridEl.classList.remove('hidden');
    renderGrid();
  } catch (err) {
    console.error('Data load failed:', err);
    loadingEl.classList.add('hidden');
    errorEl.classList.remove('hidden');
    document.getElementById('error-msg').textContent =
      '数据加载失败：' + err.message + '。请刷新页面重试。';
  }
}

// ─── Utilities ───────────────────────────────────────────────
function escHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function fmtNum(n) {
  if (!n && n !== 0) return '--';
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K';
  return n.toString();
}

// ─── Event listeners ─────────────────────────────────────────
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => switchTab(btn.dataset.tab));
});

document.getElementById('modal-close').addEventListener('click', closeModal);
document.getElementById('modal-overlay').addEventListener('click', e => {
  if (e.target === e.currentTarget) closeModal();
});

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
});

document.getElementById('search-input').addEventListener('input', e => {
  state.searchQuery = e.target.value.trim();
  renderGrid();
});

document.getElementById('sort-select').addEventListener('change', e => {
  state.sortBy = e.target.value;
  renderGrid();
});

// ─── Init ────────────────────────────────────────────────────
loadData();
// Auto-refresh every 10 minutes
setInterval(loadData, 10 * 60 * 1000);
