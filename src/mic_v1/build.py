#!/usr/bin/env python3
"""Build the standalone, bilingual version-1 MIC migration from reviewed JSON."""
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import importlib.util, json, posixpath, shutil, sys
sys.dont_write_bytecode=True

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'dist/mic-v1'
DATA=json.loads((HERE/'data/content.json').read_text(encoding='utf-8'))
MANIFEST=json.loads((HERE/'data/source-manifest.json').read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('mic_original_design',ROOT/'src/build.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
e=lambda value:escape(str(value),quote=True)
t=lambda lang,zh,en:zh if lang=='zh' else en
DIRECTIONS=[('coding','图像视频压缩编码','Image & Video Compression'),('optimization','智能调度与优化','Intelligent Scheduling & Optimization'),('embodied','具身智能','Embodied Intelligence'),('medical','医工交叉','Medicine & Engineering'),('driving','自动驾驶','Autonomous Driving')]

EN_NOTICES={
 'doctoral':'''<h2>Doctoral admissions notice</h2><h3>Application procedure</h3><p>Applicants were asked to email Professor Hanli Wang a curriculum vitae, their study plans and expectations, copies of language qualifications, and any other relevant academic work, awards or qualifications.</p><p>The original notice described a résumé review and interview by the laboratory. This is an archived notice; current admissions procedures and decisions must be confirmed with the university and laboratory.</p>''',
 'masters':'''<h2>Master’s admissions notice</h2><h3>Recommended applicants</h3><p>The historical notice described eligibility for recommended admission, participation in the School of Electronic and Information Engineering summer programme, interest in the laboratory’s research and good English proficiency.</p><h3>Entrance-examination applicants</h3><p>The notice described eligibility for admission through the examination, interest in the laboratory’s research and good English proficiency.</p><h3>Application materials</h3><p>Applicants were asked to email Professor Hanli Wang a curriculum vitae, their study plans, a certified undergraduate transcript and ranking, copies of language qualifications, and other relevant academic work, awards or qualifications.</p><p>The original notice described a résumé review and interview by the laboratory. This is an archived notice; current admissions procedures and decisions must be confirmed with the university and laboratory.</p>'''
}

def slot(lang,zh,en,cls=''):
    return base.slot(lang,zh,en,cls)

def section_head(lang,eyebrow,zh,en,sub_zh='',sub_en='',link='',link_zh='',link_en=''):
    return base.section_head(lang,eyebrow,zh,en,sub_zh,sub_en,link,link_zh,link_en)

def hero(lang,eyebrow,zh,en,sub_zh,sub_en):
    return base.page_hero(lang,eyebrow,zh,en,sub_zh,sub_en)

def body_document(lang,page,title,body):
    body=body.replace('<span aria-hidden="true">↗</span>', '')
    head=base.header(lang,page)
    active=('publications.html' if page.startswith('project-') else 'team.html' if page.startswith('faculty-') else 'research.html' if page=='research-archive.html' else 'news.html' if page.startswith('news-') else '')
    if active: head=head.replace(f'<a href="{active}">',f'<a href="{active}" aria-current="page">')
    pre='' if lang=='zh' else '../'
    return f'''<!doctype html><html lang="{'zh-CN' if lang=='zh' else 'en'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#ffffff"><title>{e(title)} | MIC · Tongji University</title><link rel="stylesheet" href="{pre}site.css"><script defer src="{pre}site.js"></script></head><body data-page="{e(page.removesuffix('.html'))}"><a class="skip" href="#main">{e(t(lang,'跳至主要内容','Skip to content'))}</a>{head}<main id="main">{body}</main>{base.footer(lang)}</body></html>'''

def make_file(lang,page,title,body):
    directory=OUT if lang=='zh' else OUT/'en';directory.mkdir(parents=True,exist_ok=True)
    (directory/page).write_text(body_document(lang,page,title,body),encoding='utf-8')

def topic_description(lang,index):
    if index==0:return DATA['research_legacy'][lang][0]['description']
    return t(lang,'该方向的具体研究内容有待课题组确认和补充。','Details for this research area are awaiting confirmation from the lab.')

def topic_carousel(lang):
    buttons=''.join(f'<button type="button" data-topic="{i}" aria-pressed="{"true" if i==0 else "false"}">{e(t(lang,zh,en))}</button>' for i,(_,zh,en) in enumerate(DIRECTIONS))
    slides=[]
    for i,(key,zh,en) in enumerate(DIRECTIONS):
        slides.append(f'''<article class="topic-slide" data-slide="{i}"{' hidden' if i else ''}>{slot(lang,'此处放置'+zh+'研究示意图','Place an image for '+en+' here')}<div class="topic-copy"><p class="index-line">{e(en)}</p><h3>{e(t(lang,zh,en))}</h3><p>{e(topic_description(lang,i))}</p><a class="text-link" href="research.html#{key}">{e(t(lang,'了解这个方向','Explore this area'))}</a></div></article>''')
    return f'''<div data-carousel><div class="topic-pills" aria-label="{e(t(lang,'选择研究方向','Choose a research area'))}">{buttons}</div><div>{''.join(slides)}</div><div class="carousel-bottom"><p>{e(t(lang,'探索 MIC 的五个研究方向。','Explore five research areas at MIC.'))}</p><div class="carousel-controls"><span data-count>01 / 05</span><button type="button" data-previous aria-label="{e(t(lang,'上一个研究方向','Previous research area'))}">←</button><button type="button" data-next aria-label="{e(t(lang,'下一个研究方向','Next research area'))}">→</button></div><span class="sr-only" data-status aria-live="polite"></span></div></div>'''

def faculty_cards(lang,directory=False):
    people=[('王瀚漓','Hanli Wang','faculty-wang.html',0),('倪张凯','Zhangkai Ni','faculty-ni.html',1),('杜杉杉','','',None),('吴秀哲','','',None)]
    cards=[]
    for name,en,path,idx in people:
        display=name if lang=='zh' or not en else en; other=en if lang=='zh' else name if en else ''
        text=DATA['faculty'][lang][idx]['bio'] if idx is not None else ''
        # Keep the full sourced biography on the corresponding detail page.
        if text:
            limit=185 if lang=='zh' else 240
            excerpt=text if len(text)<=limit else text[:limit].rsplit(' ',1)[0]+'…' if lang=='en' else text[:limit]+'…'
        else:excerpt=''
        extra=f'<a class="text-link" href="{path}">{e(t(lang,"查看简介","Full profile"))}</a>' if path else ''
        cards.append(f'''<article class="person-card">{slot(lang,'此处放置'+name+'老师照片','Place a portrait of '+(en or name)+' here')}<div><h3>{e(display)}{f'<small>{e(other)}</small>' if other else ''}</h3>{f'<p class="bio">{e(excerpt)}</p>' if excerpt else ''}{extra}</div></article>''')
    return ''.join(cards)

def paper_links(lang,paper):
    items=[]
    for link in paper.get('links',[]):
        href='project-'+link['id']+'.html' if link['kind']=='project' else link['href']
        label=t(lang,'项目介绍','Project') if link['kind']=='project' else link['label']
        suffix=t(lang,'（原站附件）',' (original attachment)') if link['kind']=='resource' and urlsplit(href).hostname=='mic.tongji.edu.cn' else ''
        items.append(f'<a class="paper-resource" href="{e(href)}">{e(label+suffix)}</a>')
    return '<div class="paper-resources">'+' '.join(items)+'</div>' if items else ''

def paper_card(lang,paper):
    return f'''<article class="paper-card" data-filter-row data-year-value="{e(paper['year'])}"><span class="year">{e(paper['year'])}</span><div><p>{e(paper['citation'])}</p>{paper_links(lang,paper)}</div></article>'''

def home(lang):
    hero_html=f'''<section class="home-hero"><div class="shell"><div class="home-hero-copy"><p class="eyebrow">MULTIMEDIA &amp; INTELLIGENT COMPUTING</p><h1>{e(t(lang,'多媒体与智能计算实验室','Multimedia & Intelligent Computing Lab'))}</h1><p class="university">TONGJI UNIVERSITY · SHANGHAI</p><p class="lead">{e(t(lang,'从图像视频编码与智能优化，到具身智能、医工交叉与自动驾驶。','From image and video coding and intelligent optimization to embodied intelligence, medical engineering and autonomous driving.'))}</p><div class="hero-actions"><a class="button primary" href="research.html">{e(t(lang,'研究方向','Our research'))}</a><a class="button secondary" href="team.html">{e(t(lang,'认识团队','Meet the team'))}</a></div></div>{slot(lang,'此处放置实验室环境或团队合影横幅','Place a lab or team banner image here','hero-slot')}</div></section>'''
    about=f'''<section class="section shell">{section_head(lang,'ABOUT MIC','关于我们','About us',link='team.html',link_zh='认识团队',link_en='Meet the team')}<div class="about-grid"><div class="body-copy"><p>{e(t(lang,'同济大学多媒体与智能计算实验室（MIC）围绕多媒体信息计算与智能系统开展研究。','The Multimedia and Intelligent Computing Lab (MIC) at Tongji University studies multimedia information computing and intelligent systems.'))}</p><p>{e(t(lang,'了解实验室研究方向、成员与论文成果。','Explore the laboratory’s research, people and publications.'))}</p></div><div class="facts"><div class="fact"><strong>{e(t(lang,'研究','RESEARCH'))}</strong><p>{e(t(lang,'五个研究方向','Five research areas'))}</p></div><div class="fact"><strong>{e(t(lang,'团队','PEOPLE'))}</strong><p>{e(t(lang,'教师、成员与校友','Faculty, members and alumni'))}</p></div><div class="fact"><strong>{e(t(lang,'位置','LOCATION'))}</strong><p>{e(t(lang,'同济大学嘉定校区','Tongji University, Jiading Campus'))}</p></div><div class="fact"><strong>{e(t(lang,'交流','CONTACT'))}</strong><p>hanliwang@tongji.edu.cn</p></div></div></div></section>'''
    research=f'''<section class="section alt"><div class="shell">{section_head(lang,'RESEARCH','研究方向','Research areas','从多媒体编码到交叉应用。','From multimedia coding to interdisciplinary applications.','research.html','全部研究方向','All research areas')}{topic_carousel(lang)}</div></section>'''
    people=f'''<section class="section shell">{section_head(lang,'PEOPLE','教师团队','Our faculty','认识 MIC 的教师。','Meet the faculty at MIC.','team.html','查看团队','Meet the team')}<div class="person-grid">{faculty_cards(lang)}</div></section>'''
    selected=[]
    for pid in DATA['home_project_ids']:
        paper=next((p for p in DATA['papers'] if any(l.get('id')==pid for l in p.get('links',[]))),None)
        if not paper:raise ValueError('Homepage paper not found: '+pid)
        selected.append(paper_card(lang,paper))
    pubs=f'''<section class="section alt"><div class="shell">{section_head(lang,'PUBLICATIONS','学术论文','Selected publications','来自原站首页的论文记录。','Publication records featured on the original site.','publications.html','查看论文','All publications')}<div class="paper-list">{''.join(selected)}</div></div></section>'''
    news_cards=''.join(f'''<a class="news-card" href="news-{key}.html"><small>2022-11-06 · {e(t(lang,'历史通知','ARCHIVED NOTICE'))}</small><h3>{e(t(lang,zh,en))}</h3><p>{e(t(lang,'历史通知；最新招生信息请联系实验室。','Archived notice; contact the lab for current information.'))}</p></a>''' for key,zh,en in [('doctoral','MIC 实验室博士生招生说明','Doctoral admissions notice'),('masters','MIC 实验室硕士生招生说明','Master’s admissions notice')])
    news=f'''<section class="section shell">{section_head(lang,'NEWS','动态','News',link='news.html',link_zh='查看动态',link_en='All news')}<div class="news-grid">{news_cards}</div></section>'''
    return hero_html+about+research+people+pubs+news+base.closing(lang)

def research_page(lang):
    heading=hero(lang,'RESEARCH','研究方向','Research areas','探索 MIC 的五个研究方向。','Explore five research areas at MIC.')
    pills='<div class="topic-pills">'+''.join(f'<a href="#{key}">{e(t(lang,zh,en))}</a>' for key,zh,en in DIRECTIONS)+'</div>'
    cards=[]
    for i,(key,zh,en) in enumerate(DIRECTIONS):
        cards.append(f'''<article class="research-row" id="{key}">{slot(lang,'此处放置'+zh+'研究示意图','Place an image for '+en+' here')}<div class="body-copy"><p class="index-line">{e(en)}</p><h2>{e(t(lang,zh,en))}</h2><p>{e(topic_description(lang,i))}</p></div></article>''')
    extra=f'''<div class="archive-callout"><div><h2>{e(t(lang,'原站研究专题','Research topics from the original site'))}</h2><p>{e(t(lang,'保留原站的专题介绍，供查阅。','Explore the research descriptions preserved from the original site.'))}</p></div><a class="button secondary" href="research-archive.html">{e(t(lang,'查看历史专题','View historical topics'))}</a></div>'''
    return heading+f'<section class="section shell">{pills}<div class="research-list">{"".join(cards)}</div>{extra}</section>'+base.closing(lang)

def research_archive(lang):
    top=hero(lang,'RESEARCH ARCHIVE','原站研究专题','Research topics from the original site','以下内容来自原站，方向归属和最新状态待课题组确认。','Descriptions are preserved from the original site; current status and classification need confirmation.')
    cards=[]
    for topic in DATA['research_legacy'][lang]:
        cards.append(f'''<article class="research-row" id="{e(topic['id'])}">{slot(lang,'此处放置'+topic['title']+'原站示意图','Place the original '+topic['title']+' illustration here')}<div class="body-copy"><h2>{e(topic['title'])}</h2><p>{e(topic['description'])}</p></div></article>''')
    return top+f'<section class="section shell"><p class="notice">{e(t(lang,"以下为原站资料快照，尚未将历史专题强行归入新的五个方向。","This is an archival snapshot; topics have not been assigned to the five current areas without confirmation."))}</p><div class="research-list">{"".join(cards)}</div></section>'+base.closing(lang)

def team_page(lang):
    top=hero(lang,'PEOPLE','团队','Our team','认识 MIC 的教师、成员与校友。','Meet the faculty, members and alumni of MIC.')
    return top+base.subnav(lang,'team.html')+f'''<section class="section shell">{section_head(lang,'FACULTY','教师团队','Faculty','教师资料来自原站与课题组提供的名单。','Faculty information is based on the original site and the lab’s supplied roster.')}<p class="notice">{e(t(lang,'原站简介整理于 2026 年 11 月，职务和成果等时间性信息有待确认。','Original-site biographies were collected in November 2026; time-sensitive roles and achievements require confirmation.'))}</p><div class="person-grid directory-grid">{faculty_cards(lang,True)}</div></section>'''+base.closing(lang)

def faculty_detail(lang,who):
    idx=0 if who=='wang' else 1;name=t(lang,'王瀚漓','Hanli Wang') if idx==0 else t(lang,'倪张凯','Zhangkai Ni')
    entry=DATA['faculty'][lang][idx]
    top=hero(lang,'FACULTY',name,name,'教师介绍','Faculty profile')
    text=f'''<section class="section shell"><a class="text-link" href="team.html">{e(t(lang,'返回团队','Back to team'))}</a><p class="notice">{e(t(lang,'以下为原站资料快照；现任职务、成果数量与联系方式等请课题组复核。','The following is an original-site snapshot. Current roles, counts and contact details need review by the lab.'))}</p><div class="profile-intro">{slot(lang,'此处放置'+('王瀚漓' if idx==0 else '倪张凯')+'老师照片','Place a faculty portrait here')}<div class="body-copy"><p>{e(entry['bio'])}</p></div></div>'''
    if idx==0:
        for section in DATA['wang_profile'][lang]:
            if section['id']=='about':continue
            lines=''.join('<li>'+' — '.join(e(x) for x in row)+'</li>' for row in section['items'])
            text+=f'<section class="profile-section" id="{e(section["id"])}"><h2>{e(section["title"])}</h2><ul>{lines}</ul></section>'
    else:
        for link in entry['links']:
            if urlsplit(link).hostname=='eezkni.github.io':text+=f'<p class="profile-external"><a class="text-link" href="{e(link)}">{e(t(lang,"教师个人主页","Faculty personal homepage"))}</a></p>'
    return top+text+'</section>'+base.closing(lang)

def records(lang,kind,title_zh,title_en,columns,notice_zh,notice_en,team=False):
    top=hero(lang,kind.upper(),title_zh,title_en,notice_zh,notice_en)
    nav=base.subnav(lang,kind+'.html') if team else ''
    heads=''.join(f'<th scope="col">{e(t(lang,a,b))}</th>' for a,b in columns)
    label=t(lang,'搜索','Search');headlabels=[t(lang,a,b) for a,b in columns]
    data=DATA[kind][lang];trs=[]
    for row in data:
        if len(row)!=len(headlabels):raise ValueError(f'{kind} row width: {row}')
        tds=''.join(f'<td data-label="{e(label)}">{e(value)}</td>' for label,value in zip(headlabels,row))
        trs.append('<tr data-filter-row>'+tds+'</tr>')
    table=f'''<section class="section shell">{section_head(lang,kind.upper(),title_zh,title_en)}<p class="notice">{e(t(lang,notice_zh,notice_en))}</p><div class="data-toolbar"><label class="field" for="record-search">{e(label)}<input id="record-search" type="search" data-search placeholder="{e(t(lang,'输入姓名或关键词','Search names or keywords'))}"></label><p class="results-count" data-results aria-live="polite">{e(t(lang,'共 '+str(len(data))+' 条',str(len(data))+' records'))}</p></div><div class="table-wrap"><table><thead><tr>{heads}</tr></thead><tbody data-records>{''.join(trs)}</tbody></table></div><p class="empty-state" data-empty hidden>{e(t(lang,'没有找到匹配的记录。','No matching records found.'))}</p></section>'''
    return top+nav+table+base.closing(lang)

def publications(lang):
    top=hero(lang,'PUBLICATIONS','学术论文','Publications','浏览并检索 MIC 的论文记录。','Browse and search publication records from MIC.')
    years=sorted({p['year'] for p in DATA['papers']},reverse=True);opts=''.join(f'<option value="{e(y)}">{e(y)}</option>' for y in years)
    notice=e(DATA['publication_notice'])
    return top+f'''<section class="section shell">{section_head(lang,'PUBLICATIONS','论文列表','Publication list','可按年份或关键词筛选。','Filter by year or keyword.')}<p class="notice">{e(t(lang,'论文资料来自原站，发表状态及附件请以原出版方和课题组核实结果为准。','Publication status and resources should be checked with the publisher and the lab.'))}</p><p class="source-license">{notice}</p><div class="data-toolbar"><label class="field" for="paper-search">{e(t(lang,'关键词','Keyword'))}<input id="paper-search" type="search" data-search placeholder="{e(t(lang,'搜索作者、论文或期刊','Search authors, titles or venues'))}"></label><label class="field" for="paper-year">{e(t(lang,'年份','Year'))}<select id="paper-year" data-year><option value="">{e(t(lang,'全部年份','All years'))}</option>{opts}</select></label><p class="results-count" data-results aria-live="polite">{e(t(lang,'共 '+str(len(DATA['papers']))+' 条',str(len(DATA['papers']))+' records'))}</p></div><div class="paper-list" data-records>{''.join(paper_card(lang,p) for p in DATA['papers'])}</div><p class="empty-state" data-empty hidden>{e(t(lang,'没有找到匹配的论文。','No matching publications found.'))}</p></section>'''+base.closing(lang)

def news_page(lang):
    top=hero(lang,'NEWS','动态与招生','News and admissions','实验室历史通知与招生信息。','Archived notices and admissions information.')
    cards=''.join(f'''<a class="news-card" href="news-{key}.html"><small>2022-11-06 · {e(t(lang,'历史通知','ARCHIVED NOTICE'))}</small><h3>{e(t(lang,zh,en))}</h3><p>{e(t(lang,'原站历史通知；当前招生要求请咨询实验室。','Archived notice; contact the lab for current admissions information.'))}</p></a>''' for key,zh,en in [('doctoral','MIC 实验室博士生招生说明','Doctoral admissions notice'),('masters','MIC 实验室硕士生招生说明','Master’s admissions notice')])
    return top+f'<section class="section shell">{section_head(lang,"ARCHIVE","历史通知","Archived notices")}<div class="news-grid">{cards}</div></section>'+base.closing(lang)

def news_detail(lang,key):
    zh='MIC 实验室博士生招生说明' if key=='doctoral' else 'MIC 实验室硕士生招生说明';en='Doctoral admissions notice' if key=='doctoral' else 'Master’s admissions notice'
    top=hero(lang,'ARCHIVED NOTICE',zh,en,'发布日期：2022-11-06','Published: 2022-11-06')
    note=t(lang,'这是 2022 年原站历史通知，不代表当前招生要求；请联系实验室确认最新信息。','This is an archived 2022 notice and does not establish current admissions requirements. Contact the lab for current information.')
    original=DATA['admissions'][key]['body']
    article=original if lang=='zh' else EN_NOTICES[key]+f'<details class="original-text"><summary>Original Chinese notice</summary>{original}</details>'
    return top+f'''<section class="section shell"><a class="text-link" href="news.html">{e(t(lang,'返回动态','Back to news'))}</a><p class="notice">{e(note)}</p><article class="legacy-article">{article}</article></section>'''+base.closing(lang)

def contact_page(lang):
    top=hero(lang,'CONTACT','联系我们','Contact','欢迎与 MIC 交流。','Get in touch with MIC.')
    labels=[('联系人','Contact','王瀚漓','Hanli Wang'),('邮箱','Email','hanliwang@tongji.edu.cn','hanliwang@tongji.edu.cn'),('办公室','Office','智信馆 424 室','Room 424'),('实验室','Laboratory','智信馆 425、219 室','Rooms 425 and 219'),('地址','Address','中国上海市嘉定区曹安公路 4800 号同济大学嘉定校区智信馆','Telecom Building, No. 4800 Cao’an Highway, Jiading District, Shanghai 201804, P. R. China')]
    fields=[]
    for zh,en,zhval,enval in labels:
        value=e(t(lang,zhval,enval))
        if en=='Email':value=f'<a href="mailto:hanliwang@tongji.edu.cn">{value}</a>'
        fields.append(f'<dt>{e(t(lang,zh,en))}</dt><dd>{value}</dd>')
    return top+f'''<section class="section shell"><div class="contact-grid"><div class="contact-card"><h2>{e(t(lang,'联系信息','Contact information'))}</h2><dl>{''.join(fields)}</dl></div>{slot(lang,'此处放置同济大学嘉定校区位置或地图','Place a map of Tongji University Jiading Campus here','map-slot')}</div></section>'''

def project_page(lang,project):
    title=project['title'];top=hero(lang,'PUBLICATION PROJECT',title,title,'原站项目资料','Project materials from the original site')
    notice=t(lang,'以下正文保留原站发布的英文资料。原站附件链接及插图状态请在迁移前复核。','The original English project description is retained below. Verify legacy downloads and illustrations before migration.')
    return top+f'''<section class="section shell"><a class="text-link" href="publications.html">{e(t(lang,'返回论文列表','Back to publications'))}</a><p class="notice">{e(notice)}</p><article class="legacy-article project-article">{project['body_'+lang]}</article></section>'''+base.closing(lang)

def build_language(lang):
    pages={
      'index.html':(t(lang,'首页','Home'),home(lang)),
      'research.html':(t(lang,'研究方向','Research'),research_page(lang)),
      'research-archive.html':(t(lang,'原站研究专题','Original research topics'),research_archive(lang)),
      'team.html':(t(lang,'团队','Team'),team_page(lang)),
      'faculty-wang.html':(t(lang,'王瀚漓','Hanli Wang'),faculty_detail(lang,'wang')),
      'faculty-ni.html':(t(lang,'倪张凯','Zhangkai Ni'),faculty_detail(lang,'ni')),
      'members.html':(t(lang,'团队成员','Members'),records(lang,'members','团队成员','Members',[('姓名','Name'),('学位','Degree'),('年级','Year'),('研究方向','Research interests')],'原站成员资料整理于 2026 年 11 月，名单可能随时间变化。','Member records were collected in November 2026 and may change over time.',True)),
      'alumni.html':(t(lang,'校友','Alumni'),records(lang,'alumni','校友','Alumni',[('姓名','Name'),('学位','Degree'),('时间','Period'),('历史去向','Recorded destination')],'所列去向为原站历史记录，可能已发生变化。','Destinations are historical records and may have changed.',True)),
      'courses.html':(t(lang,'课程信息','Courses'),records(lang,'courses','课程信息','Courses',[('学期','Term'),('课程号','Course no.'),('课程名','Course')],'以下为 2011–2021 年的历史课程记录，不代表当前开课安排。','These are historical records from 2011–2021, not a current course schedule.')),
      'publications.html':(t(lang,'学术论文','Publications'),publications(lang)),
      'news.html':(t(lang,'动态与招生','News and admissions'),news_page(lang)),
      'news-doctoral.html':(t(lang,'博士生招生历史通知','Doctoral admissions notice'),news_detail(lang,'doctoral')),
      'news-masters.html':(t(lang,'硕士生招生历史通知','Master’s admissions notice'),news_detail(lang,'masters')),
      'contact.html':(t(lang,'联系我们','Contact'),contact_page(lang))
    }
    for project in DATA['projects']:pages['project-'+project['id']+'.html']=(project['title'],project_page(lang,project))
    for page,(title,body) in pages.items():make_file(lang,page,title,body)
    print(lang,len(pages),'pages')

def write_legacy_redirects():
    for item in MANIFEST['legacy_routes']:
        original=urlsplit(item['source']).path.lstrip('/');dest=item['target']
        if not original or '..' in Path(original).parts:raise ValueError('Unsafe legacy path')
        path=OUT/original;path.parent.mkdir(parents=True,exist_ok=True)
        relative=posixpath.relpath(dest,start=posixpath.dirname(original) or '.')
        page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={e(relative)}"><meta name="viewport" content="width=device-width,initial-scale=1"><title>页面已迁移 | MIC</title></head><body><p>页面已迁移 / This page has moved: <a href="{e(relative)}">{e(relative)}</a></p></body></html>'''
        path.write_text(page,encoding='utf-8')
    print('legacy route fallback pages:',len(MANIFEST['legacy_routes']))

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'site.css').write_text((ROOT/'dist/site.css').read_text(encoding='utf-8')+'\n'+(HERE/'migration.css').read_text(encoding='utf-8'),encoding='utf-8')
    shutil.copy2(HERE/'site.js',OUT/'site.js')
    shutil.copytree(ROOT/'dist/assets',OUT/'assets',dirs_exist_ok=True)
    build_language('zh');build_language('en');write_legacy_redirects()

if __name__=='__main__':main()
