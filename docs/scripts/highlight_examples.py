"""Highlight only documentation examples; keyword interfaces are untouched."""

import html
import re
from html.parser import HTMLParser

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name


class Cells(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = []
        self.cell = None

    def handle_starttag(self, tag, _attrs):
        if tag == "tr":
            self.row = []
        elif tag in {"td", "th"}:
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self.cell is not None:
            self.row.append("".join(self.cell).strip())
            self.cell = None
        elif tag == "tr":
            self.rows.append(self.row)


def code_block(code, language):
    code = code.strip("\n")
    prefix_lines = 0
    if language == "robotframework" and "*** " not in code:
        if code.lstrip().startswith("Library"):
            code = "*** Settings ***\n" + code
            prefix_lines = 1
        else:
            code = "*** Test Cases ***\nExample\n" + "\n".join("    " + line for line in code.splitlines())
            prefix_lines = 2
    tokens = highlight(code, get_lexer_by_name(language), HtmlFormatter(nowrap=True))
    if prefix_lines:
        tokens = "\n".join(tokens.splitlines()[prefix_lines:])
    return f'<pre class="libdoc-code" data-language="{language}"><code>{tokens}</code></pre>'


def highlight_examples(document):
    def pre(match):
        body = match[1]
        language = re.search(r"language-([\w+-]+)", body)
        code = html.unescape(re.sub(r"<[^>]+>", "", body))
        if language:
            name = language[1]
        elif "${" in code or "*** Settings ***" in code:
            name = "robotframework"
        elif code.lstrip().startswith(("{", "[")):
            name = "json"
        elif code.lstrip().startswith(("robot ", "pabot ", "pip ", "poetry ", "rf-evidence ")):
            name = "bash"
        else:
            name = "text"
        return code_block(code, name)

    document = re.sub(r"<pre\b[^>]*>(.*?)</pre>", pre, document, flags=re.DOTALL)

    def table(match):
        parser = Cells()
        parser.feed(match[0])
        first = parser.rows[0][0] if parser.rows and parser.rows[0] else ""
        if not (
            first.startswith(("${", "Capture ", "Add Evidence", "Create Milestone", "Set Report"))
            or first == "Library"
        ):
            return match[0]
        code = "\n".join("    ".join(row) for row in parser.rows)
        return code_block(code, "robotframework")

    return re.sub(r"<table\b[^>]*>.*?</table>", table, document, flags=re.DOTALL)


def styles():
    light = HtmlFormatter(style="friendly").get_style_defs(".libdoc-code")
    dark = HtmlFormatter(style="monokai").get_style_defs(':root[data-theme="dark"] .libdoc-code')
    return "<style>" + light + dark + "</style>"
