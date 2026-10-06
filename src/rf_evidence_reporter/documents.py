"""Clean print reports share the HTML case, milestone and evidence hierarchy."""

from io import BytesIO
from xml.sax.saxutils import escape

from .branding import load_branding
from .builder import display_date, timezone_label
from .i18n import footer_text, translator

STATUS_PALETTE = {
    "PASS": ("168044", "E5F6EC"),
    "FAIL": ("C52D4B", "FFE8EE"),
    "ERROR": ("C52D4B", "FFE8EE"),
    "WARN": ("A26000", "FFF3C9"),
    "SKIP": ("A26000", "FFF3C9"),
    "INCOMPLETE": ("A26000", "FFF3C9"),
    "INFO": ("1467C2", "E9F2FF"),
}


def summary(case, language="en"):
    t = translator(language)
    return [
        (t("Suite"), case["suite"]),
        *case["metadata"].items(),
        (t("Inicio"), display_date(case["started_at"], language)),
        (t("Fin"), display_date(case["ended_at"], language)),
        (t("Zona horaria"), timezone_label(case["started_at"], language)),
    ]


def event_level(event):
    return event.get("level", "INFO") if event["kind"] == "message" else event.get("status", "INFO")


def status_colors(level):
    return STATUS_PALETTE.get(level, STATUS_PALETTE["INFO"])


def event_text(event):
    return f"{event_level(event)} | {event['title']}"


def printable_image(event):
    from PIL import Image

    with Image.open(BytesIO(event["_image_bytes"])) as image:
        image.load()
        content = BytesIO()
        image.save(content, format="PNG")
        content.seek(0)
        return content, image.size


def metrics(case, language):
    t = translator(language)
    duration = case.get("duration_seconds")
    return (
        f"{case['status']}   ·   "
        + (f"{duration:.2f} s" if duration is not None else t("Sin finalizar"))
        + f"   ·   ▣ {sum(e['kind'] == 'capture' for e in case['events'])} {t('capturas')}"
        + f"   ·   ! {case.get('warning_count', 0)} {t('advertencias')}"
    )


def block_metrics(block, language):
    t = translator(language)
    text = (
        f"▣ {sum(e['kind'] == 'capture' for e in block['events'])} {t('capturas')}"
        + f"   ·   ! {block['warning_count']} {t('advertencias')}"
    )
    if block.get("duration_seconds") is not None:
        text += f"   ·   ◷ {block['duration_seconds']:.2f} s"
    return text


def context(event):
    return " · ".join(str(event[key]) for key in ("page_title", "url") if event.get(key))


def render_document(case, blocks, target, format_name, *, language="en", branding=None):
    branding = branding or load_branding()
    if format_name == "pdf":
        render_pdf(case, blocks, target, language=language, branding=branding)
    else:
        render_docx(case, blocks, target, language=language, branding=branding)


def render_pdf(case, blocks, target, *, language="en", branding=None):
    from pathlib import Path
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    from reportlab.lib.utils import ImageReader

    from reportlab.platypus import KeepTogether

    branding = branding or load_branding()
    t = translator(language)
    from importlib.resources import files
    import reportlab

    bundled = Path(reportlab.__file__).parent / "fonts"
    pdfmetrics.registerFont(TTFont("EvidencePrint", str(bundled / "Vera.ttf")))
    pdfmetrics.registerFont(TTFont("EvidencePrintBold", str(bundled / "VeraBd.ttf")))
    pdfmetrics.registerFont(
        TTFont(
            "EvidenceSymbols",
            BytesIO(files("rf_evidence_reporter").joinpath("assets/symbols.ttf").read_bytes()),
        )
    )
    pdfmetrics.registerFontFamily(
        "EvidencePrint",
        normal="EvidencePrint",
        bold="EvidencePrintBold",
        italic="EvidencePrint",
        boldItalic="EvidencePrintBold",
    )
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = (
            "EvidencePrintBold" if style.name in {"Title", "Heading1", "Heading2"} else "EvidencePrint"
        )
    styles["Title"].alignment = TA_LEFT
    styles["Title"].fontSize, styles["Title"].leading = 21, 27
    styles["Title"].textColor = colors.HexColor("#17283e")
    styles.add(
        ParagraphStyle(
            "Body", fontName="EvidencePrint", fontSize=9, leading=14, spaceAfter=5, splitLongWords=True
        )
    )
    styles.add(
        ParagraphStyle(
            "Small", parent=styles["Body"], fontSize=8, leading=12, textColor=colors.HexColor("#52627c")
        )
    )
    styles.add(
        ParagraphStyle(
            "EvidenceTitle", parent=styles["Body"], fontName="EvidencePrintBold", fontSize=10, leading=15
        )
    )
    primary = branding["palette"]["primary"]
    width = A4[0] - 72
    story = []

    class MilestoneGap(Spacer):
        keepWithNext = True

    def markup(text):
        text = escape(str(text)).replace("\n", "<br/>")
        for symbol in "▣◷✓×":
            text = text.replace(symbol, '<font name="EvidenceSymbols">' + symbol + "</font>")
        return text

    def p(text, style="Body"):
        return Paragraph(markup(text), styles[style])

    def panel(title, content, accent, *, milestone=False, status=None):
        table = Table(
            [
                [title if isinstance(title, Table) else p(title, "EvidenceTitle")],
                [content or [p(t("Mensaje registrado"))]],
            ],
            colWidths=[width],
            hAlign="LEFT",
            splitInRow=1,
        )
        commands = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LINEBEFORE", (0, 0), (0, -1), 2, colors.HexColor(accent)),
        ]
        if milestone:
            commands.append(("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8f7fc")))
            table.keepWithNext = True
        else:
            commands.append(("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#dfe5ed")))
            commands.append(("LINEBEFORE", (0, 0), (0, -1), 2, colors.HexColor(accent)))
        table.setStyle(TableStyle(commands))
        if not milestone and table.wrap(width, 1000000)[1] < A4[1] - 108:
            return KeepTogether([table])
        return table

    story.extend([p(case["name"], "Title"), p(metrics(case, language)), Spacer(1, 10)])
    if case.get("description"):
        story.append(p(case["description"]))
    metadata = summary(case, language)
    rows = []
    for index in range(0, len(metadata), 2):
        pairs = metadata[index : index + 2]
        if len(pairs) == 1:
            pairs.append(("", ""))
        rows.append([p(value, "Small") for pair in pairs for value in pair])
    table = Table(
        rows, colWidths=[width * 0.18, width * 0.32, width * 0.18, width * 0.32], hAlign="LEFT", splitInRow=1
    )
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#e5eaf1")),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]
    for column in (0, 2):
        commands.append(("BACKGROUND", (column, 0), (column, -1), colors.HexColor("#f8f7fc")))
    table.setStyle(TableStyle(commands))
    story.extend([table, Spacer(1, 10)])
    if case.get("message"):
        story.append(p(t("Resultado") + ": " + case["message"]))
    if case.get("attempts"):
        story.append(p(t("Historial de intentos"), "Heading2"))
        for attempt in [*case["attempts"], case]:
            story.append(
                p(
                    f"{display_date(attempt['started_at'], language)} · {attempt['status']} · {attempt['message']}"
                )
            )
    for number, block in enumerate(blocks, 1):
        captures = [event for event in block["events"] if event["kind"] != "message"]
        if not captures:
            continue
        block_start = len(story)
        story.extend(
            [
                Spacer(1, 14),
                panel(
                    f"{number:02d}  {block['title']}",
                    [
                        p(block_metrics(block, language), "Small"),
                        *([p(block["description"])] if block.get("description") else []),
                    ],
                    primary,
                    milestone=True,
                ),
                MilestoneGap(1, 10),
            ]
        )
        for event_index, event in enumerate(captures):
            content = []
            if event.get("description"):
                content.append(p(event["description"]))
            if event.get("_image_bytes"):
                stream, (w, h) = printable_image(event)
                scale = min((width - 24) / w, 300 / h)
                content.append(Image(stream, width=w * scale, height=h * scale, hAlign="LEFT"))
            if context(event):
                content.append(p(context(event), "Small"))
            if event.get("reason"):
                content.append(p("! " + event["reason"]))
            level = event_level(event)
            status_style = ParagraphStyle(
                "EvidenceStatus",
                parent=styles["Small"],
                alignment=TA_RIGHT,
                textColor=colors.HexColor("#" + status_colors(level)[0]),
            )
            mark = "✓" if level == "PASS" else "×" if level == "FAIL" else "!" if level == "WARN" else "i"
            status = Paragraph(
                markup(f"{mark} {level} · {display_date(event.get('captured_at'), language)}"), status_style
            )
            title = Table(
                [[p(event["title"], "EvidenceTitle"), status]],
                colWidths=[(width - 24) * 0.55, (width - 24) * 0.45],
            )
            title.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )
            card = panel(title, content, "#" + status_colors(level)[0])
            if event_index == 0:
                group = story[block_start:]
                del story[block_start:]
                group.extend(card._content if isinstance(card, KeepTogether) else [card])
                story.append(KeepTogether(group))
            else:
                story.append(card)
            story.append(Spacer(1, 10))
    messages = [e for e in case["events"] if e["kind"] == "message"]
    if messages:
        story.extend([Spacer(1, 12), p(t("Logs"), "Heading2")])
        for block in blocks:
            logs = [e for e in block["events"] if e["kind"] == "message"]
            if not logs:
                continue
            heading = p(block["title"], "EvidenceTitle")
            heading.keepWithNext = True
            story.append(heading)
            for event in logs:
                story.append(p(f"{display_date(event['captured_at'], language)} · {event_text(event)}"))
                if event.get("reason") or event.get("description"):
                    story.append(p(event.get("reason") or event["description"]))

    def footer(canvas, document):
        canvas.saveState()
        canvas.drawImage(
            ImageReader(BytesIO(branding["logo_bytes"])),
            36,
            A4[1] - 48,
            width=26,
            height=26,
            preserveAspectRatio=True,
            mask="auto",
        )
        canvas.setFont("EvidencePrintBold", 9)
        canvas.setFillColor(colors.HexColor(primary))
        canvas.drawString(72, A4[1] - 37, branding["name"])
        canvas.setFont("EvidencePrint", 7)
        canvas.setFillColor(colors.HexColor("#52627c"))
        canvas.drawString(36, 23, footer_text(language))
        canvas.drawRightString(A4[0] - 36, 23, f"{t('Página')} {document.page}")
        canvas.restoreState()

    class ReportDocument(SimpleDocTemplate):
        def afterPage(self):
            footer(self.canv, self)

    ReportDocument(
        str(target),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=68,
        bottomMargin=40,
        title=case["name"],
        author="Evidence Reporter",
    ).build(story)


def render_docx(case, blocks, target, *, language="en", branding=None):
    from docx import Document
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_TAB_ALIGNMENT

    branding = branding or load_branding()
    primary = branding["palette"]["primary"].lstrip("#")
    t = translator(language)
    document = Document()
    section = document.sections[0]
    section.page_width, section.page_height = Inches(8.27), Inches(11.69)
    section.top_margin = section.bottom_margin = Inches(0.6)
    section.left_margin = section.right_margin = Inches(0.6)
    for name in ("Normal", "Title", "Heading 1", "Heading 2"):
        style = document.styles[name]
        style.font.name = "Calibri"
        style.font.color.rgb = RGBColor(0, 0, 0)
        for border in style._element.xpath(".//w:pBdr"):
            border.getparent().remove(border)
    document.styles["Normal"].font.size = Pt(9)
    document.styles["Normal"].paragraph_format.space_after = Pt(5)
    document.styles["Title"].font.size = Pt(21)
    document.styles["Title"].font.bold = True

    def shade(cell, color):
        shading = OxmlElement("w:shd")
        shading.set(qn("w:fill"), color)
        cell._tc.get_or_add_tcPr().append(shading)

    def borders(table, accent=None, milestone=False):
        borders = OxmlElement("w:tblBorders")
        for side in ("top", "left", "bottom", "right", "insideH"):
            edge = OxmlElement("w:" + side)
            edge.set(qn("w:val"), "nil" if milestone and side != "left" else "single")
            edge.set(qn("w:sz"), "12" if accent and side == "left" else "3")
            edge.set(qn("w:color"), accent if accent and side == "left" else "DFE5ED")
            borders.append(edge)
        table._tbl.tblPr.append(borders)
        margins = OxmlElement("w:tblCellMar")
        for side in ("top", "left", "bottom", "right"):
            node = OxmlElement("w:" + side)
            node.set(qn("w:w"), "120" if side in ("top", "bottom") else "180")
            node.set(qn("w:type"), "dxa")
            margins.append(node)
        table._tbl.tblPr.append(margins)

    def card(title, accent, *, milestone=False):
        table = document.add_table(rows=2, cols=1)
        table.autofit = False
        table.columns[0].width = Inches(7.07)
        borders(table, accent, milestone)
        header, body = table.cell(0, 0), table.cell(1, 0)
        if milestone:
            shade(header, "F8F7FC")
            shade(body, "F8F7FC")
        p = header.paragraphs[0]
        p.paragraph_format.keep_with_next = True
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(title)
        run.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor.from_string(accent if milestone else "17283E")
        return body

    def body_paragraph(cell, text):
        p = (
            cell.paragraphs[0]
            if not cell.paragraphs[0].text and not cell.paragraphs[0].runs
            else cell.add_paragraph()
        )
        p.add_run(str(text))
        return p

    brand = document.add_paragraph()
    brand.add_run().add_picture(BytesIO(branding["logo_bytes"]), width=Inches(0.32))
    run = brand.add_run("  " + branding["name"])
    run.bold = True
    run.font.color.rgb = RGBColor.from_string(primary)
    brand.paragraph_format.keep_with_next = True
    document.add_paragraph(case["name"], "Title")
    document.add_paragraph(metrics(case, language))
    if case.get("description"):
        document.add_paragraph(case["description"])
    metadata = summary(case, language)
    table = document.add_table(rows=0, cols=4)
    table.autofit = False
    for column, width in zip(table.columns, (1.27, 2.27, 1.27, 2.26)):
        column.width = Inches(width)
    borders(table)
    for index in range(0, len(metadata), 2):
        pairs = metadata[index : index + 2]
        if len(pairs) == 1:
            pairs.append(("", ""))
        cells = table.add_row().cells
        for cell, value in zip(cells, [value for pair in pairs for value in pair]):
            cell.text = str(value)
        for cell in (cells[0], cells[2]):
            shade(cell, "F8F7FC")
            for run in cell.paragraphs[0].runs:
                run.bold = True
                run.font.color.rgb = RGBColor.from_string(primary)
    if case.get("message"):
        document.add_paragraph(t("Resultado") + ": " + case["message"])
    if case.get("attempts"):
        document.add_heading(t("Historial de intentos"), 2)
        for attempt in [*case["attempts"], case]:
            document.add_paragraph(
                f"{display_date(attempt['started_at'], language)} · {attempt['status']} · {attempt['message']}"
            )
    for number, block in enumerate(blocks, 1):
        captures = [event for event in block["events"] if event["kind"] != "message"]
        if not captures:
            continue
        document.add_paragraph().paragraph_format.keep_with_next = True
        cell = card(f"{number:02d}  {block['title']}", primary, milestone=True)
        body_paragraph(cell, block_metrics(block, language)).paragraph_format.keep_with_next = True
        if block.get("description"):
            body_paragraph(cell, block["description"]).paragraph_format.keep_with_next = True
        document.add_paragraph().paragraph_format.keep_with_next = True
        for event in captures:
            level = event_level(event)
            cell = card(event["title"], status_colors(level)[0])
            header = cell._tc.getparent().getprevious()
            from docx.table import _Cell

            header_cell = _Cell(header[0], cell._parent)
            line = header_cell.paragraphs[0]
            line.paragraph_format.tab_stops.add_tab_stop(Inches(6.65), WD_TAB_ALIGNMENT.RIGHT)
            mark = "✓" if level == "PASS" else "×" if level == "FAIL" else "!" if level == "WARN" else "i"
            run = line.add_run(f"\t{mark} {level} · {display_date(event.get('captured_at'), language)}")
            run.font.size = Pt(8)
            run.font.color.rgb = RGBColor.from_string(status_colors(level)[0])
            if event.get("description"):
                body_paragraph(cell, event["description"])
            if event.get("_image_bytes"):
                stream, (width, height) = printable_image(event)
                scale = min(6.8 / width, 4.17 / height)
                p = body_paragraph(cell, "")
                p.add_run().add_picture(stream, width=Inches(width * scale), height=Inches(height * scale))
            if context(event):
                p = body_paragraph(cell, context(event))
                for run in p.runs:
                    run.font.size = Pt(8)
                    run.font.color.rgb = RGBColor.from_string("52627C")
            if event.get("reason"):
                body_paragraph(cell, "! " + event["reason"])
            for paragraph in cell.paragraphs[:-1]:
                paragraph.paragraph_format.keep_with_next = True
            document.add_paragraph().paragraph_format.space_after = Pt(2)
    if any(e["kind"] == "message" for e in case["events"]):
        document.add_heading(t("Logs"), 2)
        for block in blocks:
            logs = [e for e in block["events"] if e["kind"] == "message"]
            if not logs:
                continue
            document.add_heading(block["title"], 3)
            for event in logs:
                document.add_paragraph(
                    f"{display_date(event['captured_at'], language)} · {event_text(event)}"
                )
                if event.get("reason") or event.get("description"):
                    document.add_paragraph(event.get("reason") or event["description"])
    footer = section.footer.paragraphs[0]
    footer.add_run(footer_text(language) + " | " + t("Página") + " ")
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)
    for run in footer.runs:
        run.font.size = Pt(8)
    document.core_properties.title = case["name"]
    document.core_properties.author = "Evidence Reporter"
    document.save(target)
