# AI推荐日报 - 展示规则与交互逻辑

## 一、页面结构

### 1. 主页 (index.html)

| 区块 | 位置 | 内容 | 数量限制 |
|------|------|------|----------|
| 导航栏 | 顶部固定 | Logo、搜索、收藏、日期选择 | - |
| 每日精选 | 第1区块 | 编辑精选内容 | 5条 |
| 热门文章 | 第2区块 | 分类Tab + 文章卡片 | 15条 |
| GitHub Trending | 第3区块 | 热门项目卡片 | 5条 |
| arXiv最新 | 第4区块 | 论文卡片 | 5条 |
| 顶会论文 | 第5区块 | 会议Tab + 论文列表 | 每会议3条 |
| 页脚 | 底部 | 订阅、分享、归档入口 | - |

### 2. 子页面

| 页面 | 文件 | 内容 |
|------|------|------|
| 文章列表 | articles.html | 全部文章（未生成） |
| 论文列表 | papers.html | 全部论文（未生成） |
| 增强版解读 | docs/insights/*.html | 单篇论文深度解读 |

---

## 二、数据展示规则

### 1. 每日精选

```python
# 数据来源
daily_pick = data.get('daily_pick', [])[:5]

# 展示字段
- cn_title: 中文标题
- cn_summary: 中文摘要（200字）
- _type: 类型（paper/article/github）
- _reason: 推荐理由
- _score: 评分
```

**筛选规则**：
- 论文：2篇（按论文价值评分排序）
- 文章：2篇（按热度评分排序）
- GitHub：1篇（按星数排序）

### 2. 热门文章

```python
# 数据来源
articles = data.get('articles', data.get('hot_articles', []))[:15]

# Tab分类
- 全部：所有文章
- 推荐：category='wechat' 或 'tech_blog'
- Agent：标题含 'agent' 或 '智能体'
- LLM：标题含 'llm' 或 '大模型'
```

**展示字段**：
- title: 标题
- source: 来源（量子位、机器之心等）
- published: 发布日期
- summary: 摘要（80字）

### 3. GitHub Trending

```python
# 数据来源
github_projects = data.get('github_projects', [])[:5]

# 展示字段
- name: 项目名
- description: 描述
- stargazers_count: 星数
- language: 语言
- topics: 标签
```

### 4. arXiv最新

```python
# 数据来源
arxiv_papers = data.get('arxiv_papers', [])[:5]

# 展示字段
- cn_title: 中文标题
- cn_summary: 中文摘要（200字）
- authors: 作者
- published: 发布日期
- link: arXiv链接
```

### 5. 顶会论文

```python
# 数据来源
conferences = data.get('conferences', {})

# 每会议展示
- 论文数：3篇
- 排序：按工业相关性
```

---

## 三、交互逻辑

### 1. Tab切换

**热门文章Tab**：
```javascript
// 点击Tab触发
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', function() {
        // 1. 切换active状态
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        this.classList.add('active');
        
        // 2. 重新渲染文章列表
        renderHotArticles(this.dataset.tab);
    });
});
```

**Tab类型**：
- `all`: 全部文章
- `rec`: 推荐系统相关
- `agent`: Agent相关
- `llm`: LLM相关

### 2. 卡片点击

**每日精选卡片**：
```javascript
onclick="showPickDetail(index)"
// 弹出底部Modal，显示详情
```

**文章卡片**：
```javascript
onclick="showArticleDetail(index, filter)"
// 弹出底部Modal，显示文章详情
```

**GitHub卡片**：
```javascript
onclick="showGithubDetail(index)"
// 弹出底部Modal，显示项目详情
```

**论文卡片**：
```javascript
onclick="window.location.href='docs/insights/xxx.html'"
// 跳转到增强版解读页面
```

### 3. Modal弹窗

**详情Modal**：
```javascript
// 打开
function showXxxDetail(index) {
    document.getElementById('detail-modal-title').innerHTML = title;
    document.getElementById('detail-modal-body').innerHTML = body;
    document.getElementById('detail-modal-footer').innerHTML = footer;
    document.getElementById('detail-modal').classList.add('active');
}

// 关闭
function closeDetailModal() {
    document.getElementById('detail-modal').classList.remove('active');
}

// 点击遮罩关闭
onclick="if(event.target === this) closeDetailModal()"
```

**搜索Modal**：
```javascript
// 打开
function openSearch() {
    document.querySelector('.search-modal').classList.add('active');
}

// 关闭
function closeSearch() {
    document.querySelector('.search-modal').classList.remove('active');
}
```

**收藏Modal**：
```javascript
function showFavorites() { ... }
function closeFavorites() { ... }
```

**归档Modal**：
```javascript
function showArchive() { ... }
function closeArchive() { ... }
```

**订阅Modal**：
```javascript
function showSubscribeModal() { ... }
function closeSubscribeModal() { ... }
```

### 4. 搜索功能

```javascript
// 搜索过滤器
- all: 全部
- paper: 论文
- project: 项目
- article: 文章

// 搜索逻辑
function performSearch(query) {
    // 1. 遍历所有数据
    // 2. 匹配标题、摘要、作者
    // 3. 渲染搜索结果
}
```

### 5. 收藏功能

```javascript
// 点击收藏按钮
onclick="event.stopPropagation(); handleFavoriteClick(this)"

// 存储
localStorage.setItem('favorites', JSON.stringify(favorites));

// 读取
JSON.parse(localStorage.getItem('favorites') || '[]')
```

### 6. 分享功能

```javascript
function shareReport() {
    const url = window.location.href;
    navigator.clipboard.writeText(url);
    alert('链接已复制');
}
```

### 7. 返回顶部

```javascript
// 显示条件
window.scrollY > 300

// 点击
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
```

---

## 四、页面跳转

| 触发 | 目标页面 | 说明 |
|------|----------|------|
| 论文卡片点击 | docs/insights/{date}_{arxiv_id}.html | 增强版解读 |
| "更多文章"按钮 | articles.html | 全部文章（未实现） |
| "更多论文"按钮 | papers.html | 全部论文（未实现） |
| 归档日期点击 | archive/{date}/index.html | 历史日报 |

---

## 五、待完善功能

### 1. 未实现的页面
- [ ] articles.html - 全部文章列表页
- [ ] papers.html - 全部论文列表页

### 2. 待优化功能
- [ ] 搜索结果高亮
- [ ] 收藏同步到云端
- [ ] 离线缓存
- [ ] 暗黑模式

### 3. 已知问题
- [ ] 部分GitHub项目缺少cn_summary
- [ ] 部分论文摘要未翻译
- [ ] 顶会论文数据不完整

---

## 六、样式规范

### 1. 颜色
```css
--color-primary: #667eea
--color-secondary: #764ba2
--color-text: #333
--color-text-light: #666
--bg: #fafafa
--bg-card: #fff
```

### 2. 圆角
```css
卡片: 14px
按钮: 20px
Modal: 20px 20px 0 0
```

### 3. 阴影
```css
卡片: 0 2px 12px rgba(49,44,81,0.05)
Modal: 0 -4px 20px rgba(0,0,0,0.1)
```

---

*文档更新时间: 2026-04-19*
