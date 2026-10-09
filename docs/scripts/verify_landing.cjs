/* Regression checks for evidence selection, motion preferences and instant remounting. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const {JSDOM} = require('jsdom');
const script = fs.readFileSync('docs/assets/landing.js', 'utf8');
function fixture(language, reduced = false) {
  const dom = new JSDOM(fs.readFileSync(language === 'es' ? 'site/es/index.html' : 'site/index.html', 'utf8'),
    {runScripts: 'outside-only', pretendToBeVisual: true, url: 'https://example.test/'});
  const w = dom.window;
  const media = new w.EventTarget();
  media.matches = reduced;
  w.matchMedia = () => media;
  let observer, remount, next = 0;
  const frames = new Map();
  w.requestAnimationFrame = callback => { const id = ++next; frames.set(id, callback); return id; };
  w.cancelAnimationFrame = id => frames.delete(id);
  w.IntersectionObserver = class {
    constructor(callback) { observer = callback; }
    observe() {}
    disconnect() {}
  };
  w.document$ = {subscribe(callback) { remount = callback; callback(); }};
  w.eval(script);
  return {w, media, frames, query: selector => w.document.querySelector(selector), remount: () => remount(),
    intersect: value => observer([{isIntersecting: value}]),
    advance: (start, end) => { for (let time = start; time <= end; time += 100) {
      const callbacks = [...frames.values()]; frames.clear(); callbacks.forEach(callback => callback(time));
    } }};
}
for (const language of ['en', 'es']) {
  const f = fixture(language);
  const hero = f.query('[data-er-hero]');
  const pause = f.query('[data-er-pause]');
  assert.equal(hero.dataset.erStep, '0');
  f.advance(100, 4000);
  assert.equal(hero.dataset.erStep, '1');
  pause.click();
  f.advance(4100, 10000);
  assert.equal(hero.dataset.erStep, '1', 'Pause must freeze the selected evidence');
  assert.equal(f.frames.size, 0);
  pause.click();
  f.advance(10100, 14500);
  assert.equal(hero.dataset.erStep, '2');
  f.advance(14600, 22000);
  assert.equal(hero.dataset.erStep, '2', 'Automatic tour must hold the final evidence');
  f.query('[data-er-select="0"]').click();
  assert.equal(pause.getAttribute('aria-pressed'), 'true', 'Manual selection must pause the tour');
  assert.equal(f.query('[data-er-capture="0"]').hidden, false);
  assert.equal(f.query('[data-er-capture="2"]').hidden, true);
  f.query('[data-er-view="logs"]').click();
  assert.equal(f.query('#er-view-logs').hidden, false);
  assert.equal(f.query('#er-view-steps').hidden, true);
  f.query('[data-er-view="logs"]').dispatchEvent(new f.w.KeyboardEvent('keydown', {key: 'Home', bubbles: true}));
  assert.equal(f.query('[data-er-view="summary"]').getAttribute('aria-selected'), 'true');
  assert.equal(f.w.document.activeElement, f.query('[data-er-view="summary"]'));
  f.query('[data-er-replay]').click();
  assert.equal(f.query('#er-view-steps').hidden, false);
  assert.equal(hero.dataset.erStep, '0');
  f.intersect(false);
  assert.equal(f.frames.size, 0, 'No frame work while the hero is offscreen');
  assert.equal(hero.dataset.erActive, 'false');
  f.intersect(true);
  assert.equal(f.frames.size, 1);
  f.remount();
  assert.equal(f.frames.size, 1, 'Instant navigation remount must dispose the old frame');
  f.query('[data-er-pause]').click();
  assert.equal(f.query('[data-er-pause]').textContent, language === 'es' ? 'Reanudar' : 'Resume');
  assert.equal(f.frames.size, 0, 'No duplicated event handlers after remount');
  f.media.matches = true;
  f.media.dispatchEvent(new f.w.Event('change'));
  assert.equal(hero.dataset.erStep, '2');
  assert.equal(f.query('[data-er-pause]').disabled, true);
  assert.equal(f.frames.size, 0);
  f.query('[data-er-select="1"]').click();
  assert.equal(hero.dataset.erStep, '1', 'Reduced motion must allow manual selection');
  f.query('[data-er-replay]').click();
  assert.equal(hero.dataset.erStep, '2');
  assert.equal(f.frames.size, 0);
  f.w.close();
  const staticView = fixture(language, true);
  assert.equal(staticView.query('[data-er-hero]').dataset.erStep, '2');
  assert.equal(staticView.frames.size, 0);
  staticView.w.close();
}
console.log('Landing checks passed: EN/ES, step progression, pause/replay, manual views, keyboard, reduced motion and instant remount.');
