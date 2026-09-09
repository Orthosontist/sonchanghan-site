"""Curated case prose and stable, self-hosted clinical image order."""
from pathlib import Path
import html
import json

HERE = Path(__file__).resolve().parent
COPY = json.loads((HERE / 'case_copy.json').read_text())
MEDIA = json.loads((HERE / 'case_media.json').read_text())
BASE = '/images/cases/224298737298/'

def figure(src, alt, caption=''):
    e = html.escape
    return '<figure class="case-media"><img src="'+e(src, quote=True)+'" alt="'+e(alt, quote=True)+'" loading="lazy" decoding="async">'+('<figcaption>'+e(caption)+'</figcaption>' if caption else '')+'</figure>'

def render(post_id):
    out=[]
    for i,(heading,paragraph) in enumerate(COPY[post_id]['sections']):
        out.append('<h2>'+html.escape(heading)+'</h2><p>'+html.escape(paragraph)+'</p>')
        if post_id != '224298737298':
            continue
        if i == 0:
            out.append(figure(BASE+'cropped/pre-treatment.png','치료 전 구강 내 사진', '치료 전 · 2023.07.26'))
            out.append(figure(BASE+'cropped/ct.png','매복된 아래 왼쪽 제2대구치 CT 영상','진단 시 CT 영상'))
        elif i == 2:
            out.append('<div class="clinical-sequence-grid" aria-label="날짜순 자연 맹출 경과">')
            for filename, date in [('05-progress-2023-07.png','2023.07'),('06-progress-2023-10.png','2023.10'),('07-progress-2024-01.png','2024.01'),('08-progress-2024-10.png','2024.10')]:
                out.append(figure(BASE+filename,date+' 아래 왼쪽 제2대구치 방사선사진',date))
            out.append('</div>')
            out.append(figure(BASE+'cropped/treatment-course.png','위쪽 어금니 함입 장치와 아래 어금니 맹출의 변화','장치와 구강 내 변화 · 2024.04 → 2024.12'))
        elif i == 3:
            out.append(figure(BASE+'cropped/post-treatment.png','치료 후 구강 내 사진','치료 후 · 2024.12.18'))
            out.append(figure(BASE+'10-before-after.png','아래 왼쪽 제2대구치의 치료 전후 방사선사진','치료 전후 비교'))
    if post_id in MEDIA:
        out.append('<h2>치료 기록</h2>')
        for item in MEDIA[post_id]:
            out.append(figure(item['src'],item['alt']))
    out.append('<aside class="medical-note"><strong>안내</strong><p>치료 결과와 기간, 부작용의 가능성은 개인의 상태와 치료 조건에 따라 달라질 수 있습니다.</p></aside>')
    return ''.join(out)
