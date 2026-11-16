(() => {
  if (document.body.dataset.page !== 'publications') return;
  const english = document.documentElement.lang === 'en';
  const cards = [...document.querySelectorAll('[data-records] .paper-card')];
  const toolbar = document.querySelector('.data-toolbar');
  const search = document.querySelector('[data-search]');
  const year = document.querySelector('[data-year]');
  const count = document.querySelector('[data-results]');
  const empty = document.querySelector('[data-empty]');
  if (!cards.length || !toolbar || !search) return;
  const key = 'mic-publication-bookmarks-v1';
  let persistent = true;
  let saved;
  try { const parsed = JSON.parse(localStorage.getItem(key) || '[]'); saved = new Set(Array.isArray(parsed) ? parsed : []); }
  catch { persistent = false; saved = new Set(); }
  const controls = document.createElement('div'); controls.className = 'bookmark-controls';
  const label = document.createElement('label');
  const checkbox = document.createElement('input'); checkbox.type = 'checkbox'; checkbox.dataset.bookmarksOnly = '';
  const labelText = document.createElement('span'); label.append(checkbox,labelText);
  const note = document.createElement('span'); note.className = 'bookmark-note';
  controls.append(label,note); toolbar.after(controls);
  const updateLabel = () => {
    labelText.textContent = english ? `Saved only (${saved.size})` : `只看收藏（${saved.size}）`;
    note.textContent = persistent ? (english ? 'Saved in this browser only.' : '收藏仅保存在当前浏览器。') : (english ? 'Browser storage is unavailable; saved items last only for this page session.' : '浏览器不允许保存，收藏仅在本次页面中有效。');
  };
  cards.forEach(card => {
    const citation = card.querySelector('p').textContent;
    card.dataset.citation = citation;
    const button = document.createElement('button'); button.type = 'button'; button.className = 'bookmark-button';
    const paint = () => { const active = saved.has(citation); button.setAttribute('aria-pressed',String(active)); button.textContent = active ? (english?'Saved ✓':'已收藏 ✓') : (english?'Save':'收藏'); button.setAttribute('aria-label',(english?(active?'Remove saved paper: ':'Save paper: '):(active?'取消收藏论文：':'收藏论文：'))+citation.slice(0,90)); };
    button.addEventListener('click', () => {
      if (saved.has(citation)) saved.delete(citation); else saved.add(citation);
      try { localStorage.setItem(key,JSON.stringify([...saved])); } catch { persistent = false; }
      paint(); updateLabel(); search.dispatchEvent(new Event('input'));
    });
    card.append(button); paint();
  });
  const applySavedFilter = () => {
    let visible = 0;
    cards.forEach(card => { card.hidden = card.hidden || (checkbox.checked && !saved.has(card.dataset.citation)); if (!card.hidden) visible++; });
    count.textContent = english ? `${visible} of ${cards.length} records` : `显示 ${visible} / ${cards.length} 条`;
    empty.hidden = visible !== 0;
  };
  search.addEventListener('input',applySavedFilter);
  year?.addEventListener('change',applySavedFilter);
  checkbox.addEventListener('change',() => search.dispatchEvent(new Event('input')));
  updateLabel();
})();
