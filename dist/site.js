(() => {
  const english = document.documentElement.lang === 'en';
  const menuButton = document.querySelector('[data-menu-toggle]');
  const mobileMenu = document.querySelector('#mobile-menu');
  const teamButton = document.querySelector('[data-team-toggle]');
  const teamMenu = document.querySelector('#team-submenu');
  const setOpen = (button, menu, open) => {
    if (!button || !menu) return;
    menu.hidden = !open;
    button.setAttribute('aria-expanded', String(open));
  };
  menuButton?.addEventListener('click', () => setOpen(menuButton, mobileMenu, mobileMenu.hidden));
  teamButton?.addEventListener('click', () => setOpen(teamButton, teamMenu, teamMenu.hidden));
  document.addEventListener('click', event => {
    if (teamMenu && !event.target.closest('.team-nav')) setOpen(teamButton, teamMenu, false);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      if (teamMenu && !teamMenu.hidden) { setOpen(teamButton, teamMenu, false); teamButton.focus(); }
      if (mobileMenu && !mobileMenu.hidden) { setOpen(menuButton, mobileMenu, false); menuButton.focus(); }
    }
  });

  document.querySelectorAll('[data-carousel]').forEach(carousel => {
    const slides = [...carousel.querySelectorAll('[data-slide]')];
    const tabs = [...carousel.querySelectorAll('[data-topic]')];
    const counter = carousel.querySelector('[data-count]');
    const status = carousel.querySelector('[data-status]');
    let current = 0;
    const show = (index, announce = true) => {
      current = (index + slides.length) % slides.length;
      slides.forEach((slide, i) => { slide.hidden = i !== current; });
      tabs.forEach((tab, i) => tab.setAttribute('aria-pressed', String(i === current)));
      counter.textContent = `${String(current + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
      if (announce) status.textContent = english ? `Showing ${tabs[current].textContent}, ${current + 1} of ${slides.length}.` : `当前展示：${tabs[current].textContent}，第 ${current + 1} 项，共 ${slides.length} 项。`;
    };
    tabs.forEach((tab, i) => tab.addEventListener('click', () => show(i)));
    carousel.querySelector('[data-previous]').addEventListener('click', () => show(current - 1));
    carousel.querySelector('[data-next]').addEventListener('click', () => show(current + 1));
    show(0, false);
  });

  const page = document.body.dataset.page;
  const key = page === 'publications' ? 'papers' : page;
  const container = document.querySelector('[data-records]');
  if (!container) return;
  const records = window.MIC_DATA?.[key];
  if (!Array.isArray(records)) {
    container.textContent = english ? 'Records could not be loaded.' : '资料加载失败。';
    return;
  }
  const input = document.querySelector('[data-search]');
  const yearSelect = document.querySelector('[data-year]');
  const result = document.querySelector('[data-results]');
  const empty = document.querySelector('[data-empty]');
  const fragment = document.createDocumentFragment();
  const entries = [];

  if (page === 'publications') {
    const years = [...new Set(records.map(item => item.year))].sort((a, b) => Number(b) - Number(a));
    years.forEach(year => { const option = document.createElement('option'); option.value = year; option.textContent = year; yearSelect.append(option); });
    records.forEach(item => {
      const article = document.createElement('article'); article.className = 'paper-card';
      const year = document.createElement('span'); year.className = 'year'; year.textContent = item.year;
      const citation = document.createElement('p'); citation.textContent = item.citation;
      article.append(year, citation); fragment.append(article);
      entries.push({node:article, text:`${item.year} ${item.citation}`.toLocaleLowerCase(), year:item.year});
    });
  } else {
    const labels = [...document.querySelectorAll('thead th')].map(th => th.textContent.trim());
    records.forEach(item => {
      let values;
      if (page === 'members') values = [english ? item.name_en : item.name, item.degree, item.year, english ? item.interest_en : item.interest];
      else if (page === 'alumni') values = [english ? item.name_en : item.name, english ? item.degree_en : item.degree, item.period, english ? item.work_en : item.work];
      else values = [english ? item.term_en : item.term, item.number, english ? item.name_en : item.name];
      const row = document.createElement('tr');
      values.forEach((value, i) => { const cell = document.createElement('td'); cell.dataset.label = labels[i]; cell.textContent = value; row.append(cell); });
      fragment.append(row); entries.push({node:row, text:values.join(' ').toLocaleLowerCase()});
    });
  }
  container.replaceChildren(fragment);
  const filter = () => {
    const query = input.value.trim().toLocaleLowerCase();
    const year = yearSelect?.value || '';
    let visible = 0;
    entries.forEach(entry => { const match = (!query || entry.text.includes(query)) && (!year || entry.year === year); entry.node.hidden = !match; if (match) visible++; });
    result.textContent = english ? `${visible} of ${entries.length} records` : `显示 ${visible} / ${entries.length} 条`;
    empty.hidden = visible !== 0;
  };
  input.addEventListener('input', filter);
  yearSelect?.addEventListener('change', filter);
  filter();
})();
