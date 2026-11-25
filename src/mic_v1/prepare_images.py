#!/usr/bin/env python3
"""Recover exact, inventoried MIC images without altering the original bytes."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from lxml import html
from PIL import Image
import hashlib, json, time

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / 'data/content.json').read_text(encoding='utf-8'))
MANIFEST = json.loads((HERE / 'data/source-manifest.json').read_text(encoding='utf-8'))
DEST = HERE / 'assets/legacy'
MAP = HERE / 'data/image-assets.json'
if MAP.exists() or DEST.exists():
    raise SystemExit('Image output already exists; inspect it before running again.')
DEST.mkdir(parents=True)
HEADERS = {'User-Agent':'Mozilla/5.0', 'Referer':'https://mic.tongji.edu.cn/'}
MAX_BYTES = 20 * 1024 * 1024

def get_bytes(url, limit):
    p = urlsplit(url)
    if p.scheme != 'https' or p.hostname != 'mic.tongji.edu.cn':
        raise ValueError('URL is outside the original MIC host')
    last = None
    for attempt in range(2):
        try:
            with urlopen(Request(url, headers=HEADERS), timeout=55) as r:
                final = urlsplit(r.geturl())
                if r.status != 200 or final.hostname != 'mic.tongji.edu.cn':
                    raise ValueError('Unexpected response or redirect')
                content = r.read(limit + 1)
                if len(content) > limit: raise ValueError('Asset exceeds the size limit')
                return content
        except Exception as exc:
            last = str(exc)
            if attempt == 0: time.sleep(1)
    raise ValueError(last)

entries = {x['name']: x for x in MANIFEST['core']}
tasks = [('core', entries[k]) for k in ('faculty_zh', 'research_zh')] + [('project', p) for p in MANIFEST['projects']]
def page_task(job):
    kind, item = job
    try:
        body = get_bytes(item['url'], 4 * 1024 * 1024)
        digest = hashlib.sha256(body).hexdigest()
        if digest != item['sha256']: raise ValueError('Page differs from the recorded snapshot')
        urls = []
        if kind == 'project':
            doc = html.fromstring(body)
            articles = doc.xpath('//div[contains(@class,"wp_articlecontent")]')
            if not articles: raise ValueError('Project article missing')
            for img in articles[0].xpath('.//img'):
                raw = img.get('src', '')
                urls.append(urljoin(item['url'], raw))
            project = next(p for p in DATA['projects'] if p['id'] == item['id'])
            if len(urls) != project['body_zh'].count('legacy-image-slot'):
                raise ValueError('Image count differs from migrated article')
        return {'kind':kind,'id':item.get('id', item.get('name')),'status':'ok','urls':urls}
    except Exception as exc:
        return {'kind':kind,'id':item.get('id', item.get('name')),'status':'failed','error':str(exc),'urls':[]}
pages = []
with ThreadPoolExecutor(max_workers=10) as pool:
    for future in as_completed([pool.submit(page_task, j) for j in tasks]):
        result = future.result(); pages.append(result)
        print('PAGE', result['kind'], result['id'], result['status'], flush=True)
checks = {p['id']:p for p in pages if p['kind']=='core'}
inventoried = {i['source']:set(i['pages']) for i in MANIFEST['image_references']}
wanted = set()
core = {}
if checks['faculty_zh']['status'] == 'ok':
    core['faculty'] = [p['image_url'] for p in DATA['faculty']['zh']]
    wanted.update(core['faculty'])
else: core['faculty'] = []
if checks['research_zh']['status'] == 'ok':
    core['research'] = [p['image_url'] for p in DATA['research_legacy']['zh']]
    wanted.update(core['research'])
else: core['research'] = []
project_lookup = {p['id']:p for p in MANIFEST['projects']}
project_images = {}
for p in pages:
    if p['kind'] != 'project': continue
    source_page = project_lookup[p['id']]['url']
    project_images[p['id']] = []
    for url in p['urls']:
        valid = source_page in inventoried.get(url, set()) and urlsplit(url).path.startswith('/_upload/article/images/')
        project_images[p['id']].append({'source':url,'eligible':valid})
        if valid: wanted.add(url)
def image_task(url):
    try:
        raw = get_bytes(url, MAX_BYTES)
        with Image.open(BytesIO(raw)) as im:
            w,h,fmt = im.width,im.height,im.format
            im.verify()
        extensions = {'JPEG':'.jpg','PNG':'.png','GIF':'.gif','WEBP':'.webp','BMP':'.bmp'}
        if fmt not in extensions: raise ValueError('Unsupported image format '+str(fmt))
        name = hashlib.sha256(url.encode()).hexdigest()[:16] + extensions[fmt]
        (DEST / name).write_bytes(raw)
        return {'source':url,'status':'ok','file':name,'bytes':len(raw),
                'sha256':hashlib.sha256(raw).hexdigest(),'width':w,'height':h,'format':fmt}
    except Exception as exc:
        return {'source':url,'status':'failed','error':str(exc)}
assets = []
with ThreadPoolExecutor(max_workers=14) as pool:
    futures = [pool.submit(image_task, url) for url in sorted(wanted)]
    for future in as_completed(futures):
        result = future.result(); assets.append(result)
        print('IMAGE',len(assets),'/',len(wanted),result['status'],result['source'],flush=True)
report = {'snapshot_date':MANIFEST['snapshot_date'], 'core_checks':checks,
          'core':core, 'projects':project_images,
          'project_page_checks':{p['id']:{k:v for k,v in p.items() if k!='urls'} for p in pages if p['kind']=='project'},
          'assets':sorted(assets,key=lambda x:x['source'])}
MAP.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RESULT pages:',len(pages),'page failures:',sum(p['status']!='ok' for p in pages),
      'images:',len(assets),'image failures:',sum(a['status']!='ok' for a in assets),flush=True)
