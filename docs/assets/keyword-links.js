// Mark keyword documentation links, including Material's instant navigation.
(function () {
  function enhance() {
    const label = document.documentElement.lang === 'es'
      ? 'Abre en una pestaña nueva' : 'Opens in a new tab';
    document.querySelectorAll('a[href]').forEach(link => {
      const url = new URL(link.href, location.href);
      if (url.origin !== location.origin || !/\/(keywords|reference\/keywords)(\/|\.html)/.test(url.pathname)) return;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.title = label;
      if (!link.querySelector('.new-tab-hint')) {
        const hint = document.createElement('span');
        hint.className = 'new-tab-hint'; hint.textContent = ' ↗';
        hint.setAttribute('aria-label', label); link.append(hint);
      }
    });
  }
  if (typeof document$ !== 'undefined') document$.subscribe(enhance);
  else if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', enhance);
  else enhance();
})();
