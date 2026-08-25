#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速检查 GitHub Pages 实际加载的数据版本
"""
import json
import urllib.request
import os
import sys
from datetime import datetime

# 检查 GitHub Pages 线上 raw 数据
print("=== GitHub Pages 线上数据检查 ===")
print()

# 1. 检查 raw.githubusercontent.com
print("[1] raw.githubusercontent.com (源文件):")
try:
    url = "https://raw.githubusercontent.com/nomasterpiecenow/xhs-tracker/main/data.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw_data = json.loads(resp.read().decode('utf-8'))
    
    raw_gen = raw_data.get("generatedAt") or raw_data.get("insights", {}).get("generatedAt", "unknown")
    print(f"   生成时间: {raw_gen}")
    print(f"   笔记总数: {len(raw_data.get('notes', {}))}")
    
    if 'insights' in raw_data:
        ins = raw_data['insights']
        daily_count = len(ins.get('daily', []))
        print(f"   每日洞察: {daily_count} 条")
        
except Exception as e:
    print(f"   错误: {e}")

print()

# 2. 检查 GitHub Pages 实际页面
print("[2] GitHub Pages 部署页面 (nomasterpiecenow.github.io):")
try:
    url = "https://nomasterpiecenow.github.io/xhs-tracker/data.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        pages_data = json.loads(resp.read().decode('utf-8'))
    
    pages_gen = pages_data.get("generatedAt") or pages_data.get("insights", {}).get("generatedAt", "unknown")
    print(f"   生成时间: {pages_gen}")
    print(f"   笔记总数: {len(pages_data.get('notes', {}))}")
    
    if raw_gen == pages_gen:
        print(f"   ✓ 线上两个源数据一致")
    else:
        print(f"   ✗ 线上数据不一致!")
        print(f"      raw: {raw_gen}")
        print(f"      pages: {pages_gen}")
        
except Exception as e:
    print(f"   错误: {e}")

print()

# 3. 检查本地 gh-pages 仓库
print("[3] 本地 gh-pages 仓库:")
script_dir = os.path.dirname(os.path.abspath(__file__))
local_data = os.path.join(script_dir, "data.json")
if os.path.exists(local_data):
    try:
        with open(local_data, 'r', encoding='utf-8') as f:
            local_json = json.load(f)
        local_gen = local_json.get("generatedAt") or local_json.get("insights", {}).get("generatedAt", "unknown")
        print(f"   生成时间: {local_gen}")
        print(f"   笔记总数: {len(local_json.get('notes', {}))}")
        
        if local_gen == raw_gen:
            print(f"   ✓ 本地与线上 raw 一致")
        else:
            print(f"   ✗ 本地与线上不一致!")
            print(f"      本地: {local_gen}")
            print(f"      raw:  {raw_gen}")
            
    except Exception as e:
        print(f"   错误: {e}")
else:
    print(f"   文件不存在: {local_data}")

print()

# 4. 检查 git 状态
print("[4] Git 仓库状态:")
try:
    import subprocess
    result = subprocess.run(["git", "log", "--oneline", "-5"], 
                          cwd=script_dir, 
                          capture_output=True, 
                          text=True,
                          check=True)
    print("   最近 5 次提交:")
    for line in result.stdout.strip().split('\n')[:5]:
        print(f"     {line}")
except Exception as e:
    print(f"   错误: {e}")

print()
print("=== 诊断完成 ===")
print()
print("【总结】")
if raw_gen == pages_gen and raw_gen != "unknown":
    print(f"✓ GitHub Pages 已同步最新数据: {raw_gen}")
    print(f"  如果页面仍显示旧内容，可能是浏览器缓存问题")
    print(f"  请按 Ctrl+Cmd+R 或 Ctrl+F5 强制刷新")
else:
    print(f"✗ 需要检查:")
    print(f"  - raw GitHub: {raw_gen}")
    print(f"  - Pages: {pages_gen}")
    print()
    print("【可能的原因】")
    print("1. GitHub Pages 构建失败或延迟（需要 2-5 分钟）")
    print("2. 浏览器缓存了旧页面 (Ctrl+F5 强制刷新)")
    print("3. 推送到错误的分支 (应该推到 main 分支)")
    print("4. GitHub Actions Pages 构建流程出错")
