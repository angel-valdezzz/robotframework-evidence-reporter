// Keep Libdoc's native contents and controls inside a stable project header.
(function () {
  const key = 'documentation-libdoc-theme';
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let selected;
  try { selected = localStorage.getItem(key); } catch (_) {}
  if (!['light', 'dark'].includes(selected)) selected = null;
  const svg = paths => '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">'+paths+'</svg>';
  function enhance() {
    const spanish = document.documentElement.lang === 'es';
    const title = document.querySelector('.libdoc-title');
    if (!title || typeof libdocBrand === 'undefined') throw new Error('Libdoc project title not found');
    const mark = document.createElement('img');
    mark.className = 'libdoc-brand-mark'; mark.src = libdocBrand.icon; mark.alt = '';
    title.querySelector(':scope > svg')?.remove(); title.prepend(mark);
    title.querySelector('h1').textContent = libdocBrand.name;
    document.title = libdocBrand.name + ' — ' + (spanish ? 'Referencia de keywords' : 'Keyword reference');
    const header = document.createElement('div'); header.className = 'libdoc-header';
    const toolbar = document.createElement('div'); toolbar.id = 'libdoc-controls';
    toolbar.setAttribute('role','navigation');
    toolbar.setAttribute('aria-label',spanish ? 'Enlaces y ajustes de documentación' : 'Documentation links and settings');
    const labels = spanish ? ['Guía de usuario','GitHub','PyPI'] : ['User guide','GitHub','PyPI'];
    const icons = [svg('<path d="M4 4h7v16H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Zm16 0h-7v16h7a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2Z"/>'),
      '<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true"><path d="M12 .8a11.2 11.2 0 0 0-3.54 21.83c.56.1.76-.24.76-.54v-2.1c-3.12.68-3.78-1.33-3.78-1.33-.51-1.3-1.25-1.65-1.25-1.65-1.02-.7.08-.68.08-.68 1.13.08 1.72 1.16 1.72 1.16 1 .1.77 2.22 3.27 1.56.1-.72.39-1.22.71-1.5-2.49-.28-5.1-1.25-5.1-5.55 0-1.23.44-2.23 1.16-3.02-.12-.29-.5-1.43.11-2.98 0 0 .95-.3 3.08 1.15a10.7 10.7 0 0 1 5.6 0c2.13-1.45 3.08-1.15 3.08-1.15.61 1.55.23 2.69.11 2.98.72.79 1.16 1.79 1.16 3.02 0 4.31-2.62 5.27-5.12 5.54.4.35.76 1.04.76 2.1v3.1c0 .3.2.65.77.54A11.2 11.2 0 0 0 12 .8Z"/></svg>',
      '<img src="'+libdocBrand.pypiIcon+'" alt="" width="22" height="22">'];
    [libdocBrand.manual,libdocBrand.github,libdocBrand.pypi].forEach((href,index) => {
      const link = document.createElement('a'); link.href = href; link.target = '_blank';
      link.rel = 'noopener noreferrer'; link.className = 'libdoc-icon-link';
      const label = labels[index] + (spanish ? ' · Abre en una pestaña nueva' : ' · Opens in a new tab');
      link.title = label; link.setAttribute('aria-label',label);
      link.innerHTML = icons[index]+'<span class="libdoc-external" aria-hidden="true">↗</span>';
      if (index === 0) {
        link.classList.add('libdoc-guide-link');
        const text = document.createElement('span'); text.className = 'libdoc-guide-label';
        text.textContent = labels[index]; link.append(text);
      }
      toolbar.append(link);
    });
    const language = document.getElementById('language-container');
    if (!language) throw new Error('Libdoc language menu not found');
    const button = document.createElement('button'); button.id = 'libdoc-theme-toggle'; button.type = 'button';
    function apply() {
      const dark = (selected || (system.matches ? 'dark' : 'light')) === 'dark';
      document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
      const label = dark ? (spanish ? 'Modo claro' : 'Light mode') : (spanish ? 'Modo oscuro' : 'Dark mode');
      button.innerHTML = (dark ? svg('<circle cx="12" cy="12" r="4"/><path d="M12 1v3m0 16v3M1 12h3m16 0h3M4 4l2 2m12 12 2 2M4 20l2-2M18 6l2-2"/>') : svg('<path d="M20 15A9 9 0 0 1 9 4a9 9 0 1 0 11 11Z"/>'))+'<span class="libdoc-sr-only">'+label+'</span>';
      button.setAttribute('aria-label',label); button.title = label;
      button.setAttribute('aria-pressed',String(dark));
    }
    button.addEventListener('click', () => {
      selected = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(key, selected); } catch (_) {}
      apply();
    });
    toolbar.append(button,language); header.append(title,toolbar); document.body.append(header);
    system.addEventListener('change',apply); apply();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', enhance);
  else enhance();
})();
