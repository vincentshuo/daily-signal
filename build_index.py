# -*- coding: utf-8 -*-
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
import json
import re

ROOT = Path(__file__).parent
CHANNEL_ROOT = ROOT / "Channel"
MANIFEST = ROOT / "manifest.json"
OUT = ROOT / "index.html"

class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title":
            self.in_title = True
    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False
    def handle_data(self, data):
        if self.in_title:
            self.parts.append(data)

def title_for(path: Path) -> str:
    parser = TitleParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    title = "".join(parser.parts).strip()
    return title or path.stem

def discover():
    channels = []
    for channel_dir in sorted((p for p in CHANNEL_ROOT.iterdir() if p.is_dir()), key=lambda p: p.name.casefold()):
        docs = []
        for path in channel_dir.glob("*.html"):
            stat = path.stat()
            rel = path.relative_to(ROOT).as_posix()
            docs.append({
                "id": rel,
                "path": rel,
                "title": title_for(path),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                "date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y.%m.%d"),
                "channel": channel_dir.name,
            })
        docs.sort(key=lambda item: (item["modified"], item["path"]), reverse=True)
        channels.append({"id": channel_dir.name, "name": channel_dir.name, "documents": docs})
    return {"channels": channels}

INDEX = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>精读报告 · Channels</title>
<meta name="description" content="按频道整理的精读报告与阅读状态。">
<style>
@font-face{font-family:"Cormorant Garamond";font-style:italic;font-weight:500;font-display:swap;src:url("assets/fonts/cormorant-garamond-italic-latin.woff2") format("woff2")}
:root{--ink:#181818;--paper:#fff;--line:#e3e3e3;--soft:#f5f5f5;--active:#ececec;--muted:#737373;--serif:Georgia,"Times New Roman","Songti SC",serif;--sans:Arial,"Helvetica Neue",sans-serif;--display:"Cormorant Garamond",Baskerville,"Times New Roman",serif}
*{box-sizing:border-box}html{background:var(--paper)}body{margin:0;color:var(--ink);background:var(--paper);font-family:var(--sans)}button{font:inherit;color:inherit}button,a{-webkit-tap-highlight-color:transparent}button:focus-visible,a:focus-visible{outline:1px solid var(--ink);outline-offset:3px}::selection{color:var(--paper);background:var(--ink)}
.app{display:grid;grid-template-columns:216px minmax(0,1fr);min-height:100vh}.sidebar{position:sticky;top:0;align-self:start;height:100vh;height:100dvh;padding:26px 18px 20px;display:flex;flex-direction:column;gap:30px;overflow-y:auto;background:var(--paper);border-right:1px solid var(--line)}.brand{display:flex;align-items:center;padding:0 8px}.brand-name{font-size:19px;font-weight:700;letter-spacing:-.04em}.side-label{margin:0 10px 9px;color:var(--muted);font-size:10px;line-height:1.4}.channel-list{display:flex;flex-direction:column;gap:2px}.channel-button{display:flex;align-items:center;justify-content:space-between;gap:8px;width:100%;min-height:34px;border:0;border-radius:3px;background:transparent;text-align:left;padding:8px 10px;cursor:pointer;font-size:12px;line-height:18px;letter-spacing:.02em;color:var(--muted)}.channel-button:hover{color:var(--ink);background:var(--soft)}.channel-button.active{color:var(--ink);background:var(--active);font-weight:600}.count{flex:none;font-size:10px;font-weight:400;color:var(--muted);font-variant-numeric:tabular-nums}.side-foot{margin-top:auto;padding:32px 10px 0;color:var(--muted);font-size:10px;line-height:1.7}.side-foot span{display:block}.main{min-width:0;padding:24px 32px 48px}.toolbar{display:flex;justify-content:space-between;align-items:center;gap:16px;min-height:34px;margin-bottom:16px}.toolbar-heading{display:flex;align-items:center;gap:14px;min-width:0}.toolbar-title{margin:0;font-family:var(--display);font-size:32px;font-style:italic;font-weight:500;line-height:1.1;letter-spacing:-.015em}.toolbar-actions{display:flex;gap:16px;align-items:center;flex:none}.meta{font-size:10px;line-height:18px;color:var(--muted);font-variant-numeric:tabular-nums}.outline{border:0;border-bottom:1px solid var(--muted);background:transparent;padding:0 0 2px;cursor:pointer;font-size:10px;line-height:16px;color:var(--muted)}.outline:hover{color:var(--ink);border-color:var(--ink)}.menu{display:none;border:0;background:transparent;padding:4px 0;cursor:pointer;font-size:12px;line-height:18px;color:var(--ink)}.scrim{display:none}.document-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:32px;border-top:1px solid var(--ink)}.document{display:grid;grid-template-columns:24px minmax(0,1fr) 70px 32px;gap:10px;align-items:center;min-width:0;min-height:34px;padding:4px;border-bottom:1px solid var(--line);font-size:12px;line-height:20px}.document:hover,.document:focus-within{background:var(--soft)}.doc-number{color:var(--muted);font-size:10px;font-variant-numeric:tabular-nums}.doc-title{display:block;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--ink);font-family:var(--serif);font-size:12px;font-weight:400;line-height:20px;text-decoration:none}.doc-title:hover{text-decoration:underline;text-underline-offset:3px}.doc-date{color:var(--muted);font-size:10px;white-space:nowrap;font-variant-numeric:tabular-nums}.status{width:32px;min-height:24px;border:0;background:transparent;padding:2px 0;cursor:pointer;color:var(--ink);font-size:10px;line-height:20px;white-space:nowrap}.status:hover{text-decoration:underline;text-underline-offset:3px}.document.read .doc-title,.document.read .status{color:var(--muted)}.empty{grid-column:1/-1;padding:32px 4px;color:var(--muted);font-size:12px}
@media(max-width:900px){.app{display:block}.sidebar{position:fixed;z-index:20;left:0;top:0;width:232px;transform:translateX(-100%);transition:transform .18s ease-out;box-shadow:8px 0 24px rgba(0,0,0,.08)}.sidebar.open{transform:translateX(0)}.sidebar.open+.scrim{display:block;position:fixed;z-index:10;inset:0;border:0;background:rgba(0,0,0,.18);cursor:pointer}.menu{display:block}.main{padding:20px 24px 40px}body.menu-open{overflow:hidden}}
@media(max-width:700px){.main{padding:18px 16px 40px}.document-list{grid-template-columns:minmax(0,1fr)}.document{grid-template-columns:22px minmax(0,1fr) 66px 32px;gap:8px;padding-right:2px;padding-left:2px}.toolbar{gap:10px;margin-bottom:12px}.toolbar-heading{gap:10px}.toolbar-actions{gap:10px}}
@media(prefers-reduced-motion:reduce){.sidebar{transition:none}}
</style></head>
<body><div class="app"><aside class="sidebar" id="sidebar"><div class="brand"><span class="brand-name">Daily Signal</span></div><nav aria-label="报告频道"><div class="side-label">Channels</div><div class="channel-list" id="channels"></div></nav><div class="side-foot"><span id="footer-count"></span><span>阅读状态保存在本浏览器</span></div></aside><button class="scrim" id="scrim" type="button" aria-label="关闭频道菜单"></button><main class="main"><div class="toolbar"><div class="toolbar-heading"><button class="menu" id="menu" type="button" aria-label="打开频道菜单" aria-controls="sidebar" aria-expanded="false">频道</button><h1 class="toolbar-title" id="section-title">选择一个频道</h1></div><div class="toolbar-actions"><span class="meta" id="unread-summary"></span><button class="outline" id="mark-all" type="button" hidden>全部标为已读</button></div></div><section class="document-list" id="documents" aria-live="polite"></section></main></div>
<script>
const state={manifest:null,channel:null,read:new Set(JSON.parse(localStorage.getItem('reading-report-read')||'[]'))};
const $=s=>document.querySelector(s); const key=id=>id;
function href(path){return path.split('/').map(encodeURIComponent).join('/')}
function save(){localStorage.setItem('reading-report-read',JSON.stringify([...state.read]))}
function current(){return state.manifest.channels.find(c=>c.id===state.channel)||state.manifest.channels[0]}
function setMenu(open){$('#sidebar').classList.toggle('open',open);$('#menu').setAttribute('aria-expanded',String(open));document.body.classList.toggle('menu-open',open)}
function renderChannels(){const root=$('#channels');root.innerHTML='';state.manifest.channels.forEach(channel=>{const unread=channel.documents.filter(d=>!state.read.has(key(d.id))).length;const b=document.createElement('button');b.className='channel-button'+(channel.id===state.channel?' active':'');if(channel.id===state.channel)b.setAttribute('aria-current','page');b.innerHTML=`<span>${escapeHtml(channel.name)}</span><span class="count">${unread||''}</span>`;b.onclick=()=>{state.channel=channel.id;setMenu(false);render()};root.appendChild(b)})}
function escapeHtml(value){return value.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function render(){const channel=current();if(!channel)return;const unread=channel.documents.filter(d=>!state.read.has(key(d.id))).length;$('#section-title').textContent=channel.name;$('#unread-summary').textContent=`${channel.documents.length} 篇 · ${unread} 未读`;$('#mark-all').hidden=!unread;$('#mark-all').onclick=()=>{channel.documents.forEach(d=>state.read.add(key(d.id)));save();render()};const root=$('#documents');root.innerHTML='';if(!channel.documents.length){root.innerHTML='<div class="empty">这个频道还没有报告。</div>'}channel.documents.forEach((doc,i)=>{const isRead=state.read.has(key(doc.id));const row=document.createElement('div');row.className='document'+(isRead?' read':'');row.innerHTML=`<span class="doc-number">${String(i+1).padStart(2,'0')}</span><a class="doc-title" href="${href(doc.path)}" title="${escapeHtml(doc.title)}">${escapeHtml(doc.title)}</a><time class="doc-date" datetime="${doc.modified}">${doc.date}</time><button class="status" type="button" aria-pressed="${isRead}" aria-label="${isRead?'标记未读':'标记已读'}：${escapeHtml(doc.title)}">${isRead?'已读':'未读'}</button>`;row.querySelector('.status').onclick=()=>{if(state.read.has(key(doc.id)))state.read.delete(key(doc.id));else state.read.add(key(doc.id));save();render()};root.appendChild(row)});$('#footer-count').textContent=`${state.manifest.channels.length} 个频道 · ${state.manifest.channels.reduce((n,c)=>n+c.documents.length,0)} 份报告`;renderChannels()}
$('#menu').onclick=()=>setMenu(!$('#sidebar').classList.contains('open'));
$('#scrim').onclick=()=>setMenu(false);
document.addEventListener('keydown',event=>{if(event.key==='Escape')setMenu(false)});
fetch('manifest.json').then(r=>r.json()).then(manifest=>{state.manifest=manifest;state.channel=manifest.channels[0]?.id;render()}).catch(()=>{$('#documents').innerHTML='<div class="empty">无法读取 manifest.json，请先运行 build_index.py。</div>'});
</script></body></html>'''

def main():
    manifest = discover()
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT.write_text(INDEX, encoding="utf-8")
    total = sum(len(channel["documents"]) for channel in manifest["channels"])
    print(f"wrote {OUT.name} and {MANIFEST.name}: {len(manifest['channels'])} channels, {total} reports")

if __name__ == "__main__":
    main()
