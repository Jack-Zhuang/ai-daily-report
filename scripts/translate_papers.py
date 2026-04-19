#!/usr/bin/env python3
"""
AI推荐日报 - 论文翻译脚本
使用 MiniMax Token Plan (Anthropic 兼容 API) 翻译论文标题和摘要
"""

import json
import requests
import time
import os
from pathlib import Path
from datetime import datetime


class PaperTranslator:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # MiniMax Token Plan API 配置 (Anthropic 兼容)
        self.api_url = "https://api.minimaxi.com/anthropic/v1/messages"
        self.api_key = self._load_api_key()
    
    def _load_api_key(self) -> str:
        """加载 API Key"""
        # 优先从环境变量获取
        api_key = os.environ.get('MINIMAX_API_KEY', '')
        if api_key:
            return api_key
        
        # 尝试从 env.sh 加载
        env_file = Path.home() / ".openclaw" / "env.sh"
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    if line.startswith("export MINIMAX_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        
        return ""
    
    def _call_api(self, prompt: str, max_tokens: int = 300) -> str:
        """调用 MiniMax Token Plan API"""
        if not self.api_key:
            return ""
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "MiniMax-M2.7-highspeed",
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content_blocks = data.get('content', [])
                for block in content_blocks:
                    if block.get('type') == 'text':
                        return block.get('text', '').strip()
        except Exception as e:
            print(f"    ⚠️ API调用失败: {e}")
        
        return ""
    
    def translate_title(self, title: str) -> str:
        """翻译论文标题"""
        if not title:
            return title
        
        # 如果标题已经是中文，直接返回
        if any('\u4e00' <= c <= '\u9fff' for c in title):
            return title
        
        if not self.api_key:
            return title
        
        prompt = f"""你是一个专业的学术翻译。请将以下英文论文标题翻译成简洁的中文标题。

要求：
1. 保留专业术语（如 LLM、RAG、Transformer 等可不翻译）
2. 简洁有力，不超过30个汉字
3. 只输出翻译结果，不要解释

英文标题：{title}

中文标题："""

        result = self._call_api(prompt, max_tokens=100)
        return result if result else title
    
    def translate_abstract(self, abstract: str) -> str:
        """翻译论文摘要"""
        if not abstract:
            return ""
        
        # 如果摘要已经是中文，直接返回
        if any('\u4e00' <= c <= '\u9fff' for c in abstract):
            return abstract[:200]
        
        if not self.api_key:
            return abstract[:200]
        
        # 截取前 800 字符翻译
        text_to_translate = abstract[:800]
        
        prompt = f"""你是一个专业的学术翻译。请将以下英文论文摘要翻译成流畅的中文摘要。

要求：
1. 保留专业术语（如 LLM、RAG、Transformer 等可不翻译）
2. 输出 150-200 字的中文摘要
3. 语言流畅，适合技术人员阅读
4. 只输出翻译结果，不要解释

英文摘要：{text_to_translate}

中文摘要："""

        result = self._call_api(prompt, max_tokens=400)
        return result[:200] if result else abstract[:200]
    
    def translate_papers(self, papers: list) -> list:
        """翻译论文列表"""
        translated = []
        
        for i, paper in enumerate(papers):
            title = paper.get("title", "")
            summary = paper.get("summary", "")
            
            # 检查是否需要翻译
            need_title = not paper.get("cn_title")
            need_summary = not paper.get("cn_summary") and summary
            
            if not need_title and not need_summary:
                translated.append(paper)
                continue
            
            print(f"  📝 翻译论文 {i+1}/{len(papers)}: {title[:30]}...", end=" ", flush=True)
            
            # 翻译标题
            if need_title:
                paper["cn_title"] = self.translate_title(title)
            
            # 翻译摘要
            if need_summary:
                paper["cn_summary"] = self.translate_abstract(summary)
            
            translated.append(paper)
            print("✅")
            
            time.sleep(0.2)  # 避免 API 限流
        
        return translated
    
    def run(self):
        """执行翻译"""
        data_file = self.base_dir / "daily_data" / f"{self.today}.json"
        
        if not data_file.exists():
            print(f"❌ 今日数据文件不存在: {data_file}")
            return
        
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        papers = data.get("arxiv_papers", [])
        
        if not papers:
            print("❌ 没有论文需要翻译")
            return
        
        # 检查 API Key
        if not self.api_key:
            print("⚠️ 未配置 MINIMAX_API_KEY，跳过翻译")
            return
        
        print(f"\n{'='*50}")
        print(f"🌐 翻译论文标题和摘要")
        print(f"{'='*50}\n")
        
        # 翻译论文
        translated_papers = self.translate_papers(papers)
        data["arxiv_papers"] = translated_papers
        
        # 翻译每日精选中的论文
        daily_pick = data.get("daily_pick", [])
        for item in daily_pick:
            if item.get("_type") == "paper" or item.get("type") == "paper":
                if not item.get("cn_title"):
                    item["cn_title"] = self.translate_title(item.get("title", ""))
                if not item.get("cn_summary"):
                    item["cn_summary"] = self.translate_abstract(item.get("summary", ""))
        
        data["daily_pick"] = daily_pick
        
        # 保存
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 翻译完成，已保存到: {data_file}")


if __name__ == "__main__":
    translator = PaperTranslator()
    translator.run()
