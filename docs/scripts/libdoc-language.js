// Enhance Libdoc's existing language menu; use it for UI and keyword descriptions.
(function () {
  function enhance() {
    const container = document.getElementById('language-container');
    if (!container) throw new Error('Libdoc language menu not found');
    const button = container.querySelector('button');
    const menu = container.querySelector('ul');
    const spanish = document.documentElement.lang === 'es';
    const label = spanish ? 'Elegir idioma de la documentación' : 'Choose documentation language';
    button.type = 'button';
    const text = spanish ? 'Idioma: Español' : 'Language: English';
    button.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M3 5h12M9 2v3M5 5c1 5 4 8 9 10M13 5c-1 5-4 8-9 10M14 21l4-10 4 10M16 17h4"/></svg><span class="libdoc-sr-only">'+text+'</span>';
    button.title = label;
    button.setAttribute('aria-label', label);
    button.setAttribute('aria-haspopup', 'true');
    button.setAttribute('aria-expanded', 'false');
    container.querySelectorAll('ul a').forEach(link => {
      const language = link.textContent.trim().toLowerCase();
      if (!(language in libdocLanguageTargets)) throw new Error('Unexpected Libdoc language');
      link.dataset.language = language;
      link.textContent = language === 'es' ? 'Español' : 'English';
      link.href = libdocLanguageTargets[language];
      if (language === document.documentElement.lang) link.setAttribute('aria-current', 'true');
    });
    button.addEventListener('click', () => {
      button.setAttribute('aria-expanded', String(!menu.classList.contains('hidden')));
    });
    button.addEventListener('keydown', event => {
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        menu.classList.remove('hidden');
        button.setAttribute('aria-expanded', 'true');
        menu.querySelector('a').focus();
      }
    });
    container.addEventListener('keydown', event => {
      if (event.key === 'Escape') {
        menu.classList.add('hidden');
        button.setAttribute('aria-expanded', 'false');
        button.focus();
      }
    });
  }
  // Capture before Libdoc's UI-only handler: navigate to translated descriptions too.
  document.addEventListener('click', event => {
    const link = event.target.closest('#language-container a[data-language]');
    if (!link) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    const target = new URL(link.href, location.href);
    target.search = location.search;
    target.hash = location.hash;
    location.assign(target.href);
  }, true);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', enhance);
  else enhance();
})();
