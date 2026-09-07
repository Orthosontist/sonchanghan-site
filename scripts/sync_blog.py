"""Import public Naver posts as static HTML. Preserve manually edited legacy articles.
Only public PostView pages are read. Failed imports leave last good files intact.
"""
from pathlib import Path
from urllib.parse import urlsplit
from email.utils import parsedate_to_datetime
from concurrent.futures import ThreadPoolExecutor
import urllib.request, xml.etree.ElementTree as ET, re, html, json
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
BASE='https://drsonchanghan.com'
LEGACY={'224317625460':'diary-10-fixed-retainer','224303524267':'diary-9-senior-orthodontics','224298737298':'impacted-molar','224298037342':'diary-8-military-checkup','224291408505':'diary-7-retainer-protocol','224289274170':'diary-6-communication','224279052575':'diary-5-canine-substitution','224266423268':'diary-4-tmj-orthodontics','224254639310':'diary-3-orthognathic-surgery','224244031894':'diary-2-insurance-ortho','224238023886':'diary-1-implant-vs-ortho'}
# Previously held back article, duplicate biography, and empty introductory post.
SKIP={'224289955263','224234139904','224234099477'}
E=lambda x:html.escape(str(x),quote=True)
def fetch(url):
    with urllib.request.urlopen(url,timeout=30) as r:return r.read()
def sanitize(raw):
    doc=BeautifulSoup(raw,'html.parser');main=doc.select_one('.se-main-container')
    if not main or len(main.get_text(strip=True))<80:raise ValueError('Full body missing or incomplete')
    for x in main.select('script,style,form,input,button,.se-sticker'):x.decompose()
    for x in main.select('iframe,video,audio,object,embed'):x.replace_with(doc.new_string('미디어는 글 하단의 네이버 원문에서 확인하실 수 있습니다.'))
    for x in list(main.find_all(True)):
        if x.name is None:continue
        if x.name not in {'div','p','span','a','img','br','hr','b','strong','em','i','u','s','sup','sub','h2','h3','h4','ul','ol','li','table','thead','tbody','tr','td','th','blockquote','figure','figcaption'}:
            x.unwrap();continue
        attrs={}
        if x.name=='img':
            src=x.get('data-lazy-src') or x.get('src','');host=urlsplit(src).hostname or ''
            if not (src.startswith('https://') and (host.endswith('.pstatic.net') or host.endswith('.naver.net'))):x.decompose();continue
            attrs={'src':src,'alt':x.get('alt',''),'loading':'lazy','decoding':'async','referrerpolicy':'no-referrer'}
        elif x.name=='a':
            u=x.get('href','')
            if u.startswith(('https://','http://')):attrs={'href':u,'target':'_blank','rel':'noopener noreferrer'}
        elif x.name in {'td','th'}:
            for key in ('colspan','rowspan'):
                if str(x.get(key,'')).isdigit():attrs[key]=x[key]
        elif x.name in {'p','span','b','strong','em','i','u','s'}:
            # Keep highlights without importing layout, URLs, or executable CSS.
            styles=[]
            for rule in x.get('style','').split(';'):
                key,_,value=rule.partition(':');key=key.strip();value=value.strip()
                if key in {'color','background-color'} and re.fullmatch(r'#[0-9a-fA-F]{3,8}|rgba?\([0-9., %]+\)',value):styles.append(key+':'+value)
            if styles:attrs['style']=';'.join(styles)
        if 'se-quotation' in x.get('class',[]):x.name='blockquote'
        x.attrs=attrs
    for p in main.find_all('p'):
        if not p.get_text(strip=True).replace('\u200b','') and not p.find('img'):p.decompose()
    return main.decode_contents(),re.sub(r'\s+',' ',main.get_text(' ',strip=True)).replace('\u200b','')
def title_clean(t):return re.sub(r'\s*\|\s*상담일기\s*#\d+\s*$','',t).strip()
def import_item(item):
    source=item.findtext('link') or '';m=re.search(r'/ckdtgks/(\d+)',source)
    if not m:return None
    id=m.group(1)
    if id in SKIP:return None
    title=title_clean(item.findtext('title') or '기록');date=parsedate_to_datetime(item.findtext('pubDate')).isoformat();source='https://blog.naver.com/ckdtgks/'+id
    path='cases/'+LEGACY[id]+'.html' if id in LEGACY else 'journal/'+id+'.html'
    row={'id':id,'title':title,'date':date,'source':source,'path':path}
    if id in LEGACY:return row
    body,text=sanitize(fetch('https://blog.naver.com/PostView.naver?blogId=ckdtgks&logNo='+id))
    row['description']=text[:160]
    schema={'@context':'https://schema.org','@type':'BlogPosting','headline':title,'description':row['description'],'datePublished':date,'inLanguage':'ko-KR','url':BASE+'/'+path,'mainEntityOfPage':BASE+'/'+path,'isBasedOn':source,'author':{'@type':'Person','@id':BASE+'/#author','name':'손창한','url':BASE+'/#about'}}
    meta='<title>'+E(title)+' | 손창한 교정과 전문의</title><meta name="description" content="'+E(row['description'])+'"><meta name="author" content="손창한"><link rel="canonical" href="'+BASE+'/'+path+'"><meta property="og:type" content="article"><meta property="og:title" content="'+E(title)+'"><meta property="og:description" content="'+E(row['description'])+'"><meta property="og:url" content="'+BASE+'/'+path+'"><script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script>'
    page='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+meta+'<link rel="stylesheet" href="/journal/style.css"></head><body><header><a href="/">Dr. Son Chang Han</a><a href="/journal/">기록 목록</a></header><main><article><p class="eyebrow">Journal · 손창한의 기록</p><h1>'+E(title)+'</h1><p class="meta"><time datetime="'+E(date)+'">'+E(date[:10])+'</time> · <a href="/#about">교정과 전문의 손창한</a></p><div class="body">'+body+'</div><footer><p>이 글은 손창한의 네이버 블로그에 게시한 원문을 옮긴 기록입니다.</p><a href="'+source+'" target="_blank" rel="noopener noreferrer">네이버 원문 보기 ↗</a><p><a href="/journal/">← 전체 기록으로</a></p></footer></article></main><script src="/journal/lightbox.js" defer></script></body></html>'
    p=ROOT/path;p.parent.mkdir(exist_ok=True);p.write_text(page);return row

def main():
    feed=ET.fromstring(fetch('https://rss.blog.naver.com/ckdtgks.xml'));items=feed.findall('./channel/item')
    if not items:raise RuntimeError('Empty RSS; existing content preserved')
    manifest=ROOT/'journal/posts.json';old=json.loads(manifest.read_text()) if manifest.exists() else [];rows={r['id']:r for r in old};failures=[]
    def attempt(item):
        try:return import_item(item)
        except Exception as exc:failures.append((item.findtext('link'),str(exc)));return None
    with ThreadPoolExecutor(max_workers=3) as pool:
        for row in pool.map(attempt,items):
            if row:rows[row['id']]=row
    posts=sorted(rows.values(),key=lambda r:r['date'],reverse=True)
    if not posts:raise RuntimeError('No usable articles; existing content preserved')
    (ROOT/'journal').mkdir(exist_ok=True);manifest.write_text(json.dumps(posts,ensure_ascii=False,indent=2)+'\n')
    def card(r):return '<a class="case-card" href="/'+E(r['path'])+'"><div class="case-body"><p class="meta">'+E(r['date'][:10])+'</p><h3>'+E(r['title'])+'</h3><span>글 읽기 →</span></div></a>'
    block='<section id="blog-updates" style="padding:64px 6vw"><div class="journal-inner"><div class="section-header"><h2>새로운 기록</h2><a href="/journal/">전체 기록 보기 →</a></div><div class="case-grid">'+''.join(card(r) for r in posts[:6])+'</div></div></section>'
    home=ROOT/'index.html';s=home.read_text();s=re.sub(r'<!-- RSS:START -->.*?<!-- RSS:END -->',lambda _: '<!-- RSS:START -->'+block+'<!-- RSS:END -->',s,flags=re.S);home.write_text(s)
    archive='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>교정 상담일지와 일상의 기록 | 손창한</title><meta name="description" content="손창한 교정과 전문의의 교정 상담일지, 진료와 일상에 관한 기록입니다."><link rel="canonical" href="'+BASE+'/journal/"><link rel="stylesheet" href="/journal/style.css"></head><body><header><a href="/">Dr. Son Chang Han</a><a href="/#about">손창한 소개</a></header><main><p class="eyebrow">Journal</p><h1>진료와 일상의 기록</h1><p class="intro">상담실에서 만나는 질문부터, 의사이자 아빠로 살아가는 일상까지.</p><div class="archive">'+''.join(card(r) for r in posts)+'</div></main></body></html>'
    (ROOT/'journal/index.html').write_text(archive)
    urls=[BASE+'/',BASE+'/journal/']+[BASE+'/'+r['path'] for r in posts]
    (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+E(u)+'</loc></url>' for u in dict.fromkeys(urls))+'</urlset>\n')
    print('Articles available:',len(posts),'Import failures:',len(failures))
    for failure in failures:print('Skipped:',failure)
    if failures:raise SystemExit(1)
if __name__=='__main__':main()
