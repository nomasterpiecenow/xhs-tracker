# -*- coding: utf-8 -*-
"""
验证 GitHub Pages 上线的数据完整性
"""
import json
import subprocess
import sys
import urllib.request
from datetime import datetime

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 70)
    print("验证 GitHub Pages 上线数据完整性")
    print("=" * 70)
    print()
    
    # 1. 获取本地最新的 generatedAt
    print("【步骤 1/4】获取本地数据版本...")
    try:
        with open("data.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        local_gen = data.get('generatedAt') or data.get('insights', {}).get('generatedAt')
        local_gen = local_gen.replace(' ', 'T')
        if len(local_gen) == 16:
            local_gen = local_gen + ':00'
        
        print(f"  本地版本: {local_gen}")
        
    except Exception as e:
        print(f"  ❌ 获取失败: {e}")
        sys.exit(1)
    
    # 2. 获取线上数据
    print("\n【步骤 2/4】获取线上数据...")
    url_online = "https://raw.githubusercontent.com/nomasterpiecenow/xhs-tracker/main/data.json"
    
    try:
        print(f"  下载: {url_online}")
        req = urllib.request.Request(url_online, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as f:
            online_content = f.read().decode('utf-8')
        online = json.loads(online_content)
        online_gen = online.get('generatedAt') or online.get('insights', {}).get('generatedAt')
        online_gen = online_gen.replace(' ', 'T')
        if len(online_gen) == 16:
            online_gen = online_gen + ':00'
        print(f"  线上版本: {online_gen}")
    except Exception as e:
        print(f"  ❌ 获取失败: {e}")
        sys.exit(1)
    
    # 3. 检查 daily
    print("\n【步骤 3/4】验证 daily 卡片...")
    try:
        daily = online.get('insights', {}).get('daily', [])
        print(f"  共 {len(daily)} 张卡片")
        
        count_why = 0
        count_pi = 0
        
        for i, card in enumerate(daily):
            key = card.get('key', 'N/A')
            why = (card.get('why') or '').strip()
            pi = (card.get('productImplication') or '').strip()
            
            if not why:
                count_why += 1
                if count_why <= 3:
                    print(f"  ❌ 缺少 why: {key}")
            if not pi:
                count_pi += 1
                if count_pi <= 3:
                    print(f"  ❌ 缺少 PI: {key}")
        
        print(f"  缺少 why: {count_why}/{len(daily)}")
        print(f"  缺少 PI: {count_pi}/{len(daily)}")
        
    except Exception as e:
        print(f"  ❌ 验证失败: {e}")
    
    # 4. 检查 weekly
    print("\n【步骤 4/4】验证 weekly 周报...")
    try:
        weekly = online.get('insights', {}).get('weekly', {})
        items = weekly.get('items', [])
        print(f"  共 {len(items)} 张卡片")
        
        count_why_w = 0
        count_pi_w = 0
        
        for i, item in enumerate(items):
            key = item.get('key', 'N/A')
            why = (item.get('why') or '').strip()
            pi = (item.get('productImplication') or '').strip()
            
            if not why:
                count_why_w += 1
                if count_why_w <= 3:
                    print(f"  ❌ 缺少 why: {key}")
            if not pi:
                count_pi_w += 1
                if count_pi_w <= 3:
                    print(f"  ❌ 缺少 PI: {key}")
        
        print(f"  缺少 why: {count_why_w}/{len(items)}")
        print(f"  缺少 PI: {count_pi_w}/{len(items)}")
        
        # 检查 weeklyHistory
        wh = online.get('insights', {}).get('weeklyHistory', [])
        print(f"\n  周报历史期数: {len(wh)}")
        for i, period in enumerate(wh):
            items = period.get('items', [])
            gen = period.get('generatedAt', 'unknown')
            print(f"    第 {i+1} 期: {gen} ({len(items)} 张)")
        
    except Exception as e:
        print(f"  ❌ 验证失败: {e}")
    
    # 总结
    print()
    print("=" * 70)
    print("验证完成")
    print("=" * 70)
    print()
    print(f"本地版本: {local_gen}")
    print(f"线上版本: {online_gen}")
    
    if local_gen != online_gen:
        print()
        print("⚠️  警告: 本地和线上版本不一致！")
        print("提示: 如果刚刚完成推送，需要等待：")
        print("  1. GitHub Actions 构建 (1-2 分钟)")
        print("  2. GitHub Pages 部署 (1-2 分钟)")
        print("  3. CDN 刷新 (几分钟)")
        print()
        print("请等待几分钟后重新验证")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
