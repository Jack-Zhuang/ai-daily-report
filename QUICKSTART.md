# AI 推荐日报 - 快速上手指南

## 🎯 5 分钟快速开始

### 第一步：环境准备

```bash
# 克隆项目
cd ~/.openclaw/workspace
git clone <repo_url> ai_daily
cd ai_daily

# 安装依赖
pip install requests beautifulsoup4 feedparser python-dateutil PyMuPDF
```

### 第二步：配置 API

```bash
# 创建配置文件
cat > ~/.openclaw/.xiaoyienv << EOF
PERSONAL-API-KEY=your_api_key_here
PERSONAL-UID=your_uid_here
SERVICE_URL=https://celia-claw-drcn.ai.dbankcloud.cn
EOF
```

### 第三步：运行第一次采集

```bash
# 采集今天的数据
python3 scripts/collect_daily.py

# 查看采集结果
ls -lh daily_data/
```

### 第四步：生成报告

```bash
# 生成 HTML 报告
python3 scripts/generate_report.py --date $(date +%Y-%m-%d)

# 查看报告
open docs/index.html
```

### 第五步：生成封面

```bash
# 批量生成封面图
python3 scripts/batch_generate_covers.py --date $(date +%Y-%m-%d)

# 查看进度
bash scripts/check_cover_progress.sh
```

## 📅 每日工作流

### 自动化流程

```bash
# 一键运行完整流程
python3 scripts/run_daily.py
```

### 分步执行

```bash
# 1. 采集数据 (约 2 分钟)
python3 scripts/collect_daily.py

# 2. 选择每日精选 (约 10 秒)
python3 scripts/select_daily_pick.py

# 3. 翻译论文标题和摘要 (约 5 分钟)
python3 scripts/translate_papers.py

# 4. 生成报告 (约 30 秒)
python3 scripts/generate_report.py

# 5. 生成封面 (约 20-40 分钟，可后台运行)
nohup python3 scripts/batch_generate_covers.py > logs/cover_generation.log 2>&1 &

# 6. 部署 (约 10 秒)
cp -r docs/* ~/public_html/ai-daily/
```

## 🛠️ 常用命令速查

### 数据采集

```bash
# 采集 arXiv 论文
python3 scripts/collect_daily.py --source arxiv

# 采集 GitHub 项目
python3 scripts/collect_github.py

# 采集技术文章
python3 scripts/collect_articles.py

# 采集顶会论文
python3 scripts/collect_conferences.py --conference RecSys --year 2025
```

### 报告生成

```bash
# 生成今天的报告
python3 scripts/generate_report.py

# 生成指定日期的报告
python3 scripts/generate_report.py --date 2026-04-20

# 生成美化版报告
python3 scripts/generate_beautiful_report.py
```

### 封面生成

```bash
# 为今天生成封面
python3 scripts/batch_generate_covers.py

# 为指定日期生成封面（每类最多 10 条）
python3 scripts/batch_generate_covers.py --date 2026-04-20 --limit 10

# 后台运行
nohup python3 scripts/batch_generate_covers.py > logs/cover_generation.log 2>&1 &

# 查看进度
bash scripts/check_cover_progress.sh

# 更新数据文件中的封面字段
python3 scripts/update_cover_fields.py
```

### 论文解读

```bash
# 批量处理论文（生成深度解读）
python3 scripts/enhanced/batch_processor.py --limit 10

# 从第 5 篇开始处理
python3 scripts/enhanced/batch_processor.py --start 5 --limit 10

# 查看处理日志
tail -f logs/batch_process.log
```

### 部署与归档

```bash
# 部署到 Web 服务器
cp -r docs/* ~/public_html/ai-daily/
cp -r covers ~/public_html/ai-daily/

# 归档历史报告
python3 scripts/archive_manager.py --date 2026-04-20

# 查看归档
ls -lh archive/
```

## 📊 数据文件说明

### daily_data/YYYY-MM-DD.json

这是核心数据文件，包含当天采集的所有内容：

```json
{
  "date": "2026-04-20",
  "daily_pick": [
    {
      "id": "unique_id",
      "title": "原标题",
      "cn_title": "中文标题",
      "summary": "英文摘要",
      "cn_summary": "中文摘要",
      "link": "https://...",
      "source": "arxiv",
      "category": "agent",
      "cover_image": "covers/paper_2604.15037.jpg",
      "industry_score": 8.5,
      "paper_value": 7.8
    }
  ],
  "arxiv_papers": [...],
  "github_projects": [...],
  "hot_articles": [...]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一标识符 |
| `title` | string | 原始标题 |
| `cn_title` | string | 中文标题 |
| `summary` | string | 英文摘要 |
| `cn_summary` | string | 中文摘要 |
| `link` | string | 原文链接 |
| `source` | string | 来源 (arxiv/github/wechat) |
| `category` | string | 分类 (agent/llm/rec/paper) |
| `cover_image` | string | 封面图路径 |
| `industry_score` | float | 工业界评分 (0-10) |
| `paper_value` | float | 论文价值评分 (0-10) |

## 🎨 封面图管理

### 封面命名规则

```
arXiv 论文:    paper_<arxiv_id>.jpg     例: paper_2604.15037.jpg
每日精选:      pick_<index>.jpg         例: pick_1.jpg
热门文章:      article_<index>.jpg      例: article_1.jpg
GitHub 项目:   github_<index>.jpg       例: github_1.jpg
```

### 封面质量标准

- **最小尺寸**: 10KB
- **推荐尺寸**: 150KB - 350KB
- **分辨率**: 2K (推荐)
- **格式**: JPEG

### 封面生成策略

1. **检查已有封面**: 如果封面文件存在且 > 10KB，跳过
2. **检查处理进度**: 如果已在进度文件中标记，跳过
3. **AI 生成**: 使用 Seedream 生成封面

## 🔧 故障排查

### 问题 1: 采集失败

```bash
# 检查网络连接
ping arxiv.org
ping github.com

# 查看错误日志
tail -f logs/collect.log

# 手动测试采集
python3 -c "
from scripts.collect_daily import *
result = collect_arxiv()
print(f'采集到 {len(result)} 篇论文')
"
```

### 问题 2: 封面生成失败

```bash
# 检查 API 配置
cat ~/.openclaw/.xiaoyienv

# 测试 Seedream API
python3 skills/seedream-image_gen/scripts/generate_seedream.py --prompt "test"

# 查看错误日志
grep "ERROR\|FAIL" logs/cover_generation.log
```

### 问题 3: 报告生成异常

```bash
# 检查数据文件格式
python3 -m json.tool daily_data/2026-04-20.json > /dev/null

# 检查模板文件
ls -lh scripts/templates/

# 手动生成报告
python3 scripts/generate_report.py --date 2026-04-20 --verbose
```

## 📈 性能优化建议

### 1. 并行处理

```bash
# 使用多进程加速封面生成
python3 scripts/batch_generate_covers.py --workers 3
```

### 2. 缓存利用

```bash
# PDF 缓存（避免重复下载）
ls -lh paper_cache/

# 清理过期缓存（超过 7 天）
find paper_cache/ -name "*.pdf" -mtime +7 -delete
```

### 3. 后台任务

```bash
# 使用 nohup 后台运行
nohup python3 scripts/batch_generate_covers.py > logs/cover.log 2>&1 &

# 使用 screen 保持会话
screen -S ai_daily
python3 scripts/run_daily.py
# Ctrl+A+D 分离会话

# 重新连接
screen -r ai_daily
```

## 📚 进阶使用

### 自定义数据源

编辑 `config/sources.json`:

```json
{
  "arxiv": {
    "categories": ["cs.AI", "cs.LG", "cs.CL"],
    "max_results": 50,
    "sort_by": "submittedDate"
  },
  "github": {
    "languages": ["Python", "JavaScript"],
    "since": "daily",
    "topics": ["machine-learning", "deep-learning"]
  }
}
```

### 自定义报告模板

编辑 `scripts/templates/report_template.html`:

```html
<!-- 添加自定义样式 -->
<style>
.card {
    /* 你的样式 */
}
</style>

<!-- 添加自定义区块 -->
<section id="custom-section">
    <!-- 你的内容 -->
</section>
```

### 自定义封面提示词

编辑 `scripts/batch_generate_covers.py`:

```python
self.prompts = {
    'paper': "你的自定义提示词...",
    'article': "你的自定义提示词...",
    # ...
}
```

## 🎓 学习资源

- [项目文档](README.md)
- [技术架构](TECHNICAL_GUIDE.md)
- [API 文档](https://docs.openclaw.ai)
- [社区讨论](https://discord.gg/clawd)

## 💡 最佳实践

1. **定时执行**: 使用 Cron 每天固定时间运行
2. **监控日志**: 定期检查日志文件，及时发现问题
3. **备份数据**: 每周备份一次数据文件
4. **更新依赖**: 定期更新 Python 依赖包
5. **优化配置**: 根据实际情况调整采集参数

## 🆘 获取帮助

- 查看 [FAQ](FAQ.md)
- 提交 [Issue](https://github.com/your-org/ai-daily/issues)
- 加入 [Discord](https://discord.gg/clawd)
