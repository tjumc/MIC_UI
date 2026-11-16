(() => {
  const slides = [...document.querySelectorAll('[data-slide]')];
  const tabs = [...document.querySelectorAll('[data-topic]')];
  const count = document.querySelector('[data-count]');
  const status = document.querySelector('[data-status]');
  if (!slides.length || !tabs.length) return;
  let current = 0;
  const show = (index, announce = true) => {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => { slide.hidden = i !== current; });
    tabs.forEach((tab, i) => { tab.setAttribute('aria-pressed', String(i === current)); });
    count.textContent = `${String(current + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
    if (announce) status.textContent = `当前展示：${tabs[current].textContent}，第 ${current + 1} 项，共 ${slides.length} 项。`;
  };
  tabs.forEach((tab, i) => tab.addEventListener('click', () => show(i)));
  document.querySelector('[data-previous]').addEventListener('click', () => show(current - 1));
  document.querySelector('[data-next]').addEventListener('click', () => show(current + 1));
  document.querySelectorAll('.mobile-menu a').forEach(link => link.addEventListener('click', () => {
    document.querySelector('.mobile-menu').open = false;
  }));
  show(0, false);
})();
