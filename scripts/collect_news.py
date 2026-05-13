#!/usr/bin/env python3
"""
收集当天 AI 相关新闻
使用 Tavily MCP API 搜索当天 AI 资讯
"""
import os
import json
import urllib.request
import urllib.parse
from datetime import date

TODAY = date.today().isoformat()

def collect_news():
    # 从环境变量读取 Tavily API Key
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        # 尝试从配置文件读取
        env_path = os.path.expanduser("~/.hermes/.env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("TAVILY_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        break

    if not api_key:
        print("WARNING: TAVILY_API_KEY not found, returning empty news")
        return {"date": TODAY, "news": []}

    # 搜索当天 AI 新闻
    queries = [
        f"AI image generation news {TODAY}",
        f"AI music artificial intelligence {TODAY}",
        f"artificial intelligence latest {TODAY}"
    ]

    all_results = []
    for query in queries:
        try:
            url = f"https://api.tavily.com/search?q={urllib.parse.quote(query)}&api_key={api_key}&max_results=2"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
                for item in data.get("results", []):
                    item["query"] = query
                    all_results.append(item)
        except Exception as e:
            print(f"Tavily search error for '{query}': {e}")

    # 去重，按相关度排序，取前3条
    seen_urls = set()
    unique_results = []
    for item in all_results:
        url = item.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append({
                "title": item.get("title", ""),
                "snippet": item.get("content", ""),
                "url": url,
                "source": item.get("source", "")
            })

    return {
        "date": TODAY,
        "news": unique_results[:3]
    }

if __name__ == "__main__":
    data = collect_news()
    print(json.dumps(data, ensure_ascii=False, indent=2))
