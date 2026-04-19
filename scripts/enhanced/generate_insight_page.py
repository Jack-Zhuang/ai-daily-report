#!/usr/bin/env python3
"""
AI推荐日报 - 增强版论文解读页面生成器
支持 Markdown、LaTeX 公式、Mermaid 流程图渲染
"""

import json
import re
from pathlib import Path
from datetime import datetime


def generate_insight_page(md_content: str, arxiv_id: str, title: str) -> str:
    """生成增强版论文解读 HTML 页面"""
    
    # 简单的 Markdown 转 HTML
    html_content = markdown_to_html(md_content)
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - AI推荐日报</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
    
    <style>
        :root {{
            --color-primary: #667eea;
            --color-secondary: #764ba2;
            --color-text: #333;
            --color-text-light: #666;
            --bg: #fafafa;
            --bg-card: #fff;
            --border: #e0e0e0;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: var(--bg);
            color: var(--color-text);
            line-height: 1.8;
            -webkit-font-smoothing: antialiased;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        /* 导航栏 */
        .nav {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            z-index: 100;
            padding: 12px 20px;
        }}
        
        .nav-content {{
            max-width: 900px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .nav-brand {{
            font-weight: 600;
            color: var(--color-primary);
            text-decoration: none;
        }}
        
        .nav-links a {{
            color: var(--color-text-light);
            text-decoration: none;
            margin-left: 20px;
            font-size: 14px;
        }}
        
        .nav-links a:hover {{
            color: var(--color-primary);
        }}
        
        /* 文章内容 */
        article {{
            background: var(--bg-card);
            border-radius: 16px;
            padding: 40px;
            margin-top: 60px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        }}
        
        h1 {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 12px;
            color: var(--color-text);
            line-height: 1.4;
        }}
        
        h2 {{
            font-size: 22px;
            font-weight: 600;
            margin: 40px 0 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--color-primary);
            color: var(--color-text);
        }}
        
        h3 {{
            font-size: 18px;
            font-weight: 600;
            margin: 30px 0 15px;
            color: var(--color-text);
        }}
        
        h4 {{
            font-size: 16px;
            font-weight: 600;
            margin: 20px 0 10px;
            color: var(--color-text);
        }}
        
        p {{
            margin-bottom: 16px;
            color: var(--color-text);
        }}
        
        a {{
            color: var(--color-primary);
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        /* 引用块 */
        blockquote {{
            border-left: 4px solid var(--color-primary);
            padding: 12px 20px;
            margin: 20px 0;
            background: #f8f9ff;
            border-radius: 0 8px 8px 0;
            color: var(--color-text-light);
        }}
        
        /* 代码块 */
        pre {{
            background: #f6f8fa;
            border-radius: 8px;
            padding: 16px;
            overflow-x: auto;
            margin: 16px 0;
            font-size: 14px;
        }}
        
        code {{
            font-family: 'SF Mono', 'Fira Code', monospace;
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        
        pre code {{
            background: none;
            padding: 0;
        }}
        
        /* 表格 */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        
        th {{
            background: #f8f9ff;
            font-weight: 600;
        }}
        
        tr:hover {{
            background: #fafafa;
        }}
        
        /* 列表 */
        ul, ol {{
            margin: 16px 0;
            padding-left: 24px;
        }}
        
        li {{
            margin-bottom: 8px;
        }}
        
        /* 标签 */
        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 16px 0;
        }}
        
        .tag {{
            background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }}
        
        /* 元信息 */
        .meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin: 16px 0;
            color: var(--color-text-light);
            font-size: 14px;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        /* 公式样式 */
        .MathJax {{
            font-size: 1.1em !important;
        }}
        
        /* Mermaid 图表 */
        .mermaid {{
            background: #fafafa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
        }}
        
        /* 图片 */
        img {{
            max-width: 100%;
            border-radius: 8px;
            margin: 16px 0;
        }}
        
        /* 分隔线 */
        hr {{
            border: none;
            height: 1px;
            background: var(--border);
            margin: 40px 0;
        }}
        
        /* 页脚 */
        .footer {{
            text-align: center;
            padding: 40px 20px;
            color: var(--color-text-light);
            font-size: 14px;
        }}
        
        /* 响应式 */
        @media (max-width: 768px) {{
            article {{
                padding: 24px;
                margin-top: 50px;
            }}
            
            h1 {{ font-size: 24px; }}
            h2 {{ font-size: 20px; }}
        }}
    </style>
    
    <!-- MathJax 支持 -->
    <script>
        MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
                processEscapes: true
            }},
            options: {{
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
            }}
        }};
    </script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>
    
    <!-- Mermaid 支持 -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'neutral',
            themeVariables: {{
                primaryColor: '#667eea',
                primaryTextColor: '#fff',
                primaryBorderColor: '#764ba2',
                lineColor: '#666',
                secondaryColor: '#f0f0f0',
                tertiaryColor: '#fff'
            }}
        }});
    </script>
    
    <!-- 代码高亮 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            document.querySelectorAll('pre code').forEach(block => {{
                hljs.highlightElement(block);
            }});
        }});
    </script>
</head>
<body>
    <nav class="nav">
        <div class="nav-content">
            <a href="../index.html" class="nav-brand">
                <i class="fas fa-robot"></i> AI推荐日报
            </a>
            <div class="nav-links">
                <a href="https://arxiv.org/abs/{arxiv_id}" target="_blank">
                    <i class="fas fa-external-link-alt"></i> arXiv
                </a>
                <a href="../index.html">
                    <i class="fas fa-home"></i> 首页
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <article>
            {html_content}
        </article>
        
        <footer class="footer">
            <p>本文由 AI 推荐日报自动生成，仅供参考学习</p>
            <p style="margin-top: 8px;">
                <a href="https://github.com/Jack-Zhuang/ai-daily-report" target="_blank">
                    <i class="fab fa-github"></i> GitHub
                </a>
            </p>
        </footer>
    </div>
</body>
</html>"""
    
    return html


def markdown_to_html(md: str) -> str:
    """简单的 Markdown 转 HTML"""
    
    # 处理标题
    md = re.sub(r'^# (.+)$', r'<h1>\1</h1>', md, flags=re.MULTILINE)
    md = re.sub(r'^## (.+)$', r'<h2>\1</h2>', md, flags=re.MULTILINE)
    md = re.sub(r'^### (.+)$', r'<h3>\1</h3>', md, flags=re.MULTILINE)
    md = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', md, flags=re.MULTILINE)
    
    # 处理粗体
    md = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', md)
    
    # 处理斜体
    md = re.sub(r'\*(.+?)\*', r'<em>\1</em>', md)
    
    # 处理行内代码
    md = re.sub(r'`([^`]+)`', r'<code>\1</code>', md)
    
    # 处理代码块（保留语言标记）
    md = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code class="\1">\2</code></pre>', md, flags=re.DOTALL)
    
    # 处理 Mermaid 代码块
    md = re.sub(r'```mermaid\n(.*?)```', r'<div class="mermaid">\1</div>', md, flags=re.DOTALL)
    
    # 处理引用块
    md = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', md, flags=re.MULTILINE)
    
    # 处理无序列表
    md = re.sub(r'^- (.+)$', r'<li>\1</li>', md, flags=re.MULTILINE)
    md = re.sub(r'(<li>.*</li>\n?)+', r'<ul>\g<0></ul>', md)
    
    # 处理有序列表
    md = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', md, flags=re.MULTILINE)
    
    # 处理链接
    md = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', md)
    
    # 处理分隔线
    md = re.sub(r'^---$', r'<hr>', md, flags=re.MULTILINE)
    
    # 处理段落（非标签开头的行）
    lines = md.split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append('')
        elif stripped.startswith('<'):
            result.append(line)
        else:
            result.append(f'<p>{stripped}</p>')
    
    # 合并连续的空段落
    html = '\n'.join(result)
    html = re.sub(r'(<p></p>\n?)+', '', html)
    
    return html


def process_all_insights():
    """处理所有增强版解读"""
    base_dir = Path(__file__).parent.parent
    insights_dir = base_dir / "insights_enhanced"
    output_dir = base_dir / "docs" / "insights"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for md_file in insights_dir.glob("*.md"):
        print(f"处理: {md_file.name}")
        
        # 读取 Markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # 提取 arxiv_id
        match = re.search(r'(\d{4}\.\d{4,5})', md_file.name)
        arxiv_id = match.group(1) if match else ""
        
        # 提取标题
        title_match = re.search(r'^# (.+)$', md_content, re.MULTILINE)
        title = title_match.group(1) if title_match else md_file.stem
        
        # 生成 HTML
        html = generate_insight_page(md_content, arxiv_id, title)
        
        # 保存
        output_file = output_dir / f"{md_file.stem}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"  ✅ 已生成: {output_file}")


if __name__ == "__main__":
    process_all_insights()
