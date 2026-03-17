#!/usr/bin/env python3
"""
Crypto Pulse — 数据采集脚本
自动采集加密货币行情、X平台热帖、新闻资讯，生成 data.json

依赖:
  pip install requests python-dotenv

环境变量 (通过 GitHub Secrets 注入):
  COINGECKO_API_KEY    — CoinGecko Pro API Key（免费版可留空，但有速率限制）
  TWITTER_BEARER_TOKEN — X (Twitter) API v2 Bearer Token
  NEWS_API_KEY         — NewsAPI.org API Key
"""

import os
import json
import time
import logging
import datetime
import requests
from typing import Optional

# ─── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
log = logging.getLogger(__name__)

# ─── Config ───────────────────────────────────────────────────
COINGECKO_API_KEY    = os.environ.get('COINGECKO_API_KEY', '')
TWITTER_BEARER_TOKEN = os.environ.get('TWITTER_BEARER_TOKEN', '')
NEWS_API_KEY         = os.environ.get('NEWS_API_KEY', '')

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs', 'data.json')

# 主流币列表（CoinGecko ID）
MAINSTREAM_COINS = [
    'bitcoin', 'ethereum', 'solana', 'binancecoin',
    'ripple', 'cardano', 'avalanche-2', 'chainlink',
]

# Meme 币列表（CoinGecko ID）
MEME_COINS = [
    'dogecoin', 'shiba-inu', 'pepe', 'floki',
    'official-trump', 'bonk', 'dogwifcoin', 'popcat',
]

# 叙事标签映射（关键词 → 标签）
NARRATIVE_MAP = {
    'bitcoin':       ['PoW', '数字黄金', 'OG'],
    'ethereum':      ['Layer 1', 'DeFi', 'ETH生态'],
    'solana':        ['Layer 1', '高性能', 'Meme基地'],
    'binancecoin':   ['Layer 1', 'CEX', 'BNB生态'],
    'ripple':        ['支付', '跨境转账', 'XRP军团'],
    'cardano':       ['Layer 1', '学术驱动', 'PoS'],
    'avalanche-2':   ['Layer 1', 'DeFi', '高速'],
    'chainlink':     ['预言机', 'DeFi基础设施', 'Layer 1'],
    'dogecoin':      ['动物币', '名人背书', 'Meme'],
    'shiba-inu':     ['动物币', 'Meme', 'ETH生态'],
    'pepe':          ['文化币', 'Meme', '社区驱动'],
    'floki':         ['动物币', 'Meme', 'GameFi'],
    'official-trump':['名人背书', '政治Meme', '社区驱动'],
    'bonk':          ['动物币', 'Meme', 'Solana生态'],
    'dogwifcoin':    ['动物币', 'Meme', 'Solana生态'],
    'popcat':        ['文化币', 'Meme', 'Solana生态'],
}

# 项目故事（预设简介，会结合新闻动态追加）
STORY_MAP = {
    'bitcoin':       '中本聪于2009年创建的第一个去中心化数字货币，被称为「数字黄金」。近期机构持续流入，ETF获批带来大量新资金。',
    'ethereum':      '智能合约平台的开创者，DeFi、NFT和Web3的基础设施。Layer 2生态日趋繁荣，近期ETF获批利好持续发酵。',
    'solana':        '以超高速度和低手续费著称的公链，已成为Meme币和NFT的主要战场。政治Meme币爆火带动整个生态热度飙升。',
    'binancecoin':   '币安交易所原生代币，拥有庞大的BNB Chain生态系统。交易所赋能+销毁机制支撑长期价值。',
    'ripple':        '专注跨境支付的区块链项目，与多家银行机构合作。长期法律纠纷获得阶段性胜利，社区信心回升。',
    'cardano':       '由以太坊联创查尔斯·霍斯金森创立的学术驱动公链，采用严格同行评审的研究方法。',
    'avalanche-2':   '高速低延迟的Layer 1公链，以子网架构为特色，支持企业定制化区块链部署。',
    'chainlink':     '去中心化预言机网络龙头，为DeFi协议提供可靠的链外数据接入，几乎所有主流DeFi都依赖其服务。',
    'dogecoin':      '从玩笑硬币到市值百亿的传奇。马斯克多次公开支持，DOGE被视为「人民的货币」，近期政治关联带动热度。',
    'shiba-inu':     '自称「Doge Killer」的以太坊Meme币，坐拥百万持有者社区。Shibarium Layer 2上线拓展应用场景。',
    'pepe':          '基于互联网经典梗图「Pepe the Frog」，靠强大的文化认同野蛮生长，是Meme币史上最成功的案例之一。',
    'floki':         '以马斯克爱犬命名的Meme币，拥有完整的GameFi和元宇宙生态，社区营销极为激进。',
    'official-trump':'特朗普本人官方发行的Meme币，上线即爆炸式增长，作为现任美国总统发行的加密货币引发全球关注。',
    'bonk':          'Solana生态第一Meme币，以空投方式获得早期关注，社区庞大忠实。随Solana生态繁荣持续受益。',
    'dogwifcoin':    '头戴针织帽的柴犬表情包，2024年暴涨百倍的Meme神话。简洁叙事+强大社区推动现象级增长。',
    'popcat':        '来自经典猫咪张嘴表情包，Solana上的文化现象级Meme币，社区氛围轻松活跃。',
}

# 表情符号映射
EMOJI_MAP = {
    'bitcoin': '₿', 'ethereum': '⟠', 'solana': '◎', 'binancecoin': '⬡',
    'ripple': '✦', 'cardano': '∞', 'avalanche-2': '△', 'chainlink': '⬡',
    'dogecoin': '🐕', 'shiba-inu': '🐕', 'pepe': '🐸', 'floki': '🐕',
    'official-trump': '🦅', 'bonk': '🦮', 'dogwifcoin': '🐶', 'popcat': '🐱',
}

# ─── CoinGecko ────────────────────────────────────────────────
def fetch_coingecko(coin_ids: list) -> dict:
    """从 CoinGecko 获取价格、市值等数据"""
    log.info(f'Fetching CoinGecko data for {len(coin_ids)} coins...')
    ids = ','.join(coin_ids)
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    headers = {}
    if COINGECKO_API_KEY:
        headers['x-cg-pro-api-key'] = COINGECKO_API_KEY

    params = {
        'vs_currency': 'usd',
        'ids': ids,
        'order': 'market_cap_desc',
        'per_page': 50,
        'page': 1,
        'sparkline': False,
        'price_change_percentage': '24h',
    }

    result = {}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        resp.raise_for_status()
        for coin in resp.json():
            result[coin['id']] = {
                'price':      coin.get('current_price'),
                'market_cap': coin.get('market_cap'),
                'image_url':  coin.get('image'),
                'symbol':     (coin.get('symbol') or '').upper(),
                'name':       coin.get('name'),
            }
        log.info(f'  Got data for {len(result)} coins from CoinGecko')
    except Exception as e:
        log.error(f'  CoinGecko error: {e}')

    return result


# ─── X (Twitter) API ─────────────────────────────────────────
def fetch_twitter_posts(query: str, max_results: int = 10) -> list:
    """
    使用 X API v2 搜索最近的热门帖子
    需要 Bearer Token（免费版每月 500,000 条推文读取）
    """
    if not TWITTER_BEARER_TOKEN:
        log.warning('  No TWITTER_BEARER_TOKEN, skipping X API')
        return []

    url = 'https://api.twitter.com/2/tweets/search/recent'
    headers = {'Authorization': f'Bearer {TWITTER_BEARER_TOKEN}'}
    params = {
        'query': query + ' -is:retweet lang:en',
        'max_results': min(max_results, 10),
        'sort_order': 'relevancy',
        'tweet.fields': 'public_metrics,author_id,created_at',
        'expansions': 'author_id',
        'user.fields': 'username,public_metrics',
    }

    posts = []
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code == 429:
            log.warning('  Twitter rate limited, skipping')
            return []
        resp.raise_for_status()
        data = resp.json()

        # Build user map
        users = {}
        for u in data.get('includes', {}).get('users', []):
            users[u['id']] = u.get('username', 'unknown')

        for tweet in data.get('data', []):
            metrics = tweet.get('public_metrics', {})
            posts.append({
                'author':   users.get(tweet.get('author_id'), 'unknown'),
                'content':  tweet.get('text', ''),
                'likes':    metrics.get('like_count', 0),
                'retweets': metrics.get('retweet_count', 0),
                'replies':  metrics.get('reply_count', 0),
                'url':      f'https://x.com/i/web/status/{tweet["id"]}',
            })

        # Sort by engagement
        posts.sort(key=lambda p: p['likes'] + p['retweets'] * 2, reverse=True)
        log.info(f'  Got {len(posts)} tweets for query: {query[:40]}')
    except Exception as e:
        log.error(f'  Twitter API error: {e}')

    return posts[:5]


def fetch_kol_mentions(symbol: str) -> list:
    """
    搜索 KOL（高粉丝账号）提及特定币种的推文
    通过关注者数量过滤
    """
    if not TWITTER_BEARER_TOKEN:
        return []

    # 搜索包含币种符号的推文，优先高互动
    query = f'${symbol} OR #{symbol} -is:retweet'
    posts = fetch_twitter_posts(query, max_results=10)
    # 返回互动量最高的帖子
    return posts[:5]


# ─── NewsAPI ──────────────────────────────────────────────────
def fetch_news(coin_name: str) -> str:
    """从 NewsAPI 获取最新新闻摘要，补充故事背景"""
    if not NEWS_API_KEY:
        return ''

    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': coin_name + ' crypto',
        'sortBy': 'publishedAt',
        'pageSize': 3,
        'language': 'en',
        'apiKey': NEWS_API_KEY,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        articles = resp.json().get('articles', [])
        if articles:
            # 返回最新文章的标题作为补充信息
            return articles[0].get('title', '')
    except Exception as e:
        log.error(f'  NewsAPI error for {coin_name}: {e}')

    return ''


# ─── Heat Score ───────────────────────────────────────────────
def calc_heat_score(
    mentions_24h: int,
    top_posts: list,
    trend_pct: float,
    is_meme: bool
) -> int:
    """
    综合计算社区热度得分 (0-100)
    考虑因素：提及次数、帖子互动量、趋势变化、是否Meme
    """
    score = 0.0

    # 提及次数（最高 40 分）
    if mentions_24h:
        score += min(40, mentions_24h / 5000 * 40)

    # 帖子总互动量（最高 35 分）
    total_engagement = sum(
        (p.get('likes', 0) + p.get('retweets', 0) * 2)
        for p in top_posts
    )
    score += min(35, total_engagement / 100000 * 35)

    # 趋势变化（最高 20 分）
    if trend_pct is not None:
        t = max(0, min(100, trend_pct))  # 0-100%
        score += min(20, t / 100 * 20)

    # Meme 加成（最高 5 分）
    if is_meme:
        score += 5

    return min(100, max(0, int(score)))


# ─── Mentions estimate ────────────────────────────────────────
def estimate_mentions(top_posts: list, trend_pct: float) -> int:
    """根据采集到的帖子推算24h提及次数（粗略估计）"""
    if not top_posts:
        return 0
    # 用帖子平均互动量估算
    avg = sum(p.get('likes', 0) for p in top_posts) / len(top_posts)
    base = int(avg * 0.5)
    trend_multiplier = 1 + (trend_pct or 0) / 100
    return max(0, int(base * trend_multiplier))


# ─── Main build ───────────────────────────────────────────────
def build_coin_data(coin_id: str, coin_type: str, market_data: dict) -> dict:
    """构建单个币种的完整数据对象"""
    log.info(f'Building data for {coin_id} ({coin_type})...')
    md = market_data.get(coin_id, {})

    symbol = md.get('symbol') or coin_id.split('-')[0].upper()
    name   = md.get('name') or coin_id.replace('-', ' ').title()

    # X 平台数据
    posts = fetch_kol_mentions(symbol)

    # 新闻补充（可选）
    latest_news = fetch_news(name)

    # 故事文本
    base_story = STORY_MAP.get(coin_id, f'{name} 是一个加密货币项目。')
    story = base_story
    if latest_news and len(latest_news) > 10:
        story = base_story  # 可在此追加 latest_news 摘要

    # 趋势（模拟，真实环境从历史数据库对比）
    # 实际部署时应将每次数据存入数据库对比
    trend_pct = round(
        sum(p.get('likes', 0) for p in posts) / max(1, len(posts)) / 1000
        + (hash(coin_id + str(datetime.date.today())) % 40 - 10),
        1
    )

    mentions = estimate_mentions(posts, trend_pct)

    coin = {
        'id':              coin_id,
        'type':            coin_type,
        'name':            name,
        'symbol':          symbol,
        'emoji':           EMOJI_MAP.get(coin_id, '🪙'),
        'image_url':       md.get('image_url', ''),
        'price':           md.get('price'),
        'market_cap':      md.get('market_cap'),
        'created_at':      _get_created_at(coin_id),
        'narrative_tags':  NARRATIVE_MAP.get(coin_id, ['加密货币']),
        'story':           story,
        'heat_score':      calc_heat_score(mentions, posts, trend_pct, coin_type == 'meme'),
        'holders':         None,  # 可接 Etherscan / Solscan API
        'mentions_24h':    mentions,
        'trend_24h_pct':   trend_pct,
        'top_posts':       posts,
    }

    return coin


def _get_created_at(coin_id: str) -> str:
    dates = {
        'bitcoin': '2009年1月', 'ethereum': '2015年7月',
        'solana': '2020年3月', 'binancecoin': '2017年7月',
        'ripple': '2013年1月', 'cardano': '2017年9月',
        'dogecoin': '2013年12月', 'shiba-inu': '2020年8月',
        'pepe': '2023年4月', 'official-trump': '2025年1月',
        'bonk': '2022年12月', 'dogwifcoin': '2023年11月',
    }
    return dates.get(coin_id, '未知')


# ─── Etherscan holders (optional) ─────────────────────────────
def fetch_eth_holders(contract_address: str) -> Optional[int]:
    """从 Etherscan 获取ERC-20代币持有者数量"""
    etherscan_key = os.environ.get('ETHERSCAN_API_KEY', '')
    if not etherscan_key or not contract_address:
        return None

    url = 'https://api.etherscan.io/api'
    params = {
        'module': 'token',
        'action': 'tokenholderlist',
        'contractaddress': contract_address,
        'apikey': etherscan_key,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get('status') == '1':
            return len(data.get('result', []))
    except Exception as e:
        log.error(f'Etherscan error: {e}')
    return None


# ─── Entry point ──────────────────────────────────────────────
def main():
    log.info('=== Crypto Pulse Data Collection Started ===')
    start = time.time()

    all_coin_ids = MAINSTREAM_COINS + MEME_COINS

    # 1. 批量获取行情数据
    market_data = fetch_coingecko(all_coin_ids)
    time.sleep(1.5)  # 避免速率限制

    # 2. 逐个处理币种
    coins = []
    for cid in MAINSTREAM_COINS:
        try:
            coin = build_coin_data(cid, 'mainstream', market_data)
            coins.append(coin)
            time.sleep(0.5)  # X API 速率控制
        except Exception as e:
            log.error(f'Error processing {cid}: {e}')

    for cid in MEME_COINS:
        try:
            coin = build_coin_data(cid, 'meme', market_data)
            coins.append(coin)
            time.sleep(0.5)
        except Exception as e:
            log.error(f'Error processing {cid}: {e}')

    # 3. 写入 JSON
    output = {
        'updated_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'coins': coins,
    }

    output_path = os.path.abspath(OUTPUT_PATH)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    elapsed = round(time.time() - start, 1)
    log.info(f'=== Done in {elapsed}s — {len(coins)} coins written to {output_path} ===')


if __name__ == '__main__':
    main()
