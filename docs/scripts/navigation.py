"""Resolve translated pages for Material's regular and instant navigation."""

import json
from pathlib import Path

from markdown import Markdown


def _headings(source, config):
    if source.startswith("---\n"):
        source = source.split("---", 2)[-1]
    extensions = list(config.markdown_extensions)
    if "toc" not in extensions:
        extensions.append("toc")
    parser = Markdown(extensions=extensions, extension_configs=config.mdx_configs)
    parser.convert(source)

    def flatten(tokens):
        for token in tokens:
            yield token["level"], token["id"]
            yield from flatten(token["children"])

    return list(flatten(parser.toc_tokens))


def _alternates(page, config):
    current = config.theme["language"]
    source = Path(config.docs_dir) / page.file.src_uri
    headings = _headings(source.read_text(encoding="utf-8"), config)
    result = []
    for alternate in config.extra["alternate"]:
        language = alternate["lang"]
        target = Path(config.docs_dir).parent / language / page.file.src_uri
        if not target.is_file():
            raise ValueError(f"Missing {language} translation: {page.file.src_uri}")
        translated = _headings(target.read_text(encoding="utf-8"), config)
        fragments = {}
        if [level for level, _ in headings] == [level for level, _ in translated]:
            fragments = {left[1]: right[1] for left, right in zip(headings, translated, strict=True)}
        result.append(
            {
                "name": alternate["name"],
                "lang": language,
                "link": config.extra["scope"] + ("es/" if language == "es" else "") + page.url,
                "fragments": fragments,
                "current": language == current,
            }
        )
    return result


def on_page_content(html, page, config, **_kwargs):
    # Material replaces content during instant navigation but keeps the header.
    # Carry destinations inside that content so the existing selector is updated.
    data = json.dumps(_alternates(page, config), ensure_ascii=True).replace("<", "\\u003c")
    return html + f'<script type="application/json" data-doc-alternates>{data}</script>'


def on_page_context(context, page, config, **_kwargs):
    config.extra["alternate"] = _alternates(page, config)
    return context
