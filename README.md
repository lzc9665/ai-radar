# AI 雷达 🛰️

> 每周追踪全球最值得关注的 AI 工具 · 中文精选 · 自动更新

**在线访问：** `https://你的用户名.github.io/ai-radar/`

---

## 🚀 5 分钟发布到线上

### 第一步：在 GitHub 创建仓库

1. 去 [github.com/new](https://github.com/new)
2. 仓库名填 `ai-radar`
3. 选 **Public**（GitHub Pages 免费版需要公开）
4. 点 **Create repository**

### 第二步：上传代码

把 `ai-nav/` 整个文件夹内容上传到仓库根目录，或者：

```bash
cd /Users/lzc/WorkBuddy/20260408100944/ai-nav
git init
git add .
git commit -m "🚀 首次发布：AI 雷达导航站"
git branch -M main
git remote add origin https://github.com/你的用户名/ai-radar.git
git push -u origin main
```

### 第三步：开启 GitHub Pages

1. 进入仓库 → **Settings** → **Pages**
2. Source 选 **GitHub Actions**
3. 保存

### 第四步（可选）：配置 OpenAI Key 实现真正自动更新

1. 进入仓库 → **Settings** → **Secrets and variables** → **Actions**
2. 点 **New repository secret**
3. Name: `OPENAI_API_KEY`，Value: 你的 OpenAI API Key
4. 保存

> 没有 API Key 也没关系，脚本会跳过 AI 生成步骤，仅更新周数和日期。

---

## 📅 自动更新机制

- **触发时间：** 每周一 00:00 UTC（北京时间周一上午 8 点）
- **触发方式：** GitHub Actions 定时任务
- **更新内容：** 抓取 Product Hunt 热榜 + AI 新闻 → GPT-4o 提炼中文内容 → 自动提交并部署

也可以在仓库 **Actions** 页面手动点击 **Run workflow** 立即触发。

---

## 💰 变现方式

| 方式 | 定价 | 操作 |
|------|------|------|
| 周赞助 Banner | ¥299/期 | 修改 HTML 中 `.sponsor-banner` 内容 |
| 精选收录位 | ¥199/席 | 每期限 3 席，修改 `.promote-slot` 内容 |
| 深度评测文章 | ¥999/篇 | 单独发布文章页 |
| Pro 订阅 | ¥29/月 | 接入 Substack / 竹白 / 小报童 |
| 企业定制版 | 面议 | 联系邮件：contact@ai-radar.cn |

**推荐接入付费订阅：**
- [小报童](https://xiaobot.net)：无需服务器，适合个人创作者
- [竹白](https://zhubai.love)：中文邮件订阅平台，免费开始
- [Substack](https://substack.com)：国际化，支持付费

---

## 📁 文件结构

```
ai-radar/
├── index.html              # 主页（全站单文件）
├── scripts/
│   └── weekly_update.py    # 每周自动更新脚本
├── .github/
│   └── workflows/
│       └── deploy.yml      # GitHub Actions 部署配置
└── README.md
```

---

## 🔧 手动更新内容

每期内容全在 `index.html` 里的 JavaScript 数组中，直接编辑即可：

```javascript
const newProducts = [
  {
    name: "产品名",
    tagline: "一句话描述",
    desc: "详细介绍",
    icon: "🤖",
    bg: "#1a1a25",
    cat: "模型",   // 模型 编程 图像 视频 写作 智能体 效率
    votes: 394,
    featured: true,
    heat: 5,       // 1-5
    tags: ["标签1", "标签2"]
  },
  // ...
]
```

---

*AI 雷达 · Powered by WorkBuddy*
