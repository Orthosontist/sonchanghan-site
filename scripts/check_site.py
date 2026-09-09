"""Validate all public routes, article copy and locally served clinical images."""
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
from bs4 import BeautifulSoup
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
rows=[r for r in json.loads((ROOT/'journal/posts.json').read_text()) if r['category']!='exclude']
paths=['index.html','doctor/index.html','consultation/index.html','cases/index.html']+[r['path'] for r in rows]
errors=[];images=0
for name in paths:
    path=ROOT/name
    soup=BeautifulSoup(path.read_text(),'html.parser')
    if len(soup.select('h1'))!=1:errors.append((name,'h1'))
    if not soup.select_one('link[rel=canonical]'):errors.append((name,'canonical'))
    if soup.select_one('meta[name=robots][content*="noindex"]'):errors.append((name,'noindex'))
    for data in soup.select('script[type="application/ld+json"]'):json.loads(data.string)
    for tag,attr in [('a','href'),('img','src'),('script','src'),('link','href')]:
        for node in soup.select(f'{tag}[{attr}]'):
            value=node[attr];url=urlsplit(value)
            if url.scheme or url.netloc or not url.path:continue
            target=ROOT/unquote(url.path.lstrip('/')) if url.path.startswith('/') else path.parent/unquote(url.path)
            if target.is_dir():target=target/'index.html'
            if not target.is_file():errors.append((name,'missing '+value));continue
            if tag=='img':
                with Image.open(target) as image:image.verify()
                images+=1
for row in rows:
    soup=BeautifulSoup((ROOT/row['path']).read_text(),'html.parser');body=soup.select_one('.body')
    if row['category']=='case':
        for image in body.select('img'):
            if image['src'].startswith('http'):errors.append((row['id'],'external image'))
            if not image.get('alt'):errors.append((row['id'],'missing alt'))
    else:
        if not 3<=len(body.select('h2'))<=4:errors.append((row['id'],'heading count'))
        if len(body.get_text())>700:errors.append((row['id'],'long copy'))
        for unwanted in ['안녕하세요','감사합니다','인턴','위 사진','아래 사진','블로그를','ㅋㅋ','ㅎㅎ']:
            if unwanted in body.get_text():errors.append((row['id'],'unwanted '+unwanted))
        if body.select('img'):errors.append((row['id'],'consultation image'))
print(json.dumps({'public_pages':len(paths),'consultations':sum(r['category']=='consultation' for r in rows),'cases':sum(r['category']=='case' for r in rows),'local_image_references_verified':images,'errors':errors},ensure_ascii=False))
raise SystemExit(bool(errors))
