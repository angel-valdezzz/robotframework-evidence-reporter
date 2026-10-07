/* Progressive enhancement: without JS every stage remains visible. No external assets. */
(() => {
  let dispose = () => {};
  function mount() {
    dispose();
    const hero = document.querySelector('[data-er-hero]');
    if (!hero) return;
    const canvas = hero.querySelector('canvas');
    const ctx = canvas.getContext('2d');
    const pause = hero.querySelector('[data-er-pause]');
    const replay = hero.querySelector('[data-er-replay]');
    const controls = hero.querySelector('.er-animation-controls');
    const stages = [...hero.querySelectorAll('[data-stage]')];
    const es = hero.dataset.lang === 'es';
    const motion = matchMedia('(prefers-reduced-motion: reduce)');
    let paused = motion.matches, visible = true, frame = 0, last = 0, elapsed = 0, width = 0, height = 0;
    controls.hidden = false;
    function size() {
      width = hero.clientWidth; height = hero.clientHeight;
      const dpr = Math.min(devicePixelRatio || 1, 2);
      canvas.width = width * dpr; canvas.height = height * dpr;
      ctx?.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function render(time) {
      const progress = (time % 14000) / 14000;
      stages.forEach((el, i) => el.classList.toggle('is-visible', motion.matches || progress > .1 + i * .14));
      if (!ctx || !width || motion.matches) return;
      ctx.clearRect(0, 0, width, height);
      // Evidence streams converge into the report. Curves form a quiet, living field.
      const cx = width * .72, cy = height * .48;
      for (let i = 0; i < 42; i++) {
        const spread = i / 41;
        const drift = Math.sin(time / 8000 + spread * 4) * height * .08;
        const startY = height * (spread * 1.65 - .3);
        const endY = cy + (spread - .5) * height * .45;
        ctx.beginPath();
        ctx.moveTo(-40, startY);
        ctx.bezierCurveTo(width * .25, startY + drift, width * .48, cy + (spread - .5) * 70, cx, endY);
        ctx.bezierCurveTo(width * .9, endY - drift, width * 1.05, height * spread, width + 50, height * (spread * 1.4 - .2));
        ctx.strokeStyle = i % 3 === 0 ? 'rgba(103,219,233,.13)' : 'rgba(165,139,250,.16)';
        ctx.lineWidth = .8; ctx.stroke();
        const p = (time / 12000 + spread) % 1;
        const x = width * p;
        const y = startY * (1-p) + cy * p + Math.sin(p * Math.PI) * drift;
        ctx.beginPath(); ctx.arc(x, y, 1.25, 0, Math.PI * 2);
        ctx.fillStyle = i % 3 === 0 ? 'rgba(117,232,239,.55)' : 'rgba(192,169,255,.45)';ctx.fill();
      }
    }
    function updateControl() {
      pause.textContent = paused ? (es ? 'Reanudar' : 'Resume') : (es ? 'Pausar' : 'Pause');
      pause.setAttribute('aria-pressed', String(paused));
      pause.disabled = motion.matches;
      pause.title = motion.matches ? (es ? 'Movimiento reducido: vista estática' : 'Reduced motion: static view') : ''; 
    }
    function tick(now) {
      frame = 0;
      if (paused || !visible || document.hidden || motion.matches) {last = 0; return;}
      if (last) elapsed += Math.min(now - last, 80);
      last = now; render(elapsed); frame = requestAnimationFrame(tick);
    }
    function schedule() {if (!frame && !paused && visible && !document.hidden && !motion.matches) frame = requestAnimationFrame(tick);}
    function toggle() {paused = !paused; updateControl(); if (paused) {cancelAnimationFrame(frame);frame=0;last=0;} else schedule();}
    function restart() {elapsed=0;last=0; paused=motion.matches;updateControl();render(motion.matches ? 12000 : 0);schedule();}
    function preference() {paused=motion.matches;updateControl();if(motion.matches){cancelAnimationFrame(frame);frame=0;stages.forEach(el=>el.classList.add('is-visible'));}else schedule();}
    function visibility() {last=0;schedule();}
    const observer = new IntersectionObserver(entries => {visible=entries[0].isIntersecting;last=0;schedule();},{threshold:.05});
    const resize = new ResizeObserver(() => {size();render(elapsed);});
    hero.setAttribute('data-er-running','');size();render(paused ? 12000 : 0);updateControl();
    observer.observe(hero);resize.observe(hero);
    pause.addEventListener('click',toggle);replay.addEventListener('click',restart);
    motion.addEventListener('change',preference);document.addEventListener('visibilitychange',visibility);schedule();
    dispose = () => {cancelAnimationFrame(frame);observer.disconnect();resize.disconnect();pause.removeEventListener('click',toggle);replay.removeEventListener('click',restart);motion.removeEventListener('change',preference);document.removeEventListener('visibilitychange',visibility);};
  }
  if (typeof document$ !== 'undefined') document$.subscribe(mount);
  else if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',mount,{once:true});
  else mount();
})();
