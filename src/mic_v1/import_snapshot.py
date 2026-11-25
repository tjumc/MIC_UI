#!/usr/bin/env python3
"""Extract reviewable content from a read-only MIC source snapshot.

Requires lxml. Supply the snapshot directory as the sole argument. This script
never downloads files, executes source markup or uses source-site JavaScript.
"""
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from lxml import html, etree
import hashlib, json, re, sys

ROOT = Path(__file__).resolve().parent
SNAP = Path(sys.argv[1]).resolve()
BASE = 'https://mic.tongji.edu.cn/'

def clean_text(node):
    return ' '.join(' '.join(node.itertext()).replace('\xa0', ' ').split())

def doc(name):
    return html.parse(str(SNAP / (name + '.html')))

def page_url(path):
    return urljoin(BASE, path)

def rows(name):
    d = doc(name)
    tables = d.xpath('//div[contains(@class,"paging_content")]//table')
    if len(tables) < 2: raise ValueError('Expected a heading and data table: ' + name)
    return [[clean_text(c) for c in tr.xpath('./td|./th')] for tr in tables[-1].xpath('.//tr')]

def faculty(name):
    d=doc(name); entries=[]
    for tr in d.xpath('//tr[.//img[contains(@src,"_upload/article")]]'):
        cells=tr.xpath('./td')
        if len(cells)<2: continue
        text=clean_text(cells[1]); links=[urljoin(BASE,a.get('href')) for a in cells[1].xpath('.//a[@href]')]
        text=re.sub(r'\s*(\[更多信息\]|\[More information\]|\[More Info\]|\[more information\])\s*$', '', text, flags=re.I)
        entries.append({'bio':text, 'image_url':urljoin(BASE,tr.xpath('.//img/@src')[0]), 'links':links})
    if len(entries)!=2: raise ValueError('Expected two legacy faculty entries: '+name)
    return entries

def research(name):
    d=doc(name);result=[]
    cards=d.xpath('//el-tab-pane[@name="first"]//div[contains(concat(" ",normalize-space(@class)," ")," grid-item ")]')
    for i,card in enumerate(cards):
        headings=card.xpath('.//div[contains(@class,"card-head")]')
        descriptions=card.xpath('.//div[contains(@class,"item-content")]//div[contains(@class,"container")]')
        imgs=card.xpath('.//img/@src')
        if not headings or not descriptions: raise ValueError('Missing research card '+name)
        result.append({'id':f'legacy-{i+1:02d}','title':clean_text(headings[0]),'description':clean_text(descriptions[0]),'image_url':urljoin(BASE,imgs[0]) if imgs else None})
    if len(result)!=14: raise ValueError('Unexpected research topic count: '+name)
    return result

def profile(name):
    d=doc(name);sections=[]
    for heading in d.xpath('//h5[@id]'):
        parent=heading.getparent();content=parent.xpath('.//div[contains(concat(" ",normalize-space(@class)," ")," articlecontent ")]')
        if not content: continue
        items=[]
        for tr in content[0].xpath('.//tr'):
            cells=[clean_text(c) for c in tr.xpath('./td|./th')]
            cells=[x for x in cells if x]
            if cells: items.append(cells)
        if not items:
            txt=clean_text(content[0])
            if txt:items=[[txt]]
        sections.append({'id':heading.get('id'),'title':clean_text(heading),'items':items})
    if len(sections)<5:raise ValueError('Incomplete profile: '+name)
    return sections

project_manifest=json.loads((SNAP/'projects_manifest.json').read_text())['projects']
if any(p['status'] != 200 for p in project_manifest):raise ValueError('Some project pages were not retrieved')
project_paths={urlsplit(p['url']).path:'project-'+p['id']+'.html' for p in project_manifest}
project_by_path={urlsplit(p['url']).path:p['id'] for p in project_manifest}
legacy_images=defaultdict(set)
attachments=defaultdict(lambda: {'labels':set(),'pages':set()})
route_paths={
 '/sy/list.htm':'index.html','/main.htm':'en/index.html','/xstd/list.htm':'team.html','/js/list.htm':'team.html',
 '/Team/list.htm':'en/team.html','/Professor/list.htm':'en/team.html','/cy/list.htm':'members.html','/Member/list.htm':'en/members.html',
 '/xy/list.htm':'alumni.html','/Alumni/list.htm':'en/alumni.html','/yjfx/list.htm':'research.html','/Research/list.htm':'en/research.html',
 '/xslw/list.htm':'publications.html','/Publications/list.htm':'en/publications.html','/kcxx/list.htm':'courses.html','/Courses/list.htm':'en/courses.html',
 '/lxwm/list.htm':'contact.html','/Contact/list.htm':'en/contact.html','/xwlb/list.htm':'news.html','/gdxx/list.htm':'faculty-wang.html','/more_info/list.htm':'en/faculty-wang.html',
 '/50/c1/c31220a282817/page.htm':'news-doctoral.html','/50/c2/c31220a282818/page.htm':'news-masters.html',**project_paths}

def safe_href(raw, current):
    if not raw: return None
    if raw.startswith('#'): return raw
    full=urljoin(current,raw);parts=urlsplit(full)
    if parts.scheme not in ('http','https','mailto'):return None
    if parts.hostname=='mic.tongji.edu.cn':
        if parts.path==urlsplit(current).path and parts.fragment:return '#'+parts.fragment
        if parts.path in project_paths:return project_paths[parts.path]+(('#'+parts.fragment) if parts.fragment else '')
        if parts.path in route_paths:return route_paths[parts.path]+(('#'+parts.fragment) if parts.fragment else '')
        return 'https://mic.tongji.edu.cn'+parts.path+(('?'+parts.query) if parts.query else '')+(('#'+parts.fragment) if parts.fragment else '')
    return full

def sanitize(root,current,lang):
    node=deepcopy(root)
    allowed={'div','p','span','strong','b','em','i','u','ul','ol','li','table','thead','tbody','tr','td','th','br','a','blockquote','pre','code','sub','sup','h1','h2','h3','h4','h5','h6'}
    for el in list(node.iter()):
        if not isinstance(el.tag,str):
            if el.getparent() is not None:el.drop_tree()
            continue
        tag=el.tag.lower()
        if tag in ('script','style','iframe','object','embed','link','form','input','button'):
            if el.getparent() is not None:el.drop_tree()
            continue
        if tag=='img':
            raw=el.get('src','');source=urljoin(current,raw)
            if raw.startswith('data:'):
                source='inline-image-sha256:'+hashlib.sha256(raw.encode()).hexdigest()
            if source:legacy_images[source].add(current)
            parent=el.getparent()
            if parent is None:continue
            box=html.Element('span');box.set('class','legacy-image-slot');box.text=('原站插图：图片暂留白' if lang=='zh' else 'Original illustration: image placeholder');box.tail=el.tail;parent.replace(el,box)
            continue
        if tag not in allowed:el.tag='span'
        if el.tag=='h1':el.tag='h2'
        attrs={}; ident=el.get('id') or el.get('name')
        if ident and re.fullmatch(r'[A-Za-z0-9_:.-]{1,100}',ident):attrs['id']=ident
        if tag=='a':
            raw=el.get('href');target=safe_href(raw,current)
            if target:
                attrs['href']=target
                u=urlsplit(target)
                if u.hostname=='mic.tongji.edu.cn' and u.path.startswith('/_upload/article/files/'):
                    attachments[target]['labels'].add(clean_text(el) or '原站附件');attachments[target]['pages'].add(current)
        el.attrib.clear();el.attrib.update(attrs)
    for a in node.xpath('.//a[starts-with(@href,"#fn:")]'):
        ref='fnref:'+a.get('href').split(':',1)[1]
        if not node.xpath('.//*[@id=$ref]',ref=ref):a.set('id',ref)
    for a in node.xpath('.//a[starts-with(@href,"#fnref:")]'):
        target='fn:'+a.get('href').split(':',1)[1]
        if not node.xpath('.//*[@id=$target]',target=target):a.getparent().set('id',target)
    return ''.join(etree.tostring(x,encoding='unicode',method='html') for x in node)

papers=[];current_year=None
body=doc('publications_zh').xpath('//div[contains(@class,"paging_content")]')[0]
for child in body:
    heading=clean_text(child)
    if child.tag=='p' and re.fullmatch(r'20\d{2}',heading):current_year=heading;continue
    if child.tag!='ul':continue
    if not current_year:raise ValueError('Publication year missing')
    for li in child.xpath('./li'):
        clone=deepcopy(li);links=[]
        for a in clone.xpath('.//a[@href]'):
            raw=a.get('href');full=urljoin(page_url('xslw/list.htm'),raw);path=urlsplit(full).path
            if path in project_by_path:
                links.append({'kind':'project','id':project_by_path[path],'label':'Project','original_url':full})
            else:
                target=safe_href(raw,page_url('xslw/list.htm'))
                if target:
                    label=clean_text(a) or 'Resource';links.append({'kind':'resource','href':target,'label':label,'original_url':full})
                    u=urlsplit(target)
                    if u.hostname=='mic.tongji.edu.cn' and u.path.startswith('/_upload/article/files/'):
                        attachments[target]['labels'].add(label);attachments[target]['pages'].add(page_url('xslw/list.htm'))
            a.drop_tree()
        text=clean_text(clone);text=re.sub(r'\[\s*Project\s*:\s*\]', '', text, flags=re.I);text=re.sub(r'\[\s*\]', '', text);text=' '.join(text.split())
        if text:papers.append({'year':current_year,'citation':text,'links':links})
if len(papers)!=236:raise ValueError('Unexpected publication count: '+str(len(papers)))

projects=[]
for item in sorted(project_manifest,key=lambda x:int(x['id'])):
    d=html.parse(str(SNAP/'projects'/(item['id']+'.html')));content=d.xpath('//div[contains(@class,"wp_articlecontent")]')
    if not content:raise ValueError('Missing project article '+item['id'])
    title=' '.join((d.findtext('.//title') or '').split()) or ('Project '+item['id'])
    projects.append({'id':item['id'],'title':title,'source_url':item['url'],'body_zh':sanitize(content[0],item['url'],'zh'),'body_en':sanitize(content[0],item['url'],'en')})

core_entries=json.loads((SNAP/'core_manifest.json').read_text())['pages']
profile_en=(SNAP/'wang_profile_en.html').read_bytes()
core_entries.append({'name':'wang_profile_en','url':page_url('more_info/list.htm'),'final_url':page_url('more_info/list.htm'),'status':200,'bytes':len(profile_en),'sha256':hashlib.sha256(profile_en).hexdigest()})
core_urls={x['name']:x['url'] for x in core_entries}
for page in ['home_zh','home_en','faculty_zh','faculty_en','research_zh','research_en','contact_zh','contact_en']:
    d=doc(page)
    for i in d.xpath('//img[@src]'):
        raw=i.get('src')
        if 'static/image/' in raw or '/_upload/article/images/' in raw:legacy_images[urljoin(BASE,raw)].add(core_urls[page])
    if page.startswith('home'):
        for element in d.xpath('//*[@style]'):
            for raw in re.findall(r'url\(([^)]+)\)',element.get('style','')):
                raw=raw.strip('\"\'')
                if 'static/image/' in raw:legacy_images[urljoin(BASE,raw)].add(core_urls[page])

news={}
for key,name in [('doctoral','admission_phd'),('masters','admission_masters')]:
    d=doc(name);content=d.xpath('//div[contains(@class,"wp_articlecontent")]')
    if not content:raise ValueError('Missing admission notice '+name)
    news[key]={'source_url':next(x['url'] for x in json.loads((SNAP/'core_manifest.json').read_text())['pages'] if x['name']==name),'body':sanitize(content[0],BASE,'zh')}

home_project_ids=[]
for a in doc('home_zh').xpath('//a[@href]'):
    m=re.search(r'c9778a(\d+)/page\.htm',a.get('href',''))
    if m and m.group(1) in {x['id'] for x in projects} and m.group(1) not in home_project_ids:home_project_ids.append(m.group(1))
content={'snapshot_date':'2026-11-25','home_project_ids':home_project_ids,'publication_notice':clean_text(body[0]),'members':{'zh':rows('members_zh'),'en':rows('members_en')},'alumni':{'zh':rows('alumni_zh'),'en':rows('alumni_en')},'courses':{'zh':rows('courses_zh'),'en':rows('courses_en')},'faculty':{'zh':faculty('faculty_zh'),'en':faculty('faculty_en')},'wang_profile':{'zh':profile('wang_profile'),'en':profile('wang_profile_en')},'research_legacy':{'zh':research('research_zh'),'en':research('research_en')},'papers':papers,'projects':projects,'admissions':news}
(ROOT/'data/content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest={'snapshot_date':'2026-11-25','core':core_entries,'projects':project_manifest,'legacy_routes':[{'source':'https://mic.tongji.edu.cn'+k,'target':v} for k,v in sorted(route_paths.items())],'image_references':[{'source':u,'pages':sorted(v)} for u,v in sorted(legacy_images.items())],'attachments':[{'url':u,'labels':sorted(v['labels']),'pages':sorted(v['pages'])} for u,v in sorted(attachments.items())]}
(ROOT/'data/source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('members',len(content['members']['zh']),'alumni',len(content['alumni']['zh']),'courses',len(content['courses']['zh']),'papers',len(papers),'projects',len(projects),'historical research',len(content['research_legacy']['zh']),'image references',len(manifest['image_references']),'attachments',len(manifest['attachments']))
