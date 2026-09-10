"""Shared four-page presentation; article content stays in the existing pipeline."""
import html
import json
import re

BASE = 'https://drsonchanghan.com'
E = lambda value: html.escape(str(value), quote=True)
NAV = [('/', '홈'), ('/doctor/', '의사'), ('/consultation/', '상담 일기'), ('/cases/', '치료 증례')]


def navigation(active):
    links = ''.join(f'<a href="{url}"' + (' aria-current="page"' if url == active else '') + f'>{label}</a>' for url, label in NAV)
    return '<a class="skip-link" href="#main-content">본문 바로가기</a><header class="site-header"><div class="site-header-inner"><a class="site-brand" href="/">손창한<span>치과교정과 전문의</span></a><nav class="site-nav" aria-label="주 메뉴">'+links+'</nav></div></header>'


def footer():
    return '<footer class="site-footer"><div><strong>Dr. Son Chang Han</strong><p>교정과 전문의 손창한의 진료 철학과 기록</p></div><a href="https://blog.naver.com/ckdtgks" target="_blank" rel="noopener noreferrer">네이버 블로그</a><a href="/admin/" rel="nofollow">관리자</a></footer>'


def person():
    return {'@type':'Person','@id':BASE+'/#author','name':'손창한','alternateName':'Son Chang Han','url':BASE+'/doctor/','jobTitle':'치과교정과 전문의 · 서울대학교치과병원 임상강사','sameAs':['https://blog.naver.com/ckdtgks'],'worksFor':{'@type':'Organization','name':'서울대학교치과병원'}}


def page(path, title, description, content, data):
    data = {'@context':'https://schema.org','@graph':[data,person()]}
    encoded = json.dumps(data,ensure_ascii=False).replace('</','<\\/')
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} | 손창한 교정과 전문의</title><meta name="description" content="{E(description)}"><meta name="author" content="손창한">
<link rel="canonical" href="{BASE+path}"><meta property="og:type" content="website"><meta property="og:locale" content="ko_KR"><meta property="og:title" content="{E(title)} | 손창한"><meta property="og:description" content="{E(description)}"><meta property="og:url" content="{BASE+path}">
<script type="application/ld+json">{encoded}</script>
<link rel="stylesheet" href="/site.css"></head><body class="site-page">{navigation('/cases/' if path.startswith('/cases/') else '/consultation/' if path.startswith('/consultation/') else path)}<main id="main-content">{content}</main>{footer()}</body></html>
'''


def tile(row, case_titles):
    from case_duration import markup as duration_markup
    is_case = row['category'] == 'case'
    label, title = case_titles.get(row['id'], ('치료 증례', row['title'])) if is_case else ('상담 일기', row['title'])
    if is_case:title=row['title']
    return f'<a class="record-card {"case-record" if is_case else "journal-record"}" href="/{E(row["path"])}"><div class="record-copy"><p class="record-meta">{E(label)} <time datetime="{E(row["date"])}">{E(row["date"][:10])}</time></p><h2>{E(title)}</h2>{duration_markup(row)}<p>{E(row["summary"])}</p><span class="read-link">{"증례" if is_case else "일기"} 읽기 →</span></div></a>'


def archive(kind, rows, case_titles, page_number=1):
    is_case = kind == 'case'
    label, path, english = ('치료 증례','/cases/','Clinical cases') if is_case else ('상담 일기','/consultation/','Consultation journal')
    description = '환자의 고민에서 진단, 치료계획과 결과까지. 치료를 선택한 이유와 과정을 기록합니다.' if is_case else '진료실에서 자주 만나는 질문에 먼저 짧게 답하고, 그 이유를 차근히 설명합니다.'
    base_path = path
    page_count = max(1, (len(rows)+9)//10)
    start_index = (page_number-1)*10
    visible = rows[start_index:start_index+10]
    path = base_path if page_number == 1 else base_path+f'page/{page_number}/'
    content = f'<section class="page-heading"><div class="content-width"><p class="eyebrow">{english}</p><h1>{label}</h1><p class="lead">{description}</p></div></section><div class="content-width archive-section"><p class="collection-count">전체 {len(rows)}편 · {page_number} / {page_count} 페이지</p><ol class="compact-record-list" start="{start_index+1}">'
    for i,row in enumerate(visible,start_index+1):
        content += f'<li><a href="/{E(row["path"])}"><span class="list-number" aria-hidden="true">{i:02}</span><span class="list-title">{E(row["title"])}</span><span aria-hidden="true">→</span></a></li>'
    content += '</ol><nav class="archive-pagination" aria-label="목록 페이지">'
    for number in range(1,page_count+1):
        target = base_path if number == 1 else base_path+f'page/{number}/'
        current = ' aria-current="page"' if number == page_number else ''
        content += f'<a href="{target}" aria-label="{number}페이지"{current}>{number}</a>'
    content += '</nav>'
    content += '<div class="record-grid '+('case-grid' if is_case else 'journal-grid')+'">'+''.join(tile(row,case_titles) for row in rows)+'</div>'
    if is_case: content += '<p class="case-note">개별 환자의 치료 기록입니다. 치료 방법과 기간, 결과는 환자의 상태에 따라 달라질 수 있습니다.</p>'
    content += '</div>'
    data = {'@type':'CollectionPage','name':label,'description':description,'url':BASE+path,'inLanguage':'ko-KR','author':{'@id':BASE+'/#author'},'mainEntity':{'@type':'ItemList','numberOfItems':len(rows),'itemListElement':[{'@type':'ListItem','position':i,'url':BASE+'/'+row['path'],'name':row['title']} for i,row in enumerate(rows,1)]}}
    return page(path,label,description,content,data)


def home(consultations, cases, case_titles):
    content = '''<section class="home-hero"><div class="content-width hero-layout"><div class="hero-copy"><p class="eyebrow">Orthodontist · Son Chang Han</p><h1>좋은 교정은<br>시작이 다릅니다.</h1><p class="lead">서두르지 않고, 충분히 설명하며<br>함께 답을 찾아갑니다.</p><p class="hero-identity">교정과 전문의 손창한<br><span>서울대학교치과병원 치과교정과 임상강사</span></p><a class="primary-link" href="/doctor/">의사 소개</a></div><div class="hero-portrait"><img src="/images/hero-photo.jpg" alt="교정과 전문의 손창한" fetchpriority="high"></div></div></section>
<section class="content-width home-section" id="about"><div class="section-heading"><div><p class="eyebrow">About the doctor</p><h2>충분히 이해하고,<br>함께 결정하는 교정.</h2></div><div><p>치료를 시작할 때는 충분히 이해하고,<br>치료를 마칠 때는 서로 납득할 수 있는 것.<br>저에게는, 그것이 좋은 교정입니다.</p><a class="read-link" href="/doctor/">손창한의 진료 철학과 약력 →</a></div></div></section>
<section class="records-overview"><div class="content-width"><p class="eyebrow">Two records</p><div class="record-paths"><a href="/consultation/"><span>01 · Consultation journal</span><h2>상담 일기</h2><p>교정을 고민하며 생기는 질문과 답변</p><span class="read-link">상담 일기 전체 보기 →</span></a><a href="/cases/"><span>02 · Clinical cases</span><h2>치료 증례</h2><p>진단과 선택의 이유, 치료 과정과 결과</p><span class="read-link">치료 증례 전체 보기 →</span></a></div></div></section>'''
    for label,path,rows in [('최근 상담 일기','/consultation/',consultations[:2]),('대표 치료 증례','/cases/',cases[:3])]:
        content += f'<section class="content-width home-section"><div class="section-bar"><h2>{label}</h2><a class="read-link" href="{path}">전체 보기 →</a></div><div class="record-grid {"case-grid" if path=="/cases/" else "journal-grid"}">'+''.join(tile(row,case_titles).replace('<h2>','<h3>').replace('</h2>','</h3>') for row in rows)+'</div></section>'
    return page('/','손창한 · 교정과 전문의','교정과 전문의 손창한의 진료 철학과 약력, 상담 일기와 치료 증례를 소개합니다.',content,{'@type':'WebSite','@id':BASE+'/#website','url':BASE+'/','name':'손창한 | 교정과 전문의','inLanguage':'ko-KR','author':{'@id':BASE+'/#author'}})


def doctor():
    content = '''<section class="page-heading"><div class="content-width"><p class="eyebrow">About the doctor</p><h1>교정과 전문의 손창한</h1><p class="lead">서울대학교치과병원 치과교정과 임상강사 · 치의학박사</p></div></section><section class="content-width doctor-layout"><div class="doctor-portrait"><img src="/images/profile-outdoor.jpg" alt="교정과 전문의 손창한" decoding="async"></div><div><p class="eyebrow">Philosophy</p><h2>먼저 당신을 이해하고,<br>함께 답을 찾습니다.</h2><div class="doctor-letter"><p>비슷한 치열이라도 교정을 고민하는 이유는 저마다 다릅니다. 먼저 당신을 이해하고, 그 이해를 바탕으로 진단합니다.</p><p>치료를 시작할 때는 충분히 이해하고,<br>치료를 마칠 때는 서로 납득할 수 있는 것.</p><p>그리고 몇 년 뒤 정기검진에서<br>웃으며 다시 만날 수 있는 것.</p><p>저에게는, 그것이 좋은 교정입니다.</p></div></div></section><section class="content-width credentials-section"><p class="eyebrow">Profile</p><h2>약력</h2><dl class="profile-facts"><div><dt>전문의</dt><dd>보건복지부 인증 치과교정과 전문의</dd></div><div><dt>현재</dt><dd>서울대학교치과병원 치과교정과 임상강사</dd></div><div><dt>수련</dt><dd>서울대학교치과병원 인턴<br>서울대학교치과병원 치과교정과 전공의 수료</dd></div><div><dt>학위</dt><dd>서울대학교 치의학대학원 치과교정학 박사</dd></div></dl></section><section class="principles"><div class="content-width"><p class="eyebrow">Principles</p><h2>진료의 원칙</h2><div class="principle-grid"><div><span>01</span><h3>모든 판단에는 이유가 있습니다.</h3><p>발치와 비발치, 장치의 선택, 치료의 방향까지. 충분한 근거 위에서 판단하고 그 이유를 설명합니다.</p></div><div><span>02</span><h3>치료는 함께 결정합니다.</h3><p>충분한 설명을 바탕으로 치료의 방향을 함께 고민합니다. 환자가 무엇을 궁금해하는지 놓치지 않습니다.</p></div><div><span>03</span><h3>장치를 떼는 날이 끝이 아닙니다.</h3><p>장치를 제거한 뒤에도 유지와 변화를 함께 살핍니다.</p></div></div></div></section>'''
    return page('/doctor/','의사 소개','교정과 전문의 손창한의 진료 철학과 약력. 서울대학교치과병원 치과교정과 임상강사, 치의학박사.',content,{'@type':'ProfilePage','url':BASE+'/doctor/','name':'교정과 전문의 손창한 소개','mainEntity':{'@id':BASE+'/#author'}})


def decorate_article(text, active):
    # Safe shell-only changes: keep all original clinical prose and images intact.
    text = text.replace(BASE+'/#about',BASE+'/doctor/').replace('href="/#about"','href="/doctor/"').replace('href="../index.html#about"','href="/doctor/"')
    if '/site.css' not in text: text = text.replace('</head>','<link rel="stylesheet" href="/site.css"></head>')
    text = re.sub(r'<a class="skip-link".*?</a>', '', text, flags=re.S)
    text = re.sub(r'<header\b[^>]*>.*?</header>', '', text, count=1, flags=re.S)
    text = re.sub(r'<body[^>]*>', '<body class="article-page">'+navigation(active), text, count=1)
    if 'id="main-content"' not in text:
        text = text.replace('<main>','<main id="main-content">',1) if '<main>' in text else text.replace('<div class="wrap">','<div class="wrap" id="main-content" role="main">',1)
    return text


def build(root, consultations, cases, case_titles):
    (root/'doctor').mkdir(exist_ok=True)
    (root/'index.html').write_text(home(consultations,cases,case_titles))
    (root/'doctor/index.html').write_text(doctor())
    for kind, rows, directory in [('consultation',consultations,'consultation'),('case',cases,'cases')]:
        for number in range(1,max(1,(len(rows)+9)//10)+1):
            destination=root/directory/('index.html' if number==1 else f'page/{number}/index.html')
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_text(archive(kind,rows,case_titles,number))
    for row in consultations+cases:
        path = root/row['path']
        if path.exists(): path.write_text(decorate_article(path.read_text(), '/cases/' if row['category']=='case' else '/consultation/'))
