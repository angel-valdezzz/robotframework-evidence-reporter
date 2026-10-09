/* Ambient motion is independent of navigation, search and the genuine report examples. */
(() => {
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let paused = false, dispose = () => {};
  function mount() {
    dispose();
    const hero = document.querySelector('[data-er-hero]');
    const pause = hero?.querySelector('[data-er-pause]');
    const search = document.querySelector('.er-search-trigger');
    const es = document.documentElement.lang === 'es';
    const cleanups = [];
    function listen(element, event, callback) {
      if (!element) return;
      element.addEventListener(event, callback);
      cleanups.push(() => element.removeEventListener(event, callback));
    }
    function update() {
      document.body.dataset.erMotionPaused = String(paused || motion.matches);
      if (!pause) return;
      pause.hidden = false;
      pause.disabled = motion.matches;
      pause.setAttribute('aria-pressed', String(paused || motion.matches));
      pause.querySelector('span:last-child').textContent = motion.matches
        ? (es ? 'Movimiento reducido' : 'Reduced motion')
        : paused ? (es ? 'Reanudar animación' : 'Resume animation')
        : (es ? 'Pausar animación' : 'Pause animation');
    }
    listen(pause, 'click', () => { paused = !paused; update(); });
    listen(search, 'keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        search.click();
      }
    });
    listen(motion, 'change', update);
    update();
    dispose = () => cleanups.forEach(cleanup => cleanup());
  }
  if (typeof document$ !== 'undefined') document$.subscribe(mount);
  else if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
