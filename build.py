#!/usr/bin/env python3
"""
静态站点生成器
读取 data/ 目录下的 JSON 文件，生成完整静态 HTML 站点
输出到 dist/ 目录
"""
import os
import json
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DIST_DIR = BASE_DIR / "dist"
SRC_DIR = BASE_DIR / "src"

# 确保输出目录存在
DIST_DIR.mkdir(parents=True, exist_ok=True)
(DIST_DIR / "date").mkdir(parents=True, exist_ok=True)
(DIST_DIR / "assets/css").mkdir(parents=True, exist_ok=True)
(DIST_DIR / "assets/js").mkdir(parents=True, exist_ok=True)

def load_data():
    """加载所有日期的 JSON 数据"""
    all_data = []
    if DATA_DIR.exists():
        for json_file in sorted(DATA_DIR.glob("*.json")):
            if json_file.name == "README.md":
                continue
            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)
                    all_data.append(data)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
    return sorted(all_data, key=lambda x: x.get("date", ""), reverse=True)

def generate_css():
    """生成深色主题 CSS"""
    return """/* 全局深色主题 */
:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --bg-card: #1a1a24;
    --text-primary: #e8e8f0;
    --text-secondary: #8888a0;
    --accent: #7c5af0;
    --accent2: #4fa3f7;
    --border: #2a2a3a;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
}

/* 顶部导航 */
header {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    padding: 1rem 2rem;
    position: sticky;
    top: 0;
    z-index: 100;
}

header h1 {
    font-size: 1.2rem;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}

.date-nav {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.date-nav a {
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 0.85rem;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    border: 1px solid var(--border);
    transition: all 0.2s;
}

.date-nav a:hover, .date-nav a.active {
    color: var(--text-primary);
    border-color: var(--accent);
    background: rgba(124, 90, 240, 0.1);
}

/* 主容器 */
.container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 2rem;
}

.date-header {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}

/* 新闻区块 */
.section { margin-bottom: 3rem; }
.section-title {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent2);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.news-list { display: flex; flex-direction: column; gap: 1rem; }

.news-item {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
}

.news-item h3 {
    font-size: 1rem;
    margin-bottom: 0.5rem;
}

.news-item h3 a {
    color: var(--text-primary);
    text-decoration: none;
}

.news-item h3 a:hover {
    color: var(--accent);
}

.news-item .snippet {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
}

.news-item .source {
    font-size: 0.8rem;
    color: var(--text-secondary);
    opacity: 0.7;
}

/* 图片网格 */
.gallery {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
}

.gallery img {
    width: 100%;
    aspect-ratio: 1;
    object-fit: cover;
    border-radius: 12px;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    border: 1px solid var(--border);
}

.gallery img:hover {
    transform: scale(1.02);
    box-shadow: 0 8px 30px rgba(124, 90, 240, 0.2);
}

/* 音乐播放列表 */
.music-list {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

.music-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    transition: background 0.2s;
}

.music-item:last-child { border-bottom: none; }
.music-item:hover { background: rgba(124, 90, 240, 0.05); }
.music-item.playing { background: rgba(124, 90, 240, 0.1); }

.music-icon {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.music-icon svg { width: 20px; height: 20px; fill: white; }

.music-info { flex: 1; min-width: 0; }
.music-info .name {
    font-size: 0.95rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.music-info .extra {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.play-btn {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: none;
    background: var(--accent);
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s;
}

.play-btn:hover { background: var(--accent2); }

/* 灯箱 */
.lightbox {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.95);
    z-index: 1000;
    align-items: center;
    justify-content: center;
}

.lightbox.active { display: flex; }

.lightbox img {
    max-width: 90vw;
    max-height: 90vh;
    border-radius: 8px;
}

.lightbox-close {
    position: absolute;
    top: 20px;
    right: 30px;
    font-size: 2rem;
    color: white;
    cursor: pointer;
    background: none;
    border: none;
}

.lightbox-nav {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    font-size: 2rem;
    color: white;
    cursor: pointer;
    background: rgba(255,255,255,0.1);
    border: none;
    padding: 1rem;
    border-radius: 8px;
}

.lightbox-nav.prev { left: 20px; }
.lightbox-nav.next { right: 20px; }

/* 响应式 */
@media (max-width: 600px) {
    .container { padding: 1rem; }
    header { padding: 1rem; }
    .gallery { grid-template-columns: repeat(2, 1fr); gap: 0.5rem; }
}

/* 空状态 */
.empty {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--text-secondary);
}

.empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}
"""

def generate_js():
    """生成前端 JS"""
    return """
// 图片灯箱
class Lightbox {
    constructor() {
        this.images = [];
        this.current = 0;
        this.el = document.getElementById('lightbox');
        this.imgEl = this.el?.querySelector('img');
        this.bind();
    }

    bind() {
        document.querySelectorAll('.gallery img').forEach((img, i) => {
            img.addEventListener('click', () => this.open(i));
        });
        this.el?.querySelector('.lightbox-close')?.addEventListener('click', () => this.close());
        this.el?.querySelector('.prev')?.addEventListener('click', () => this.prev());
        this.el?.querySelector('.next')?.addEventListener('click', () => this.next());
        document.addEventListener('keydown', e => {
            if (!this.el?.classList.contains('active')) return;
            if (e.key === 'Escape') this.close();
            if (e.key === 'ArrowLeft') this.prev();
            if (e.key === 'ArrowRight') this.next();
        });
    }

    open(index) {
        this.images = Array.from(document.querySelectorAll('.gallery img')).map(img => img.src);
        this.current = index;
        this.show();
        this.el.classList.add('active');
    }

    close() {
        this.el.classList.remove('active');
    }

    prev() {
        this.current = (this.current - 1 + this.images.length) % this.images.length;
        this.show();
    }

    next() {
        this.current = (this.current + 1) % this.images.length;
        this.show();
    }

    show() {
        if (this.imgEl) this.imgEl.src = this.images[this.current];
    }
}

// 音乐播放
class MusicPlayer {
    constructor() {
        this.current = null;
        this.audio = new Audio();
        this.bind();
    }

    bind() {
        document.querySelectorAll('.music-item').forEach((item, i) => {
            item.addEventListener('click', () => this.play(i));
        });
    }

    play(index) {
        const items = document.querySelectorAll('.music-item');
        const src = items[index]?.dataset.src;
        if (!src) return;

        document.querySelectorAll('.music-item').forEach(el => el.classList.remove('playing'));

        if (this.current === index && !this.audio.paused) {
            this.audio.pause();
            this.current = null;
        } else {
            this.audio.src = src;
            this.audio.play();
            this.current = index;
            items[index].classList.add('playing');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Lightbox();
    new MusicPlayer();
});
"""

def generate_page(data, all_dates):
    """生成单日页面 HTML"""
    date_str = data.get("date", "")
    images = data.get("images", [])
    music = data.get("music", [])
    news = data.get("news", [])

    # 日期导航
    date_nav_html = ""
    for d in all_dates:
        active = "active" if d["date"] == date_str else ""
        date_nav_html += f'<a href="/date/{d["date"]}/" class="{active}">{d["date"]}</a>'

    # 新闻
    news_html = ""
    if news:
        for item in news:
            news_html += f"""
        <div class="news-item">
            <h3><a href="{item['url']}" target="_blank">{item['title']}</a></h3>
            <p class="snippet">{item['snippet']}</p>
            <span class="source">{item.get('source', '')}</span>
        </div>"""
    else:
        news_html = '<div class="empty"><div class="empty-icon">📰</div><p>今日暂无新闻</p></div>'

    # 图片
    images_html = ""
    if images:
        for img in images:
            img_url = img.get("r2_url", f"file://{img['path']}")
            images_html += f'<img src="{img_url}" alt="{img["filename"]}" loading="lazy">'
    else:
        images_html = '<div class="empty"><div class="empty-icon">🖼️</div><p>今日暂无图片</p></div>'

    # 音乐
    music_html = ""
    if music:
        for i, m in enumerate(music):
            m_url = m.get("r2_url", f"file://{m['path']}")
            music_html += f"""
        <div class="music-item" data-src="{m_url}">
            <div class="music-icon">
                <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            </div>
            <div class="music-info">
                <div class="name">{m["filename"]}</div>
            </div>
            <button class="play-btn">▶</button>
        </div>"""
    else:
        music_html = '<div class="empty"><div class="empty-icon">🎵</div><p>今日暂无音乐</p></div>'

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{date_str} - AI Daily</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <header>
        <h1>🤖 AI Daily</h1>
        <nav class="date-nav">{date_nav_html}</nav>
    </header>
    <main class="container">
        <div class="date-header">📅 {date_str}</div>

        <section class="section">
            <h2 class="section-title">📰 AI 资讯</h2>
            <div class="news-list">{news_html}</div>
        </section>

        <section class="section">
            <h2 class="section-title">🖼️ 今日图片</h2>
            <div class="gallery">{images_html}</div>
        </section>

        <section class="section">
            <h2 class="section-title">🎵 今日音乐</h2>
            <div class="music-list">{music_html}</div>
        </section>
    </main>

    <div id="lightbox" class="lightbox">
        <button class="lightbox-close">&times;</button>
        <button class="lightbox-nav prev">&#10094;</button>
        <img src="" alt="">
        <button class="lightbox-nav next">&#10095;</button>
    </div>

    <script src="/assets/js/main.js"></script>
</body>
</html>"""

def generate_index(pages_data):
    """生成首页（最新一天的内容）"""
    if not pages_data:
        return generate_page({
            "date": date.today().isoformat(),
            "images": [],
            "music": [],
            "news": []
        }, [{"date": date.today().isoformat()}])
    return pages_data[0]

def main():
    all_data = load_data()
    print(f"Loaded {len(all_data)} days of data")

    # 写入静态资源
    css_dir = DIST_DIR / "assets" / "css"
    css_dir.mkdir(parents=True, exist_ok=True)
    (css_dir / "style.css").write_text(generate_css(), encoding="utf-8")

    js_dir = DIST_DIR / "assets" / "js"
    js_dir.mkdir(parents=True, exist_ok=True)
    (js_dir / "main.js").write_text(generate_js(), encoding="utf-8")

    # 生成每个日期页面
    for data in all_data:
        date_str = data.get("date", "")
        if not date_str:
            continue
        page = generate_page(data, all_data)
        out_path = DIST_DIR / "date" / date_str / "index.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page)
        print(f"Generated: {out_path}")

    # 生成首页
    index_page = generate_index(all_data)
    with open(DIST_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(index_page)
    print(f"Generated: {DIST_DIR / 'index.html'}")

    print(f"\\nDone! Output in {DIST_DIR}")

if __name__ == "__main__":
    main()
