/* Selected evidence ribbon. Material owns search, theme and locale navigation. */
(() => {
  'use strict';
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let paused=false, elapsed=0, dispose=()=>{};
  function mount() {
    dispose();
    const hero=document.querySelector('[data-er-hero]');
    const pause=hero?.querySelector('[data-er-pause]');
    const es=document.documentElement.lang==='es';
    const cleanups=[];
    function listen(element,type,handler) {
      if(!element)return;
      element.addEventListener(type,handler);cleanups.push(()=>element.removeEventListener(type,handler));
    }
    dispose=()=>cleanups.forEach(cleanup=>cleanup());
    function update() {
      document.body.dataset.erMotionPaused=String(paused||motion.matches);
      if(!pause)return;
      pause.hidden=false;pause.disabled=motion.matches;
      pause.setAttribute('aria-pressed',String(paused||motion.matches));
      pause.querySelector('span:last-child').textContent=motion.matches
        ? (es?'Movimiento reducido':'Reduced motion')
        : paused?(es?'Reanudar animación':'Resume animation'):(es?'Pausar animación':'Pause animation');
    }
    function syncHeaderMotion() {
      if(hero)return;
      const animation=selector=>document.querySelector(selector)?.getAnimations?.().find(item=>item.animationName==='er-header-flow');
      const header=animation('.md-header'),tabs=animation('.md-tabs');
      if(header&&tabs&&header.currentTime!==null)tabs.currentTime=header.currentTime;
    }
    listen(document.querySelector('.er-search-trigger'),'keydown',event=>{
      if(event.key==='Enter'||event.key===' '){event.preventDefault();event.currentTarget.click();}
    });
    listen(window,'resize',syncHeaderMotion);
    syncHeaderMotion();update();
    if(!hero){listen(motion,'change',update);return;}
    const $=selector=>hero.querySelector(selector);
    for(const link of hero.querySelectorAll('a[href^="#"]')) listen(link,'click',event=>{
      const target=document.getElementById(link.hash.slice(1));if(!target)return;
      event.preventDefault();target.scrollIntoView({behavior:motion.matches?'auto':'smooth',block:'start'});
      if(!target.hasAttribute('tabindex'))target.setAttribute('tabindex','-1');
      target.focus({preventScroll:true});
    });
    let reduced=motion.matches;
  // One continuous evidence ribbon. Its panes are an abstract visual metaphor,
  // not mock report controls. The genuine generated report is embedded below.
  const canvas = $('#er-stage');
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const labels = [...hero.querySelectorAll('.er-sequence-labels li')];
  const TAU = Math.PI * 2;
  const HOLD = 1.5, TRANSIT = .85, STEP = HOLD + TRANSIT;
  const PERIOD = STEP * 6;
  const colors = [[180,150,252],[71,212,217],[105,142,222]];
  let width=0, height=0, previous=null, request=0, visible=true;
  const rgba = (c,a) => `rgba(${c.join(',')},${a})`;
  function focusWeights(time) {
    const segment = (time % (STEP * 3)) / STEP;
    const current = Math.floor(segment);
    const local = (segment-current)*STEP;
    const blend = local < HOLD ? 0 : (1-Math.cos(Math.PI*(local-HOLD)/TRANSIT))/2;
    const values=[0,0,0]; values[current]=1-blend; values[(current+1)%3]=blend;
    return values;
  }
  function point(angle, phase) {
    const area = height-156;
    const lean = Math.sin(angle+.45);
    return {
      x:width*.5 + Math.sin(angle)*width*.285 + Math.cos(angle*2+phase)*width*.05,
      y:78 + area*.5 + Math.cos(angle)*area*.39 + Math.sin(angle*2+phase)*area*.026,
      z:lean,
      scale:.65+.35*(lean+1)/2
    };
  }
  function tangent(angle, phase) {
    const a=point(angle-.001,phase), b=point(angle+.001,phase);
    const length=Math.hypot(b.x-a.x,b.y-a.y);
    return {x:-(b.y-a.y)/length,y:(b.x-a.x)/length};
  }
  function ribbon(phase, front) {
    // Depth-sorted band facets keep the front and returning ribbon continuous.
    const steps=180;
    for(let i=0;i<steps;i++) {
      const a=i/steps*TAU, b=(i+1)/steps*TAU;
      const pa=point(a,phase), pb=point(b,phase);
      if ((pa.z>=0)!==front) continue;
      const na=tangent(a,phase), nb=tangent(b,phase);
      const thickness=Math.min(57,width*.085);
      const ra=thickness*pa.scale, rb=thickness*pb.scale;
      const mix=(pa.z+1)/2;
      const color=colors[0].map((v,j)=>Math.round(v*(1-mix)+colors[1][j]*mix));
      ctx.fillStyle=rgba(color,front?.075:.03);
      ctx.beginPath();
      ctx.moveTo(pa.x+na.x*ra,pa.y+na.y*ra);
      ctx.lineTo(pb.x+nb.x*rb,pb.y+nb.y*rb);
      ctx.lineTo(pb.x-nb.x*rb,pb.y-nb.y*rb);
      ctx.lineTo(pa.x-na.x*ra,pa.y-na.y*ra);
      ctx.closePath();ctx.fill();
      ctx.strokeStyle=rgba(color,front?.23:.08);ctx.lineWidth=.7;
      for(const direction of [-1,1]){
        ctx.beginPath();ctx.moveTo(pa.x+na.x*ra*direction,pa.y+na.y*ra*direction);
        ctx.lineTo(pb.x+nb.x*rb*direction,pb.y+nb.y*rb*direction);ctx.stroke();
      }
    }
  }
  function pane(p,color,energy,angle,phase,index) {
    const w=Math.min(170,width*.285)*p.scale;
    const h=w*.67;
    const tilt=Math.sin(angle)*.23 + Math.sin(phase)*.06;
    const opacity=.20 + .8*(p.z+1)/2;
    ctx.save();ctx.translate(p.x,p.y);ctx.rotate(tilt);
    ctx.globalAlpha=opacity;
    const fill=ctx.createLinearGradient(-w/2,-h/2,w/2,h/2);
    fill.addColorStop(0,rgba(color,.15+energy*.16));fill.addColorStop(1,'rgba(13,19,39,.9)');
    ctx.fillStyle=fill;ctx.strokeStyle=rgba(color,.28+energy*.58);ctx.lineWidth=1;
    ctx.shadowBlur=energy*22;ctx.shadowColor=rgba(color,.42);
    ctx.beginPath();ctx.roundRect(-w/2,-h/2,w,h,7);ctx.fill();ctx.stroke();ctx.shadowBlur=0;
    // Inner aperture and exposure: visual capture language, without invented UI.
    ctx.beginPath();ctx.roundRect(-w/2+10,-h/2+10,w-20,h-20,4);ctx.clip();
    const exposure=Math.sin(phase+index*.6)*w*.42;
    const sheen=ctx.createLinearGradient(exposure-38,0,exposure+38,0);
    sheen.addColorStop(0,rgba(color,0));sheen.addColorStop(.5,rgba(color,.12+energy*.18));sheen.addColorStop(1,rgba(color,0));
    ctx.fillStyle=sheen;ctx.fillRect(exposure-38,-h/2,76,h);
    ctx.strokeStyle=rgba(color,.15+energy*.2);ctx.lineWidth=.7;
    ctx.beginPath();ctx.roundRect(-w/2+10,-h/2+10,w-20,h-20,4);ctx.stroke();
    ctx.restore();
  }
  function draw(time) {
    ctx.clearRect(0,0,width,height);
    const phase=time/PERIOD*TAU;
    const weights=reduced?[.65,.65,.65]:focusWeights(time);
    const glow=ctx.createRadialGradient(width*.52,height*.51,0,width*.52,height*.51,width*.55);
    glow.addColorStop(0,'rgba(87,68,204,.075)');glow.addColorStop(.55,'rgba(21,85,113,.055)');glow.addColorStop(1,'rgba(9,13,28,0)');
    ctx.fillStyle=glow;ctx.fillRect(0,42,width,height-93);
    const panes=Array.from({length:8},(_,i)=>{const angle=phase+i/8*TAU;return {i,angle,p:point(angle,phase)}}).sort((a,b)=>a.p.z-b.p.z);
    ribbon(phase,false);
    for(const {i,angle,p} of panes.filter(v=>v.p.z<0))pane(p,colors[i%3],weights[i%3]*.5,angle,phase,i);
    ribbon(phase,true);
    for(const {i,angle,p} of panes.filter(v=>v.p.z>=0))pane(p,colors[i%3],weights[i%3],angle,phase,i);
    labels.forEach((label,i)=>{label.dataset.active=String(reduced||weights[i]>.55)});
  }
  function resize(){
    const bounds=$('#er-sequence').getBoundingClientRect();width=bounds.width;height=bounds.height;
    const ratio=Math.min(devicePixelRatio||1,2);
    canvas.width=Math.round(width*ratio);canvas.height=Math.round(height*ratio);
    ctx.setTransform(ratio,0,0,ratio,0,0);draw(elapsed);
  }
  const running=()=>!paused&&!reduced&&!document.hidden && hero.isConnected&&visible;
  function frame(now){
    request=0;if(!running()){previous=null;return;}
    if(previous!==null)elapsed=(elapsed+Math.min((now-previous)/1000,.06))%PERIOD;
    previous=now;draw(elapsed);request=requestAnimationFrame(frame);
  }
  function synchronize(){
    if(request)cancelAnimationFrame(request);request=0;previous=null;update();draw(elapsed);
    if(running())request=requestAnimationFrame(frame);
  }
  listen(pause, 'click', () => { paused = !paused; synchronize(); });
  listen(motion, 'change', () => { reduced = motion.matches; synchronize(); });
  listen(document, 'visibilitychange', synchronize);
  if ('IntersectionObserver' in window) {
    const intersection = new IntersectionObserver(entries => {visible=entries[0].isIntersecting;synchronize();},{threshold:0});
    intersection.observe($('#er-sequence')); cleanups.push(() => intersection.disconnect());
  }
  const observer = new ResizeObserver(resize); observer.observe($('#er-sequence'));
  cleanups.push(() => observer.disconnect(), () => {if(request)cancelAnimationFrame(request);});
  resize(); hero.classList.add('er-motion-ready'); synchronize();
  }
  if(typeof document$!=='undefined')document$.subscribe(mount);
  else if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount,{once:true});
  else mount();
})();
