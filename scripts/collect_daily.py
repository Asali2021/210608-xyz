#!/usr/bin/env python3
"""
每日内容收集主脚本
1. 收集 MiniMax 当天生成的图片和音乐
2. 收集 Tavily AI 新闻
3. 上传图片/音乐到 Cloudflare R2
4. 输出 data/YYYY-MM-DD.json 元数据
"""
import os
import sys
import json
import glob
import shutil
import hashlib
import urllib.request
import urllib.parse
import urllib.error
from datetime import date
from pathlib import Path

# R2 配置（留空，后续由 GitHub Actions Secrets 注入）
R2_CONFIG = {
    "account_id": os.getenv("R2_ACCOUNT_ID", ""),
    "access_key_id": os.getenv("R2_ACCESS_KEY_ID", ""),
    "secret_access_key": os.getenv("R2_SECRET_ACCESS_KEY", ""),
    "bucket_name": os.getenv("R2_BUCKET_NAME", "ai-daily-assets"),
}

TODAY = date.today().isoformat()
def get_hermes_base():
    """获取 Hermes 工作区路径（兼容 WSL 和 Windows）"""
    # WSL 环境：/mnt/d/ -> D:\
    import platform
    if platform.system() == "Linux" and os.path.exists("/mnt/d"):
        return "/mnt/d/HermesFiles"
    # Windows Python
    if os.path.exists("D:\\"):
        return "D:\\HermesFiles"
    # 备用
    return os.path.expanduser("~/HermesFiles")

BASE = get_hermes_base()
DATA_DIR = Path(__file__).parent.parent / "data"
OUT_JSON = DATA_DIR / f"{TODAY}.json"


def get_r2_client():
    """创建 R2 S3 兼容客户端"""
    if not R2_CONFIG["account_id"] or not R2_CONFIG["access_key_id"]:
        return None
    try:
        import boto3
        return boto3.client(
            "s3",
            endpoint_url=f"https://{R2_CONFIG['account_id']}.r2.dev",
            aws_access_key_id=R2_CONFIG["access_key_id"],
            aws_secret_access_key=R2_CONFIG["secret_access_key"],
        )
    except ImportError:
        print("WARNING: boto3 not installed, skipping R2 upload")
        return None


def upload_to_r2(client, local_path, r2_key):
    """上传文件到 R2，返回公开 URL"""
    try:
        client.upload_file(local_path, R2_CONFIG["bucket_name"], r2_key)
        return f"https://assets.210608.xyz/{r2_key}"
    except Exception as e:
        print(f"R2 upload error: {e}")
        return None


def file_hash(path):
    """计算文件 MD5（用于去重）"""
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def collect_images_and_music():
    """扫描当天生成的图片和音乐"""
    images = []
    music = []

    # 图片
    for ext in ["png", "jpg", "jpeg", "webp"]:
        for f in glob.glob(f"{BASE}/images/**/{TODAY}*.{ext}", recursive=True):
            if not os.path.isfile(f):
                continue
            r2_key = f"images/{TODAY}/{os.path.basename(f)}"
            images.append({
                "filename": os.path.basename(f),
                "local_path": f,
                "r2_key": r2_key,
                "date": TODAY
            })

    # 音乐
    for ext in ["mp3", "wav"]:
        for f in glob.glob(f"{BASE}/music/**/{TODAY}*.{ext}", recursive=True):
            if not os.path.isfile(f):
                continue
            r2_key = f"music/{TODAY}/{os.path.basename(f)}"
            music.append({
                "filename": os.path.basename(f),
                "local_path": f,
                "r2_key": r2_key,
                "date": TODAY
            })

    return images[:3], music[:2]


def collect_news():
    """通过 Tavily API 收集当天 AI 新闻"""
    api_key = os.getenv("TAVILY_API_KEY", "")

    # 尝试从本地配置文件读取
    if not api_key:
        env_path = Path.home() / ".hermes" / ".env"
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.startswith("TAVILY_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip('"')
                        break

    if not api_key:
        print("WARNING: TAVILY_API_KEY not found, news will be empty")
        return []

    queries = [
        f"AI image generation latest news {TODAY}",
        f"AI music artificial intelligence {TODAY}",
        "artificial intelligence latest",
    ]

    all_results = []
    seen_urls = set()

    for query in queries:
        try:
            url = f"https://api.tavily.com/search?q={urllib.parse.quote(query)}&api_key={api_key}&max_results=3"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                for item in data.get("results", []):
                    url_val = item.get("url", "")
                    if url_val and url_val not in seen_urls:
                        seen_urls.add(url_val)
                        all_results.append({
                            "title": item.get("title", ""),
                            "snippet": item.get("content", "")[:200],
                            "url": url_val,
                            "source": item.get("source", "")
                        })
        except Exception as e:
            print(f"Tavily query error '{query}': {e}")

    return all_results[:3]


def main():
    print(f"[{TODAY}] Starting daily collection...")

    # Step 1: 收集图片和音乐
    print("Collecting images and music...")
    images, music = collect_images_and_music()
    print(f"  Found {len(images)} images, {len(music)} music files")

    # Step 2: 上传到 R2
    r2_client = get_r2_client()
    if r2_client:
        print("Uploading to R2...")
        for img in images:
            url = upload_to_r2(r2_client, img["local_path"], img["r2_key"])
            img["r2_url"] = url or f"file://{img['local_path']}"
            print(f"  Uploaded: {img['filename']} -> {url}")
        for m in music:
            url = upload_to_r2(r2_client, m["local_path"], m["r2_key"])
            m["r2_url"] = url or f"file://{m['local_path']}"
            print(f"  Uploaded: {m['filename']} -> {url}")
    else:
        print("R2 not configured, using local paths")
        for img in images:
            img["r2_url"] = f"file://{img['local_path']}"
        for m in music:
            m["r2_url"] = f"file://{m['local_path']}"

    # Step 3: 收集新闻
    print("Collecting news...")
    news = collect_news()
    print(f"  Found {len(news)} news items")

    # Step 4: 组装 JSON
    data = {
        "date": TODAY,
        "images": images,
        "music": music,
        "news": news
    }

    # Step 5: 写入 JSON 文件
    DATA_DIR.mkdir(exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved: {OUT_JSON}")
    print(f"Done! {len(images)} imgs, {len(music)} songs, {len(news)} news")

    # 如果在 GitHub Actions 中，输出 JSON 供后续使用
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.getenv("GITHUB_OUTPUT"), "a") as f:
            f.write(f"has_content={'true' if (images or music) else 'false'}\n")

    return data


if __name__ == "__main__":
    main()
