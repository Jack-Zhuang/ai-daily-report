#!/usr/bin/env python3
"""
AI推荐日报 - 每日精选自动筛选脚本
基于多维度评分系统自动筛选高质量内容
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class DailyPickSelector:
    """每日精选筛选器"""
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # 关键词权重配置
        self.keyword_weights = {
            # 核心领域关键词（权重高）
            "recommendation": 5, "recommender": 5, "推荐": 5,
            "agent": 5, "智能体": 5, "AI Agent": 5,
            "LLM": 4, "大模型": 4, "GPT": 4, "Claude": 4,
            "RAG": 4, "检索增强": 4,
            
            # 技术热点关键词
            "multimodal": 3, "多模态": 3,
            "embedding": 3, "向量": 3,
            "personalization": 3, "个性化": 3,
            "CTR": 3, "转化率": 3,
            "transformer": 3, "attention": 3,
            
            # 工业实践关键词
            "production": 2, "工业": 2, "实践": 2,
            "optimization": 2, "优化": 2,
            "scalable": 2, "大规模": 2,
            
            # 前沿趋势关键词
            "SOTA": 3, "state-of-the-art": 3,
            "novel": 2, "创新": 2,
            "breakthrough": 3, "突破": 3,
        }
        
        # 来源权重（不同来源的可信度）
        self.source_weights = {
            "arxiv": 1.2,
            "机器之心": 1.0,
            "新智元": 1.0,
            "量子位": 1.0,
            "PaperWeekly": 1.1,
            "字节跳动技术团队": 1.0,
            "美团技术团队": 1.0,
            "InfoQ技术文章": 0.9,
            "36氪快讯": 0.7,
            "知乎热榜": 0.6,
        }
        
        # 每日精选配置
        self.pick_config = {
            "total_count": 5,  # 总共5篇
            "paper_count": 2,  # 论文2篇
            "article_count": 2,  # 文章2篇
            "github_count": 1,  # GitHub项目1篇
        }
    
    def calculate_score(self, item: Dict[str, Any]) -> float:
        """
        计算综合评分
        公式：创新性*0.3 + 工业价值*0.3 + 热度*0.25 + 时效性*0.15
        """
        # 1. 关键词匹配分（代表创新性和工业价值）
        title = item.get("title", "").lower()
        summary = item.get("summary", item.get("cn_summary", "")).lower()
        content = title + " " + summary
        
        keyword_score = 0
        for keyword, weight in self.keyword_weights.items():
            if keyword.lower() in content:
                keyword_score += weight
        
        # 归一化到1-5分
        keyword_score = min(5, keyword_score / 3)
        
        # 2. 来源权重
        source = item.get("source", "")
        source_weight = self.source_weights.get(source, 0.8)
        
        # 3. 热度分（基于views/likes/stars）
        popularity_score = 3  # 默认中等
        if "stars" in item:
            popularity_score = min(5, item["stars"] / 1000)
        elif "views" in item:
            popularity_score = min(5, item["views"] / 100)
        elif "likes" in item:
            popularity_score = min(5, item["likes"] / 10)
        
        # 4. 时效性分
        freshness_score = 5  # 默认最新
        pub_date = item.get("published", item.get("date", self.today))
        if isinstance(pub_date, str):
            try:
                pub_datetime = datetime.strptime(pub_date[:10], "%Y-%m-%d")
                days_old = (datetime.now() - pub_datetime).days
                freshness_score = max(1, 5 - days_old * 0.5)
            except:
                pass
        
        # 综合评分
        final_score = (
            keyword_score * 0.35 +      # 关键词匹配（最重要）
            popularity_score * 0.25 +   # 热度
            freshness_score * 0.20 +    # 时效性
            3 * 0.20                    # 基础分
        ) * source_weight
        
        return round(final_score, 2)
    
    def select_papers(self, papers: List[Dict], count: int = 2) -> List[Dict]:
        """筛选论文"""
        if not papers:
            return []
        
        # 计算评分
        for paper in papers:
            paper["_score"] = self.calculate_score(paper)
        
        # 按评分排序
        sorted_papers = sorted(papers, key=lambda x: x.get("_score", 0), reverse=True)
        
        # 去重（避免相似主题）
        selected = []
        for paper in sorted_papers:
            if len(selected) >= count:
                break
            
            # 检查是否与已选论文主题相似
            is_similar = False
            for sel in selected:
                title1 = paper.get("title", "").lower()
                title2 = sel.get("title", "").lower()
                # 简单相似度检查
                common_words = set(title1.split()) & set(title2.split())
                if len(common_words) > 3:
                    is_similar = True
                    break
            
            if not is_similar:
                selected.append(paper)
        
        return selected
    
    def select_articles(self, articles: List[Dict], count: int = 2) -> List[Dict]:
        """筛选文章"""
        if not articles:
            return []
        
        # 计算评分
        for article in articles:
            article["_score"] = self.calculate_score(article)
        
        # 按评分排序
        sorted_articles = sorted(articles, key=lambda x: x.get("_score", 0), reverse=True)
        
        # 去重
        selected = []
        seen_sources = set()
        
        for article in sorted_articles:
            if len(selected) >= count:
                break
            
            # 避免同一来源过多
            source = article.get("source", "")
            if source not in seen_sources or len(selected) >= count - 1:
                selected.append(article)
                seen_sources.add(source)
        
        return selected
    
    def select_github(self, projects: List[Dict], count: int = 1) -> List[Dict]:
        """筛选GitHub项目"""
        if not projects:
            return []
        
        # 计算评分
        for project in projects:
            project["_score"] = self.calculate_score(project)
        
        # 按评分排序
        sorted_projects = sorted(projects, key=lambda x: x.get("_score", 0), reverse=True)
        
        return sorted_projects[:count]
    
    def generate_daily_pick(self, data: Dict) -> List[Dict]:
        """生成每日精选"""
        daily_pick = []
        
        # 1. 筛选论文
        papers = data.get("arxiv_papers", [])
        selected_papers = self.select_papers(papers, self.pick_config["paper_count"])
        for paper in selected_papers:
            paper["_type"] = "paper"
            paper["_reason"] = self._generate_reason(paper)
            daily_pick.append(paper)
        
        # 2. 筛选文章
        articles = data.get("hot_articles", [])
        selected_articles = self.select_articles(articles, self.pick_config["article_count"])
        for article in selected_articles:
            article["_type"] = "article"
            article["_reason"] = self._generate_reason(article)
            daily_pick.append(article)
        
        # 3. 筛选GitHub项目
        projects = data.get("github_projects", [])
        selected_projects = self.select_github(projects, self.pick_config["github_count"])
        for project in selected_projects:
            project["_type"] = "github"
            project["_reason"] = self._generate_reason(project)
            daily_pick.append(project)
        
        # 如果精选不足，从文章中补充
        if len(daily_pick) < self.pick_config["total_count"]:
            remaining = self.pick_config["total_count"] - len(daily_pick)
            all_items = papers + articles + projects
            selected_ids = {item.get("id") or item.get("link") for item in daily_pick}
            
            for item in all_items:
                if remaining <= 0:
                    break
                item_id = item.get("id") or item.get("link")
                if item_id not in selected_ids:
                    item["_type"] = item.get("type", "article")
                    item["_reason"] = self._generate_reason(item)
                    daily_pick.append(item)
                    remaining -= 1
        
        return daily_pick[:self.pick_config["total_count"]]
    
    def _generate_reason(self, item: Dict) -> str:
        """生成推荐理由"""
        score = item.get("_score", 0)
        title = item.get("title", "")
        item_type = item.get("_type", "article")
        
        reasons = []
        
        # 基于评分
        if score >= 4.5:
            reasons.append("高分推荐")
        elif score >= 4.0:
            reasons.append("优质内容")
        
        # 基于类型
        type_names = {
            "paper": "前沿论文",
            "article": "技术文章",
            "github": "开源项目"
        }
        reasons.append(type_names.get(item_type, "精选内容"))
        
        # 基于关键词
        title_lower = title.lower()
        if "agent" in title_lower or "智能体" in title_lower:
            reasons.append("Agent热点")
        elif "llm" in title_lower or "大模型" in title_lower:
            reasons.append("LLM前沿")
        elif "recommend" in title_lower or "推荐" in title_lower:
            reasons.append("推荐系统")
        
        return " | ".join(reasons[:3])
    
    def run(self) -> List[Dict]:
        """执行筛选流程"""
        # 加载今日数据
        data_file = self.base_dir / "daily_data" / f"{self.today}.json"
        
        if not data_file.exists():
            print(f"❌ 今日数据文件不存在: {data_file}")
            return []
        
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"\n{'='*50}")
        print(f"🎯 每日精选筛选 - {self.today}")
        print(f"{'='*50}")
        
        print(f"\n📊 输入数据统计:")
        print(f"  - arXiv论文: {len(data.get('arxiv_papers', []))} 篇")
        print(f"  - 热门文章: {len(data.get('hot_articles', []))} 篇")
        print(f"  - GitHub项目: {len(data.get('github_projects', []))} 个")
        
        # 生成精选
        daily_pick = self.generate_daily_pick(data)
        
        print(f"\n✅ 筛选结果: {len(daily_pick)} 篇精选")
        print(f"\n📰 每日精选:")
        for i, item in enumerate(daily_pick, 1):
            print(f"  {i}. [{item.get('_type', '?')}] {item.get('title', '')[:50]}...")
            print(f"     评分: {item.get('_score', 0)} | 理由: {item.get('_reason', '')}")
        
        # 更新数据文件
        data["daily_pick"] = daily_pick
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 已保存到: {data_file}")
        
        return daily_pick


if __name__ == "__main__":
    selector = DailyPickSelector()
    selector.run()
