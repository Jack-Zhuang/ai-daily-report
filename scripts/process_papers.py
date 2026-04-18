#!/usr/bin/env python3
"""
AI推荐日报 - 论文处理脚本
下载论文、解析内容、生成中文摘要
"""

import json
import urllib.request
import re
import os
from pathlib import Path

class PaperProcessor:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.cache_dir = self.base_dir / "cache" / "papers"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def download_paper_source(self, arxiv_id: str) -> Path:
        """下载论文 TeX 源码"""
        # 规范化 ID
        safe_id = arxiv_id.replace('.', '_')
        tar_path = self.cache_dir / f"{safe_id}.tar.gz"
        extract_dir = self.cache_dir / safe_id
        
        if extract_dir.exists():
            print(f"  ✓ 已存在: {safe_id}")
            return extract_dir
        
        # 下载
        url = f"https://www.arxiv.org/src/{arxiv_id}"
        print(f"  下载: {url}")
        
        try:
            urllib.request.urlretrieve(url, tar_path)
            
            # 解压
            import tarfile
            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(extract_dir)
            
            print(f"  ✓ 解压完成")
            return extract_dir
        except Exception as e:
            print(f"  ✗ 下载失败: {e}")
            return None
    
    def find_main_tex(self, extract_dir: Path) -> Path:
        """查找主 TeX 文件"""
        for name in ['main.tex', 'paper.tex', 'article.tex']:
            path = extract_dir / name
            if path.exists():
                return path
        
        # 查找第一个 .tex 文件
        for path in extract_dir.glob('*.tex'):
            if 'bib' not in path.name.lower():
                return path
        
        return None
    
    def extract_abstract(self, tex_path: Path) -> str:
        """从 TeX 文件提取摘要"""
        if not tex_path or not tex_path.exists():
            return ""
        
        try:
            with open(tex_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 查找 \begin{abstract}...\end{abstract}
            match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', 
                            content, re.DOTALL)
            if match:
                abstract = match.group(1)
                # 清理 LaTeX 命令
                abstract = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', abstract)
                abstract = re.sub(r'\\[a-zA-Z]+', '', abstract)
                abstract = re.sub(r'[{}]', '', abstract)
                abstract = ' '.join(abstract.split())
                return abstract[:1000]
            
            return ""
        except Exception as e:
            print(f"    提取摘要失败: {e}")
            return ""
    
    def translate_to_chinese(self, text: str, title: str = "") -> tuple:
        """翻译为中文（简化版，实际应调用翻译API）"""
        # 这里使用简单的规则翻译
        # 实际应该调用 MiniMax 或其他翻译 API
        
        # 常见术语翻译
        translations = {
            'recommendation': '推荐',
            'recommender': '推荐',
            'agent': '智能体',
            'LLM': '大语言模型',
            'large language model': '大语言模型',
            'collaborative filtering': '协同过滤',
            'neural network': '神经网络',
            'deep learning': '深度学习',
            'machine learning': '机器学习',
            'attention': '注意力',
            'transformer': 'Transformer',
            'user': '用户',
            'item': '物品',
            'rating': '评分',
            'preference': '偏好',
        }
        
        # 简单替换
        cn_text = text
        for en, cn in translations.items():
            cn_text = cn_text.replace(en, cn)
        
        # 生成中文标题（简化）
        cn_title = title
        for en, cn in translations.items():
            cn_title = cn_title.replace(en, cn)
        
        return cn_title, cn_text
    
    def process_paper(self, paper: dict) -> dict:
        """处理单篇论文"""
        arxiv_id = paper.get('id', paper.get('arxiv_id', ''))
        title = paper.get('title', '')
        summary = paper.get('summary', '')
        
        print(f"\n处理: {title[:50]}...")
        
        # 尝试下载源码
        extract_dir = self.download_paper_source(arxiv_id)
        
        if extract_dir:
            # 查找主文件
            tex_path = self.find_main_tex(extract_dir)
            if tex_path:
                # 提取摘要
                abstract = self.extract_abstract(tex_path)
                if abstract:
                    summary = abstract
                    print(f"  ✓ 提取到摘要: {len(abstract)}字")
        
        # 翻译
        cn_title, cn_summary = self.translate_to_chinese(summary, title)
        
        # 更新论文信息
        paper['cn_title'] = cn_title if cn_title != title else title
        paper['cn_summary'] = cn_summary if cn_summary != summary else summary
        paper['summary'] = summary
        
        return paper
    
    def process_all(self, papers: list) -> list:
        """处理所有论文"""
        processed = []
        for paper in papers:
            try:
                p = self.process_paper(paper)
                processed.append(p)
            except Exception as e:
                print(f"  ✗ 处理失败: {e}")
                processed.append(paper)
        
        return processed


if __name__ == "__main__":
    import sys
    
    # 加载论文
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'cache/arxiv_papers.json'
    with open(input_file, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    print(f"加载 {len(papers)} 篇论文")
    
    # 处理
    processor = PaperProcessor()
    processed = processor.process_all(papers[:10])  # 先处理前10篇
    
    # 保存
    output_file = 'cache/arxiv_papers_processed.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已处理 {len(processed)} 篇论文")
    print(f"保存到: {output_file}")
