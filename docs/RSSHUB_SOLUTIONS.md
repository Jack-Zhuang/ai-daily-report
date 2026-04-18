# RSSHub 解决方案

## 问题分析

公共RSSHub实例不稳定，经常超时。以下是几种解决方案：

---

## 方案1: 自建RSSHub（推荐）

### Docker部署（最简单）
```bash
# 拉取镜像
docker pull diygod/rsshub

# 启动服务
docker run -d --name rsshub -p 1200:1200 diygod/rsshub

# 使用
# http://localhost:1200/zhihu/topic/19554298
```

### Docker Compose部署（生产环境）
```yaml
# docker-compose.yml
version: '3'
services:
  rsshub:
    image: diygod/rsshub
    restart: always
    ports:
      - "1200:1200"
    environment:
      NODE_ENV: production
      CACHE_TYPE: redis
      REDIS_URL: redis://redis:6379/
      PUPPETEER_WS_ENDPOINT: ws://browserless:3000
    depends_on:
      - redis
      - browserless

  redis:
    image: redis:alpine
    restart: always
    volumes:
      - redis-data:/data

  browserless:
    image: browserless/chrome
    restart: always

volumes:
  redis-data:
```

```bash
docker-compose up -d
```

---

## 方案2: 使用第三方RSS服务

### 2.1 Feed43（无需部署）
- 网址: http://feed43.com/
- 将任意网页转为RSS
- 免费版有限制，付费版更稳定

### 2.2 Huginn（自建自动化）
- GitHub: https://github.com/huginn/huginn
- 可抓取任意网站生成RSS
- 支持复杂的数据处理流程

```bash
docker run -d --name huginn -p 3000:3000 huginn/huginn
```

---

## 方案3: 直接调用API（绕过RSS）

### 3.1 知乎API
```python
import requests

# 知乎话题API
url = "https://www.zhihu.com/api/v4/topics/19554298/feeds/essence"
headers = {
    'User-Agent': 'Mozilla/5.0...',
    'x-api-version': '3.0.40'
}
response = requests.get(url, headers=headers)
```

### 3.2 微信公众号（通过搜狗微信）
```python
# 搜狗微信搜索
url = "https://weixin.sogou.com/weixin"
params = {
    'type': 1,  # 公众号
    'query': '机器之心'
}
```

---

## 方案4: 使用备用数据源

### 4.1 技术博客RSS（更稳定）
- 美团技术团队: `https://tech.meituan.com/feed`
- 字节跳动: `https://juejin.cn/rss`
- InfoQ: `https://www.infoq.cn/feed`

### 4.2 arXiv API（最稳定）
```python
import arxiv

# 搜索推荐系统论文
search = arxiv.Search(
    query="recommendation system",
    max_results=10,
    sort_by=arxiv.SortCriterion.SubmittedDate
)
```

---

## 方案5: 混合方案（当前采用）

```python
# 优先级顺序
sources = [
    1. 技术博客RSS（稳定）
    2. arXiv API（最稳定）
    3. 知乎/微信（RSSHub，可能超时）
    4. 备用模拟数据（兜底）
]
```

---

## 推荐方案

**短期**：使用方案5（混合方案），已实现

**中期**：自建RSSHub（方案1），需要服务器

**长期**：直接调用各平台API（方案3），需要申请API权限

---

## 需要您提供

1. **服务器**：用于部署RSSHub（可选）
2. **API权限**：知乎/微信公众号开发者权限（可选）
3. **确认方案**：选择哪种方案继续？
