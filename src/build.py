#!/usr/bin/env python3
"""Generate the static bilingual MIC site. No runtime build tools are required."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'dist'

def t(lang, zh, en):
    return zh if lang == 'zh' else en

def e(value):
    return escape(str(value), quote=True)

TOPICS = [
    {'id':'coding','zh':'图像视频压缩编码','en':'Image & Video Compression',
     'desc_zh':'探索图像与视频数据的高效表示、压缩编码与传输。','desc_en':'Exploring efficient representation, compression and transmission of image and video data.',
     'keys_zh':'图像编码 · 视频编码 · 数据压缩','keys_en':'Image coding · Video coding · Compression'},
    {'id':'optimization','zh':'智能调度与优化','en':'Intelligent Scheduling & Optimization',
     'desc_zh':'围绕复杂场景中的调度与优化问题，探索智能决策方法。','desc_en':'Exploring intelligent decision methods for scheduling and optimization in complex settings.',
     'keys_zh':'智能调度 · 优化方法 · 智能决策','keys_en':'Scheduling · Optimization · Decision making'},
    {'id':'embodied','zh':'具身智能','en':'Embodied Intelligence',
     'desc_zh':'探索智能体与环境交互中的感知、决策与行动。','desc_en':'Studying perception, decision making and action as agents interact with their environment.',
     'keys_zh':'环境感知 · 智能决策 · 交互行动','keys_en':'Perception · Decision making · Interaction'},
    {'id':'medical','zh':'医工交叉','en':'Medicine & Engineering',
     'desc_zh':'探索工程技术与医学需求的结合，关注医疗相关数据与智能方法。','desc_en':'Connecting engineering methods with medical needs, data and intelligent computing.',
     'keys_zh':'医工交叉 · 医学数据 · 智能方法','keys_en':'Medical engineering · Medical data · Intelligent methods'},
    {'id':'driving','zh':'自动驾驶','en':'Autonomous Driving',
     'desc_zh':'探索自动驾驶场景中的环境感知、场景理解与智能决策。','desc_en':'Exploring perception, scene understanding and intelligent decisions for autonomous driving.',
     'keys_zh':'环境感知 · 场景理解 · 智能决策','keys_en':'Perception · Scene understanding · Decision making'}
]
TEACHERS = [
    {'name':'王瀚漓','en':'Hanli Wang','role_zh':'长聘教授 · 博士生导师','role_en':'Tenured Professor · Doctoral Supervisor',
     'bio_zh':'主要从事多媒体信息处理、计算机视觉和机器学习等方面的研究。','bio_en':'Research interests include multimedia signal processing, computer vision and machine learning.'},
    {'name':'倪张凯','en':'Zhangkai Ni','role_zh':'副教授 · 硕士生导师','role_en':'Associate Professor · Master’s Supervisor',
     'bio_zh':'主要研究领域包括感知图像处理、计算机视觉和计算摄影。','bio_en':'Research interests include perceptual image processing, computer vision and computational photography.'},
    {'name':'杜杉杉','en':'','role_zh':'','role_en':'','bio_zh':'','bio_en':''},
    {'name':'吴秀哲','en':'','role_zh':'','role_en':'','bio_zh':'','bio_en':''}
]
NAV = [('index.html','首页','Home'),('research.html','研究方向','Research'),('team.html','团队','Team'),('publications.html','学术论文','Publications'),('courses.html','课程信息','Courses'),('news.html','动态','News'),('contact.html','联系我们','Contact')]

def slot(lang, zh, en, cls=''):
    return f'<div class="image-slot {e(cls)}"><strong>{e(t(lang,zh,en))}</strong><small>{e(t(lang,"图片待提供","Image to be provided"))}</small></div>'

def emblems(lang):
    prefix = '' if lang == 'zh' else '../'
    return f'<span class="brand-emblems"><img class="emblem" src="{prefix}assets/logo_tongji.png" alt="{e(t(lang,"同济大学校标","Tongji University emblem"))}" width="44" height="44"><img class="emblem" src="{prefix}assets/logo_mic.png" alt="{e(t(lang,"MIC 实验室徽章","MIC laboratory emblem"))}" width="44" height="44"></span>'

def header(lang, page):
    active = 'team.html' if page in ('members.html','alumni.html') else page
    parts=[]
    for path,zh,en in NAV:
        current=' aria-current="page"' if active==path else ''
        label=e(t(lang,zh,en))
        if path=='team.html':
            parts.append(f'<div class="team-nav"><a href="team.html"{current}>{label}</a><button class="team-toggle" type="button" data-team-toggle aria-expanded="false" aria-controls="team-submenu" aria-label="{e(t(lang,"展开团队子菜单","Open team submenu"))}">⌄</button><div class="team-submenu" id="team-submenu" hidden><a href="members.html">{e(t(lang,"成员","Members"))}</a><a href="alumni.html">{e(t(lang,"校友","Alumni"))}</a></div></div>')
        else:
            parts.append(f'<a href="{path}"{current}>{label}</a>')
    switch=('en/'+page) if lang=='zh' else ('../'+page)
    switch_label='EN' if lang=='zh' else '中文'
    links=''.join(parts)+f'<a class="language" href="{switch}" lang="{"en" if lang=="zh" else "zh-CN"}">{switch_label}</a>'
    mobile=[]
    for path,zh,en in NAV:
        current=' aria-current="page"' if active==path else ''
        mobile.append(f'<a href="{path}"{current}>{e(t(lang,zh,en))}</a>')
        if path=='team.html': mobile.extend([f'<a href="members.html">{e(t(lang,"团队成员","Members"))}</a>',f'<a href="alumni.html">{e(t(lang,"校友","Alumni"))}</a>'])
    mobile.append(f'<a href="{switch}" lang="{"en" if lang=="zh" else "zh-CN"}">{switch_label}</a>')
    return f'''<header class="site-header"><div class="shell header-row"><a class="brand" href="index.html" aria-label="{e(t(lang,'MIC 首页','MIC home'))}">{emblems(lang)}<span class="brand-text">{e(t(lang,'多媒体与智能计算实验室','Multimedia & Intelligent Computing Lab'))}<small>{e(t(lang,'Multimedia & Intelligent Computing Lab','Tongji University'))}</small></span></a><nav class="desktop-nav" aria-label="{e(t(lang,'主导航','Main navigation'))}">{links}</nav><button class="menu-toggle" type="button" data-menu-toggle aria-expanded="false" aria-controls="mobile-menu">{e(t(lang,'菜单','Menu'))} ☰</button></div><nav class="shell mobile-nav" id="mobile-menu" aria-label="{e(t(lang,'手机导航','Mobile navigation'))}" hidden>{''.join(mobile)}</nav></header>'''

def footer(lang):
    items=[('research.html','研究方向','Research'),('team.html','教师团队','Faculty'),('members.html','成员','Members'),('alumni.html','校友','Alumni'),('publications.html','学术论文','Publications'),('courses.html','课程信息','Courses'),('news.html','动态','News'),('contact.html','联系我们','Contact')]
    links=''.join(f'<a href="{path}">{e(t(lang,zh,en))}</a>' for path,zh,en in items)
    return f'''<footer class="footer shell"><div><div class="footer-brand">{emblems(lang)}<strong>MIC<span>.</span></strong></div><p>{e(t(lang,'多媒体与智能计算实验室','Multimedia and Intelligent Computing Lab'))}<br>{e(t(lang,'同济大学 · 中国上海','Tongji University · Shanghai, China'))}</p></div><div><h3>{e(t(lang,'探索','EXPLORE'))}</h3><div class="footer-links">{links}</div></div><div><h3>{e(t(lang,'联系','CONTACT'))}</h3><div class="footer-links"><a href="mailto:hanliwang@tongji.edu.cn">hanliwang@tongji.edu.cn</a></div><p>{e(t(lang,'上海市嘉定区曹安公路 4800 号','4800 Cao’an Highway, Jiading, Shanghai'))}</p></div></footer>'''

def section_head(lang, eyebrow, zh, en, sub_zh='', sub_en='', link='', link_zh='', link_en=''):
    sub=f'<p>{e(t(lang,sub_zh,sub_en))}</p>' if sub_zh else ''
    action=f'<a class="text-link" href="{e(link)}">{e(t(lang,link_zh,link_en))} <span aria-hidden="true">↗</span></a>' if link else ''
    return f'<div class="section-head"><div><p class="eyebrow">{e(eyebrow)}</p><h2><span>{e(t(lang,zh,en))}</span></h2>{sub}</div>{action}</div>'

def page_hero(lang, eyebrow, zh, en, sub_zh, sub_en):
    return f'<section class="page-hero"><div class="shell"><p class="eyebrow">{e(eyebrow)}</p><h1>{e(t(lang,zh,en))}</h1><p>{e(t(lang,sub_zh,sub_en))}</p></div></section>'

def subnav(lang, active):
    options=[('team.html','教师团队','Faculty'),('members.html','团队成员','Members'),('alumni.html','校友','Alumni')]
    return '<nav class="shell subnav" aria-label="'+e(t(lang,'团队导航','Team navigation'))+'">'+''.join(f'<a href="{path}"'+(' aria-current="page"' if path==active else '')+'>'+e(t(lang,zh,en))+'</a>' for path,zh,en in options)+'</nav>'

def document(lang, page, body, data=None):
    prefix='' if lang=='zh' else '../'
    title=next((t(lang,zh,en) for path,zh,en in NAV if path==page), t(lang,'团队成员','Members') if page=='members.html' else t(lang,'校友','Alumni'))
    data_tag=f'<script defer src="{prefix}data/{data}.js"></script>' if data else ''
    return f'''<!doctype html><html lang="{'zh-CN' if lang=='zh' else 'en'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#ffffff"><title>{e(title)} | MIC · Tongji University</title><link rel="stylesheet" href="{prefix}site.css">{data_tag}<script defer src="{prefix}site.js"></script></head><body data-page="{e(page.removesuffix('.html'))}"><a class="skip" href="#main">{e(t(lang,'跳至主要内容','Skip to content'))}</a>{header(lang,page)}<main id="main">{body}</main>{footer(lang)}</body></html>'''

def person_cards(lang, directory=False):
    result=[]
    for person in TEACHERS:
        name=person['name'] if lang=='zh' or not person['en'] else person['en']
        other=person['en'] if lang=='zh' else (person['name'] if person['en'] else '')
        role=person['role_'+lang]; bio=person['bio_'+lang]
        picture=slot(lang,'此处放置'+person['name']+'老师照片','Place a portrait of '+(person['en'] or person['name'])+' here')
        heading=f'<h3>{e(name)}'+(f'<small>{e(other)}</small>' if other else '')+'</h3>'
        details=(f'<p class="role">{e(role)}</p>' if role else '')+(f'<p class="bio">{e(bio)}</p>' if bio else '')
        result.append(f'<article class="person-card">{picture}<div>{heading}{details}</div></article>')
    return ''.join(result)

def carousel(lang):
    buttons=''.join(f'<button type="button" data-topic="{i}" aria-pressed="{"true" if i==0 else "false"}">{e(topic[lang])}</button>' for i,topic in enumerate(TOPICS))
    slides=[]
    for i,topic in enumerate(TOPICS):
        hidden='' if i==0 else ' hidden'
        picture=slot(lang,'此处放置'+topic['zh']+'研究示意图','Place an image for '+topic['en']+' here')
        slides.append(f'<article class="topic-slide" data-slide="{i}"{hidden}>{picture}<div class="topic-copy"><p class="index-line">{i+1:02d} / 05 &nbsp; {e(topic["en"])}</p><h3>{e(topic[lang])}</h3><p>{e(topic["desc_"+lang])}</p><a class="text-link" href="research.html#{topic["id"]}">{e(t(lang,"了解这个方向","Explore this area"))} <span aria-hidden="true">↗</span></a></div></article>')
    return f'''<div data-carousel><div class="topic-pills" aria-label="{e(t(lang,'选择研究方向','Choose a research area'))}">{buttons}</div><div>{''.join(slides)}</div><div class="carousel-bottom"><p>{e(t(lang,'探索 MIC 的五个研究方向。','Explore five areas of research at MIC.'))}</p><div class="carousel-controls"><span data-count>01 / 05</span><button type="button" data-previous aria-label="{e(t(lang,'上一个研究方向','Previous research area'))}">←</button><button type="button" data-next aria-label="{e(t(lang,'下一个研究方向','Next research area'))}">→</button></div><span class="sr-only" data-status aria-live="polite"></span></div></div>'''

def home(lang):
    hero=f'''<section class="home-hero"><div class="shell"><div class="home-hero-copy"><p class="eyebrow">MULTIMEDIA &amp; INTELLIGENT COMPUTING</p><h1>{e(t(lang,'多媒体与智能计算实验室','Multimedia & Intelligent Computing Lab'))}</h1><p class="university">TONGJI UNIVERSITY · SHANGHAI</p><p class="lead">{e(t(lang,'从图像视频编码与智能优化，到具身智能、医工交叉与自动驾驶。','From image and video coding and intelligent optimization to embodied intelligence, medical engineering and autonomous driving.'))}</p><div class="hero-actions"><a class="button primary" href="research.html">{e(t(lang,'研究方向','Our research'))} <span aria-hidden="true">↗</span></a><a class="button secondary" href="team.html">{e(t(lang,'认识团队','Meet the team'))} <span aria-hidden="true">↗</span></a></div></div>{slot(lang,'此处放置实验室环境或团队合影横幅','Place a lab or team banner image here','hero-slot')}</div></section>'''
    about=f'''<section class="section shell">{section_head(lang,'ABOUT MIC','关于我们','About us',link='team.html',link_zh='认识团队',link_en='Meet the team')}<div class="about-grid"><div class="body-copy"><p>{e(t(lang,'同济大学多媒体与智能计算实验室（MIC）围绕多媒体信息计算与智能系统开展研究。','The Multimedia and Intelligent Computing Lab (MIC) at Tongji University studies multimedia information computing and intelligent systems.'))}</p><p>{e(t(lang,'我们关注视觉数据的高效表示和复杂问题的智能优化，探索计算技术与多领域的结合。','We explore efficient representations of visual data, intelligent optimization and the connections between computing and other fields.'))}</p></div><div class="facts"><div class="fact"><strong>{e(t(lang,'研究','RESEARCH'))}</strong><p>{e(t(lang,'五个研究方向','Five research areas'))}</p></div><div class="fact"><strong>{e(t(lang,'团队','PEOPLE'))}</strong><p>{e(t(lang,'教师、成员与校友','Faculty, members and alumni'))}</p></div><div class="fact"><strong>{e(t(lang,'位置','LOCATION'))}</strong><p>{e(t(lang,'同济大学嘉定校区','Tongji University, Jiading Campus'))}</p></div><div class="fact"><strong>{e(t(lang,'交流','CONTACT'))}</strong><p>hanliwang@tongji.edu.cn</p></div></div></div></section>'''
    research=f'''<section class="section alt"><div class="shell">{section_head(lang,'RESEARCH','研究方向','Research areas','从多媒体编码到交叉应用。','From multimedia coding to interdisciplinary applications.','research.html','全部研究方向','All research areas')}{carousel(lang)}</div></section>'''
    people=f'''<section class="section shell">{section_head(lang,'PEOPLE','教师团队','Our faculty','认识 MIC 的教师。','Meet the faculty at MIC.','team.html','查看团队','Meet the team')}<div class="person-grid">{person_cards(lang)}</div></section>'''
    selected=[
      ('2026','Shanshan Du and Hanli Wang, Visual Dialog with Semantic Consistency: an External Knowledge-driven Approach, Neural Networks, vol. 197, Article 108523, May 2026.'),
      ('2026','Zhangkai Ni, Menglin Han, Wenhan Yang, Hanli Wang, Lin Ma, and Sam Kwong, Contrastive Mean Teacher for Robust Low-Light Image Enhancement, International Journal of Computer Vision, vol. 134, Article 346, Jul. 2026.'),
      ('2025','Peiqi Yang, Zhangkai Ni, Hanli Wang, Wenhan Yang, Shiqi Wang, and Sam Kwong, Shell-Guided Compression of Voxel Radiance Fields, IEEE Transactions on Image Processing, vol. 34, pp. 1179-1191, 2025.')]
    cards=''.join(f'<article class="paper-card"><span class="year">{year}</span><p>{e(text)}</p></article>' for year,text in selected)
    papers=f'''<section class="section alt"><div class="shell">{section_head(lang,'PUBLICATIONS','学术论文','Selected publications','探索团队的研究成果。','Explore work from the lab.','publications.html','查看论文','All publications')}<div class="paper-list">{cards}</div></div></section>'''
    news_cards=f'''<div class="news-grid"><a class="news-card" href="news.html#doctoral"><small>2022-11-06 · {e(t(lang,'历史通知','ARCHIVED NOTICE'))}</small><h3>{e(t(lang,'MIC 实验室博士生招生说明','Doctoral admissions notice'))}</h3><p>{e(t(lang,'历史通知；最新招生信息请联系实验室。','Archived notice; contact the lab for current information.'))}</p></a><a class="news-card" href="news.html#masters"><small>2022-11-06 · {e(t(lang,'历史通知','ARCHIVED NOTICE'))}</small><h3>{e(t(lang,'MIC 实验室硕士生招生说明','Master’s admissions notice'))}</h3><p>{e(t(lang,'历史通知；最新招生信息请联系实验室。','Archived notice; contact the lab for current information.'))}</p></a></div>'''
    news=f'''<section class="section shell">{section_head(lang,'NEWS','动态','News',link='news.html',link_zh='查看动态',link_en='All news')}{news_cards}</section>'''
    return hero+about+research+people+papers+news+closing(lang)

def closing(lang):
    return f'''<section class="closing"><div class="shell closing-inner"><div><p class="eyebrow">TONGJI UNIVERSITY · MIC</p><h2>{e(t(lang,'与我们联系','Get in touch'))}</h2><p>{e(t(lang,'了解研究、团队与实验室信息。','Learn more about the research and people at MIC.'))}</p></div><a class="button primary" href="contact.html">{e(t(lang,'联系我们','Contact us'))} <span aria-hidden="true">↗</span></a></div></section>'''

def research(lang):
    hero=page_hero(lang,'RESEARCH','研究方向','Research areas','从多媒体编码到交叉应用，探索 MIC 的五个研究方向。','Explore five research areas, from multimedia coding to interdisciplinary applications.')
    pills='<div class="topic-pills">'+''.join(f'<a href="#{topic["id"]}">{e(topic[lang])}</a>' for topic in TOPICS)+'</div>'
    cards=[]
    for i,topic in enumerate(TOPICS):
        picture=slot(lang,'此处放置'+topic['zh']+'研究示意图','Place an image for '+topic['en']+' here')
        cards.append(f'''<article class="research-row" id="{topic['id']}">{picture}<div class="body-copy"><p class="index-line">{i+1:02d} / 05 &nbsp; {e(topic['en'])}</p><h2>{e(topic[lang])}</h2><p>{e(topic['desc_'+lang])}</p><p class="keywords">{e(topic['keys_'+lang])}</p></div></article>''')
    return hero+f'<section class="section shell">{pills}<div class="research-list">{"".join(cards)}</div></section>'+closing(lang)

def team(lang):
    hero=page_hero(lang,'PEOPLE','团队','Our team','认识 MIC 的教师、成员与校友。','Meet the faculty, members and alumni of MIC.')
    return hero+subnav(lang,'team.html')+f'''<section class="section shell">{section_head(lang,'FACULTY','教师团队','Faculty','研究背后，是对问题保持好奇的人。','The people behind the research.')}<div class="person-grid directory-grid">{person_cards(lang,True)}</div></section>'''+closing(lang)

def table_page(lang, page, data, title_zh, title_en, sub_zh, sub_en, columns, notice_zh, notice_en, with_team_nav=False):
    hero=page_hero(lang, data.upper(), title_zh, title_en, sub_zh, sub_en)
    nav=subnav(lang,page) if with_team_nav else ''
    heads=''.join(f'<th scope="col">{e(t(lang,zh,en))}</th>' for zh,en in columns)
    label=e(t(lang,'搜索','Search'))
    notice=f'<p class="notice">{e(t(lang,notice_zh,notice_en))}</p>' if notice_zh else ''
    content=f'''<section class="section shell"><div class="section-head"><div><p class="eyebrow">{e(data.upper())}</p><h2><span>{e(t(lang,title_zh,title_en))}</span></h2></div></div>{notice}<div class="data-toolbar"><label class="field" for="record-search">{label}<input id="record-search" type="search" data-search placeholder="{e(t(lang,'输入姓名或关键词','Search names or keywords'))}"></label><p class="results-count" data-results aria-live="polite"></p></div><div class="table-wrap"><table><thead><tr>{heads}</tr></thead><tbody data-records><tr><td colspan="{len(columns)}">{e(t(lang,'正在加载资料…','Loading records…'))}</td></tr></tbody></table></div><p class="empty-state" data-empty hidden>{e(t(lang,'没有找到匹配的记录。','No matching records found.'))}</p><noscript><p class="notice">{e(t(lang,'请启用 JavaScript 以查看和搜索资料。','Enable JavaScript to view and search these records.'))}</p></noscript></section>'''
    return hero+nav+content+closing(lang)

def publications(lang):
    hero=page_hero(lang,'PUBLICATIONS','学术论文','Publications','浏览并检索 MIC 的论文记录。','Browse and search publication records from MIC.')
    return hero+f'''<section class="section shell">{section_head(lang,'PUBLICATIONS','论文列表','Publication list','可按年份或关键词筛选。','Filter by year or keyword.')}<div class="data-toolbar"><label class="field" for="paper-search">{e(t(lang,'关键词','Keyword'))}<input id="paper-search" type="search" data-search placeholder="{e(t(lang,'搜索作者、论文或期刊','Search authors, titles or venues'))}"></label><label class="field" for="paper-year">{e(t(lang,'年份','Year'))}<select id="paper-year" data-year><option value="">{e(t(lang,'全部年份','All years'))}</option></select></label><p class="results-count" data-results aria-live="polite"></p></div><div class="paper-list" data-records><p class="empty-state">{e(t(lang,'正在加载论文…','Loading publications…'))}</p></div><p class="empty-state" data-empty hidden>{e(t(lang,'没有找到匹配的论文。','No matching publications found.'))}</p><noscript><p class="notice">{e(t(lang,'请启用 JavaScript 以查看和搜索论文。','Enable JavaScript to view and search publications.'))}</p></noscript></section>'''+closing(lang)

def news(lang):
    hero=page_hero(lang,'NEWS','动态','News','实验室通知与信息。','Updates and notices from the lab.')
    a=t(lang,'MIC 实验室博士生招生说明','Doctoral admissions notice')
    b=t(lang,'MIC 实验室硕士生招生说明','Master’s admissions notice')
    note=t(lang,'本通知发布于 2022 年。最新招生信息请联系实验室。','This notice was published in 2022. Please contact the lab for current admissions information.')
    return hero+f'''<section class="section shell">{section_head(lang,'ARCHIVE','历史通知','Archived notices')}<div class="news-grid"><article class="news-card" id="doctoral"><small>2022-11-06</small><h3>{e(a)}</h3><p>{e(note)}</p><a class="text-link" href="contact.html">{e(t(lang,'联系实验室','Contact the lab'))} ↗</a></article><article class="news-card" id="masters"><small>2022-11-06</small><h3>{e(b)}</h3><p>{e(note)}</p><a class="text-link" href="contact.html">{e(t(lang,'联系实验室','Contact the lab'))} ↗</a></article></div></section>'''

def contact(lang):
    hero=page_hero(lang,'CONTACT','联系我们','Contact','欢迎与 MIC 交流。','Get in touch with MIC.')
    labels=[('联系人','CONTACT','王瀚漓','Hanli Wang'),('邮箱','EMAIL','hanliwang@tongji.edu.cn','hanliwang@tongji.edu.cn'),('办公室','OFFICE','智信馆 424 室','Room 424, Zhixin Building'),('实验室','LABORATORY','智信馆 425、219 室','Rooms 425 and 219, Zhixin Building'),('地址','ADDRESS','中国上海市嘉定区曹安公路 4800 号同济大学嘉定校区智信馆','Zhixin Building, Tongji University Jiading Campus, 4800 Cao’an Highway, Shanghai, China')]
    fields=[]
    for zh,en,value_zh,value_en in labels:
        value=e(t(lang,value_zh,value_en))
        if en=='EMAIL': value=f'<a href="mailto:hanliwang@tongji.edu.cn">{value}</a>'
        fields.append(f'<dt>{e(t(lang,zh,en))}</dt><dd>{value}</dd>')
    return hero+f'''<section class="section shell"><div class="contact-grid"><div class="contact-card"><h2>{e(t(lang,'联系信息','Contact information'))}</h2><dl>{''.join(fields)}</dl></div>{slot(lang,'此处放置同济大学嘉定校区位置或地图','Place a map of Tongji University Jiading Campus here','map-slot')}</div></section>'''

def make_pages(lang):
    pages={
      'index.html':(home(lang),None),
      'research.html':(research(lang),None),
      'team.html':(team(lang),None),
      'members.html':(table_page(lang,'members.html','members','团队成员','Members','认识实验室成员。','Meet the members of the lab.',[('姓名','Name'),('学位','Degree'),('年级','Year'),('研究方向','Research interests')],'成员资料整理于 2026 年 11 月，名单与研究方向可能随时间变化。','Member records were collected in November 2026 and may change over time.',True),'members'),
      'alumni.html':(table_page(lang,'alumni.html','alumni','校友','Alumni','认识曾在 MIC 学习与研究的校友。','Meet alumni who studied and worked at MIC.',[('姓名','Name'),('学位','Degree'),('时间','Period'),('历史去向','Recorded destination')],'所列去向为历史记录，可能已发生变化。','Destinations are historical records and may have changed.',True),'alumni'),
      'publications.html':(publications(lang),'papers'),
      'courses.html':(table_page(lang,'courses.html','courses','课程信息','Courses','实验室相关课程的历史记录。','Historical records of courses associated with the lab.',[('学期','Term'),('课程号','Course no.'),('课程名','Course')],'以下为 2011–2021 年的历史课程记录，不代表当前开课安排。','These are historical records from 2011–2021, not a current course schedule.'),'courses'),
      'news.html':(news(lang),None),
      'contact.html':(contact(lang),None)
    }
    directory=OUT if lang=='zh' else OUT/'en'
    directory.mkdir(parents=True,exist_ok=True)
    for page,(body,data) in pages.items():
        (directory/page).write_text(document(lang,page,body,data),encoding='utf-8')
    print(lang, len(pages), 'pages generated')

if __name__=='__main__':
    make_pages('zh')
    make_pages('en')
