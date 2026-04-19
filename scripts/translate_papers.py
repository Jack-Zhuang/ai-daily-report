#!/usr/bin/env python3
"""
AI推荐日报 - 论文翻译脚本
使用 MiniMax API 翻译论文标题和摘要
"""

import json
import requests
import time
from pathlib import Path
from datetime import datetime


class PaperTranslator:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # MiniMax API 配置
        self.api_url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        self.api_key = self._load_api_key()
    
    def _load_api_key(self) -> str:
        """加载 API Key"""
        # 尝试从环境变量或配置文件加载
        env_file = self.base_dir.parent / ".xiaoyienv"
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    if line.startswith("PERSONAL-API-KEY="):
                        return line.split("=", 1)[1].strip().strip('"')
        
        # 备用：从 translator.py 获取
        translator_file = self.base_dir / "scripts" / "translator.py"
        if translator_file.exists():
            with open(translator_file, "r") as f:
                content = f.read()
                import re
                match = re.search(r'api_key\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
        
        return ""
    
    def translate_title(self, title: str) -> str:
        """翻译论文标题"""
        if not title or not self.api_key:
            return title
        
        # 如果标题已经是中文，直接返回
        if any('\u4e00' <= c <= '\u9fff' for c in title):
            return title
        
        try:
            payload = {
                "model": "abab6.5s-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的学术翻译。请将英文论文标题翻译成简洁的中文，保留专业术语。只输出翻译结果，不要解释。"
                    },
                    {
                        "role": "user",
                        "content": f"翻译这个论文标题：{title}"
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 200
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", title)
        except Exception as e:
            print(f"    ⚠️ 标题翻译失败: {e}")
        
        return title
    
    def translate_abstract(self, abstract: str) -> str:
        """翻译论文摘要"""
        if not abstract or not self.api_key:
            return abstract[:200] if abstract else ""
        
        # 如果摘要已经是中文，直接返回
        if any('\u4e00' <= c <= '\u9fff' for c in abstract):
            return abstract[:200]
        
        try:
            # 截取前 500 字符翻译
            text_to_translate = abstract[:500]
            
            payload = {
                "model": "abab6.5s-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的学术翻译。请将英文论文摘要翻译成流畅的中文，保留专业术语。输出 150 字以内的中文摘要。"
                    },
                    {
                        "role": "user",
                        "content": f"翻译这个论文摘要：{text_to_translate}"
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 300
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")[:200]
        except Exception as e:
            print(f"    ⚠️ 摘要翻译失败: {e}")
        
        return abstract[:200] if abstract else ""
    
    def translate_papers(self, papers: list) -> list:
        """翻译论文列表"""
        translated = []
        
        for i, paper in enumerate(papers):
            title = paper.get("title", "")
            summary = paper.get("summary", "")
            
            print(f"  📝 翻译论文 {i+1}/{len(papers)}: {title[:30]}...", end=" ", flush=True)
            
            # 翻译标题
            cn_title = self.translate_title(title)
            paper["cn_title"] = cn_title
            
            # 翻译摘要
            cn_summary = self.translate_abstract(summary)
            paper["cn_summary"] = cn_summary
            
            translated.append(paper)
            print("✅")
            
            time.sleep(0.3)  # 避免 API 限流
        
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
