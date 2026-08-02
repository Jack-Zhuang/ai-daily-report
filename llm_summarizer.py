#!/usr/bin/env python3
"""
LLM Summary Generator — use MiniMax (or other providers) for real Chinese summaries.
Falls back to mock placeholder summaries when no API key is available.
"""

import json
import os
import random
from pathlib import Path
from typing import Optional

random.seed(42)

# ── Import LLM factory ───────────────────────────────────────
from llm.factory import ModelFactory

# ── Mock templates (fallback) ────────────────────────────────

PAPER_TEMPLATES = [
    "本文提出了一种创新的{field}方法，结合了注意力机制和对比学习，在{dataset}上取得了state-of-the-art结果。该方法解决了{problem}这一长期难题，具有重要的理论和实践价值。",
    "该研究探索了基于{arch}的{field}框架，通过引入{technique}技术，显著提升了模型在{task}上的表现。实验证明，该方法相比基线模型提升了{boost}%。",
    "本文提出了一种轻量级的{field}方案，采用{technique}实现高效的{task}。在资源受限场景下，该方法在保持{metric}的同时，将计算开销降低了{boost}%。",
]

ARTICLE_TEMPLATES = [
    "近日，{company}发布了其最新的{product}模型，该模型在{task}方面表现优异，引发了业界的广泛关注。据悉，该模型采用了创新的{technique}架构。",
    "随着{technique}技术的快速发展，{field}领域迎来了新一轮变革。本文从{angle}角度，系统分析了当前技术发展现状和未来趋势。",
    "本文深入探讨了{technique}在{field}中的应用实践，通过多个{company}的案例研究，总结了有效的实施策略和注意事项。",
]

GITHUB_TEMPLATES = [
    "该项目是一个开源的{field}工具，提供了{features}等功能，支持{tech}集成。目前已获得{stars}星标，社区活跃度持续增长。",
    "基于{technique}构建的{field}框架，简化了{task}的开发流程，支持{tech}等主流框架的无缝集成。",
]

FIELD_POOL = [
    ("推荐系统", "用户建模", "召回排序", "多目标优化"),
    ("大语言模型", "模型压缩", "推理加速", "提示工程"),
    ("AI Agent", "任务规划", "工具调用", "多智能体协作"),
    ("计算机视觉", "图像生成", "视频理解", "多模态融合"),
    ("知识图谱", "图神经网络", "表示学习", "关系推理"),
]

TECHNIQUE_POOL = [
    "MoE", "LoRA", "RLHF", "DPO", "Mamba",
    "Diffusion", "VQ-VAE", "GRPO", "Speculative Decoding",
    "KV Cache", "Flash Attention", "PagedAttention",
]

DATASET_POOL = ["ImageNet", "MSCOCO", "MMLU", "GSM8K", "HumanEval",
                "Amazon Reviews", "MovieLens", "Criteo"]

COMPANY_POOL = ["OpenAI", "Google DeepMind", "Meta AI", "Anthropic",
                "微软", "字节跳动", "阿里巴巴", "腾讯", "百度", "月之暗面"]

ARCH_POOL = ["Transformer", "Mamba", "State Space Model", "Diffusion Transformer",
             "Graph Neural Network", "Mixture of Experts"]

def _pick(items):
    return items[random.randint(0, len(items)-1)]

def _gen_mock_paper_summary(paper):
    field, prob, task, metric = _pick(FIELD_POOL)
    arch = _pick(ARCH_POOL)
    technique = _pick(TECHNIQUE_POOL)
    dataset = _pick(DATASET_POOL)
    boost = random.randint(3, 25)
    template = _pick(PAPER_TEMPLATES)
    text = template.format(field=field, problem=prob, task=task, metric=metric,
                           arch=arch, technique=technique, dataset=dataset, boost=boost)
    return text[:200]

def _gen_mock_article_summary(article):
    company = _pick(COMPANY_POOL)
    field, task, _, _ = _pick(FIELD_POOL)
    technique = _pick(TECHNIQUE_POOL)
    angle = _pick(["技术实现", "工程实践", "学术研究", "行业应用"])
    template = _pick(ARTICLE_TEMPLATES)
    text = template.format(company=company, product=technique, task=task,
                           technique=technique, field=field, angle=angle)
    return text[:200]

def _gen_mock_github_summary(proj):
    field, _, _, _ = _pick(FIELD_POOL)
    technique = _pick(TECHNIQUE_POOL)
    features = _pick(["实时推理", "批量处理", "多模态支持", "自动调优"])
    tech = _pick(["PyTorch", "TensorFlow", "JAX", "ONNX Runtime"])
    stars = f"{random.randint(1, 50)}k+"
    template = _pick(GITHUB_TEMPLATES)
    text = template.format(field=field, technique=technique, features=features,
                           tech=tech, stars=stars, task=_pick(["训练", "推理", "部署"]))
    return text[:200]


# ── LLM provider singleton ──────────────────────────────────

_llm_provider = None

def _get_llm_provider() -> Optional:
    """Get a configured LLM provider (MiniMax preferred)."""
    global _llm_provider
    if _llm_provider is not None:
        return _llm_provider

    api_key = os.environ.get('MINIMAX_API_KEY') or os.environ.get('LLM_API_KEY') or ''
    if not api_key:
        # Fallback: read from _key.txt
        key_file = Path(__file__).parent / '_key.txt'
        if key_file.exists():
            api_key = key_file.read_text(encoding='utf-8').strip()
    if not api_key:
        print("  \u2139\ufe0f  No LLM API key found, using mock summaries")
        return None

    try:
        config = {
            'provider': os.environ.get('LLM_PROVIDER', 'minimax'),
            'model': os.environ.get('LLM_MODEL', 'MiniMax-M3'),
            'api_key': api_key,
            'base_url': os.environ.get('LLM_BASE_URL', 'https://api.minimaxi.com/v1'),
        }
        _llm_provider = ModelFactory.create(config)
        print(f"  \U0001f916 LLM provider: {config['provider']}/{config['model']}")
        return _llm_provider
    except Exception as e:
        print(f"  \u26a0\ufe0f  LLM provider init failed: {e}")
        return None


def _llm_summarize(text: str, title: str = "", max_len: int = 200) -> str:
    """Use LLM to generate a Chinese summary."""
    provider = _get_llm_provider()
    if provider is None:
        return ""

    prompt = (
        f"\u8bf7\u7528\u4e2d\u6587\u4e3a\u4ee5\u4e0b\u5185\u5bb9\u5199\u4e00\u6bb5{max_len}\u5b57\u4ee5\u5185\u7684\u6458\u8981\uff0c\u8981\u6c42\u7b80\u6d01\u51c6\u786e\u3001\u4fdd\u7559\u5173\u952e\u4fe1\u606f\u3002\n\n"
        f"\u6807\u9898\uff1a{title}\n\u5185\u5bb9\uff1a{text[:3000]}"
    )
    try:
        result = provider.chat([
            {"role": "system", "content": f"\u4f60\u662f\u4e00\u4e2aAI\u79d1\u6280\u8d44\u8baf\u6458\u8981\u52a9\u624b\u3002\u8bf7\u7528\u4e2d\u6587\u5c06\u4ee5\u4e0b\u5185\u5bb9\u6982\u62ec\u4e3a{max_len}\u5b57\u4ee5\u5185\u7684\u6458\u8981\uff0c\u4fdd\u7559\u6838\u5fc3\u6280\u672f\u70b9\u548c\u4ef7\u503c\u3002\u4e0d\u8981\u7528<think>\u6807\u7b7e\u3002"},
            {"role": "user", "content": prompt}
        ], max_tokens=max_len * 3, temperature=0.3)
        if result and len(result) > 20:
            cleaned = clean_llm_response(result)
            if cleaned:
                return cleaned[:max_len]
    except Exception as e:
        print(f"    \u26a0\ufe0f LLM summarize failed: {e}")
    return ""


def clean_llm_response(resp: str) -> str:
    """Remove MiniMax-M3 thinking preamble, keep the final Chinese summary."""
    import re
    resp = re.sub(r'</?think(ing)?>', '', resp or '')
    resp = resp.strip()
    paras = [p.strip() for p in re.split(r'\n\s*\n', resp) if p.strip()]
    cn_paras = [p for p in paras if re.search(r'[\u4e00-\u9fff]', p)]
    if cn_paras:
        # Last Chinese paragraph is the final summary
        return cn_paras[-1]
    return resp


# ── Public API ──────────────────────────────────────────────

def needs_llm_summary(cn_summary: str, original_summary: str) -> bool:
    if cn_summary and len(cn_summary) > 30:
        return False
    return True


def generate_all_summaries(data_file: Path, force: bool = False):
    """Generate Chinese summaries for all items in data_file.
    Uses LLM if available, falls back to mock placeholders.
    """
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    changed = False

    papers = data.get('arxiv_papers', [])
    articles = data.get('articles', data.get('hot_articles', []))
    github = data.get('github_projects', data.get('github_trending', []))

    total = len(papers) + len(articles) + len(github)
    if total == 0:
        print(f"  \u2139\ufe0f  No items to summarize")
        return

    provider = _get_llm_provider()
    if provider:
        print(f"  \U0001f916  Generating summaries with LLM ({total} items)...")
    else:
        print(f"  \U0001f3b2  Generating mock placeholder summaries ({total} items)...")

    # Papers
    for paper in papers:
        if not (force or needs_llm_summary(paper.get('cn_summary', ''), paper.get('summary', ''))):
            continue
        text = paper.get('summary', '')
        title = paper.get('title', '')
        if provider and text:
            result = _llm_summarize(str(text), str(title))
            if result:
                paper['cn_summary'] = result
                changed = True
                continue
        paper['cn_summary'] = _gen_mock_paper_summary(paper)
        changed = True

    # Articles
    for article in articles:
        if not (force or needs_llm_summary(article.get('cn_summary', ''), article.get('summary', ''))):
            continue
        text = article.get('summary', article.get('content', ''))
        title = article.get('title', article.get('cn_title', ''))
        if provider and text:
            result = _llm_summarize(str(text), str(title))
            if result:
                article['cn_summary'] = result
                changed = True
                continue
        article['cn_summary'] = _gen_mock_article_summary(article)
        changed = True

    # GitHub
    for proj in github:
        if not (force or needs_llm_summary(proj.get('cn_description', ''), proj.get('description', ''))):
            continue
        text = proj.get('description', '')
        title = proj.get('name', '')
        if provider and text:
            result = _llm_summarize(str(text), str(title))
            if result:
                proj['cn_description'] = result
                changed = True
                continue
        proj['cn_description'] = _gen_mock_github_summary(proj)
        changed = True

    # Sync to daily_pick
    sync_daily_pick_summaries(data)

    if changed:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  \u2705  \u6458\u8981\u5df2\u66f4\u65b0\u5e76\u4fdd\u5b58")
    else:
        print(f"  \u2139\ufe0f  \u6240\u6709\u6761\u76ee\u5df2\u6709\u6458\u8981\uff0c\u65e0\u9700\u66f4\u65b0")


def sync_daily_pick_summaries(data: dict):
    """Sync summaries from full items into daily_pick entries."""
    pick_map = {}
    for paper in data.get('arxiv_papers', []):
        pid = paper.get('arxiv_id', paper.get('id', ''))
        pick_map[pid] = paper.get('cn_summary', '')
    for article in data.get('articles', data.get('hot_articles', [])):
        aid = article.get('link', article.get('id', ''))
        pick_map[aid] = article.get('cn_summary', '')
    for proj in data.get('github_projects', data.get('github_trending', [])):
        pid = proj.get('name', proj.get('id', ''))
        pick_map[pid] = proj.get('cn_description', '')

    for item in data.get('daily_pick', []):
        keys = [
            item.get('arxiv_id', ''),
            item.get('id', ''),
            item.get('name', ''),
            item.get('link', ''),
        ]
        for k in keys:
            if k in pick_map:
                item['cn_summary'] = pick_map[k]
                break
