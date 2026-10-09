/* The persistent Material header must follow the newly mounted page. */
(() => {
  "use strict";
  function sync() {
    const metadata = document.querySelector("[data-doc-alternates]");
    if (!metadata) return;
    const alternates = JSON.parse(metadata.textContent);
    let fragment;
    try { fragment = decodeURIComponent(location.hash.slice(1)); }
    catch { fragment = ""; }
    for (const link of document.querySelectorAll("[data-doc-language]")) {
      const target = alternates.find(alt => alt.lang === link.dataset.docLanguage);
      if (!target) continue;
      const url = new URL(target.link, location.href);
      url.search = location.search;
      url.hash = target.fragments[fragment] || "";
      link.href = url.href;
      if (target.current) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    }
  }
  // Keep the generated page and translated section authoritative. Material's
  // body-level locale handler otherwise rebuilds URLs from the sitemap.
  for (const link of document.querySelectorAll("[data-doc-language]")) {
    link.addEventListener("click", event => event.stopPropagation());
  }
  for (const button of document.querySelectorAll(".md-select button")) {
    button.addEventListener("pointerdown", sync);
    button.addEventListener("keydown", event => {
      if (event.key === "Enter" || event.key === " ") sync();
    });
  }
  if (typeof document$ !== "undefined") document$.subscribe(sync);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", sync, {once: true});
  else sync();
  addEventListener("hashchange", sync);
  // Refresh before a user follows a selector retained from an earlier page.
  document.addEventListener("click", event => {
    if (event.target.closest("[data-doc-language]")) sync();
  }, true);
})();
