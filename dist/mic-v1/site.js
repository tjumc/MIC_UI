(() => {
  const english = document.documentElement.lang === 'en';
  const setOpen = (button, menu, open) => { if (!button || !menu) return; menu.hidden = !open; button.setAttribute('aria-expanded', String(open)); };
  const menuButton = document.querySelector('[data-menu-toggle]');
  const mobileMenu = document.querySelector('#mobile-menu');
  const teamButton = document.querySelector('[data-team-toggle]');
  const teamMenu = document.querySelector('#team-submenu');
  menuButton?.addEventListener('click', () => setOpen(menuButton, mobileMenu, mobileMenu.hidden));
  teamButton?.addEventListener('click', () => setOpen(teamButton, teamMenu, teamMenu.hidden));
  document.addEventListener('click', event => { if (teamMenu && !event.target.closest('.team-nav')) setOpen(teamButton, teamMenu, false); });
  document.addEventListener('keydown', event => { if (event.key !== 'Escape') return; if (teamMenu && !teamMenu.hidden) { setOpen(teamButton, teamMenu, false); teamButton.focus(); } if (mobileMenu && !mobileMenu.hidden) { setOpen(menuButton, mobileMenu, false); menuButton.focus(); } });
  document.querySelectorAll('[data-carousel]').forEach(carousel => {
    const slides=[...carousel.querySelectorAll('[data-slide]')],tabs=[...carousel.querySelectorAll('[data-topic]')];
    const counter=carousel.querySelector('[data-count]'),status=carousel.querySelector('[data-status]'); let current=0;
    const show=(index,announce=true) => { current=(index+slides.length)%slides.length; slides.forEach((slide,i)=>{slide.hidden=i!==current;}); tabs.forEach((tab,i)=>tab.setAttribute('aria-pressed',String(i===current))); counter.textContent=`${String(current+1).padStart(2,'0')} / ${String(slides.length).padStart(2,'0')}`; if(announce) status.textContent=english?`Showing ${tabs[current].textContent}, ${current+1} of ${slides.length}.`:`当前展示：${tabs[current].textContent}，第 ${current+1} 项，共 ${slides.length} 项。`; };
    tabs.forEach((tab,i)=>tab.addEventListener('click',()=>show(i)));carousel.querySelector('[data-previous]').addEventListener('click',()=>show(current-1));carousel.querySelector('[data-next]').addEventListener('click',()=>show(current+1));show(0,false);
  });
  const container=document.querySelector('[data-records]'), input=document.querySelector('[data-search]');
  if (!container || !input) return;
  const entries=[...container.querySelectorAll('[data-filter-row]')].map(node=>({node,text:node.textContent.toLocaleLowerCase(),year:node.dataset.yearValue||''}));
  const year=document.querySelector('[data-year]'),count=document.querySelector('[data-results]'),empty=document.querySelector('[data-empty]');
  const filter=()=>{const query=input.value.trim().toLocaleLowerCase(),selected=year?.value||'';let visible=0;entries.forEach(x=>{const match=(!query||x.text.includes(query))&&(!selected||x.year===selected);x.node.hidden=!match;if(match)visible++;});if(count)count.textContent=english?`${visible} of ${entries.length} records`:`显示 ${visible} / ${entries.length} 条`;if(empty)empty.hidden=visible!==0;};
  input.addEventListener('input',filter);year?.addEventListener('change',filter);filter();
})();
