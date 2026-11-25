#!/usr/bin/env python3
"""Regression checks for generated content, internal links and old-URL fallbacks."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit
import hashlib, json, re, unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]/'dist/mic-v1'
DATA=json.loads((HERE/'data/content.json').read_text(encoding='utf-8'))
MANIFEST=json.loads((HERE/'data/source-manifest.json').read_text(encoding='utf-8'))
IMAGES=json.loads((HERE/'data/image-assets.json').read_text(encoding='utf-8'))
ASSETS={x['source']:x for x in IMAGES['assets'] if x['status']=='ok'}

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=set();self.refs=[];self.h1=0;self.cards=0;self.img=[];self.meta=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.add(a['id'])
        if tag=='h1':self.h1+=1
        if 'data-filter-row' in a:self.cards+=1
        if tag=='img':self.img.append((a.get('src'),a.get('alt')))
        if tag=='meta' and a.get('http-equiv','').lower()=='refresh':self.meta.append(a.get('content',''))
        for key in ('href','src'):
            if key in a:self.refs.append(a[key])

def parse(path):
    p=Page();p.feed(path.read_text(encoding='utf-8'));return p

class MigrationTests(unittest.TestCase):
    def test_expected_content_is_static_and_bilingual(self):
        self.assertEqual((len(DATA['members']['zh']),len(DATA['members']['en'])),(17,17))
        self.assertEqual((len(DATA['alumni']['zh']),len(DATA['alumni']['en'])),(62,62))
        self.assertEqual((len(DATA['courses']['zh']),len(DATA['courses']['en'])),(46,46))
        self.assertEqual(len(DATA['papers']),236);self.assertEqual(len(DATA['projects']),45)
        self.assertEqual((len(DATA['research_legacy']['zh']),len(DATA['research_legacy']['en'])),(14,14))
        for lang in ('','en/'):
            for name,count in [('members',17),('alumni',62),('courses',46),('publications',236)]:
                self.assertEqual(parse(ROOT/lang/(name+'.html')).cards,count)
            for project in DATA['projects']:
                self.assertTrue((ROOT/lang/('project-'+project['id']+'.html')).is_file())

    def test_home_has_user_requested_topics_and_staff(self):
        home=(ROOT/'index.html').read_text(encoding='utf-8')
        for word in ['图像视频压缩编码','智能调度与优化','具身智能','医工交叉','自动驾驶','王瀚漓','倪张凯','杜杉杉','吴秀哲']:
            self.assertIn(word,home)
        self.assertEqual(len(DATA['home_project_ids']),4)
        self.assertIn('2022-11-06',(ROOT/'news-doctoral.html').read_text(encoding='utf-8'))

    def test_all_internal_links_and_fragments(self):
        pages=list(ROOT.rglob('*.html'))+list(ROOT.rglob('*.htm'));cache={}
        def get(p):
            if p not in cache:cache[p]=parse(p)
            return cache[p]
        failures=[]
        for page in pages:
            parsed=get(page)
            if page.suffix=='.html' and parsed.h1!=1:failures.append(f'{page}: expected one h1, got {parsed.h1}')
            for href in parsed.refs:
                if not href:continue
                url=urlsplit(href)
                if url.scheme:
                    if url.scheme not in ('http','https','mailto','tel'):failures.append(f'{page}: unsafe scheme {href}')
                    continue
                target=(page.parent/unquote(url.path)).resolve() if url.path else page.resolve()
                if not target.is_relative_to(ROOT.resolve()):failures.append(f'{page}: outside site {href}');continue
                if target.is_dir():target=target/'index.html'
                if not target.is_file():failures.append(f'{page}: missing {href}');continue
                if url.fragment and target.suffix in ('.html','.htm') and unquote(url.fragment) not in get(target).ids:failures.append(f'{page}: missing fragment {href}')
        self.assertEqual(failures,[],'\n'.join(failures[:30]))

    def test_old_url_fallbacks_and_images(self):
        for item in MANIFEST['legacy_routes']:
            old=urlsplit(item['source']).path.lstrip('/');path=ROOT/old
            self.assertTrue(path.is_file(),old);self.assertTrue(parse(path).meta,old)
        self.assertEqual(len(MANIFEST['attachments']),48)
        self.assertGreaterEqual(len(MANIFEST['image_references']),250)
        for path in ROOT.rglob('*.html'):
            for src,alt in parse(path).img:
                self.assertTrue(src and not urlsplit(src).scheme,f'{path}: nonlocal image {src}')
                self.assertTrue(alt,f'{path}: image without alt')
                self.assertTrue((path.parent/src).resolve().is_file(),f'{path}: missing image {src}')
        for source,item in ASSETS.items():
            image=ROOT/'assets/legacy'/item['file']
            self.assertTrue(image.is_file(),source)
            self.assertEqual(hashlib.sha256(image.read_bytes()).hexdigest(),item['sha256'],source)

    def test_known_portraits_and_research_images(self):
        for lang,prefix in [('zh',''),('en','en/')]:
            team=(ROOT/prefix/'team.html').read_text(encoding='utf-8')
            for i,name in [(0,'王瀚漓'),(1,'倪张凯')]:
                asset=ASSETS[DATA['faculty']['zh'][i]['image_url']]
                self.assertIn(asset['file'],team,name)
                detail=(ROOT/prefix/('faculty-'+('wang' if i==0 else 'ni')+'.html')).read_text(encoding='utf-8')
                self.assertIn(asset['file'],detail,name)
            for name in ['杜杉杉','吴秀哲']:
                self.assertIn(name,team)
            self.assertIn('Place a portrait of 杜杉杉 here' if lang=='en' else '此处放置杜杉杉老师照片',team)
            archive=(ROOT/prefix/'research-archive.html').read_text(encoding='utf-8')
            for topic in DATA['research_legacy'][lang]:
                if topic['image_url'] in ASSETS:self.assertIn(ASSETS[topic['image_url']]['file'],archive)
            research=(ROOT/prefix/'research.html').read_text(encoding='utf-8')
            coding=ASSETS[DATA['research_legacy']['zh'][0]['image_url']]['file']
            self.assertIn(coding,research)
            self.assertEqual(research.count('class="image-slot has-image research-image"'),1)
            self.assertIn('object-fit:contain',(ROOT/'site.css').read_text(encoding='utf-8'))

    def test_project_figures_follow_original_page_order(self):
        for project in DATA['projects']:
            figures=IMAGES['projects'].get(project['id'],[])
            for lang,prefix in [('zh',''),('en','en/')]:
                page=(ROOT/prefix/('project-'+project['id']+'.html')).read_text(encoding='utf-8')
                inserted=re.findall(r'<span class="legacy-figure"><img [^>]*src="([^"]+)"',page)
                expected=[ASSETS[x['source']]['file'] for x in figures if x['eligible'] and x['source'] in ASSETS]
                self.assertEqual([x.rsplit('/',1)[-1] for x in inserted],expected,project['id'])
                total=project['body_'+lang].count('legacy-image-slot')
                self.assertEqual(len(inserted)+page.count('legacy-image-slot'),total,project['id'])

if __name__=='__main__':unittest.main(verbosity=2)
