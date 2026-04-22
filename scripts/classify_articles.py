#!/usr/bin/env python3
"""
使用 LLM 智能分类文章
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import requests

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

class ArticleClassifier:
    """文章智能分类器"""
    
    def __init__(self):
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.api_key = self._get_api_key()
        self.model = "glm-4-flash"  # 快速模型，成本低
        
    def _get_api_key(self) -> str:
        """获取 API Key"""
        # 从环境变量获取
        import os
        api_key = os.environ.get("GLM_API_KEY") or os.environ.get("ZHIPU_API_KEY")
        if api_key:
            return api_key
        
        # 从配置文件获取
        config_file = Path(__file__).parent.parent / "config" / "api_keys.json"
        if config_file.exists():
            config = json.loads(config_file.read_text())
            return config.get("zhipu_api_key", "")
        
        return ""
    
    def classify_batch(self, articles: List[Dict], batch_size: int = 10) -> List[Dict]:
        """批量分类文章"""
        results = []
        
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i+batch_size]
            print(f"正在分类 {i+1}-{min(i+batch_size, len(articles))}/{len(articles)}...")
            
            for article in batch:
                result = self.classify_single(article)
                if result:
                    article.update(result)
                results.append(article)
        
        return results
    
    def classify_single(self, article: Dict) -> Optional[Dict]:
        """分类单篇文章"""
        title = article.get("title", "") or article.get("cn_title", "")
        summary = article.get("summary", "") or article.get("cn_summary", "")
        
        # 截取前500字符
        text = f"标题：{title}\n摘要：{summary[:500]}"
        
        prompt = f"""分析这篇文章，判断：
1. 分类：rec（推荐系统）/ agent（智能体）/ llm（大语言模型）之一，如果都不匹配返回 "other"
2. 是否广告：包括招聘、课程推广、付费内容等
3. 是否AI相关：文章内容是否与人工智能、机器学习、深度学习相关

{text}

只返回JSON格式，不要其他内容：
{{"category": "rec/agent/llm/other", "is_ad": true/false, "is_ai": true/false, "reason": "简短理由"}}"""

        try:
            response = self._call_api(prompt)
            if response:
                # 解析 JSON
                result = self._parse_response(response)
                return result
        except Exception as e:
            print(f"  分类失败: {title[:30]}... - {e}")
        
        return None
    
    def _call_api(self, prompt: str) -> Optional[str]:
        """调用 GLM API"""
        if not self.api_key:
            print("⚠️ 未配置 GLM API Key，使用规则分类")
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 200
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f"API 错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"API 调用失败: {e}")
            return None
    
    def _parse_response(self, response: str) -> Optional[Dict]:
        """解析 API 响应"""
        try:
            # 提取 JSON
            import re
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "category": result.get("category", "rec"),
                    "is_ad": result.get("is_ad", False),
                    "is_ai": result.get("is_ai", True),
                    "classify_reason": result.get("reason", "")
                }
        except:
            pass
        
        return None


def classify_with_rules(article: Dict) -> Dict:
    """规则分类（备用方案）"""
    title = article.get("title", "") or article.get("cn_title", "")
    summary = article.get("summary", "") or article.get("cn_summary", "")
    text = (title + " " + summary).lower()
    
    # 广告关键词
    ad_keywords = ["招聘", "内推", "求职", "简历", "面试", "课程", "培训", "报名",
                   "优惠", "促销", "购买", "订阅", "会员", "付费", "广告", "限时"]
    is_ad = any(kw in title for kw in ad_keywords)
    
    # AI 相关
    ai_keywords = ["AI", "人工智能", "大模型", "LLM", "GPT", "Claude", "OpenAI", "DeepSeek",
                   "Agent", "智能体", "推荐系统", "机器学习", "深度学习", "神经网络",
                   "Transformer", "RAG", "多模态", "计算机视觉", "NLP", "自然语言",
                   "强化学习", "知识图谱", "向量数据库", "Embedding", "微调", "训练",
                   "推理", "模型", "算法", "论文", "arXiv", "GitHub", "开源",
                   "机器人", "自动化", "自动驾驶", "AIGC", "生成式", "ChatGPT"]
    is_ai = any(kw.lower() in text.lower() for kw in ai_keywords)
    
    # 分类
    if any(kw in text for kw in ["agent", "智能体", "多智能体", "autonomous"]):
        category = "agent"
    elif any(kw in text for kw in ["llm", "大模型", "gpt", "claude", "llama", "transformer",
                                    "语言模型", "chat", "对话", "prompt", "rag"]):
        category = "llm"
    elif any(kw in text for kw in ["推荐", "recommend", "recsys", "召回", "排序", "ctr"]):
        category = "rec"
    else:
        category = "rec" if is_ai else "other"
    
    return {
        "category": category,
        "is_ad": is_ad,
        "is_ai": is_ai,
        "classify_reason": "规则分类"
    }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="智能分类文章")
    parser.add_argument("--input", "-i", default="archive/2026-04-22/data.json", help="输入数据文件")
    parser.add_argument("--output", "-o", default=None, help="输出数据文件")
    parser.add_argument("--use-llm", action="store_true", help="使用 LLM 分类")
    args = parser.parse_args()
    
    # 加载数据
    base_dir = Path(__file__).parent.parent
    input_file = base_dir / args.input
    data = json.loads(input_file.read_text())
    
    articles = data.get("articles", [])
    print(f"文章总数: {len(articles)}")
    
    # 分类
    if args.use_llm:
        classifier = ArticleClassifier()
        articles = classifier.classify_batch(articles)
    else:
        print("使用规则分类...")
        for article in articles:
            result = classify_with_rules(article)
            article.update(result)
    
    # 过滤
    filtered = [a for a in articles if not a.get("is_ad", False) and a.get("is_ai", True)]
    print(f"过滤后: {len(filtered)} 篇（移除 {len(articles) - len(filtered)} 篇）")
    
    # 统计
    cats = {}
    for a in filtered:
        cat = a.get("category", "other")
        cats[cat] = cats.get(cat, 0) + 1
    
    print("\n分类统计:")
    for cat in ["rec", "agent", "llm", "other"]:
        print(f"  {cat}: {cats.get(cat, 0)}")
    
    # 保存
    data["articles"] = filtered
    output_file = base_dir / (args.output or args.input)
    output_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"\n✅ 已保存到 {output_file}")


if __name__ == "__main__":
    main()
