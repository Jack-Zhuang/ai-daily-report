# AI 推荐日报 - 技术架构文档

## 🏗️ 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI 推荐日报系统                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  数据采集层   │  │  数据处理层   │  │  内容生成层   │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│         ↓                  ↓                  ↓                     │
│  ┌──────────────────────────────────────────────────────┐          │
│  │                    数据存储层                          │          │
│  │  daily_data/ | covers/ | insights_enhanced/ | cache/ │          │
│  └──────────────────────────────────────────────────────┘          │
│         ↓                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  报告生成层   │  │  发布归档层   │  │  监控日志层   │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 📦 模块详解

### 1. 数据采集模块

#### 1.1 arXiv 论文采集

**脚本**: `collect_daily.py`, `collect_conferences.py`

**数据源**:
- arXiv API: `http://export.arxiv.org/api/query`
- 分类: cs.AI, cs.LG, cs.CL, cs.IR, cs.CV

**采集流程**:
```python
1. 构建查询 URL (分类 + 时间范围)
2. 发送 HTTP 请求获取 XML 响应
3. 解析 XML 提取论文元数据
4. 计算工业界评分 (industry_score)
5. 计算论文价值评分 (paper_value)
6. 保存到 daily_data/YYYY-MM-DD.json
```

**评分算法**:
```python
industry_score = (
    0.3 * has_implementation +
    0.2 * company_affiliation +
    0.2 * practical_keywords +
    0.15 * benchmark_results +
    0.15 * dataset_usage
)

paper_value = (
    0.4 * industry_score +
    0.3 * novelty_score +
    0.3 * citation_potential
)
```

#### 1.2 GitHub 项目采集

**脚本**: `collect_github.py`

**数据源**:
- GitHub Trending API
- GitHub Search API

**采集策略**:
```python
1. 获取 trending repositories (daily/weekly)
2. 过滤 AI/ML 相关项目
3. 提取项目元数据 (stars, forks, language)
4. 计算增长率和热度
5. 保存到 daily_data
```

#### 1.3 技术文章采集

**脚本**: `collect_articles.py`, `collect_wechat_rss.py`

**数据源**:
- InfoQ: https://www.infoq.cn
- 机器之心: https://www.jiqizhixin.com
- 量子位: https://www.qbitai.com
- 微信公众号 (via RSSHub)

**采集流程**:
```python
1. 发送 HTTP 请求获取页面
2. 使用 BeautifulSoup 解析 HTML
3. 提取文章标题、摘要、链接
4. 使用 AI 生成中文摘要
5. 分类打标签
```

### 2. 数据处理模块

#### 2.1 每日精选选择

**脚本**: `select_daily_pick.py`, `build_daily_pick.py`

**选择策略**:
```python
def select_daily_pick(papers, articles, projects):
    candidates = []

    # 从论文中选择 (top 3)
    papers_sorted = sorted(papers, key=lambda x: x['paper_value'], reverse=True)
    candidates.extend(papers_sorted[:3])

    # 从文章中选择 (top 1)
    articles_sorted = sorted(articles, key=lambda x: x['views'], reverse=True)
    candidates.extend(articles_sorted[:1])

    # 从项目中选择 (top 1)
    projects_sorted = sorted(projects, key=lambda x: x['growth_rate'], reverse=True)
    candidates.extend(projects_sorted[:1])

    return candidates[:5]
```

#### 2.2 论文翻译

**脚本**: `translate_papers.py`, `translator.py`

**翻译流程**:
```python
1. 提取论文标题和摘要
2. 调用 MiniMax API 进行翻译
3. 保留专业术语 (不翻译)
4. 保存翻译结果到数据文件
```

**术语处理**:
```python
KEEP_ORIGINAL = [
    "Transformer", "BERT", "GPT", "LLM",
    "Attention", "Embedding", "Fine-tuning",
    "RAG", "Agent", "Multi-Agent"
]
```

### 3. 内容生成模块

#### 3.1 论文深度解读

**脚本**: `enhanced/batch_processor.py`

**处理流程**:
```
┌─────────────┐
│ 1. PDF 下载  │
└──────┬──────┘
       ↓
┌─────────────┐
│ 2. 内容提取  │  ← paper_extractor.py
└──────┬──────┘
       ↓
┌─────────────┐
│ 3. AI 解读   │  ← insight_generator.py
└──────┬──────┘
       ↓
┌─────────────┐
│ 4. Markdown  │
└──────┬──────┘
       ↓
┌─────────────┐
│ 5. HTML 页面 │  ← generate_insight_page.py
└─────────────┘
```

**PDF 内容提取** (`paper_extractor.py`):
```python
class PaperExtractor:
    def extract(self, arxiv_id, title):
        # 1. 下载 PDF
        pdf_path = self.download_pdf(arxiv_id)

        # 2. 解析 PDF 结构
        doc = fit.open(pdf_path)

        # 3. 提取各部分内容
        sections = self.parse_sections(doc)
        figures = self.parse_figures(doc)
        tables = self.parse_tables(doc)
        equations = self.parse_equations(doc)
        references = self.parse_references(doc)

        return PaperContent(
            arxiv_id=arxiv_id,
            title=title,
            abstract=abstract,
            sections=sections,
            figures=figures,
            tables=tables,
            equations=equations,
            references=references
        )
```

**AI 解读生成** (`insight_generator.py`):
```python
class EnhancedInsightGenerator:
    def generate_deep_insight(self, paper_content):
        # 构建提示词
        prompt = self.build_prompt(paper_content)

        # 调用 MiniMax API
        result = self.call_api(prompt)

        # 解析 JSON 结果
        insight = json.loads(result)

        # 生成增强内容
        mermaid = self.generate_mermaid_diagram(insight['method'])
        code = self.generate_code_example(insight['method'])
        formulas = self.generate_formulas(paper_content.equations)

        return {
            'insight': insight,
            'mermaid': mermaid,
            'code': code,
            'formulas': formulas
        }
```

#### 3.2 封面图生成

**脚本**: `batch_generate_covers.py`

**生成策略**:
```python
class BatchCoverGenerator:
    def generate_cover(self, item, category, index):
        # 1. 检查已有封面
        if self.has_valid_cover(item):
            return item['cover_image']

        # 2. 生成提示词
        prompt = self.get_prompt(category)

        # 3. 调用 Seedream API
        image_url = self.call_seedream(prompt)

        # 4. 下载并保存
        cover_path = self.save_cover(image_url, category, index)

        return cover_path
```

**命名规则**:
```python
# arXiv 论文使用 arxiv_id
cover_name = f"paper_{arxiv_id}.jpg"

# 其他内容使用 category + index
cover_name = f"{category}_{index}.jpg"
```

### 4. 报告生成模块

**脚本**: `generate_report.py`

**生成流程**:
```python
def generate_report(date):
    # 1. 加载数据
    data = load_daily_data(date)

    # 2. 生成各部分 HTML
    daily_pick_html = generate_daily_pick_section(data['daily_pick'])
    papers_html = generate_papers_section(data['arxiv_papers'])
    github_html = generate_github_section(data['github_projects'])

    # 3. 组装完整页面
    html = assemble_page(
        daily_pick_html,
        papers_html,
        github_html,
        template='report_template.html'
    )

    # 4. 写入文件
    write_file(f'docs/index.html', html)

    # 5. 归档
    archive_report(date, html)
```

**页面结构**:
```html
<!DOCTYPE html>
<html>
<head>
    <!-- 样式和脚本 -->
</head>
<body>
    <!-- 导航栏 -->
    <nav>...</nav>

    <!-- 每日精选 -->
    <section id="daily-pick">...</section>

    <!-- arXiv 论文 -->
    <section id="arxiv-papers">...</section>

    <!-- GitHub 项目 -->
    <section id="github-projects">...</section>

    <!-- 历史归档 -->
    <section id="archive">...</section>

    <!-- JavaScript 交互 -->
    <script>...</script>
</body>
</html>
```

## 🔌 API 集成

### MiniMax API

**用途**: 论文解读、翻译、摘要生成

**配置**:
```python
API_URL = "https://api.minimaxi.com/anthropic/v1/messages"
MODEL = "MiniMax-M2.7-highspeed"
```

**调用示例**:
```python
def call_api(self, prompt, max_tokens=4000):
    headers = {
        "x-api-key": self.api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "MiniMax-M2.7-highspeed",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(API_URL, json=payload, headers=headers)
    return response.json()
```

### Seedream API

**用途**: 封面图生成

**配置**:
```python
SERVICE_URL = "https://celia-claw-drcn.ai.dbankcloud.cn"
SKILL_ID = "seedream"
```

**调用示例**:
```python
def generate_image(self, prompt):
    payload = {
        "actions": [{
            "actionExecutorTask": {
                "actionName": "seedreamBatch5",
                "content": {
                    "prompt": prompt,
                    "size": "2K",
                    "watermark": True
                }
            }
        }]
    }

    response = requests.post(SERVICE_URL, json=payload, headers=headers, stream=True)

    # 解析 SSE 响应
    for line in response.iter_lines():
        if line.startswith('data:'):
            result = json.loads(line[5:])
            image_url = extract_image_url(result)
            return image_url
```

## 💾 数据存储

### 文件结构

```
daily_data/
├── 2026-04-20.json          # 当天原始数据
└── 2026-04-19.json          # 历史数据

covers/
├── paper_2604.15037.jpg     # 论文封面
├── pick_1.jpg               # 精选封面
└── github_1.jpg             # 项目封面

insights_enhanced/
├── 2026-04-20_2604.15037.md # 论文解读 Markdown
└── 2026-04-20_2604.14878.md

docs/
├── index.html               # 主报告
└── insights/
    ├── 2026-04-20_2604.15037.html
    └── 2026-04-20_2604.14878.html

archive/
├── 2026-04-20/
│   ├── index.html
│   └── insights/
└── index.json               # 归档索引
```

### 数据格式

**daily_data/YYYY-MM-DD.json**:
```json
{
  "date": "2026-04-20",
  "daily_pick": [
    {
      "id": "unique_id",
      "title": "Original Title",
      "cn_title": "中文标题",
      "summary": "English abstract...",
      "cn_summary": "中文摘要...",
      "link": "https://arxiv.org/abs/2604.15037",
      "source": "arxiv",
      "category": "agent",
      "cover_image": "covers/paper_2604.15037.jpg",
      "published": "2026-04-20",
      "industry_score": 8.5,
      "paper_value": 7.8
    }
  ],
  "arxiv_papers": [...],
  "github_projects": [...],
  "hot_articles": [...]
}
```

## 🚀 部署方案

### 方案一：静态部署

```bash
# 1. 生成报告
python3 scripts/generate_report.py --date 2026-04-20

# 2. 生成封面
python3 scripts/batch_generate_covers.py --date 2026-04-20

# 3. 部署到 Web 服务器
rsync -av --delete docs/ covers/ /var/www/ai-daily/
```

### 方案二：自动化部署

**Cron 定时任务**:
```bash
# 每天早上 8 点执行
0 8 * * * cd /path/to/ai_daily && python3 scripts/run_daily.py >> logs/cron.log 2>&1
```

**自动化脚本** (`run_daily.py`):
```python
def run_daily():
    # 1. 采集数据
    collect_daily()

    # 2. 选择精选
    select_daily_pick()

    # 3. 翻译论文
    translate_papers()

    # 4. 生成报告
    generate_report()

    # 5. 生成封面
    generate_covers()

    # 6. 部署
    deploy()

    # 7. 归档
    archive()

    # 8. 推送通知
    push_notification()
```

## 📊 监控指标

### 关键指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| 采集成功率 | 数据采集成功率 | > 95% |
| 封面生成率 | 封面生成成功率 | > 90% |
| 报告生成时间 | 完整报告生成时间 | < 5 分钟 |
| API 调用成功率 | API 调用成功率 | > 98% |

### 日志监控

```bash
# 查看采集日志
tail -f logs/collect.log

# 查看封面生成进度
bash scripts/check_cover_progress.sh

# 查看批量处理状态
grep -E "成功|失败|跳过" logs/batch_process.log | tail -20
```

## 🔒 安全考虑

### API 密钥管理

```bash
# 不要将密钥提交到 Git
echo ".xiaoyienv" >> .gitignore
echo "*.key" >> .gitignore

# 使用环境变量
export MINIMAX_API_KEY="your_key"
export PERSONAL_API_KEY="your_key"
```

### 数据备份

```bash
# 每日备份
tar -czf backup_$(date +%Y%m%d).tar.gz daily_data/ covers/ insights_enhanced/

# 保留最近 30 天
find . -name "backup_*.tar.gz" -mtime +30 -delete
```

## 🐛 故障排查

### 常见问题

**1. PDF 下载失败**
```python
# 检查网络连接
curl -I https://arxiv.org/pdf/2604.15037.pdf

# 使用代理
proxies = {"http": "http://proxy:port", "https": "http://proxy:port"}
response = requests.get(url, proxies=proxies)
```

**2. API 调用超时**
```python
# 增加超时时间
response = requests.post(url, json=payload, timeout=120)

# 添加重试机制
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_api_with_retry(prompt):
    return call_api(prompt)
```

**3. 封面生成失败**
```bash
# 检查 Seedream 服务状态
curl -I https://celia-claw-drcn.ai.dbankcloud.cn/health

# 查看错误日志
grep "ERROR\|FAIL" logs/cover_generation.log
```

## 📈 性能优化

### 并发处理

```python
from concurrent.futures import ThreadPoolExecutor

def process_papers_parallel(papers, max_workers=5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_paper, p) for p in papers]
        results = [f.result() for f in futures]
    return results
```

### 缓存策略

```python
# PDF 缓存
if pdf_cache.exists() and pdf_cache.age() < 7*24*3600:  # 7 天
    return pdf_cache
else:
    return download_pdf(arxiv_id)

# API 响应缓存
@lru_cache(maxsize=100)
def translate_text(text):
    return call_translation_api(text)
```

## 🔮 未来规划

### 短期目标

- [ ] 支持更多数据源 (Reddit, Hacker News)
- [ ] 优化封面生成质量
- [ ] 添加用户订阅功能
- [ ] 支持多语言

### 长期目标

- [ ] 构建知识图谱
- [ ] 实现个性化推荐
- [ ] 开发移动端应用
- [ ] 建立社区平台
