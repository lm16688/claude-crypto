# 🔥 Crypto Pulse — 加密货币热点监控

> 实时追踪全网加密货币社区热度、X平台热帖与名人动态

**网站地址：** `https://lm16688.github.io/claude-crypto/`

---

## 功能特色

| 功能 | 说明 |
|------|------|
| **双板块展示** | 主流币 vs Meme 币分类浏览 |
| **社区热度评分** | 综合提及量、互动数、趋势计算 0-100 分 |
| **X平台热帖** | 展示每个币种最高互动的5条推文 |
| **实时行情** | 接入 CoinGecko API 获取价格与市值 |
| **自动更新** | GitHub Actions 每4小时自动采集数据 |
| **全端适配** | 响应式设计，手机/平板/桌面完美适配 |

---

## 快速开始

### 1. Fork 或克隆仓库

```bash
git clone https://github.com/lm16688/claude-crypto.git
cd claude-crypto
```

### 2. 配置 GitHub Secrets

在仓库 **Settings → Secrets and variables → Actions** 中添加以下 Secret：

| Secret 名称 | 来源 | 是否必须 |
|------------|------|---------|
| `TWITTER_BEARER_TOKEN` | [X Developer Portal](https://developer.x.com) | ⭐ 推荐 |
| `COINGECKO_API_KEY` | [CoinGecko API](https://www.coingecko.com/en/api) | 可选（免费版限速） |
| `NEWS_API_KEY` | [NewsAPI.org](https://newsapi.org) | 可选 |
| `ETHERSCAN_API_KEY` | [Etherscan](https://etherscan.io/apis) | 可选（持有者数量） |

> ⚠️ **安全提示**：所有 API Key 必须通过 Secrets 注入，绝不可硬编码在代码中。

### 3. 启用 GitHub Pages

1. 进入仓库 **Settings → Pages**
2. Source 选择 **Deploy from a branch**
3. Branch 选择 `main`，文件夹选择 `/docs`
4. 保存后等待约1分钟，即可通过 `https://lm16688.github.io/claude-crypto/` 访问

### 4. 手动触发数据更新

在 **Actions → Update Crypto Data → Run workflow** 手动运行。

---

## 项目结构

```
claude-crypto/
├── .github/
│   └── workflows/
│       └── update-data.yml   # 定时任务配置（每4小时）
├── scripts/
│   └── collect_data.py       # Python数据采集主脚本
├── docs/                     # GitHub Pages 部署目录
│   ├── index.html            # 主页面
│   ├── data.json             # 自动生成的数据文件
│   └── assets/
│       ├── style.css         # 样式文件
│       └── app.js            # 前端逻辑
└── README.md
```

---

## 数据字段说明

每个币种包含以下数据：

```json
{
  "id": "bitcoin",
  "type": "mainstream",         // mainstream | meme
  "name": "Bitcoin",
  "symbol": "BTC",
  "price": 98500,
  "market_cap": 1950000000000,
  "created_at": "2009年1月",
  "narrative_tags": ["PoW", "数字黄金"],
  "story": "项目背景故事...",
  "heat_score": 95,             // 0-100 社区热度
  "holders": 50000000,          // 持有者数量（如有）
  "mentions_24h": 250000,       // 24小时提及次数
  "trend_24h_pct": 12.5,        // 提及量24h变化%
  "top_posts": [                // X平台热门帖子
    {
      "author": "elonmusk",
      "content": "...",
      "likes": 180000,
      "retweets": 42000,
      "replies": 15000,
      "url": "https://x.com/..."
    }
  ]
}
```

---

## 获取 X API Bearer Token（免费版步骤）

1. 访问 [developer.x.com](https://developer.x.com)
2. 登录后点击 **+ Create Project**
3. 创建 App，进入 **Keys and Tokens** 页面
4. 生成 **Bearer Token**（免费版每月可读取 50万条推文）
5. 复制 Token，添加到 GitHub Secrets 的 `TWITTER_BEARER_TOKEN`

---

## 本地运行（开发调试）

```bash
# 安装依赖
pip install requests python-dotenv

# 创建 .env 文件（本地测试用）
echo "TWITTER_BEARER_TOKEN=your_token_here" > .env
echo "COINGECKO_API_KEY=your_key_here" >> .env

# 运行采集脚本
python scripts/collect_data.py

# 在浏览器打开 docs/index.html 查看效果
```

---

## 注意事项

- 本站数据仅供参考，**不构成任何投资建议**
- 数据采集遵守各平台 robots.txt 及服务条款
- X API 免费版每月限 50万条推文读取，请合理分配
- CoinGecko 免费版有速率限制，建议申请 Pro API Key

---

*Made with ❤️ by Crypto Pulse · Powered by GitHub Actions & GitHub Pages*
