#!/usr/bin/env python3
"""
跨天更新测试脚本
验证所有脚本是否正确使用动态日期
"""

import re
import sys
from pathlib import Path
from datetime import datetime

def check_hardcoded_dates(script_path: Path) -> list:
    """检查脚本中的硬编码日期"""
    issues = []
    content = script_path.read_text(encoding='utf-8')
    
    # 检查硬编码日期格式 YYYY-MM-DD
    date_pattern = r'["\'](\d{4}-\d{2}-\d{2})["\']'
    matches = re.findall(date_pattern, content)
    
    for match in matches:
        # 排除注释中的示例
        line_num = content[:content.index(match)].count('\n') + 1
        line = content.split('\n')[line_num - 1]
        
        # 跳过注释行
        if line.strip().startswith('#') or line.strip().startswith('*'):
            continue
        
        # 跳过合理的日期（如会议日期）
        if '2025年' in line or '2026年' in line or 'conference' in line.lower():
            continue
        
        # 跳过测试数据
        if 'test_paper' in line or 'test_data' in line or '__main__' in line or 'arxiv_id' in line:
            continue
        
        # 跳过 API 版本号
        if 'version' in line.lower() or 'anthropic-version' in line:
            continue
        
        issues.append(f"  行 {line_num}: 发现硬编码日期 {match}")
    
    return issues

def check_dynamic_date_usage(script_path: Path) -> bool:
    """检查是否正确使用动态日期"""
    content = script_path.read_text(encoding='utf-8')
    
    # 检查是否有动态日期获取
    has_datetime_now = 'datetime.now()' in content or 'date.today()' in content
    has_today_var = 'self.today' in content or 'self.date' in content
    has_fstring_date = 'f"{today}' in content or "f'{today}" in content
    has_format_date = 'strftime' in content
    
    return has_datetime_now or has_today_var or has_fstring_date or has_format_date

def main():
    scripts_dir = Path(__file__).parent
    base_dir = scripts_dir.parent
    
    print("=" * 60)
    print("🔍 跨天更新测试")
    print("=" * 60)
    print(f"📅 当前日期: {datetime.now().strftime('%Y-%m-%d')}")
    print()
    
    # 检查所有 Python 脚本
    all_issues = []
    all_scripts = list(scripts_dir.glob("*.py"))
    
    print(f"📂 检查 {len(all_scripts)} 个脚本...\n")
    
    for script in sorted(all_scripts):
        if script.name.startswith('_') or script.name.startswith('test_'):
            continue
        
        issues = check_hardcoded_dates(script)
        has_dynamic = check_dynamic_date_usage(script)
        
        if issues:
            print(f"❌ {script.name}")
            for issue in issues:
                print(issue)
            all_issues.extend(issues)
        elif has_dynamic:
            print(f"✅ {script.name} - 使用动态日期")
        else:
            print(f"⚠️  {script.name} - 未检测到日期逻辑")
    
    print()
    print("=" * 60)
    
    if all_issues:
        print(f"❌ 发现 {len(all_issues)} 个硬编码日期问题")
        return 1
    else:
        print("✅ 所有脚本都正确使用动态日期")
        return 0

if __name__ == "__main__":
    sys.exit(main())
