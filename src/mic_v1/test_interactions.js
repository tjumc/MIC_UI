'use strict';
// Exercise the shipped event handlers with a minimal DOM double; this is not a browser visual test.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname,'site.js'),'utf8');
function element(fields={}) {
  return Object.assign({ hidden:false, textContent:'', value:'', dataset:{}, attributes:{}, listeners:{}, focused:false,
    addEventListener(type,fn){(this.listeners[type] ||= []).push(fn);},
    dispatch(type,event={}){for(const fn of this.listeners[type]||[])fn(event);},
    setAttribute(key,value){this.attributes[key]=value;},
    focus(){this.focused=true;}
  },fields);
}
function harness(lang='zh-CN') {
  const menu=element({hidden:true}),team=element({hidden:true}),menuButton=element(),teamButton=element();
  const tabs=Array.from({length:5},(_,i)=>element({textContent:'topic '+i}));
  const slides=Array.from({length:5},(_,i)=>element({hidden:i!==0}));
  const count=element(),status=element(),previous=element(),next=element();
  const carousel=element({querySelectorAll(sel){return sel==='[data-slide]'?slides:tabs;},querySelector(sel){return {'[data-count]':count,'[data-status]':status,'[data-previous]':previous,'[data-next]':next}[sel];}});
  const rows=[element({textContent:'2025 Shell-Guided Compression',dataset:{yearValue:'2025'}}),element({textContent:'2026 Image Recognition',dataset:{yearValue:'2026'}}),element({textContent:'2025 Video Coding',dataset:{yearValue:'2025'}})];
  const container=element({querySelectorAll(){return rows;}}),search=element(),year=element(),results=element(),empty=element({hidden:true});
  const selectors={'[data-menu-toggle]':menuButton,'#mobile-menu':menu,'[data-team-toggle]':teamButton,'#team-submenu':team,'[data-records]':container,'[data-search]':search,'[data-year]':year,'[data-results]':results,'[data-empty]':empty};
  const doc=element({documentElement:{lang},querySelector(sel){return selectors[sel]||null;},querySelectorAll(sel){return sel==='[data-carousel]'?[carousel]:[];}});
  vm.runInNewContext(source,{document:doc});
  return {doc,menu,team,menuButton,teamButton,tabs,slides,count,status,previous,next,rows,search,year,results,empty};
}
for (const lang of ['zh-CN','en']) {
  const x=harness(lang);
  x.menuButton.dispatch('click');assert.equal(x.menu.hidden,false);assert.equal(x.menuButton.attributes['aria-expanded'],'true');
  x.doc.dispatch('keydown',{key:'Escape'});assert.equal(x.menu.hidden,true);assert.equal(x.menuButton.focused,true);
  x.teamButton.dispatch('click');assert.equal(x.team.hidden,false);x.doc.dispatch('keydown',{key:'Escape'});assert.equal(x.team.hidden,true);
  x.tabs[3].dispatch('click');assert.equal(x.slides[3].hidden,false);assert.equal(x.tabs[3].attributes['aria-pressed'],'true');assert.equal(x.count.textContent,'04 / 05');
  x.next.dispatch('click');x.next.dispatch('click');assert.equal(x.slides[0].hidden,false);assert.equal(x.count.textContent,'01 / 05');
  x.previous.dispatch('click');assert.equal(x.slides[4].hidden,false);
  x.search.value='compression';x.search.dispatch('input');assert.deepEqual(x.rows.map(row=>row.hidden),[false,true,true]);
  x.year.value='2026';x.year.dispatch('change');assert.equal(x.empty.hidden,false);assert.ok(x.results.textContent.includes('0'));
  x.search.value='';x.search.dispatch('input');assert.deepEqual(x.rows.map(row=>row.hidden),[true,false,true]);
}
console.log('Menu, carousel, search and year filtering passed for Chinese and English DOM doubles.');
