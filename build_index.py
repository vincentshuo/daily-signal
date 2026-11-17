from pathlib import Path
from html import escape
from datetime import datetime

ROOT = Path(__file__).parent
OUT = ROOT / "index.html"

def title_for(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    marker = "<title>"
    if marker in text.lower():
        start = text.lower().find(marker) + len(marker)
        end = text.lower().find("</title>", start)
        if end > start:
            return text[start:end].strip()
    return path.stem

docs = sorted((p for p in ROOT.rglob("*.html") if p.name != "index.html"), key=lambda p: p.stat().st_mtime, reverse=True)
cards = []
for path in docs:
    rel = path.relative_to(ROOT).as_posix()
    title = title_for(path)
    modified = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y.%m.%d")
    cards.append(f'''<a class="card" href="{escape(rel)}">
      <span class="card-index">{len(cards)+1:02d}</span>
      <span class="card-body"><span class="card-title">{escape(title)}</span><span class="card-meta">{modified} · HTML reading report</span></span>
      <span class="arrow">↗</span>
    </a>''')

html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Daily Signal · YouTube daily feed</title>
<meta name="description" content="A quiet, daily reading feed for ideas found on YouTube.">
<style>
:root{{color-scheme:dark;--bg:#11120f;--paper:#f2efe7;--muted:#a9aa9f;--line:#34362f;--accent:#d6f06a;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--paper);font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,"Helvetica Neue",Arial,sans-serif;}}
main{{max-width:980px;margin:0 auto;padding:8vw 6vw 10vw}}header{{display:flex;justify-content:space-between;align-items:flex-start;border-top:1px solid var(--line);padding-top:18px;margin-bottom:16vh}}
.eyebrow,.card-meta,.footer{{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}}h1{{font-size:clamp(54px,10vw,116px);line-height:.88;letter-spacing:-.07em;font-weight:500;max-width:760px;margin:0 0 28px}}.intro{{max-width:420px;color:var(--muted);font-size:17px;line-height:1.55;margin-left:auto}}
.list{{border-top:1px solid var(--line)}}.card{{display:grid;grid-template-columns:56px 1fr 30px;gap:18px;align-items:start;text-decoration:none;color:inherit;border-bottom:1px solid var(--line);padding:26px 0;transition:padding .25s ease,color .25s ease}}.card:hover{{padding-left:12px;color:var(--accent)}}.card-index{{font-size:12px;color:var(--muted);padding-top:4px}}.card-body{{display:grid;gap:12px}}.card-title{{font-size:clamp(20px,3vw,30px);line-height:1.2;letter-spacing:-.025em}}.card-meta{{letter-spacing:.08em}}.arrow{{font-size:22px;color:var(--accent);opacity:.75}}.footer{{display:flex;justify-content:space-between;margin-top:34px}}
</style></head><body><main><header><span class="eyebrow">Daily Signal / 001</span><span class="eyebrow">YouTube → Ideas</span></header>
<section><p class="eyebrow">A daily reading feed</p><h1>Signals worth<br>keeping.</h1><p class="intro">Long-form notes from the videos that stayed with me. One quiet shelf for new ideas, every day.</p></section>
<section class="list" aria-label="Reading reports">{''.join(cards)}</section><footer class="footer"><span>{len(docs):02d} reports</span><span>Updated locally · synced to GitHub Pages</span></footer>
</main></body></html>'''
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(docs)} reports)")
