/* Regression checks for page-preserving language links and native theme scope. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {JSDOM} = require('jsdom');

const root = path.resolve(__dirname, '../..');
const site = path.join(root, 'site');
const script = fs.readFileSync(path.join(root, 'docs/assets/navigation.js'), 'utf8');
const origin = 'https://angel-valdezzz.github.io';
function files(directory) {
  return fs.readdirSync(directory, {withFileTypes: true}).flatMap(entry => {
    const file = path.join(directory, entry.name);
    return entry.isDirectory() ? files(file) : [file];
  });
}
const pages = files(site).filter(file => file.endsWith('.html')).map(file => {
  const html = fs.readFileSync(file, 'utf8');
  const dom = new JSDOM(html, {runScripts: 'outside-only', url: origin});
  const metadata = dom.window.document.querySelector('[data-doc-alternates]');
  if (!metadata) {dom.window.close(); return null;}
  const targets = JSON.parse(metadata.textContent);
  const current = targets.find(target => target.current);
  dom.reconfigure({url: origin + current.link});
  return {file, html, dom, targets, current};
}).filter(Boolean);
assert(pages.length > 0, 'No translated pages found');
const scope = pages[0].targets.find(target => target.lang === 'en').link.split('/')[1];
const base = `/${scope}/`;

for (const page of pages) {
  const document = page.dom.window.document;
  assert(page.html.includes(`__md_scope=new URL("${base}"`), 'Locale must use the project theme scope');
  for (const target of page.targets) {
    const link = document.querySelector(`[data-doc-language="${target.lang}"]`);
    assert.equal(link.getAttribute('href'), target.link, page.file);
    const relative = target.link.slice(base.length);
    const targetFile = path.join(site, relative, 'index.html');
    assert(fs.existsSync(targetFile), `Missing translated destination ${target.link}`);
    const translated = new JSDOM(fs.readFileSync(targetFile, 'utf8'));
    for (const [from, to] of Object.entries(target.fragments)) {
      assert(document.getElementById(from), `Invalid source section ${from}`);
      assert(translated.window.document.getElementById(to), `Invalid translated section ${to}`);
    }
    translated.window.close();
  }
  const canonicalAlternates = [...document.querySelectorAll('link[rel="alternate"][hreflang]')];
  for (const target of page.targets) {
    assert(canonicalAlternates.some(link => link.getAttribute('href') === target.link), 'hreflang must preserve the page');
  }
}

// Reuse one header while swapping page content, as Material instant navigation does.
const persistent = pages[0].dom;
let mounted;
persistent.window.document$ = {subscribe(callback) {mounted = callback; callback();}};
persistent.window.eval(script);
for (const page of pages) {
  // Material removes scripts from fetched page content before mounting it.
  const incoming = page.dom.window.document.querySelector('[data-doc-alternates]').cloneNode(true);
  assert.notEqual(incoming.tagName, 'SCRIPT', 'Metadata must survive Material script removal');
  const metadata = persistent.window.document.querySelector('[data-doc-alternates]');
  metadata.textContent = JSON.stringify(page.targets);
  const fragment = Object.keys(page.targets.find(target => !target.current).fragments)[0];
  persistent.window.history.replaceState({}, '', page.current.link + '?search=retained' + (fragment ? '#' + fragment : ''));
  mounted();
  for (const target of page.targets) {
    const link = persistent.window.document.querySelector(`[data-doc-language="${target.lang}"]`);
    const actual = new URL(link.href);
    assert.equal(actual.pathname, target.link, 'Instant navigation retained a stale language destination');
    assert.equal(actual.search, '?search=retained');
    assert.equal(decodeURIComponent(actual.hash.slice(1)), target.fragments[fragment] || '');
    assert.equal(link.hasAttribute('aria-current'), target.current);
  }
}

// Run Material's generated storage helpers with the same origin and storage.
const english = pages.find(page => page.current.lang === 'en');
const spanish = pages.find(page => page.current.lang === 'es');
for (const page of [english, spanish]) {
  const helpers = [...page.dom.window.document.scripts].find(element => element.textContent.includes('__md_scope='));
  page.dom.window.eval(helpers.textContent);
}
english.dom.window.eval('__md_set("__palette", {color:{scheme:"slate"}})');
const key = base + '.__palette';
spanish.dom.window.localStorage.setItem(key, english.dom.window.localStorage.getItem(key));
assert.equal(spanish.dom.window.eval('__md_get("__palette").color.scheme'), 'slate');
spanish.dom.window.eval('__md_set("__palette", {color:{scheme:"default"}})');
english.dom.window.localStorage.setItem(key, spanish.dom.window.localStorage.getItem(key));
assert.equal(english.dom.window.eval('__md_get("__palette").color.scheme'), 'default');
for (const page of pages) page.dom.window.close();
console.log(`Navigation checks passed: ${pages.length} EN/ES pages, instant navigation, sections and shared theme storage.`);
