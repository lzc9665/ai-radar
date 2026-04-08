#!/usr/bin/env python3
"""
AI 雷达 · 每周自动更新脚本
- 抓取 Product Hunt 热榜
- 搜索本周 AI 新闻
- 用 GPT-4o 提炼中文内容
- 更新 index.html 中的数据

运行：python scripts/weekly_update.py
环境变量：OPENAI_API_KEY
"""

import os
import re
import json
import datetime
import requests
from bs4 import BeautifulSoup

# ──────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR       = os.path.dirname(SCRIPT_DIR)
INDEX_HTML     = os.path.join(ROOT_DIR, "index.html")

now      = datetime.datetime.now()
week_num = now.isocalendar()[1]
year     = now.year

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36"
}


# ──────────────────────────────────────────────────────────
# 1. 抓取 Product Hunt 本周榜（通过第三方镜像）
# ──────────────────────────────────────────────────────────
def fetch_producthunt_week() -> list[dict]:
    """抓取当前周的 Product Hunt 热榜产品"""
    url = f"https://producthunt.programnotes.cn/en/p/product-hunt-daily-{now.strftime('%Y-%m-%d')}/"
    print(f"[PH] 抓取 {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print(f"[PH] HTTP {r.status_code}，尝试前一天...")
            yesterday = (now - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            url = f"https://producthunt.programnotes.cn/en/p/product-hunt-daily-{yesterday}/"
            r = requests.get(url, headers=HEADERS, timeout=15)

        soup = BeautifulSoup(r.text, "html.parser")
        products = []

        # 解析表格
        for row in soup.select("table tr"):
            cells = row.find_all("td")
            if len(cells) >= 3:
                rank_cell = cells[0].get_text(strip=True)
                try:
                    rank = int(rank_cell)
                except ValueError:
                    continue
                name_cell  = cells[1].get_text(strip=True)
                votes_cell = cells[-1].get_text(strip=True)
                votes_num  = re.search(r"\d+", votes_cell)
                products.append({
                    "rank":  rank,
                    "name":  name_cell,
                    "votes": int(votes_num.group()) if votes_num else 0,
                    "desc":  "",
                })
                if rank >= 10:
                    break
        return products[:10]
    except Exception as e:
        print(f"[PH] 抓取失败：{e}")
        return []


# ──────────────────────────────────────────────────────────
# 2. 搜索本周 AI 新闻（Serper API / DuckDuckGo 备用）
# ──────────────────────────────────────────────────────────
def fetch_ai_news() -> list[str]:
    """返回本周 AI 新闻标题列表"""
    # 方案A：直接调 DuckDuckGo Instant Answer（无需 key）
    queries = [
        f"AI产品 新发布 {now.strftime('%Y年%m月')}",
        f"人工智能 大模型 发布 {now.strftime('%Y-%m')}",
    ]
    titles = []
    for q in queries:
        try:
            r = requests.get(
                "https://api.duckduckgo.com/",
                params={"q": q, "format": "json", "no_html": 1, "t": "ai-radar"},
                headers=HEADERS, timeout=10
            )
            data = r.json()
            for topic in data.get("RelatedTopics", [])[:5]:
                if isinstance(topic, dict) and "Text" in topic:
                    titles.append(topic["Text"][:120])
        except Exception as e:
            print(f"[News] 搜索失败：{e}")
    return titles[:15]


# ──────────────────────────────────────────────────────────
# 3. 用 GPT-4o 生成本周产品 JS 数据
# ──────────────────────────────────────────────────────────
def generate_products_with_ai(ph_products: list, news: list) -> dict:
    """调用 OpenAI 生成本周产品 JSON 数据"""
    if not OPENAI_API_KEY:
        print("[AI] 未设置 OPENAI_API_KEY，使用占位数据")
        return _placeholder_data()

    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    ph_text   = json.dumps(ph_products, ensure_ascii=False, indent=2)
    news_text = "\n".join(f"- {n}" for n in news)

    prompt = f"""
你是「AI 雷达」周报的内容编辑。根据下方本周真实数据，生成两个 JavaScript 数组：

## 本周 Product Hunt 热榜
{ph_text}

## 本周 AI 新闻标题
{news_text}

## 输出格式
请严格输出如下 JSON（不要 markdown 代码块，纯 JSON）：
{{
  "newProducts": [
    {{
      "name": "产品英文名",
      "tagline": "15字内中文卖点",
      "desc": "50-80字中文功能描述，突出核心价值",
      "icon": "单个 emoji",
      "bg": "#1a1a25",
      "cat": "模型|编程|图像|视频|写作|智能体|效率 中选一",
      "votes": 数字或null,
      "featured": true/false,
      "heat": 1-5整数,
      "tags": ["标签1", "标签2", "标签3"]
    }}
  ],
  "newsItems": [
    {{
      "emoji": "单个 emoji",
      "title": "事件标题（30字内）",
      "sub": "补充说明（40字内，含关键数字）",
      "badge": "hot|new|warn|data 中选一"
    }}
  ]
}}

要求：
- newProducts 10条，全部来自 Product Hunt 热榜，按票数降序
- newsItems 8-10条，来自新闻标题提炼
- 所有内容为中文
- bg 颜色使用深色系（如 #1a1e28）
- heat 根据票数/热度打分：>300票=5，200-300=4，100-200=3，<100=2
"""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=3000,
    )
    text = resp.choices[0].message.content.strip()
    # 清理可能的 markdown
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    return json.loads(text)


def _placeholder_data() -> dict:
    """无 API key 时的占位数据"""
    return {
        "newProducts": [],
        "newsItems":   []
    }


# ──────────────────────────────────────────────────────────
# 4. 更新 index.html
# ──────────────────────────────────────────────────────────
def update_index_html(data: dict):
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # 更新周数标题
    html = re.sub(
        r"第\s*\d+\s*周\s*·\s*[\d.]+",
        f"第 {week_num} 周 · {now.strftime('%Y.%m.%d')}",
        html
    )
    html = re.sub(
        r"本周实时更新\s*·\s*[\d年月第周]+",
        f"本周实时更新 · {year}年{now.month}月第{(now.day-1)//7+1}周",
        html
    )

    # 替换 newProducts 数组
    if data.get("newProducts"):
        new_js = "const newProducts = " + json.dumps(
            data["newProducts"], ensure_ascii=False, indent=2
        ) + ";"
        html = re.sub(
            r"const newProducts\s*=\s*\[.*?\];",
            new_js,
            html,
            flags=re.DOTALL
        )

    # 替换新闻条目
    if data.get("newsItems"):
        news_html_items = []
        badge_map = {
            "hot":  ("badge-hot",  "🔥 爆"),
            "new":  ("badge-new",  "NEW"),
            "warn": ("badge-warn", "⚠️ 注意"),
            "data": ("badge-data", "📊 数据"),
        }
        for item in data["newsItems"]:
            bc, bt = badge_map.get(item.get("badge","new"), ("badge-new","NEW"))
            news_html_items.append(f"""      <div class="news-item">
        <span class="news-emoji">{item['emoji']}</span>
        <div class="news-body">
          <div class="news-title">{item['title']}</div>
          <div class="news-sub">{item['sub']}</div>
        </div>
        <span class="news-badge {bc}">{bt}</span>
      </div>""")

        news_block = "\n".join(news_html_items)
        html = re.sub(
            r'(<div class="news-list">).*?(</div>\s*</div>\s*<!-- 本周趋势数据)',
            rf'\1\n{news_block}\n    \2',
            html,
            flags=re.DOTALL
        )

    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[✓] index.html 已更新：第 {week_num} 周")


# ──────────────────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"=== AI 雷达 自动更新 · 第 {week_num} 周 ===")

    print("[1/3] 抓取 Product Hunt...")
    ph = fetch_producthunt_week()
    print(f"      获得 {len(ph)} 个产品")

    print("[2/3] 搜索 AI 新闻...")
    news = fetch_ai_news()
    print(f"      获得 {len(news)} 条新闻")

    print("[3/3] AI 生成内容并更新 HTML...")
    data = generate_products_with_ai(ph, news)
    update_index_html(data)

    print("=== 完成 ===")
