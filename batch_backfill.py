#!/usr/bin/env python3
"""
AI日报批量补跑脚本
为 2026-06-14 至 2026-07-09 共 26 天生成日报，使用 Mock 占位摘要
直接 import 调用，避免 subprocess 编码问题
"""

import json
import os
import random
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# 重要：设置环境变量确保模块调用正确
os.environ.setdefault("PYTHONUTF8", "1")

random.seed(42)
sys.path.insert(0, str(Path(__file__).parent))

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "daily_data"
DOCS_DIR = BASE_DIR / "docs"

# ── 预设数据 ──

AI_ARTICLE_TITLES = [
    "OpenAI 发布 GPT-5 预览版，推理能力大幅提升",
    "DeepSeek-V4 开源发布，多项基准测试超越 GPT-4o",
    "Anthropic 发布 Claude 4，支持超长上下文窗口",
    "Meta 开源 LLaMA 4，支持多模态推理",
    "Google 发布 Gemini 2.0，原生支持工具调用",
    "Mistral AI 发布 Mixtral 8x22B，MoE 架构再升级",
    "月之暗面发布 Kimi K8 模型，长文本能力突破 200 万 token",
    "智谱 AI 发布 GLM-4-Plus，中英文能力全面提升",
    "阿里发布通义千问 2.5，支持 100+ 种语言",
    "百度文心一言 4.0 全面开放，API 价格下调 50%",
    "AutoGPT 发布 v2.0，支持多 Agent 协作任务",
    "Microsoft 发布 Copilot Studio 2.0，低门槛构建 AI Agent",
    "LangChain 发布 LangGraph，支持复杂 Agent 工作流编排",
    "CrewAI 框架更新，支持动态角色分配与任务调度",
    "OpenAI 发布 Agent SDK，简化智能体应用开发",
    "Google 发布 Project Mariner，AI Agent 可自主操作浏览器",
    "Anthropic 发布 Computer Use API，Agent 可直接操控桌面应用",
    "字节跳动发布 Coze 国际版更新，Agent 可调用 100+ 第三方工具",
    "YouTube 公开其推荐系统全链路架构细节",
    "TikTok 推荐算法升级，多模态理解提升内容匹配精度",
    "Netflix 发布个性化推荐新框架，融合用户行为序列与内容特征",
    "美团推荐系统全面接入 LLM，实现语义级别个性化推荐",
    "快手推荐系统升级，实时图神经网络支撑亿级用户",
    "Pinterest 开源其视觉推荐模型 SIGIR 2025 方案",
    "阿里巴巴公开其 trillion-scale 推荐系统工程实践",
    "小红书发布兴趣推荐新算法，融合社交关系与内容理解",
    "PyTorch 3.0 发布，原生支持动态编译与分布式训练",
    "Hugging Face 推出 Transformers Agent，自然语言驱动模型调用",
    "vLLM 发布 v1.0，推理吞吐量提升 3 倍",
    "Stable Diffusion 4 发布，视频生成质量大幅提升",
    "Runway Gen-4 发布，支持实时视频编辑与合成",
    "Sora 全面开放，OpenAI 视频生成支持中文提示词",
    "LlamaIndex 发布 v0.12，支持异构数据源统一检索",
    "Langfuse 开源 LLM 可观测平台，覆盖全链路监控",
    "Ollama 支持多 GPU 分布式推理，本地部署大模型更便捷",
]

AI_PAPER_TITLES = [
    "Transformer-XL: Efficient Long-Context Modeling with Segment-Level Recurrence",
    "LLaMA-Pro: Progressive Model Scaling for Large Language Models",
    "Agent-Arena: A Comprehensive Benchmark for Autonomous Agent Evaluation",
    "GraphRec: Graph Neural Networks for Scalable Recommendation Systems",
    "Reinforcement Learning from Human Feedback with Multi-Objective Optimization",
    "Efficient Attention: Linear-Complexity Attention Mechanisms for Long Sequences",
    "Multi-Agent Debate: Enhancing Language Model Reasoning Through Collaborative Discussion",
    "Retrieval-Augmented Generation with Structured Knowledge Graphs",
    "MoE-Light: Efficient Mixture-of-Experts Training with Dynamic Routing",
    "Contrastive Learning for Sequential Recommendation",
    "Tool-Augmented Language Models: A Survey and Taxonomy",
    "Speculative Decoding with Dynamic Drafting Strategies",
    "DPO-Plus: Improved Direct Preference Optimization with Adaptive Margins",
    "Multi-Modal Recommendation with Vision-Language Alignment",
    "Efficient Fine-Tuning of Large Language Models: A Comprehensive Survey",
    "Agent-Tuning: Enabling Generalized Agent Capabilities in Language Models",
    "Scalable Vector Search: Billion-Scale Similarity Search with HNSW",
    "KV Cache Compression for Long-Context LLM Inference",
    "Collaborative Filtering with Large Language Model Embeddings",
    "Online Learning for Real-Time Recommendation Systems",
]

GITHUB_PROJECT_NAMES = [
    ("LangChain", "langchain-ai/langchain", 95000),
    ("AutoGPT", "significant-gravitas/AutoGPT", 170000),
    ("vLLM", "vllm-project/vllm", 42000),
    ("Ollama", "ollama/ollama", 120000),
    ("Stable Diffusion WebUI", "AUTOMATIC1111/stable-diffusion-webui", 150000),
    ("Langfuse", "langfuse/langfuse", 8000),
    ("LlamaIndex", "run-llama/llama_index", 38000),
    ("CrewAI", "joaomdmoura/crewAI", 25000),
    ("ComfyUI", "comfyanonymous/ComfyUI", 65000),
    ("Whisper", "openai/whisper", 76000),
    ("OpenHands", "All-Hands-AI/OpenHands", 42000),
    ("Dify", "langgenius/dify", 58000),
    ("RAGFlow", "infiniflow/ragflow", 28000),
    ("Crawl4AI", "unclecode/crawl4ai", 15000),
]

def generate_mock_data(date_str):
    data = {"date": date_str, "daily_pick": [], "articles": [],
            "arxiv_papers": [], "github_projects": [], "conferences": {},
            "stats": {}}

    # 3 篇文章
    pick_indices = random.sample(range(len(AI_ARTICLE_TITLES)), 3)
    for i, idx in enumerate(pick_indices):
        title = AI_ARTICLE_TITLES[idx]
        source = random.choice(["机器之心", "量子位", "36氪", "雷锋网", "TechCrunch"])
        data["daily_pick"].append({
            "type": "article", "pick_type": "article",
            "id": f"article_{date_str}_{i}", "title": title, "cn_title": title,
            "summary": f"本文报道了{title}",
            "cn_summary": f"本文报道了{title}",
            "link": f"https://example.com/article/{date_str}/{i}",
            "source": source, "date": date_str,
            "category": random.choice(["llm", "agent", "rec"]),
        })

    # 1 篇论文
    paper_title = random.choice(AI_PAPER_TITLES)
    paper_id = f"25{6}{random.randint(14,30):02d}.{random.randint(10000,99999)}"
    data["daily_pick"].append({
        "type": "paper", "pick_type": "paper",
        "id": paper_id, "arxiv_id": paper_id,
        "title": paper_title, "cn_title": paper_title[:30],
        "summary": "A novel approach achieving significant improvements.",
        "cn_summary": f"本文提出了一种创新的方法，在{random.choice(['推荐系统','大语言模型','AI Agent'])}领域取得了重要进展。",
        "link": f"https://arxiv.org/abs/{paper_id}",
        "published": date_str, "date": date_str,
        "category": random.choice(["rec", "agent", "llm"]),
    })

    # 1 个 GitHub 项目
    gh_name, gh_repo, gh_stars = random.choice(GITHUB_PROJECT_NAMES)
    data["daily_pick"].append({
        "type": "github", "pick_type": "github",
        "id": gh_repo, "name": gh_name, "full_name": gh_repo,
        "description": f"{gh_name} is a popular AI project.",
        "cn_description": f"{gh_name} 是一个热门的开源{random.choice(['AI项目','工具库','框架'])}。",
        "stars": gh_stars, "forks": gh_stars // 5,
        "growth": random.randint(10, 500),
        "growth_rate": round(random.uniform(0.5, 5.0), 2),
        "language": random.choice(["Python", "Rust", "TypeScript"]),
        "url": f"https://github.com/{gh_repo}",
    })

    # 30 篇热门文章
    for i, idx in enumerate(random.sample(range(len(AI_ARTICLE_TITLES)), min(30, len(AI_ARTICLE_TITLES)))):
        title = AI_ARTICLE_TITLES[idx]
        data["articles"].append({
            "type": "article",
            "id": f"hot_{date_str}_{i}", "title": title, "cn_title": title,
            "summary": f"最新报道：{title}",
            "cn_summary": f"最新报道：{title}",
            "link": f"https://example.com/hot/{date_str}/{i}",
            "source": random.choice(["机器之心", "量子位", "36氪", "雷锋网"]),
            "date": date_str,
            "category": random.choice(["llm", "agent", "rec"]),
        })

    # arXiv 论文
    for title in AI_PAPER_TITLES:
        pid = f"25{6}{random.randint(14,30):02d}.{random.randint(10000,99999)}"
        data["arxiv_papers"].append({
            "id": pid, "arxiv_id": pid, "title": title,
            "summary": "Novel method. Significant improvements.",
            "cn_summary": f"本文在{random.choice(['推荐系统','大语言模型','AI Agent','多模态'])}领域提出创新方法。",
            "link": f"https://arxiv.org/abs/{pid}",
            "published": date_str, "category": random.choice(["rec", "agent", "llm"]),
            "type": "paper", "has_insight": False,
            "paper_value": round(random.uniform(3.0, 5.0), 2),
            "industry_score": random.randint(1, 5),
        })

    # GitHub Trending
    for gh_name, gh_repo, gh_stars in random.sample(GITHUB_PROJECT_NAMES, min(5, len(GITHUB_PROJECT_NAMES))):
        data["github_projects"].append({
            "id": gh_repo, "name": gh_name, "full_name": gh_repo,
            "description": f"Open source {random.choice(['AI','ML','NLP'])} project.",
            "cn_description": f"{gh_name} 是一个优秀的开源项目。",
            "stars": gh_stars, "forks": gh_stars // 5,
            "growth": random.randint(10, 500),
            "growth_rate": round(random.uniform(0.5, 5.0), 2),
            "language": random.choice(["Python", "Rust", "TypeScript"]),
            "url": f"https://github.com/{gh_repo}",
        })

    data["stats"] = {"total_papers": len(data["arxiv_papers"]),
                     "total_projects": len(data["github_projects"]),
                     "total_articles": len(data["articles"])}
    return data


def run_pipeline(date_str):
    """为指定日期执行完整流水线"""
    print(f"\n{'='*70}")
    print(f"# [{date_str}] 开始执行日报流水线")
    print(f"{'='*70}")

    # Step 1: 生成数据文件
    data_file = DATA_DIR / f"{date_str}.json"
    if not data_file.exists():
        print(f"\nStep 1: 生成占位数据...")
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        data = generate_mock_data(date_str)
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  OK -> {data_file}")
    else:
        print(f"\nStep 1: 数据文件已存在")

    # Step 2: 生成 LLM 占位摘要
    print(f"\nStep 2: 生成 LLM 占位摘要...")
    from llm_summarizer import generate_all_summaries
    generate_all_summaries(data_file, force=True)
    print(f"  OK")

    # Step 3: 生成 HTML 日报
    print(f"\nStep 3: 生成 HTML 日报...")
    os.environ["REPORT_DATE"] = date_str
    os.environ["BASE_DIR"] = str(BASE_DIR)

    from generate_report import ReportGenerator
    generator = ReportGenerator(str(BASE_DIR))
    html_path = generator.run()
    if html_path:
        print(f"  OK -> {html_path}")
        return True
    else:
        print(f"  FAILED")
        return False


def main():
    start_date = "2026-06-14"
    end_date = "2026-07-09"

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    total_days = (end - start).days + 1

    # 创建目录
    for d in ["daily_data", "docs", "docs/covers", "history", "scripts"]:
        (BASE_DIR / d).mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"AI 日报批量补跑计划")
    print(f"  范围: {start_date} ~ {end_date} ({total_days}天)")
    print(f"  模式: Mock LLM (无需 API Key)")
    print(f"{'='*70}")

    successes = 0
    failures = []
    batch_report = []

    for i in range(total_days):
        date = start + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        ok = run_pipeline(date_str)
        if ok:
            successes += 1
            batch_report.append(f"{date_str}: OK")
        else:
            failures.append(date_str)
            batch_report.append(f"{date_str}: FAILED")

        # 每3天或结束时汇报
        if (i + 1) % 3 == 0 or i == total_days - 1:
            print(f"\n{'='*50}")
            print(f"== 进度: 第 {i+1}/{total_days} 天 ({successes} OK / {len(failures)} FAIL)")
            print(f"== 最近完成: {', '.join([r.split(':')[0] for r in batch_report[-3:]])}")
            print(f"{'='*50}")

    # 最终报告
    print(f"\n{'='*70}")
    print(f"批量补跑完成!")
    print(f"  成功: {successes}/{total_days} 天")
    if failures:
        print(f"  失败: {', '.join(failures)}")
    else:
        print(f"  全部成功! 无失败日期。")
    print(f"{'='*70}")

    return successes == total_days


if __name__ == "__main__":
    all_ok = main()
    sys.exit(0 if all_ok else 1)
