#!/usr/bin/env python3
"""Build two additional bilingual MIC concepts from the shared, sourced content."""
from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('mic_base', ROOT / 'src/build.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
original_document, original_research, original_team = base.document, base.research, base.team
t, e, slot = base.t, base.e, base.slot
raw = (ROOT / 'dist/data/papers.js').read_text(encoding='utf-8').split('window.MIC_DATA.papers=',1)[1].strip().removesuffix(';')
papers = [p for p in json.loads(raw) if p['year'] in ('2025','2026')][:2]

def paper_highlights(lang):
    cards=''.join('<article class="paper-card"><span class="year">'+e(p['year'])+'</span><p>'+e(p['citation'])+'</p></article>' for p in papers)
    return '<div class="paper-list">'+cards+'</div>'

def hero_journal(lang):
    return f'''<section class="journal-hero shell"><div class="journal-topline"><span>TONGJI UNIVERSITY / SHANGHAI</span><span>MIC LABORATORY</span></div><div class="journal-hero-grid"><div class="journal-hero-copy"><p class="eyebrow">MULTIMEDIA &amp; INTELLIGENT COMPUTING</p><h1>{t(lang,'多媒体与<br>智能计算<span>实验室</span>','Multimedia<br>&amp; Intelligent<span>Computing Lab</span>')}</h1><p class="journal-intro">{e(t(lang,'在多媒体信息处理与智能系统的交汇处，探索计算与现实世界的连接。','Exploring connections between computing and the world through multimedia and intelligent systems.'))}</p><div class="journal-actions"><a class="button primary" href="research.html">{e(t(lang,'探索研究方向','Explore our research'))} ↗</a><a class="text-link" href="team.html">{e(t(lang,'认识团队','Meet the team'))} ↗</a></div></div>{slot(lang,'此处放置实验室环境或团队合影','Place a laboratory or team image here','journal-image')}</div><div class="journal-bottomline"><span>RESEARCH / PEOPLE / PUBLICATIONS</span><span>{e(t(lang,'同济大学 · 嘉定校区','TONGJI UNIVERSITY · JIADING'))}</span></div></section>'''

def journal_home(lang):
    links=''.join(f'''<a class="journal-topic" href="research.html#{x['id']}"><span class="journal-number">{i+1:02d}</span><span><strong>{e(x[lang])}</strong><small>{e(x['en'] if lang=='zh' else x['keys_en'])}</small></span><span class="journal-arrow" aria-hidden="true">↗</span></a>''' for i,x in enumerate(base.TOPICS))
    return hero_journal(lang)+f'''<section class="section shell journal-research"><div class="journal-section-grid"><div><p class="eyebrow">01 / RESEARCH</p><h2>{e(t(lang,'研究方向','Research areas'))}</h2><p>{e(t(lang,'五个方向，共同探索信息与智能。','Five areas, exploring information and intelligence.'))}</p><a class="text-link" href="research.html">{e(t(lang,'全部研究方向','Explore all areas'))} ↗</a></div><div class="journal-topic-list">{links}</div></div></section><section class="section journal-people"><div class="shell">{base.section_head(lang,'02 / PEOPLE','教师团队','Our faculty','认识 MIC 的教师。','Meet the faculty at MIC.','team.html','查看团队','Meet the team')}<div class="person-grid">{base.person_cards(lang)}</div></div></section><section class="section shell journal-papers">{base.section_head(lang,'03 / PUBLICATIONS','学术论文','Publications','探索团队已有的论文记录。','Explore publication records from the lab.','publications.html','浏览论文','Browse publications')}{paper_highlights(lang)}</section>{base.closing(lang)}'''

def journal_research(lang):
    nav=''.join(f'<a href="#{x["id"]}" data-research-link><span>{i+1:02d}</span>{e(x[lang])}<b aria-hidden="true">↗</b></a>' for i,x in enumerate(base.TOPICS))
    panels=[]
    for i,x in enumerate(base.TOPICS):
        panels.append(f'''<article class="journal-panel" id="{x['id']}" data-research-panel><p class="index-line">RESEARCH AREA &nbsp; {i+1:02d} / 05</p><h2>{e(x[lang])}</h2><p class="journal-panel-desc">{e(x['desc_'+lang])}</p><p class="journal-keywords">{e(x['keys_'+lang])}</p>{slot(lang,'此处放置'+x['zh']+'研究示意图','Place an image for '+x['en']+' here')}</article>''')
    return base.page_hero(lang,'RESEARCH INDEX','研究方向','Research areas','从多媒体编码到交叉应用，探索 MIC 的五个研究方向。','Explore five research areas at MIC.')+f'''<section class="section shell"><div class="journal-explorer"><nav class="journal-research-nav" aria-label="{e(t(lang,'选择研究方向','Select a research area'))}"><p class="eyebrow">{e(t(lang,'研究索引','RESEARCH INDEX'))}</p>{nav}</nav><div class="journal-panels">{''.join(panels)}</div></div></section>'''+base.closing(lang)

def portal_home(lang):
    cards=''.join(f'''<a class="portal-topic" href="research.html#{x['id']}"><span class="portal-topic-number">{i+1:02d} / RESEARCH</span><h3>{e(x[lang])}</h3><p>{e(x['desc_'+lang])}</p><span class="portal-topic-link">{e(t(lang,'了解方向','Explore area'))} ↗</span></a>''' for i,x in enumerate(base.TOPICS))
    hero=f'''<section class="portal-hero"><div class="shell portal-hero-grid"><div class="portal-hero-copy"><p class="eyebrow">TONGJI UNIVERSITY / MIC LAB</p><h1>{t(lang,'让计算<br><span>连接更多可能</span>','Computing for<br><span>new possibilities</span>')}</h1><p class="portal-lab-name">{e(t(lang,'同济大学多媒体与智能计算实验室','Multimedia & Intelligent Computing Lab, Tongji University'))}</p><p class="portal-hero-desc">{e(t(lang,'探索多媒体、智能优化与交叉领域的研究。','Research in multimedia, intelligent optimization and interdisciplinary applications.'))}</p><div class="portal-actions"><a class="button primary" href="research.html">{e(t(lang,'探索研究','Explore research'))} ↗</a><a class="button secondary" href="team.html">{e(t(lang,'了解团队','Meet the team'))} ↗</a></div></div>{slot(lang,'此处放置实验室环境或团队合影','Place a laboratory or team image here','portal-hero-image')}</div></section>'''
    return hero+f'''<section class="portal-strip"><div class="shell portal-strip-inner"><div><strong>05</strong><span>{e(t(lang,'研究方向','RESEARCH AREAS'))}</span></div><div><strong>04</strong><span>{e(t(lang,'教师','FACULTY'))}</span></div><div><strong>MIC</strong><span>{e(t(lang,'同济大学 · 嘉定校区','TONGJI · JIADING'))}</span></div></div></section><section class="section shell portal-research">{base.section_head(lang,'OUR RESEARCH','从问题出发','Research areas','了解 MIC 的五个研究方向。','Explore the five areas of research at MIC.','research.html','查看全部','View all')}<div class="portal-topics">{cards}</div></section><section class="section portal-people"><div class="shell">{base.section_head(lang,'OUR PEOPLE','与团队相遇','Meet the team','认识 MIC 的教师、成员与校友。','Meet the faculty, members and alumni at MIC.','team.html','浏览团队','Explore team')}<div class="person-grid">{base.person_cards(lang)}</div></div></section><section class="section shell portal-papers">{base.section_head(lang,'PUBLICATIONS','研究成果','Publications','按年份或关键词浏览论文记录。','Browse publication records by year or keyword.','publications.html','浏览与收藏论文','Browse publications')}{paper_highlights(lang)}</section>{base.closing(lang)}'''

def make_document(style):
    def document(lang,page,body,data=None):
        html=original_document(lang,page,body,data)
        old='' if lang=='zh' else '../'
        shared='../../' if lang=='zh' else '../../../'
        theme='' if lang=='zh' else '../'
        html=html.replace(f'href="{old}site.css"',f'href="{shared}site.css"')
        html=html.replace(f'src="{old}site.js"',f'src="{shared}site.js"')
        html=html.replace(f'src="{old}data/',f'src="{shared}data/')
        html=html.replace('</head>',f'<link rel="stylesheet" href="{theme}theme.css"><script defer src="{theme}variant.js"></script></head>')
        html=html.replace('<body data-page=',f'<body class="concept-{style}" data-page=')
        return html
    return document

for style in ('journal','portal'):
    base.OUT=ROOT/'dist/concepts'/style
    base.document=make_document(style)
    base.home=journal_home if style=='journal' else portal_home
    base.research=journal_research if style=='journal' else original_research
    base.team=original_team
    base.make_pages('zh')
    base.make_pages('en')
