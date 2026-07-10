#!/usr/bin/env python3
"""
Mock LLM Summarizer — 离线占位摘要生成
无需 API key，用预设模板填充中文摘要
"""

import json
import random
from pathlib import Path

random.seed(42)

# ── 预设摘要模板 ──────────────────────────────────────────────

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

# ── 公开接口 ──────────────────────────────────────────────────

def needs_llm_summary(cn_summary: str, original_summary: str) -> bool:
    if cn_summary and len(cn_summary) > 30:
        return False
    return True

def generate_all_summaries(data_file: Path, force: bool = False):
    """为 data_file 中的所有条目生成占位摘要"""
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    changed = False

    for paper in data.get('arxiv_papers', []):
        if force or needs_llm_summary(paper.get('cn_summary', ''), paper.get('summary', '')):
            paper['cn_summary'] = _gen_mock_paper_summary(paper)
            changed = True

    for article in data.get('articles', data.get('hot_articles', [])):
        if force or needs_llm_summary(article.get('cn_summary', ''), article.get('summary', '')):
            article['cn_summary'] = _gen_mock_article_summary(article)
            changed = True

    for proj in data.get('github_projects', data.get('github_trending', [])):
        if force or needs_llm_summary(proj.get('cn_description', ''), proj.get('description', '')):
            proj['cn_description'] = _gen_mock_github_summary(proj)
            changed = True

    # 同步 cn_summary 到 daily_pick
    sync_daily_pick_summaries(data)

    if changed:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  ✅ 摘要已更新")
    else:
        print(f"  ℹ️  所有条目已有摘要，无需更新")

def sync_daily_pick_summaries(data: dict):
    """把完整条目的摘要同步到 daily_pick 中的对应项"""
    pick_map = {}
    # 构建索引
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
        # 尝试所有可能的键
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
