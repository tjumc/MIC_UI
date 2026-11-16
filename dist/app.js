const areas = [
  { title: '信息编码', en: 'Information Coding', short: '高效表示视觉信息，为存储、传输和智能分析提供基础。', desc: '研究如何减少视觉信号中的冗余，以更高效的方式存储和传输数据，并为视觉分析与处理提供数据表示。', tags: ['信息编码'] },
  { title: '视觉理解', en: 'Visual Understanding', short: '从图像与视频中理解内容，并建立视觉与语言的联系。', desc: '关注图像、视频与文本之间的语义关联，以及对视觉内容的检索、描述和行为识别。', tags: ['自然语言片段检索', '跨模态检索', '图像描述', '视频描述', '视频段落描述', '视觉故事叙述', '行为检测'] },
  { title: '视觉推理', en: 'Visual Reasoning', short: '结合视觉和语言信息，研究问答、对话与常识推理。', desc: '结合图像与语言中的信息，探索回答问题、开展多轮对话以及给出推理依据的方法。', tags: ['视觉问答', '视觉对话', '视觉常识推理'] },
  { title: '图像处理', en: 'Image Processing', short: '改善图像质量，并研究图像质量的评估。', desc: '围绕图像修复、图像增强与图像质量评估，研究视觉数据的质量和处理。', tags: ['图像修复', '图像增强', '图像质量评估'] }
];
const people = [
  { name: '王瀚漓', en: 'HANLI WANG', title: '长聘教授 · 博士生导师', bio: '同济大学长聘教授，博士生导师。主要从事多媒体信息处理、计算机视觉和机器学习等方面的研究。', interests: ['多媒体信息处理', '计算机视觉', '机器学习'], img: 'https://mic.tongji.edu.cn/_upload/article/images/6a/b6/0a8b22404e289d8a148b3bff3ca9/bd646cd4-835d-4220-ba50-23d7a2be890c.jpg', url: 'https://mic.tongji.edu.cn/gdxx/list.htm', initial:'W' },
  { name: '倪张凯', en: 'ZHANGKAI NI', title: '副教授 · 硕士生导师', bio: '同济大学副教授，硕士生导师。主要研究领域包括感知图像处理、计算机视觉和计算摄影。', interests: ['感知图像处理', '计算机视觉', '计算摄影'], img: 'https://mic.tongji.edu.cn/_upload/article/images/6a/b6/0a8b22404e289d8a148b3bff3ca9/ce958c37-fcc9-45d9-968e-7bb2fa10b85e.jpg', url: 'https://eezkni.github.io/', initial:'N' }
];
const num = n => String(n + 1).padStart(2, '0');
const tagList = (tags, cls='tags') => `<div class="${cls}">${tags.map(t=>`<span>${t}</span>`).join('')}</div>`;
const portrait = p => `<div class="portrait"><span aria-hidden="true">${p.initial}</span><img src="${p.img}" alt="${p.name}教师照片" loading="lazy" onerror="this.hidden=true"></div>`;
const peopleMarkup = (variant) => people.map((p,i) => {
  if (variant === 'a') return `<article class="a-person">${portrait(p)}<div class="a-person-copy"><p class="person-index">FACULTY / ${num(i)}</p><h3>${p.name}<span>${p.en}</span></h3><p class="person-title">${p.title}</p><p class="person-bio">${p.bio}</p>${tagList(p.interests)}<a href="${p.url}">了解更多 <span>↗</span></a></div></article>`;
  if (variant === 'b') return `<article class="b-person"><div class="b-person-top"><span>FACULTY / ${num(i)}</span><span>MIC LAB</span></div><div class="b-person-body">${portrait(p)}<div><p class="person-title">${p.title}</p><h3>${p.name}</h3><p class="b-person-en">${p.en}</p></div></div><p class="person-bio">${p.bio}</p>${tagList(p.interests)}<a href="${p.url}">教师资料 <span>↗</span></a></article>`;
  return `<article class="c-person"><div class="c-person-number">${num(i)} <span>/ FACULTY</span></div>${portrait(p)}<div class="c-person-copy"><p class="c-person-en">${p.en}</p><h3>${p.name}<span>${p.title}</span></h3><p>${p.bio}</p><div class="c-interests"><span>研究领域</span><div>${p.interests.join(' / ')}</div></div><a href="${p.url}">更多教师资料 ↗</a></div></article>`;
}).join('');
const variant = document.body.dataset.variant;
const peopleRoot = document.querySelector('[data-people]');
if (peopleRoot) peopleRoot.innerHTML = peopleMarkup(variant);
const researchRoot = document.querySelector('[data-research]');
if (researchRoot && variant === 'a') researchRoot.innerHTML = areas.map((a,i)=>`<details class="a-area"><summary><span class="a-area-top"><span>${num(i)} / RESEARCH AREA</span><span class="a-area-icon" aria-hidden="true">↗</span></span><span class="a-area-title">${a.title}<small>${a.en}</small></span><span class="a-area-desc">${a.short}</span><span class="a-area-more">查看研究子项 <b aria-hidden="true">＋</b></span></summary><div class="a-area-detail">${tagList(a.tags)}</div></details>`).join('');
if (researchRoot && variant === 'c') researchRoot.innerHTML = areas.map((a,i)=>`<details class="c-area"><summary><span class="c-area-num">${num(i)}</span><span class="c-area-heading"><strong>${a.title}</strong><small>${a.en}</small></span><span class="c-area-short">${a.short}</span><span class="c-area-plus" aria-hidden="true">＋</span></summary><div class="c-area-detail"><p>${a.desc}</p>${tagList(a.tags)}</div></details>`).join('');
if (variant === 'b') {
  const tabs = document.querySelector('[data-tabs]'), panel = document.querySelector('[data-panel]');
  function selectArea(index) {
    const a = areas[index];
    tabs.innerHTML = areas.map((item,i)=>`<button type="button" class="b-tab ${i===index?'is-active':''}" aria-pressed="${i===index}" data-area="${i}"><span>${num(i)}</span><strong>${item.title}<small>${item.en}</small></strong><b aria-hidden="true">↗</b></button>`).join('');
    panel.innerHTML = `<div class="b-panel-top"><span>RESEARCH AREA / ${num(index)}</span><span class="lime">● &nbsp; SELECTED</span></div><div class="b-panel-content"><div class="b-panel-symbol" aria-hidden="true"><span>✳</span></div><p class="b-panel-en">${a.en.toUpperCase()}</p><h3>${a.title}</h3><p class="b-panel-desc">${a.desc}</p><p class="b-panel-label">研究子项 / TOPICS</p>${tagList(a.tags)}</div><div class="b-panel-bottom">MULTIMEDIA & INTELLIGENT COMPUTING <span>0${index+1} / 04</span></div>`;
  }
  tabs.addEventListener('click', event=>{const button=event.target.closest('[data-area]');if(button){const index=Number(button.dataset.area);selectArea(index);tabs.querySelector(`[data-area="${index}"]`).focus();}});
  selectArea(0);
}
