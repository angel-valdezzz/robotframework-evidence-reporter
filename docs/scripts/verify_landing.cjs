/* Regression checks for accessible ambient motion, native search and instant navigation. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const {JSDOM} = require('jsdom');
const script = fs.readFileSync('docs/assets/landing.js', 'utf8');
for (const language of ['en', 'es']) {
  for (const reduced of [false, true]) {
    const dom = new JSDOM(fs.readFileSync(language === 'es' ? 'site/es/index.html' : 'site/index.html', 'utf8'),
      {runScripts: 'outside-only', pretendToBeVisual: true, url: 'https://example.test/'});
    const w = dom.window;
    const media = new w.EventTarget();
    media.matches = reduced;
    w.matchMedia = () => media;
    let remount;
    w.document$ = {subscribe(callback) { remount = callback; callback(); }};
    w.eval(script);
    const q = selector => w.document.querySelector(selector);
    assert.equal(q('.er-preview'), null, 'The invented report must not remain on home');
    assert.equal(q('.er-scroll-cue').getAttribute('href'), '#er-content');
    assert.ok(q('#er-content').querySelector('.er-format-preview'), 'Real examples must remain below home');
    const report = q('.er-action-secondary').getAttribute('href');
    assert.ok(report.endsWith(language === 'es' ? 'demo/es/passed.html' : 'demo/passed.html'));
    const pause = q('[data-er-pause]');
    assert.equal(pause.hidden, false);
    assert.equal(pause.disabled, reduced);
    assert.equal(w.document.body.dataset.erMotionPaused, String(reduced));
    if (!reduced) {
      pause.click();
      assert.equal(w.document.body.dataset.erMotionPaused, 'true');
      remount();
      pause.click();
      assert.equal(w.document.body.dataset.erMotionPaused, 'false', 'Remount must not duplicate pause handlers');
      let searchClicks = 0;
      q('.er-search-trigger').addEventListener('click', () => searchClicks++);
      q('.er-search-trigger').dispatchEvent(new w.KeyboardEvent('keydown', {key:'Enter',bubbles:true,cancelable:true}));
      assert.equal(searchClicks, 1, 'Keyboard must activate native search once');
      media.matches = true;
      media.dispatchEvent(new w.Event('change'));
      assert.equal(pause.disabled, true);
      assert.equal(w.document.body.dataset.erMotionPaused, 'true');
      media.matches = false;
      media.dispatchEvent(new w.Event('change'));
      assert.equal(w.document.body.dataset.erMotionPaused, 'false');
    }
    q('[data-er-hero]').remove();
    remount();
    assert.equal(w.document.body.dataset.erMotionPaused, String(reduced));
    dom.window.close();
  }
}
console.log('Landing checks passed: EN/ES, real examples, scroll target, pause, keyboard search, reduced motion and remount.');
