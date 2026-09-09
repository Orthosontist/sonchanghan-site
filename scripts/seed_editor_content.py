"""Import existing article structure once. Never overwrite editor changes."""
from pathlib import Path
import json
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'content/articles';folder.mkdir(parents=True,exist_ok=True)

def picture(node):
    img=node.find('img');caption=node.find('figcaption')
    return {'type':'image','src':img['src'],'alt':img.get('alt',''),'caption':caption.get_text(' ',strip=True) if caption else ''}

for row in json.loads((ROOT/'journal/posts.json').read_text()):
    if row['category']=='exclude':continue
    target=folder/(row['id']+'.json')
    if target.exists():continue
    body=BeautifulSoup((ROOT/row['path']).read_text(),'html.parser').select_one('.body')
    blocks=[]
    for node in body.children:
        if not getattr(node,'name',None):continue
        if node.name in ('h2','h3','p'):
            blocks.append({'type':'paragraph' if node.name=='p' else 'heading','text':node.get_text(' ',strip=True)})
        elif node.name=='figure':blocks.append(picture(node))
        elif 'clinical-sequence-grid' in node.get('class',[]):
            blocks.append({'type':'sequence','images':[picture(f) for f in node.find_all('figure')]})
        elif node.name!='aside':raise ValueError('Unhandled content: '+node.name)
    data={'title':row['title'],'summary':row['summary'],'category':row['category'],'blocks':blocks}
    target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
