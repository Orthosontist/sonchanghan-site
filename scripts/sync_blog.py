"""Refresh RSS excerpts; never present truncated RSS as full articles."""
from pathlib import Path
import urllib.request,xml.etree.ElementTree as ET,re,html
root=Path(__file__).resolve().parents[1]
with urllib.request.urlopen('https://rss.blog.naver.com/ckdtgks.xml',timeout=30) as r:
    feed=ET.fromstring(r.read())
items=feed.findall('./channel/item')
if not items: raise RuntimeError('No RSS entries; preserving existing content')
cards=[]
for item in items[:12]:
    title=item.findtext('title') or ''; link=item.findtext('link') or ''
    if not re.match(r'https?://(?:m\.)?blog\.naver\.com/',link): continue
    excerpt=html.unescape(re.sub('<[^>]+>','',item.findtext('description') or ''))[:220]
    cards.append('<a class="case-card" href="'+html.escape(link,quote=True)+'" target="_blank" rel="noopener"><div class="case-body"><h3>'+html.escape(title)+'</h3><p>'+html.escape(excerpt)+'…</p><span>네이버에서 전문 읽기 ↗</span></div></a>')
block='<section id="blog-updates" style="padding:64px 6vw"><div class="journal-inner"><h2>블로그의 새로운 기록</h2><p style="margin:20px 0">최근 글의 일부를 소개합니다. 전문은 네이버 블로그에서 읽으실 수 있습니다.</p><div class="case-grid">'+''.join(cards)+'</div></div></section>'
p=root/'index.html';s=p.read_text();start='<!-- RSS:START -->';end='<!-- RSS:END -->'
if start not in s:s=s.replace('<!-- FOOTER -->',start+end+'\n<!-- FOOTER -->')
s=re.sub(re.escape(start)+'.*?'+re.escape(end),lambda m:start+block+end,s,flags=re.S);p.write_text(s)
print(f'Refreshed {len(cards)} RSS excerpts')
