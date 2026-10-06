const fs = require('fs');
const path = require('path');
const assert = require('assert');
const { JSDOM, VirtualConsole } = require('jsdom');
(async () => {
  const relative = process.argv[2] || 'keywords/index.html';
  const models = [];
  const repo = process.cwd();
  {
    for (const lang of ['en','es']) {
      const file = path.join(repo, 'site', lang === 'es' ? 'es' : '', relative);
      const errors = [];
      const vc = new VirtualConsole();
      vc.on('jsdomError', error => errors.push(error));
      const html = fs.readFileSync(file,'utf8');
      models.push(JSON.parse(html.match(/libdoc = ([^\n]+)\n/)[1]));
      const dom = new JSDOM(fs.readFileSync(file,'utf8').replace(/type=module/g,'type="text/javascript"'), { url:'https://example.test/'+(lang==='es'?'es/':'')+relative,runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:vc,beforeParse(window) {
        window.matchMedia = () => ({matches:false,addEventListener(){},removeEventListener(){}});
        window.scrollTo=()=>{};window.HTMLElement.prototype.scrollIntoView=()=>{};
        window.CSS={escape:value=>value};
      }});
      await new Promise(resolve=>dom.window.addEventListener('load',resolve));
      if (errors.length) throw errors[0];
      const document=dom.window.document;
      assert.equal(document.documentElement.lang,lang);
      const header=document.querySelector('.libdoc-header');
      assert(header && header.contains(document.querySelector('.libdoc-title')));
      assert.equal(dom.window.getComputedStyle(header).position,'fixed');
      assert(Number(dom.window.getComputedStyle(header).zIndex)>1000);
      const navigation=[...header.querySelectorAll('.libdoc-icon-link')];
      assert.equal(navigation.length,3);
      assert.equal(dom.window.getComputedStyle(header.querySelector('#language-container button svg path')).stroke,'white');
      for (const link of navigation) {
        assert.equal(link.target,'_blank');
        assert.equal(link.rel,'noopener noreferrer');
        assert(link.getAttribute('aria-label') && link.title);
      }
      assert.equal(navigation[0].getAttribute('href'),'../');
      assert(navigation[1].href.startsWith('https://github.com/angel-valdezzz/'));
      assert(navigation[2].href.startsWith('https://pypi.org/project/'));
      assert(document.querySelectorAll('.libdoc-code span').length>3);
      const theme=document.querySelector('#libdoc-theme-toggle');
      assert(theme, 'Visible Libdoc theme control');
      assert.equal(document.documentElement.getAttribute('data-theme'),'light');
      theme.click();
      assert.equal(document.documentElement.getAttribute('data-theme'),'dark');
      assert.equal(theme.getAttribute('aria-pressed'),'true');
      assert.equal(dom.window.localStorage.getItem('documentation-libdoc-theme'),'dark');
      assert.equal(theme.textContent,lang==='es'?'Modo claro':'Light mode');
      theme.click();
      assert.equal(document.documentElement.getAttribute('data-theme'),'light');
      assert.equal(theme.getAttribute('aria-pressed'),'false');

      const button=document.querySelector('#language-container button');
      assert(button);
      assert(button.textContent.includes(lang==='es'?'Idioma: Español':'Language: English'));
      const links=[...document.querySelectorAll('#language-container ul a')];
      assert.deepEqual(links.map(a=>a.textContent),['English','Español']);
      assert(links.find(a=>a.dataset.language==='es').href.includes('/es/'));
      assert(!links.find(a=>a.dataset.language==='en').href.includes('/es/'));
      assert.equal(button.getAttribute('aria-expanded'),'false');
      button.click();assert.equal(button.getAttribute('aria-expanded'),'true');
      button.dispatchEvent(new dom.window.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
      assert.equal(button.getAttribute('aria-expanded'),'false');
      assert(document.querySelector('.documentation-language-help').textContent.includes(lang==='es'?'selector Idioma':'Language menu'));
      assert(!document.querySelector('.documentation-language-help a[href*="/es/"]'));
      if (lang==='es') assert(document.body.textContent.includes('Introducción'));
      const keywords=[...document.querySelectorAll('.kw-name')].map(e=>e.textContent);
      assert.equal(keywords.length, models.at(-1).keywords.length);
      console.log(repo,lang,'native menu, labels, keyboard, UI and description hint OK',keywords.length);
      dom.window.close();
    }
  }
  function withoutDocs(value) {
    if (Array.isArray(value)) return value.map(withoutDocs);
    if (value && typeof value === 'object') return Object.fromEntries(
      Object.entries(value).filter(([key])=>!['doc','shortdoc','generated','lang'].includes(key))
        .map(([key,value])=>[key,withoutDocs(value)])
    );
    return value;
  }
  assert.deepEqual(withoutDocs(models[0]), withoutDocs(models[1]));
  console.log('Both languages preserve keyword names, signatures, types and defaults.');
})().catch(error=>{console.error(error);process.exitCode=1;});
