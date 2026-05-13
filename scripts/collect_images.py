#!/usr/bin/env python3
"""
收集当天 MiniMax 生成的图片和音乐
扫描 D:\HermesFiles\ 下当天的文件，返回元数据
"""
import os
import json
import glob
from datetime import date

TODAY = date.today().isoformat()
BASE = "/mnt/d/HermesFiles"

def collect_daily():
    images = []
    music = []

    # 扫描当天图片
    for ext in ["png", "jpg", "jpeg", "webp"]:
        for f in glob.glob(f"{BASE}/images/**/{TODAY}*.{ext}", recursive=True):
            images.append({
                "filename": os.path.basename(f),
                "path": f,
                "date": TODAY
            })

    # 扫描当天音乐
    for ext in ["mp3", "wav"]:
        for f in glob.glob(f"{BASE}/music/**/{TODAY}*.{ext}", recursive=True):
            music.append({
                "filename": os.path.basename(f),
                "path": f,
                "date": TODAY
            })

    # 限制数量
    data = {
        "date": TODAY,
        "images": images[:3],
        "music": music[:2]
    }
    return data

if __name__ == "__main__":
    data = collect_daily()
    print(json.dumps(data, ensure_ascii=False, indent=2))
