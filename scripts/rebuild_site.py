"""Build the public consultation/case taxonomy and AI-readable article layer.

Run after sync_blog.py. Existing article URLs are retained so previously indexed
pages do not lose search equity.
"""
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import html, json, re
from bs4 import BeautifulSoup
from site_pages import build as build_four_pages

ROOT=Path(__file__).resolve().parents[1]; BASE='https://drsonchanghan.com'; UPDATED=date.today().isoformat()
E=lambda value:html.escape(str(value),quote=True)
PERSONAL={'224373757419','224354464965','224285092639','224284304710','224236743246'}
CASES={'224389591858','224379790553','224367766837','224363724085','224353239670','224348849201','224347421988','224342451500','224341965456','224298737298'}
CASE_CARD={
'224298737298':('부분교정 · 매복치','매복 어금니 자연 맹출'),'224341965456':('부분교정 · 보철 전 교정','임플란트 전 어금니 함입'),'224342451500':('성장기 · 발치교정','심한 총생과 덧니 교정'),'224347421988':('성인 · 비발치','총생과 정중선 교정'),'224348849201':('성인 · 비발치','나비 앞니 전체교정'),'224353239670':('성인 · 비발치','짧은 치근을 고려한 배열 개선'),'224363724085':('성인 · 복합치료','고난도 II급 부정교합 교정'),'224367766837':('성장기 · 매복치','수평 매복 영구치 견인'),'224379790553':('수술교정 · 골격성 3급','주걱턱 수술교정 · 14개월'),'224389591858':('성인 · 비발치','앞니 공간과 정중선 교정')}
TITLE_FIX={'224289274170':'소통이 치료입니다 ("다른 병원에서 치료 중인데, 잘 되고 있는지 모르겠어요")'}
SUMMARY={
'224403787474':'양악수술은 전신마취와 수술을 동반하므로 위험이 전혀 없지는 않습니다. 다만 수술 전 평가, 마취·수술 중 감시와 수술 후 관리를 체계적으로 시행하면 위험을 줄일 수 있으며 개인별 위험도는 건강 상태와 수술 범위에 따라 달라집니다.',
'224397969906':'양악수술 후 티타늄 플레이트를 모든 환자가 반드시 제거해야 하는 것은 아닙니다. 이물감·염증·노출 또는 영상검사 방해처럼 제거를 고려할 이유가 있을 때 수술 부위와 시기를 함께 평가합니다.',
'224383899601':'인접한 유치 사이가 서로 맞닿기 시작하면 칫솔만으로 닦기 어려운 면이 생기므로 치실 사용을 고려할 수 있습니다. 어린아이는 보호자가 직접 도와 안전하게 사용하는 것이 중요합니다.',
'224366709586':'교정치료 중 치근흡수는 발생할 수 있지만 대부분은 임상적으로 큰 문제가 없는 범위에 머뭅니다. 치료 전 위험요인을 확인하고 정기 방사선검사로 변화량을 관찰하며 필요하면 교정력을 조절해야 합니다.',
'224351729417':'치간삭제는 적응증에 맞춰 법랑질 범위 안에서 양을 통제해 시행하면 공간을 확보하는 유용한 방법입니다. 필요한 부위와 삭제량은 치아 형태·배열·우식 위험을 고려해 개별적으로 결정해야 합니다.',
'224317625460':'고정식 유지장치는 많은 경우 장기간, 때로는 거의 평생 유지하는 것이 권장됩니다. 접착 탈락·와이어 변형·치석을 확인하기 위해 장치가 붙어 있어도 정기검진이 필요합니다.',
'224303524267':'나이 자체는 교정치료의 금기사항이 아닙니다. 60대 이상에서도 치료가 가능하지만 치아와 잇몸 상태, 전신질환과 치료 목표를 먼저 확인해 치료 범위와 속도를 정해야 합니다.',
'224298037342':'일반적인 덧니·돌출입·반대교합만으로 보충역 판정을 받기는 어렵습니다. 병역판정은 공식 기준과 저작기능, 영상검사 등 객관적 소견을 함께 평가하므로 최신 규정을 확인해야 합니다.',
'224291408505':'가철식 유지장치는 초기에는 충분한 시간 착용하고 이후 상태에 따라 야간 착용으로 줄이는 경우가 많습니다. 정확한 기간은 치료 전 치열과 재발 위험에 따라 달라 담당 교정과의사의 지침을 따라야 합니다.',
'224289274170':'다른 병원에서 교정 중 치료 방향이 궁금하다면 먼저 현재 주치의에게 질문하는 것이 좋습니다. 치료의 연속성을 유지하면서 설명이 부족한 부분을 확인하는 과정이 환자에게 가장 안전합니다.',
'224279052575':'선천적 측절치 결손은 송곳니 대치, 공간 유지 후 보철 등 여러 선택지가 있습니다. 골격과 안모, 교합, 치아 형태와 성장 상태를 함께 보고 장기 계획을 세워야 합니다.',
'224266423268':'턱관절 통증이 있다고 교정치료를 무조건 못 하는 것은 아니지만 먼저 통증의 원인과 현재 상태를 평가해야 합니다. 교정치료만으로 턱관절 질환이 해결된다고 단정해서도 안 됩니다.',
'224254639310':'수술교정은 일반적으로 술전 교정, 악교정수술, 술후 교정의 세 단계로 진행됩니다. 각 단계의 기간과 치료 순서는 부정교합과 수술계획에 따라 달라집니다.',
'224244031894':'일반적인 교정치료는 비급여이지만 구순구개열 등 일부 선천성 악안면기형은 기준을 충족하면 건강보험이 적용될 수 있습니다. 진단명과 치료기관 요건을 함께 확인해야 합니다.',
'224238023886':'상실된 어금니 공간을 임플란트로 회복할지 교정으로 닫을지는 나이만으로 결정하지 않습니다. 남은 치아의 위치, 골격과 교합, 뼈 상태와 치료기간을 종합해 선택해야 합니다.',
'224389591858':'벌어진 앞니와 정중선 불일치를 보철 삭제 없이 개선하기 위해 비발치 교정치료를 선택한 성인 증례입니다. 진단과 선택 이유, 1년 3개월의 치료 과정을 함께 기록했습니다.',
'224379790553':'주걱턱을 동반한 골격성 3급 부정교합에서 수술교정을 시행한 증례입니다. 술전·술후 교정을 포함해 약 14개월 동안 진행한 치료계획과 결과를 기록했습니다.',
'224367766837':'가로로 매복된 영구치의 위치와 맹출 가능성을 평가한 뒤 교정적 견인을 시행한 성장기 증례입니다. 진단부터 견인 과정과 최종 배열까지 기록했습니다.',
'224298737298':'매복된 아래 제2대구치의 자연 맹출을 관찰하면서 위쪽 과맹출 치아를 함께 함입한 부분교정 증례입니다.'}

def category(row):
    title=row['title']; post_id=row['id']
    if post_id in PERSONAL or re.search(r'\[(?:근황|독서)\]|잡념|주절주절|전쟁',title): return 'exclude'
    if post_id in CASES or '증례' in title: return 'case'
    if post_id=='224289274170': return 'consultation'
    return 'consultation' if re.search(r'교정|치아|치실|양악|턱관절|유지장치|부정교합|임플란트|발치|앞니|어금니|영구치|플레이트',title) else 'exclude'

def summary(row):
    if row['id'] in SUMMARY:return SUMMARY[row['id']]
    if row['category']=='case':return row['title']+'의 진단, 치료계획과 진행 과정을 기록한 교정증례입니다.'
    raw=row.get('description','').strip()
    return raw if raw else '교정과 전문의 손창한이 환자분들이 자주 묻는 질문에 먼저 답하고 판단 기준과 주의사항을 설명합니다.'

def source_body(text):
    match=re.search(r'<div class="body">(.*?)</div>\s*(?:<section|<aside|<footer)',text,re.S)
    return match.group(1) if match else ''

def assets(body,path):
    soup=BeautifulSoup(body,'html.parser'); first=soup.find('img',src=True); image=urljoin(BASE+'/'+path,first['src']) if first else ''
    citations=[]
    for link in soup.find_all('a',href=True):
        url=link['href']; host=urlsplit(url).hostname or ''
        if url.startswith('http') and 'naver.com' not in host and 'drsonchanghan.com' not in host and url not in citations:citations.append(url)
    return image,citations[:8]

def schema(row,body):
    label='교정증례' if row['category']=='case' else '상담일기'; url=BASE+'/'+row['path']; image,citations=assets(body,row['path'])
    data={'@context':'https://schema.org','@type':'BlogPosting','headline':row['title'],'description':row['summary'],'datePublished':row['date'],'dateModified':row['updated'],'inLanguage':'ko-KR','url':url,'mainEntityOfPage':url,'articleSection':label,'isBasedOn':row['source'],'about':{'@type':'MedicalSpecialty','name':'Orthodontics'},'author':{'@type':'Person','@id':BASE+'/#author','name':'손창한','alternateName':'Son Chang Han','jobTitle':'치과교정과 전문의 · 서울대학교치과병원 임상강사','url':BASE+'/#about','sameAs':['https://blog.naver.com/ckdtgks']},'publisher':{'@id':BASE+'/#author'}}
    if image:data['image']=image
    if citations:data['citation']=citations
    return data,image,citations

def render(row,body):
    label='교정증례' if row['category']=='case' else '상담일기'; section='cases' if row['category']=='case' else 'consultation'; data,image,citations=schema(row,body); url=BASE+'/'+row['path']
    sources=''
    if citations:sources='<section class="sources"><h2>근거와 출처</h2><ul>'+''.join('<li><a href="'+E(link)+'" target="_blank" rel="noopener noreferrer">'+E(urlsplit(link).hostname or link)+' ↗</a></li>' for link in citations)+'</ul></section>'
    meta='<title>'+E(row['title'])+' | 손창한 교정과 전문의</title><meta name="description" content="'+E(row['summary'])+'"><meta name="author" content="손창한"><link rel="canonical" href="'+url+'"><meta property="og:type" content="article"><meta property="og:locale" content="ko_KR"><meta property="og:title" content="'+E(row['title'])+'"><meta property="og:description" content="'+E(row['summary'])+'"><meta property="og:url" content="'+url+'">'+(('<meta property="og:image" content="'+E(image)+'">') if image else '')+'<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+'</script>'
    return '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+meta+'<link rel="stylesheet" href="/journal/style.css"><link rel="stylesheet" href="/journal/ai-readable.css"></head><body><header><a href="/">Dr. Son Chang Han</a><a href="/'+section+'/">'+label+' 목록</a></header><main><article><p class="eyebrow">'+('Clinical Case' if section=='cases' else 'Consultation Journal')+' · 손창한의 기록</p><h1>'+E(row['title'])+'</h1><p class="meta"><time datetime="'+E(row['date'])+'">'+E(row['date'][:10])+'</time> · <a href="/#about">교정과 전문의 손창한</a> · 홈페이지 업데이트 <time datetime="'+row['updated']+'">'+row['updated']+'</time></p><aside class="answer-box"><span>'+('증례 요약' if section=='cases' else '핵심 답변')+'</span><p>'+E(row['summary'])+'</p></aside><div class="body">'+body+'</div>'+sources+'<aside class="author-card"><strong>작성자 · 손창한</strong><p>보건복지부 인증 치과교정과 전문의 · 치의학박사<br>서울대학교치과병원 치과교정과 임상강사</p></aside><footer><p>네이버 블로그에 게시한 글을 바탕으로 홈페이지에서 분류·요약한 기록입니다.</p><a href="'+row['source']+'" target="_blank" rel="noopener noreferrer">네이버 원문 보기 ↗</a><p><a href="/'+section+'/">← '+label+' 전체 보기</a></p></footer></article></main><script src="/journal/lightbox.js" defer></script></body></html>'

def enhance_legacy(row,text):
    if row['category']=='consultation':
        text=text.replace('상담일지','상담일기')
    if '/journal/ai-readable.css' not in text:text=text.replace('</head>','<link rel="stylesheet" href="/journal/ai-readable.css"></head>')
    if 'class="answer-box"' not in text:
        box='<aside class="answer-box"><span>'+('증례 요약' if row['category']=='case' else '핵심 답변')+'</span><p>'+E(row['summary'])+'</p></aside>'
        text=re.sub(r'(<div class="meta"[^>]*>.*?</div>)',r'\1'+box,text,count=1,flags=re.S)
    text=re.sub(r'href="\.\./index\.html#journal"','href="/'+('cases' if row['category']=='case' else 'consultation')+'/"',text,count=1)
    block=re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)
    if block:
        try:
            data=json.loads(block.group(1)); body=re.search(r'<div class="body">(.*)</div>',text,re.S); data.update(schema(row,body.group(1) if body else '')[0]); data['name']=row['title']+' | 손창한 교정과 전문의'; encoded=json.dumps(data,ensure_ascii=False).replace('</','<\\/'); text=text[:block.start(1)]+encoded+text[block.end(1):]
        except json.JSONDecodeError:pass
    text=re.sub(r'(<meta name="description" content=")[^"]*(")',r'\1'+E(row['summary'])+r'\2',text,count=1)
    text=re.sub(r'(<meta property="og:description" content=")[^"]*(")',r'\1'+E(row['summary'])+r'\2',text,count=1)
    if row['id'] in TITLE_FIX:
        page_title=E(row['title'])+' | 손창한 교정과 전문의'
        text=re.sub(r'<title>.*?</title>','<title>'+page_title+'</title>',text,count=1,flags=re.S)
        text=re.sub(r'(<meta property="og:title" content=")[^"]*(")',r'\1'+E(row['title'])+r'\2',text,count=1)
        text=re.sub(r'<h1>.*?</h1>','<h1>'+E(row['title'])+'</h1>',text,count=1,flags=re.S)
    return text

def card(row):
    image=''; title=row['title']; card_meta=row['date'][:10]
    if row['category']=='case':
        card_meta,title=CASE_CARD.get(row['id'],('교정증례',row['title'])); thumb='/images/case-thumbnails/'+row['id']+'.webp'; image='<img class="archive-thumb" src="'+thumb+'" alt="'+E(row['title'])+' 치료 전후 썸네일" loading="lazy" decoding="async">'
    return '<a class="archive-card" href="/'+E(row['path'])+'">'+image+'<div class="archive-card-body"><p class="card-meta">'+E(card_meta)+'</p><h2>'+E(title)+'</h2><p>'+E(row['summary'])+'</p><span>글 읽기 →</span></div></a>'

def home_blocks(consultations,cases):
    consult='<div class="article-list">'+''.join('<a class="article-row" href="'+E(row['path'])+'"><span class="article-no">'+str(index).zfill(2)+'</span><div><h3>'+E(row['title'])+'</h3><p>'+E(row['summary'])+'</p></div><span class="arrow">↗</span></a>' for index,row in enumerate(consultations[:4],1))+'</div>'
    featured=[]
    for post_id in ('224379790553','224389591858','224367766837'):
        row=next((item for item in cases if item['id']==post_id),None)
        if row:featured.append(row)
    for row in cases:
        if row not in featured and len(featured)<3:featured.append(row)
    cards=[]
    for row in featured[:3]:
        label,title=CASE_CARD.get(row['id'],('교정증례',row['title'])); thumb='images/case-thumbnails/'+row['id']+'.webp'; image='<div class="case-image case-image-static"><img src="'+thumb+'" alt="'+E(row['title'])+' 치료 전후 썸네일" loading="lazy" decoding="async"></div>'
        cards.append('<article class="case-card">'+image+'<a class="case-info" href="'+E(row['path'])+'"><span class="case-type">'+E(label)+'</span><h3>'+E(title)+'</h3><span class="case-open">증례 보기 ↗</span></a></article>')
    return consult,'<div class="case-grid">'+''.join(cards)+'</div>'

def update_home(consultations,cases):
    consult,cases_html=home_blocks(consultations,cases)
    for filename in ('index-redesign.html','index.html'):
        path=ROOT/filename
        if not path.exists():continue
        text=path.read_text()
        if '<!-- CONSULTATION:START -->' not in text:continue
        text=re.sub(r'<!-- CONSULTATION:START -->.*?<!-- CONSULTATION:END -->','<!-- CONSULTATION:START -->'+consult+'<!-- CONSULTATION:END -->',text,flags=re.S)
        text=re.sub(r'<!-- CASES:START -->.*?<!-- CASES:END -->','<!-- CASES:START -->'+cases_html+'<!-- CASES:END -->',text,flags=re.S)
        if filename=='index.html':
            text=re.sub(r'\s*<meta name="robots" content="noindex,follow">','',text,count=1)
            text=re.sub(r'\s*<div class="preview-note">.*?</div>','',text,count=1,flags=re.S)
        path.write_text(text.rstrip()+'\n')

def archive(kind,rows):
    is_case=kind=='case'; label='교정증례' if is_case else '상담일기'; section='cases' if is_case else 'consultation'; description='진단과 치료계획, 선택의 이유와 결과를 기록한 손창한 교정과 전문의의 교정증례입니다.' if is_case else '진료실에서 자주 만나는 교정 질문에 손창한 교정과 전문의가 먼저 답하고 그 이유를 설명합니다.'; url=BASE+'/'+section+'/'
    data={'@context':'https://schema.org','@type':'CollectionPage','name':label+' | 손창한 교정과 전문의','description':description,'url':url,'inLanguage':'ko-KR','author':{'@id':BASE+'/#author'}}
    return '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+label+' | 손창한 교정과 전문의</title><meta name="description" content="'+description+'"><link rel="canonical" href="'+url+'"><script type="application/ld+json">'+json.dumps(data,ensure_ascii=False)+'</script><link rel="stylesheet" href="/journal/style.css"><link rel="stylesheet" href="/journal/ai-readable.css"></head><body><header><a href="/">Dr. Son Chang Han</a><a href="/'+('consultation' if is_case else 'cases')+'/">'+('상담일기' if is_case else '교정증례')+'</a></header><main><p class="eyebrow">'+('Clinical Cases' if is_case else 'Consultation Journal')+'</p><h1>'+label+'</h1><p class="intro">'+description+'</p><div class="archive archive-rich '+('case-archive' if is_case else 'consultation-archive')+'">'+''.join(card(row) for row in rows)+'</div></main></body></html>'

def main():
    manifest=ROOT/'journal/posts.json'; posts=json.loads(manifest.read_text()); normalized=[]
    for old in posts:
        row=dict(old); row['title']=TITLE_FIX.get(row['id'],row['title']); row['category']=category(row); row['updated']=row.get('updated') or UPDATED; row['summary']=summary(row); row['description']=row['summary']; normalized.append(row)
        path=ROOT/row['path']
        if not path.exists():continue
        text=path.read_text()
        if row['category']=='exclude':
            if 'name="robots"' not in text:path.write_text(text.replace('</head>','<meta name="robots" content="noindex,follow"></head>'))
        elif row['path'].startswith('journal/'):
            text=re.sub(r'<meta name="robots" content="noindex,follow">','',text); body=source_body(text)
            if body:path.write_text(render(row,body))
        else:path.write_text(enhance_legacy(row,re.sub(r'<meta name="robots" content="noindex,follow">','',text)))
    normalized.sort(key=lambda row:row['date'],reverse=True); manifest.write_text(json.dumps(normalized,ensure_ascii=False,indent=2)+'\n')
    consultations=[row for row in normalized if row['category']=='consultation']; cases=[row for row in normalized if row['category']=='case']
    public=[row for row in normalized if row['category']!='exclude']
    site_updated=max((row['updated'][:10] for row in public),default=UPDATED)
    (ROOT/'consultation').mkdir(exist_ok=True); (ROOT/'cases').mkdir(exist_ok=True)
    (ROOT/'consultation/index.html').write_text(archive('consultation',consultations)); (ROOT/'cases/index.html').write_text(archive('case',cases))
    update_home(consultations,cases)
    build_four_pages(ROOT, consultations, cases, CASE_CARD)
    (ROOT/'journal/index.html').write_text('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="robots" content="noindex,follow"><link rel="canonical" href="'+BASE+'/consultation/"><meta http-equiv="refresh" content="0;url=/consultation/"><title>상담일기 | 손창한</title></head><body><a href="/consultation/">상담일기로 이동</a></body></html>')
    urls=[(BASE+'/',site_updated),(BASE+'/doctor/',site_updated),(BASE+'/consultation/',site_updated),(BASE+'/cases/',site_updated)]+[(BASE+'/'+row['path'],row['updated']) for row in public]; seen=set(); unique=[]
    for url,lastmod in urls:
        if url not in seen:unique.append((url,lastmod));seen.add(url)
    (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+E(url)+'</loc><lastmod>'+E(lastmod[:10])+'</lastmod></url>' for url,lastmod in unique)+'</urlset>\n')
    print('Consultations:',len(consultations),'Cases:',len(cases),'Excluded:',len(normalized)-len(consultations)-len(cases))

if __name__=='__main__':main()
