(() => {
  const panels = [...document.querySelectorAll('[data-research-panel]')];
  const links = [...document.querySelectorAll('[data-research-link]')];
  if (!panels.length) return;
  const update = () => {
    const requested = decodeURIComponent(location.hash.slice(1));
    const selected = panels.some(panel => panel.id === requested) ? requested : panels[0].id;
    panels.forEach(panel => { panel.hidden = panel.id !== selected; });
    links.forEach(link => { if (link.getAttribute('href') === `#${selected}`) link.setAttribute('aria-current','true'); else link.removeAttribute('aria-current'); });
    document.querySelectorAll('a.language, #mobile-menu a[lang]').forEach(link => { const target = new URL(link.href); target.hash = selected; link.href = target.href; });
  };
  window.addEventListener('hashchange', update);
  update();
})();
