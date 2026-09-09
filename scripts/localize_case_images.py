"""Cache authorized clinical images locally; never replace a failed fetch with HTML."""
import hashlib
import io
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from PIL import Image
from bs4 import BeautifulSoup
from rebuild_site import category

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / 'images/cases/remote-map.json'

def main():
    mapping = json.loads(MAP.read_text()) if MAP.exists() else {}
    rows = json.loads((ROOT / 'journal/posts.json').read_text())
    urls = set()
    for row in rows:
        if category(row) != 'case': continue
        soup = BeautifulSoup((ROOT / row['path']).read_text(), 'html.parser')
        urls.update(img['src'] for img in soup.select('.body img[src]') if img['src'].startswith('https://'))
    def download(url):
        if url in mapping and (ROOT / mapping[url].lstrip('/')).exists():
            with Image.open(ROOT / mapping[url].lstrip('/')) as image: image.verify()
            return url, mapping[url]
        host = urlsplit(url).hostname or ''
        if not host.endswith(('.pstatic.net', '.naver.net')): raise ValueError('Unapproved image host: ' + host)
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=35) as response: payload = response.read()
        with Image.open(io.BytesIO(payload)) as image:
            extension = {'JPEG':'jpg','PNG':'png','WEBP':'webp','GIF':'gif'}[image.format]
            image.verify()
        relative = '/images/cases/imported/' + hashlib.sha256(url.encode()).hexdigest()[:24] + '.' + extension
        target = ROOT / relative.lstrip('/')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        return url, relative
    failures = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {url:pool.submit(download, url) for url in sorted(urls)}
        for url, future in futures.items():
            try:
                key, value = future.result(); mapping[key] = value
            except Exception as error: failures.append((url,str(error)))
    MAP.parent.mkdir(parents=True, exist_ok=True)
    MAP.write_text(json.dumps(mapping, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'remote_images':len(urls),'cached':len(mapping),'failures':failures},ensure_ascii=False))
    if failures: raise SystemExit(1)

if __name__ == '__main__': main()
