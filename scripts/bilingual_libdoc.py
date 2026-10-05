"""Generate translated Libdoc without changing the executable keyword interface."""

import ast
import copy
import hashlib
import json
import posixpath
import re
from pathlib import Path

from robot.libdocpkg import LibraryDocumentation


def generate(library: str, root: Path, relative: str, _site_url: str) -> None:
    original = LibraryDocumentation(library)
    translated = copy.deepcopy(original)
    catalog = json.loads((root / "docs/translations/es/libdoc.json").read_text(encoding="utf-8"))
    entries = {"introduction": (original, translated)}
    entries.update({f"init:{a.name}": (a, b) for a, b in zip(original.inits, translated.inits, strict=True)})
    entries.update(
        {f"keyword:{a.name}": (a, b) for a, b in zip(original.keywords, translated.keywords, strict=True)}
    )
    if set(entries) != set(catalog):
        raise ValueError(f"Libdoc translation keys differ: {set(entries) ^ set(catalog)}")
    for key, (source, target) in entries.items():
        entry = catalog[key]
        digest = hashlib.sha256(source.doc.encode("utf-8")).hexdigest()
        if entry["source_sha256"] != digest or not entry["text"].strip():
            raise ValueError(f"Missing or outdated Libdoc translation: {key}")
        set_doc(target, entry["text"])
    models = {"en": original, "es": translated}
    for language, model in models.items():
        output = root / "docs" / language / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        model.convert_docs_to_html()
        hint = (
            "Usa el selector Idioma, arriba a la derecha, para elegir inglés o español. "
            "Cambia los controles y las descripciones; las keywords conservan sus nombres."
            if language == "es"
            else "Use the Language menu at the top right to choose English or Spanish. "
            "It changes controls and descriptions; keyword names remain the same."
        )
        set_doc(model, f'<p class="documentation-language-help">{hint}</p>' + model.doc)
        model.save(str(output), format="HTML", lang=language)
        localize_menu(output, root, relative, language)


def localize_menu(output: Path, root: Path, relative: str, language: str) -> None:
    """Extend the generated native menu without depending on minified symbol names."""
    document = output.read_text(encoding="utf-8")
    pattern = re.compile(r"JSON\.parse\(('(?:\\.|[^'\\])*')\)")
    match = None
    english = None
    for candidate in pattern.finditer(document):
        try:
            data = json.loads(ast.literal_eval(candidate[1]))
        except (ValueError, SyntaxError):
            continue
        if isinstance(data, dict) and "en" in data and "chooseLanguage" in data["en"]:
            match, english = candidate, data["en"]
            break
    if match is None or english is None:
        raise ValueError("Unsupported Libdoc language bundle; review the native menu adapter")
    spanish = json.loads((root / "docs/translations/es/libdoc-ui.json").read_text(encoding="utf-8"))
    if set(english) - set(spanish):
        raise ValueError(f"Libdoc UI translation keys differ: {set(english) - set(spanish)}")
    bundle = json.dumps({"en": english, "es": {key: spanish[key] for key in english}}, ensure_ascii=True)
    # Double JSON encoding is a JavaScript string literal, without quote replacement.
    replacement = "JSON.parse(" + json.dumps(bundle) + ")"
    document = document[: match.start()] + replacement + document[match.end() :]
    document = re.sub(r"(<html[^>]*\blang=)[^ >]+", r"\g<1>" + language, document, count=1)
    current = ("es/" if language == "es" else "") + relative
    targets = {
        lang: posixpath.relpath(("es/" if lang == "es" else "") + relative, posixpath.dirname(current))
        for lang in ("en", "es")
    }
    script = (Path(__file__).parent / "libdoc-language.js").read_text(encoding="utf-8")
    theme_script = (Path(__file__).parent / "libdoc-theme.js").read_text(encoding="utf-8")
    style = """<style>
#language-container {width:auto;max-width:220px}
#language-container button {font:inherit;padding:12px;cursor:pointer;color:var(--text-color)}
#language-container ul a {display:block;padding:6px 12px}
#language-container a[aria-current] {font-weight:bold}
.documentation-language-help {border-left:3px solid #008c95;padding:8px 12px}
@media(max-width:600px) {#language-container button {font-size:12px;padding:10px 6px}}

</style>"""
    document += (
        style
        + "<script>const libdocLanguageTargets="
        + json.dumps(targets)
        + ";"
        + script
        + theme_script
        + "</script>"
    )
    theme_style = (Path(__file__).parent / "libdoc-theme.css").read_text(encoding="utf-8")
    document += "<style>" + theme_style + "</style>"
    output.write_text(document, encoding="utf-8")


def set_doc(model: object, text: str) -> None:
    """RF 7.4 exposes LibraryDoc.doc as read-only; 7.5 adds its public setter."""
    try:
        model.doc = text
    except AttributeError:
        model._doc = text
