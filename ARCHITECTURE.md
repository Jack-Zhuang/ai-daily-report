# AI推荐日报 - 项目架构规范

> **重要**: 此文档定义了项目的文件结构和路径规范，所有修改必须遵循此规范！

## 1. GitHub Pages 配置

- **Pages 源目录**: `/docs`
- **访问 URL**: `https://jack-zhuang.github.io/ai-daily-report/`
- **关键规则**: 只有 `docs/` 目录下的文件会被部署到线上

## 2. 文件结构规范

```
ai_daily/
├── docs/                          # GitHub Pages 根目录（唯一部署源）
│   ├── index.html                 # 主页（唯一版本）
│   ├── conferences/               # 会议论文列表页面
│   │   ├── arXiv_2026.html       # arXiv 论文列表
│   │   ├── KDD_2025.html
│   │   ├── WSDM_2025.html
│   │   └── ...
│   ├── insights/                  # 论文解读页面
│   │   ├── figures/              # 论文图表
│   │   │   └── 2604_21593/
│   │   │       ├── fig_1.jpeg
│   │   │       └── ...
│   │   └── 2026-04-26_2604_21593.html
│   ├── covers/                    # 封面图
│   └── archive/                   # 归档
│
├── index.html                     # 开发版本（需同步到 docs/）
├── conferences/                   # 开发版本（仅用于本地开发）
│   └── arXiv_2026/
│       └── index.html
│
├── cache/                         # 数据缓存（不部署）
│   ├── arxiv_cache.json
│   └── github_cache.json
│
└── daily_data/                    # 原始数据（不部署）
```

## 3. 路径引用规范

### 3.1 在 `docs/index.html` 中的引用

由于 `docs/` 是 GitHub Pages 的根目录，所有路径都相对于 `docs/`：

```html
<!-- 正确 -->
<a href="conferences/arXiv_2026.html">arXiv 论文</a>
<a href="insights/2026-04-26_2604_21593.html">论文解读</a>
<img src="covers/xxx.jpg">

<!-- 错误 -->
<a href="docs/conferences/...">  <!-- 多了 docs/ 前缀 -->
<a href="conferences/arXiv_2026/index.html">  <!-- 应该是 .html 文件 -->
```

### 3.2 在 `docs/conferences/*.html` 中的引用

```html
<!-- 返回主页 -->
<a href="../index.html">返回日报</a>

<!-- 跳转到论文解读 -->
<a href="../insights/2026-04-26_2604_21593.html">查看解读</a>
```

### 3.3 在 `docs/insights/*.html` 中的引用

```html
<!-- 引用图表 -->
<img src="figures/2604_21593/fig_1.jpeg">

<!-- 返回主页 -->
<a href="../index.html">返回日报</a>
```

## 4. 文件命名规范

| 类型 | 命名格式 | 示例 |
|------|----------|------|
| 主页 | `index.html` | `docs/index.html` |
| 会议页面 | `{会议名}_{年份}.html` | `docs/conferences/KDD_2025.html` |
| 论文解读 | `{日期}_{论文ID}.html` | `docs/insights/2026-04-26_2604_21593.html` |
| 论文图表 | `fig_{序号}.jpeg` | `docs/insights/figures/2604_21593/fig_1.jpeg` |

## 5. 同步规则

### 5.1 主页同步

根目录的 `index.html` 是开发版本，修改后必须同步到 `docs/index.html`：

```bash
cp index.html docs/index.html
# 然后修复路径引用
sed -i 's|docs/insights/|insights/|g' docs/index.html
sed -i 's|docs/conferences/|conferences/|g' docs/index.html
sed -i 's|conferences/\([^/]*\)/index\.html|conferences/\1.html|g' docs/index.html
```

### 5.2 会议页面同步

```bash
# 从开发目录同步到 docs
cp conferences/arXiv_2026/index.html docs/conferences/arXiv_2026.html
```

## 6. Git 提交检查清单

每次提交前必须检查：

- [ ] `docs/index.html` 是否是最新版本
- [ ] 所有路径引用是否正确（无 `docs/` 前缀）
- [ ] 会议页面是否同步到 `docs/conferences/`
- [ ] 论文解读页面是否在 `docs/insights/`
- [ ] 图表文件是否在 `docs/insights/figures/`

## 7. 常见错误及修复

| 错误 | 原因 | 修复方法 |
|------|------|----------|
| 页面 404 | 文件不在 `docs/` 目录 | 复制到 `docs/` 对应位置 |
| 链接失效 | 路径多了 `docs/` 前缀 | 使用相对路径，去掉 `docs/` |
| 图片不显示 | 图表路径错误 | 检查 `figures/` 相对路径 |
| 内容不更新 | 只修改了根目录文件 | 同步到 `docs/` 目录 |

## 8. 自动化脚本

创建同步脚本 `sync_to_docs.sh`：

```bash
#!/bin/bash
# 同步所有文件到 docs 目录

# 同步主页
cp index.html docs/index.html
sed -i 's|docs/insights/|insights/|g' docs/index.html
sed -i 's|docs/conferences/|conferences/|g' docs/index.html

# 同步会议页面
for conf in conferences/*/; do
    name=$(basename "$conf")
    if [ -f "${conf}index.html" ]; then
        cp "${conf}index.html" "docs/conferences/${name}.html"
    fi
done

echo "同步完成！"
```

---

**最后更新**: 2026-04-26
**维护者**: AI推荐日报项目组
