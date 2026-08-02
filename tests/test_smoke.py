"""冒烟测试：核心模块可导入、基础功能可用。

占位测试集 —— 等 KIMI云仔的完整测试套件（63用例）合入后扩展。
"""


def test_core_modules_importable():
    import llm.factory
    import llm_summarizer
    import collect_daily
    import generate_report

    assert hasattr(llm.factory, "ModelFactory")


def test_factory_has_minimax_provider():
    from llm.factory import ModelFactory

    assert "minimax" in ModelFactory.PROVIDERS
