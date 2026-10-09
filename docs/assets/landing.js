/* Progressive enhancement: without JS, the final evidence remains fully readable. */
(() => {
  let dispose = () => {};
  function mount() {
    dispose();
    const hero = document.querySelector('[data-er-hero]');
    if (!hero) return;
    const pause = hero.querySelector('[data-er-pause]');
    const replay = hero.querySelector('[data-er-replay]');
    const controls = hero.querySelector('.er-animation-controls');
    const buttons = [...hero.querySelectorAll('[data-er-select]')];
    const captures = [...hero.querySelectorAll('[data-er-capture]')];
    const contexts = [...hero.querySelectorAll('[data-er-context]')];
    const tabs = [...hero.querySelectorAll('[data-er-view]')];
    const panels = [...hero.querySelectorAll('.er-view')];
    const live = hero.querySelector('.er-live-status');
    const es = hero.dataset.lang === 'es';
    const motion = matchMedia('(prefers-reduced-motion: reduce)');
    let paused = motion.matches, visible = true, frame = 0, last = 0;
    let elapsed = motion.matches ? 7600 : 0;
    let step = -1, view = 'steps';
    const cleanups = [];
    const listen = (element, event, callback) => {
      element.addEventListener(event, callback);
      cleanups.push(() => element.removeEventListener(event, callback));
    };
    function selectStep(index, announce = false) {
      if (step === index) return;
      step = index;
      hero.dataset.erStep = String(index);
      buttons.forEach((button, i) => button.setAttribute('aria-pressed', String(i === index)));
      captures.forEach((capture, i) => { capture.hidden = i !== index; });
      contexts.forEach((context, i) => { context.hidden = i !== index; });
      if (announce) live.textContent = contexts[index].querySelector('h3').textContent;
    }
    function updateControl() {
      pause.textContent = paused ? (es ? 'Reanudar' : 'Resume') : (es ? 'Pausar' : 'Pause');
      pause.setAttribute('aria-pressed', String(paused));
      pause.disabled = motion.matches;
      pause.title = motion.matches ? (es ? 'Movimiento reducido: vista estática' : 'Reduced motion: static view') : '';
      hero.dataset.erActive = String(!paused && visible && !document.hidden && !motion.matches);
    }
    function stop() {
      cancelAnimationFrame(frame);
      frame = 0;
      last = 0;
    }
    function schedule() {
      updateControl();
      if (!frame && !paused && visible && !document.hidden && !motion.matches) frame = requestAnimationFrame(tick);
    }
    function tick(now) {
      frame = 0;
      if (paused || !visible || document.hidden || motion.matches) { last = 0; return; }
      if (last) elapsed += Math.min(now - last, 100);
      last = now;
      if (view === 'steps') selectStep(elapsed < 3800 ? 0 : elapsed < 7600 ? 1 : 2);
      frame = requestAnimationFrame(tick);
    }
    function setPaused(value) {
      paused = value;
      stop();
      schedule();
    }
    function selectView(value, manual = false) {
      view = value;
      tabs.forEach(tab => {
        const selected = tab.dataset.erView === value;
        tab.setAttribute('aria-selected', String(selected));
        tab.tabIndex = selected ? 0 : -1;
      });
      panels.forEach(panel => { panel.hidden = panel.id !== 'er-view-' + value; });
      if (manual) setPaused(true);
    }
    function restart() {
      elapsed = motion.matches ? 7600 : 0;
      selectView('steps');
      selectStep(motion.matches ? 2 : 0);
      hero.dataset.erComplete = String(motion.matches);
      setPaused(motion.matches);
    }
    function preference() {
      stop();
      if (motion.matches) {
        elapsed = 7600;
        selectStep(2);
      }
      paused = motion.matches;
      schedule();
    }
    function visibility() {
      stop();
      schedule();
    }
    controls.hidden = false;
    buttons.forEach((button, index) => {
      button.disabled = false;
      listen(button, 'click', () => {
        elapsed = index * 3800;
        setPaused(true);
        selectStep(index, true);
      });
    });
    tabs.forEach((tab, index) => {
      tab.disabled = false;
      listen(tab, 'click', () => selectView(tab.dataset.erView, true));
      listen(tab, 'keydown', event => {
        let next;
        if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
        else if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
        else if (event.key === 'Home') next = 0;
        else if (event.key === 'End') next = tabs.length - 1;
        else return;
        event.preventDefault();
        selectView(tabs[next].dataset.erView, true);
        tabs[next].focus();
      });
    });
    listen(pause, 'click', () => {
      if (motion.matches) return;
      if (paused && view !== 'steps') selectView('steps');
      setPaused(!paused);
    });
    listen(replay, 'click', restart);
    listen(motion, 'change', preference);
    listen(document, 'visibilitychange', visibility);
    const observer = new IntersectionObserver(entries => {
      visible = entries[0].isIntersecting;
      stop();
      schedule();
    }, {threshold: .05});
    observer.observe(hero);
    selectStep(motion.matches ? 2 : 0);
    updateControl();
    schedule();
    dispose = () => {
      stop();
      observer.disconnect();
      cleanups.forEach(cleanup => cleanup());
      hero.dataset.erActive = 'false';
    };
  }
  if (typeof document$ !== 'undefined') document$.subscribe(mount);
  else if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount, {once: true});
  else mount();
})();
