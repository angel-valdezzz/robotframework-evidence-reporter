// Use Libdoc's native light/dark CSS, with a persistent, accessible control.
(function () {
  const key = 'documentation-libdoc-theme';
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let selected;
  try { selected = localStorage.getItem(key); } catch (_) { /* Storage may be disabled. */ }
  if (!['light', 'dark'].includes(selected)) selected = null;
  function enhance() {
    const title = document.querySelector('.libdoc-title');
    if (title && typeof libdocBrand !== 'undefined') {
      const mark = document.createElement('img');
      mark.className = 'libdoc-brand-mark';
      mark.src = libdocBrand.icon;
      mark.alt = '';
      title.querySelector(':scope > svg')?.remove();
      title.prepend(mark);
      const heading = title.querySelector('h1');
      if (heading) heading.textContent = libdocBrand.name;
      document.title = libdocBrand.name + ' — ' + (document.documentElement.lang === 'es' ? 'Referencia de keywords' : 'Keyword reference');
    }
    const language = document.getElementById('language-container');
    if (!language) throw new Error('Libdoc language menu not found');
    const toolbar = document.createElement('div');
    toolbar.id = 'libdoc-controls';
    const button = document.createElement('button');
    button.id = 'libdoc-theme-toggle';
    button.type = 'button';
    const spanish = document.documentElement.lang === 'es';
    function apply() {
      const dark = (selected || (system.matches ? 'dark' : 'light')) === 'dark';
      document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
      button.textContent = dark ? (spanish ? 'Modo claro' : 'Light mode') : (spanish ? 'Modo oscuro' : 'Dark mode');
      button.setAttribute('aria-label', button.textContent);
      button.title = button.textContent;
      button.setAttribute('aria-pressed', String(dark));
    }
    button.addEventListener('click', () => {
      selected = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(key, selected); } catch (_) { /* Still works for this page. */ }
      apply();
    });
    toolbar.append(button, language);
    document.body.append(toolbar);
    system.addEventListener('change', apply);
    apply();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', enhance);
  else enhance();
})();
