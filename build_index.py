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
    return {"generatedAt": datetime.now().isoformat(timespec="seconds"), "channels": channels}

INDEX = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>精读报告 · Channels</title>
<meta name="description" content="按频道整理的精读报告与阅读状态。">
<style>
:root{--ink:#181818;--paper:#fff;--line:#dedede;--soft:#f6f6f6;--muted:#999;--serif:Georgia,"Times New Roman","Songti SC",serif;--sans:Arial,"Helvetica Neue",sans-serif}
*{box-sizing:border-box}html{background:var(--paper)}body{margin:0;color:var(--ink);background:var(--paper);font-family:var(--serif)}button{font:inherit;color:inherit}.app{max-width:900px;margin:0 auto;min-height:100vh}.sidebar{padding:30px 20px 0;display:flex;flex-direction:column;align-items:center;gap:22px;background:var(--paper)}.brand{display:flex;align-items:center;justify-content:center}.brand-mark{display:none}.brand-name{font-family:var(--sans);font-size:25px;font-weight:700;letter-spacing:-.08em}.side-label{display:none}.channel-list{display:flex;flex-wrap:wrap;justify-content:center;gap:0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:12px 0}.channel-button{border:0;background:transparent;text-align:center;padding:0 18px;cursor:pointer;font-family:var(--sans);font-size:11px;letter-spacing:.11em;text-transform:uppercase;color:#777}.channel-button:hover,.channel-button.active{color:var(--ink)}.channel-button.active{font-weight:700}.count{font-size:10px;color:#aaa;margin-left:5px}.side-foot{display:none}.main{min-width:0;padding:0 42px 72px}.topbar{display:flex;justify-content:center;align-items:center;padding:26px 0 0}.kicker{font-family:var(--sans);font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#aaa}.menu{display:none}.hero{display:block;padding:72px 0 64px;text-align:center;border-bottom:1px solid var(--line)}h1{font-family:var(--sans);font-size:clamp(38px,6vw,64px);font-weight:400;line-height:1;letter-spacing:-.05em;text-transform:uppercase;margin:0}.hero-note{margin:24px auto 0;color:#999;line-height:1.6;font-size:14px}.hero-note strong{display:block;color:var(--ink);font-family:var(--sans);font-size:12px;font-weight:400;letter-spacing:.12em;text-transform:uppercase;margin-bottom:8px}.toolbar{display:flex;justify-content:space-between;align-items:baseline;padding:38px 0 18px;gap:12px}.toolbar-title{font-family:var(--sans);font-size:14px;font-weight:700;letter-spacing:.08em;text-transform:uppercase}.toolbar-actions{display:flex;gap:12px;align-items:center}.meta{font-family:var(--sans);font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:#aaa}.outline{border:0;border-bottom:1px solid #888;background:transparent;padding:0 0 3px;cursor:pointer;font-family:var(--sans);font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:#777}.outline:hover{color:var(--ink);border-color:var(--ink)}.document-list{border-top:1px solid var(--ink)}.document{display:grid;grid-template-columns:42px minmax(0,1fr) auto;gap:18px;align-items:start;padding:32px 0;border-bottom:1px solid var(--line);text-decoration:none;color:inherit}.document:hover{background:var(--soft);margin:0 -12px;padding-left:12px;padding-right:12px}.doc-number{font-family:var(--sans);font-size:10px;color:#aaa;padding-top:5px}.doc-title{font-family:var(--serif);font-size:clamp(21px,2.6vw,30px);font-weight:400;line-height:1.23;letter-spacing:-.025em;margin:0 0 12px}.doc-meta{display:flex;gap:12px;align-items:center;font-family:var(--sans);font-size:10px;letter-spacing:.05em;color:#aaa;text-transform:uppercase}.status{color:#777;font-size:10px}.document.read .status{color:#aaa}.document.read .doc-title{color:#999}.mark{border:0;background:transparent;cursor:pointer;font-family:var(--sans);font-size:10px;letter-spacing:.04em;text-transform:uppercase;padding:5px 0;color:#999;white-space:nowrap}.mark:hover{color:var(--ink)}.empty{padding:50px 0;color:#999}.footer{border-top:1px solid var(--line);margin-top:54px;padding-top:16px;color:#aaa;font-family:var(--sans);font-size:10px;letter-spacing:.06em;text-transform:uppercase;display:flex;justify-content:space-between;gap:12px}
@media(max-width:760px){.app{width:100%}.sidebar{padding:24px 16px 0}.brand-name{font-size:22px}.channel-list{gap:12px 0}.channel-button{padding:0 10px}.main{padding:0 20px 52px}.hero{padding:54px 0 44px}.toolbar{align-items:flex-start;flex-direction:column;padding-top:28px}.document{grid-template-columns:26px minmax(0,1fr);gap:10px;padding:25px 0}.mark{grid-column:2;text-align:left;padding-top:0}.document:hover{margin:0 -8px;padding-left:8px;padding-right:8px}.footer{display:block}.footer span{display:block;margin-top:7px}}
</style></head>
<body><div class="app"><aside class="sidebar" id="sidebar"><div class="brand"><span class="brand-mark"></span><span class="brand-name">精读档案</span></div><nav><div class="side-label">Channels</div><div class="channel-list" id="channels"></div></nav><div class="side-foot">本地目录即频道来源。<br>新增 <code>Channel/</code> 下的文件夹后，监听器会同步首页。</div></aside><main class="main"><div class="topbar"><div class="kicker">READING REPORTS / 2026</div><button class="menu" id="menu" aria-label="打开频道菜单">频道</button></div><section class="hero"><h1 id="hero-title">Reading<br>reports.</h1><div class="hero-note"><strong id="hero-count">0</strong><span>份报告，按频道归档。<br>阅读状态保存在本浏览器。</span></div></section><div class="toolbar"><div class="toolbar-title" id="section-title">选择一个频道</div><div class="toolbar-actions"><span class="meta" id="unread-summary"></span><button class="outline" id="mark-all" hidden>全部标为已读</button></div></div><section class="document-list" id="documents" aria-live="polite"></section><footer class="footer"><span id="footer-count"></span><span>目录驱动 · 静态同步</span></footer></main></div>
<script>
const state={manifest:null,channel:null,read:new Set(JSON.parse(localStorage.getItem('reading-report-read')||'[]'))};
const $=s=>document.querySelector(s); const key=id=>id;
function href(path){return path.split('/').map(encodeURIComponent).join('/')}
function save(){localStorage.setItem('reading-report-read',JSON.stringify([...state.read]))}
function current(){return state.manifest.channels.find(c=>c.id===state.channel)||state.manifest.channels[0]}
function renderChannels(){const root=$('#channels');root.innerHTML='';state.manifest.channels.forEach(channel=>{const unread=channel.documents.filter(d=>!state.read.has(key(d.id))).length;const b=document.createElement('button');b.className='channel-button'+(channel.id===state.channel?' active':'');b.innerHTML=`<span>${escapeHtml(channel.name)}</span><span class="count">${unread||''}</span>`;b.onclick=()=>{state.channel=channel.id;$('#sidebar').classList.remove('open');render()};root.appendChild(b)})}
function escapeHtml(value){return value.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function render(){const channel=current();if(!channel)return;const unread=channel.documents.filter(d=>!state.read.has(key(d.id))).length;$('#section-title').textContent=channel.name;$('#hero-count').textContent=channel.documents.length;$('#unread-summary').textContent=`${unread} unread`;$('#mark-all').hidden=!unread;$('#mark-all').onclick=()=>{channel.documents.forEach(d=>state.read.add(key(d.id)));save();render()};const root=$('#documents');root.innerHTML='';if(!channel.documents.length){root.innerHTML='<div class="empty">这个频道还没有报告。</div>'}channel.documents.forEach((doc,i)=>{const isRead=state.read.has(key(doc.id));const row=document.createElement('div');row.className='document'+(isRead?' read':'');row.innerHTML=`<span class="doc-number">${String(i+1).padStart(2,'0')}</span><div><h2 class="doc-title">${escapeHtml(doc.title)}</h2><div class="doc-meta"><span>${doc.date}</span><span class="status">${isRead?'已读':'未读'}</span></div></div><button class="mark" type="button">${isRead?'标记未读':'标记已读'}</button>`;row.querySelector('.mark').onclick=()=>{if(state.read.has(key(doc.id)))state.read.delete(key(doc.id));else state.read.add(key(doc.id));save();render()};row.querySelector('.doc-title').onclick=()=>location.href=href(doc.path);root.appendChild(row)});$('#footer-count').textContent=`${state.manifest.channels.length} channels · ${state.manifest.channels.reduce((n,c)=>n+c.documents.length,0)} reports`;renderChannels()}
$('#menu').onclick=()=>$('#sidebar').classList.toggle('open');
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
