#!/usr/bin/env python3
"""
AI推荐日报 - 翻译模块
使用 MiniMax API 进行翻译
"""

import json
import requests
import os
from pathlib import Path

class MiniMaxTranslator:
    def __init__(self):
        # 从环境变量获取 API Key
        self.api_key = os.environ.get('MINIMAX_API_KEY', '')
        self.group_id = os.environ.get('MINIMAX_GROUP_ID', '')
        self.base_url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        
        # 如果没有环境变量，尝试从 .xiaoyienv 加载
        if not self.api_key:
            env_file = Path.home() / ".openclaw" / ".xiaoyienv"
            if env_file.exists():
                for line in env_file.read_text().splitlines():
                    if line.startswith('PERSONAL-API-KEY='):
                        self.api_key = line.split('=', 1)[1].strip().strip('"')
                    elif line.startswith('PERSONAL-UID='):
                        self.group_id = line.split('=', 1)[1].strip().strip('"')
    
    def translate(self, text: str, target_lang: str = "中文") -> str:
        """翻译文本"""
        if not text:
            return ""
        
        # 如果已经是中文，直接返回
        chinese_ratio = sum(1 for c in text if '\u4e00' <= c <= '\u9fff') / max(len(text), 1)
        if chinese_ratio > 0.3:
            return text
        
        # 尝试使用免费翻译 API
        try:
            # 使用 MyMemory 翻译 API（免费）
            translated = self._mymemory_translate(text)
            if translated and any('\u4e00' <= c <= '\u9fff' for c in translated):
                return translated
        except:
            pass
        
        # 使用增强的规则翻译
        return self._enhanced_translate(text)
    
    def _mymemory_translate(self, text: str) -> str:
        """使用免费翻译 API"""
        import urllib.parse
        
        # 截取前500字符（API限制）
        text_to_translate = text[:500]
        
        # 尝试 Google Translate（通过 translate.googleapis.com）
        try:
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh&dt=t&q={urllib.parse.quote(text_to_translate)}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result and result[0]:
                    translated = ''.join([item[0] for item in result[0] if item[0]])
                    if translated:
                        return translated
        except:
            pass
        
        # 备用：MyMemory API
        try:
            url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text_to_translate)}&langpair=en|zh"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('responseStatus') == 200:
                    return result.get('responseData', {}).get('translatedText', '')
        except:
            pass
        
        return ""
    
    def _simple_translate(self, text: str) -> str:
        """简单规则翻译（备用）"""
        translations = {
            'recommendation': '推荐',
            'recommender': '推荐',
            'recommend': '推荐',
            'agent': '智能体',
            'agents': '智能体',
            'LLM': '大语言模型',
            'large language model': '大语言模型',
            'Large Language Model': '大语言模型',
            'collaborative filtering': '协同过滤',
            'neural network': '神经网络',
            'neural networks': '神经网络',
            'deep learning': '深度学习',
            'machine learning': '机器学习',
            'attention': '注意力',
            'attention mechanism': '注意力机制',
            'transformer': 'Transformer',
            'user': '用户',
            'users': '用户',
            'item': '物品',
            'items': '物品',
            'rating': '评分',
            'ratings': '评分',
            'preference': '偏好',
            'preferences': '偏好',
            'model': '模型',
            'models': '模型',
            'system': '系统',
            'systems': '系统',
            'method': '方法',
            'methods': '方法',
            'approach': '方法',
            'approaches': '方法',
            'framework': '框架',
            'frameworks': '框架',
            'algorithm': '算法',
            'algorithms': '算法',
            'learning': '学习',
            'training': '训练',
            'inference': '推理',
            'generation': '生成',
            'generative': '生成式',
            'personalized': '个性化',
            'personalization': '个性化',
            'multi-modal': '多模态',
            'multimodal': '多模态',
            'knowledge graph': '知识图谱',
            'graph neural network': '图神经网络',
            'reinforcement learning': '强化学习',
            'self-supervised': '自监督',
            'semi-supervised': '半监督',
            'unsupervised': '无监督',
            'supervised': '有监督',
            'embedding': '嵌入',
            'embeddings': '嵌入',
            'representation': '表示',
            'feature': '特征',
            'features': '特征',
            'dataset': '数据集',
            'benchmark': '基准',
            'evaluation': '评估',
            'experiment': '实验',
            'experiments': '实验',
            'result': '结果',
            'results': '结果',
            'performance': '性能',
            'accuracy': '准确率',
            'precision': '精确率',
            'recall': '召回率',
            'F1': 'F1值',
            'AUC': 'AUC',
            'CTR': '点击率',
            'conversion': '转化',
            'optimization': '优化',
            'optimize': '优化',
            'loss': '损失',
            'function': '函数',
            'parameter': '参数',
            'parameters': '参数',
            'weight': '权重',
            'weights': '权重',
            'layer': '层',
            'layers': '层',
            'hidden': '隐藏',
            'output': '输出',
            'input': '输入',
            'sequence': '序列',
            'temporal': '时序',
            'temporal dynamics': '时序动态',
            'behavior': '行为',
            'behaviors': '行为',
            'interaction': '交互',
            'interactions': '交互',
            'session': '会话',
            'sessions': '会话',
            'context': '上下文',
            'contextual': '上下文',
            'cold start': '冷启动',
            'data sparsity': '数据稀疏',
            'scalability': '可扩展性',
            'efficiency': '效率',
            'effectiveness': '有效性',
            'robust': '鲁棒',
            'robustness': '鲁棒性',
            'privacy': '隐私',
            'privacy-preserving': '隐私保护',
            'federated': '联邦',
            'federated learning': '联邦学习',
        }
        
        result = text
        for en, cn in sorted(translations.items(), key=lambda x: -len(x[0])):
            result = result.replace(en, cn)
        
        return result
    
    def _enhanced_translate(self, text: str) -> str:
        """增强的规则翻译"""
        # 先进行基础翻译
        result = self._simple_translate(text)
        
        # 如果结果还是大部分英文，添加提示
        english_ratio = sum(1 for c in result if c.isascii() and c.isalpha()) / max(len(result), 1)
        if english_ratio > 0.5:
            # 标记为需要人工翻译
            return f"[待翻译] {result}"
        
        return result
    
    def translate_title(self, title: str) -> str:
        """翻译标题"""
        return self.translate(title, "中文标题")
    
    def translate_abstract(self, abstract: str) -> str:
        """翻译摘要"""
        return self.translate(abstract, "中文摘要")


# 全局实例
_translator = None

def get_translator():
    global _translator
    if _translator is None:
        _translator = MiniMaxTranslator()
    return _translator

def translate(text: str) -> str:
    """便捷翻译函数"""
    return get_translator().translate(text)


if __name__ == "__main__":
    # 测试
    translator = MiniMaxTranslator()
    
    test_title = "SAGER: Self-Evolving User Policy Skills for Recommendation Agent"
    test_abstract = "Large language model (LLM) based recommendation agents personalize what they know through evolving per-user semantic memory, but their reasoning remains a static system prompt shared across all users."
    
    print("=== 测试翻译 ===")
    print(f"原标题: {test_title}")
    print(f"翻译后: {translator.translate_title(test_title)}")
    print()
    print(f"原摘要: {test_abstract[:100]}...")
    print(f"翻译后: {translator.translate_abstract(test_abstract)[:100]}...")
