"""Ordered text/image blocks, shared by the CMS and static article renderer."""
from pathlib import Path
import html
import json
from urllib.parse import urlsplit, unquote

ROOT=Path(__file__).resolve().parents[1]

def load(post_id):
    path=ROOT/'content/articles'/f'{post_id}.json'
    return json.loads(path.read_text()) if path.exists() else None

def image(item):
    src=item['src']; parsed=urlsplit(src)
    if parsed.scheme or parsed.netloc or not src.startswith('/images/') or '..' in unquote(src).split('/'):
        raise ValueError('Clinical images must use local /images/ paths')
    if not (ROOT/unquote(src.lstrip('/'))).is_file():raise ValueError('Missing image: '+src)
    alt=item.get('alt','').strip()
    if not alt:raise ValueError('Image description is required')
    caption=item.get('caption','')
    size=item.get('size','wide')
    if size not in {'wide','medium','compact'}:raise ValueError('Unknown image size')
    return '<figure class="case-media media-'+size+'"><img src="'+html.escape(src,quote=True)+'" alt="'+html.escape(alt,quote=True)+'" loading="lazy" decoding="async">'+('<figcaption>'+html.escape(caption)+'</figcaption>' if caption else '')+'</figure>'

def render(data, category):
    out=[]
    for block in data['blocks']:
        kind=block['type']
        if kind in ('heading','paragraph'):
            tag='h2' if kind=='heading' else 'p'
            out.append('<'+tag+'>'+html.escape(block['text'])+'</'+tag+'>')
        elif kind=='image':out.append(image(block))
        elif kind=='sequence':
            layout=block.get('layout','timeline')
            if layout not in {'timeline','comparison','triptych'}:raise ValueError('Unknown image group layout')
            css='clinical-sequence-grid' if layout=='timeline' else 'media-comparison'+(' media-triptych' if layout=='triptych' else '')
            out.append('<div class="'+css+'">'+''.join(image(i) for i in block['images'])+'</div>')
        else:raise ValueError('Unknown content block: '+kind)
    note='치료 결과와 기간, 부작용의 가능성은 개인의 상태와 치료 조건에 따라 달라질 수 있습니다.' if category=='case' else '이 글은 일반적인 정보이며 개인별 진단과 치료계획은 달라질 수 있습니다.'
    return ''.join(out)+'<aside class="medical-note"><strong>안내</strong><p>'+note+'</p></aside>'
