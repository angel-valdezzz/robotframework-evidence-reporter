"""Print formats preserve the same case, milestone and evidence hierarchy as HTML."""

from io import BytesIO
from xml.sax.saxutils import escape

from .builder import display_date, timezone_label


def summary(case):
    rows = [
        ("Suite", case["suite"]),
        ("Estatus de ejecución", case["status"]),
        ("Inicio", display_date(case["started_at"])),
        ("Fin", display_date(case["ended_at"])),
        ("Zona horaria", timezone_label(case["started_at"])),
        (
            "Duración",
            f"{case['duration_seconds']:.2f} s" if case["duration_seconds"] is not None else "Sin finalizar",
        ),
    ]
    return [*rows, *case["metadata"].items()]


def event_text(event):
    level = event.get("level", "INFO") if event["kind"] == "message" else event.get("status", "INFO")
    return f"{level} | {event['title']}"


def printable_image(event):
    # Native print engines consistently support PNG, including transparent WebP sources.
    from PIL import Image

    with Image.open(BytesIO(event["_image_bytes"])) as image:
        image.load()
        content = BytesIO()
        image.save(content, format="PNG")
        content.seek(0)
        return content, image.size


def render_document(case, blocks, target, format_name):
    if format_name == "pdf":
        render_pdf(case, blocks, target)
    else:
        render_docx(case, blocks, target)


def render_pdf(case, blocks, target):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        Image,
        KeepTogether,
        PageBreak,
    )
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from pathlib import Path
    import reportlab

    fonts = Path(reportlab.__file__).parent / "fonts"
    pdfmetrics.registerFont(TTFont("EvidenceVera", str(fonts / "Vera.ttf")))
    pdfmetrics.registerFont(TTFont("EvidenceVeraBold", str(fonts / "VeraBd.ttf")))
    pdfmetrics.registerFontFamily(
        "EvidenceVera",
        normal="EvidenceVera",
        bold="EvidenceVeraBold",
        italic="EvidenceVera",
        boldItalic="EvidenceVeraBold",
    )

    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = (
            "EvidenceVeraBold" if "Heading" in style.name or style.name == "Title" else "EvidenceVera"
        )
    styles.add(ParagraphStyle("Evidence", parent=styles["Normal"], fontSize=9, leading=13, spaceAfter=8))
    styles.add(ParagraphStyle("BlockDescription", parent=styles["Evidence"], keepWithNext=True))
    styles["Title"].alignment = TA_LEFT
    styles["Title"].fontSize = 21
    styles["Title"].leading = 26
    styles["Heading1"].fontSize = 15
    styles["Heading1"].leading = 19
    styles["Normal"].leading = 14
    story = []

    def paragraph(text, style="Evidence"):
        # Escape markup and allow long unbroken metadata to wrap inside tables.
        return Paragraph(escape(str(text)).replace("\n", "<br/>"), styles[style])

    story.extend([paragraph("Evidence Reporter"), paragraph(case["name"], "Title")])
    if case["description"]:
        story.append(paragraph(case["description"]))
    rows = [[paragraph(key), paragraph(value)] for key, value in summary(case)]
    table = Table(rows, colWidths=[1.5 * inch, 5.05 * inch], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef0fa")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#d9deeb")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.extend([table, Spacer(1, 12)])
    if case["message"]:
        story.append(paragraph(case["message"]))
    if case.get("attempts"):
        story.append(paragraph("Historial de intentos", "Heading1"))
        for attempt in [*case["attempts"], case]:
            story.append(
                paragraph(
                    f"{display_date(attempt['started_at'])} | {attempt['status']} | {attempt['message']}"
                )
            )
    captures_on_page = 0
    for block in blocks:
        if block.get("id"):
            story.append(PageBreak())
            captures_on_page = 0
        story.append(paragraph(block["title"], "Heading1"))
        if block["description"]:
            story.append(paragraph(block["description"], "BlockDescription"))
        for event in block["events"]:
            content = [paragraph(event_text(event), "Heading2")]
            if event.get("description"):
                content.append(paragraph(event["description"]))
            if event.get("_image_bytes"):
                if captures_on_page == 2:
                    story.append(PageBreak())
                    captures_on_page = 0
                captures_on_page += 1
                stream, (width, height) = printable_image(event)
                scale = min(6.55 * inch / width, 3.15 * inch / height, 1)
                content.append(Image(stream, width=width * scale, height=height * scale, hAlign="LEFT"))
                content.append(paragraph(display_date(event["captured_at"])))
                # Keep each caption and full screenshot together. The bounded height avoids oversized pages.
                story.append(KeepTogether(content))
            else:
                story.extend(content)
            if event.get("reason"):
                story.append(paragraph(event["reason"]))
            story.append(Spacer(1, 8))

    def footer(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#52657c"))
        canvas.drawString(36, 23, "Evidence Reporter | Reporte individual de negocio")
        canvas.drawRightString(A4[0] - 36, 23, f"Página {document.page}")
        canvas.restoreState()

    SimpleDocTemplate(
        str(target),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=40,
        title=case["name"],
        author="Evidence Reporter",
    ).build(story, onFirstPage=footer, onLaterPages=footer)


def render_docx(case, blocks, target):
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    document = Document()
    section = document.sections[0]
    section.page_width, section.page_height = Inches(8.27), Inches(11.69)
    section.top_margin = section.bottom_margin = Inches(0.6)
    section.left_margin = section.right_margin = Inches(0.6)
    for name in ["Normal", "Title", "Heading 1", "Heading 2"]:
        style = document.styles[name]
        style.font.name = "Calibri"
        style.font.color.rgb = RGBColor(0, 0, 0)
        if style._element.pPr is not None:
            for border in list(style._element.pPr.findall(qn("w:pBdr"))):
                style._element.pPr.remove(border)
    document.styles["Normal"].font.size = Pt(10)
    document.styles["Normal"].paragraph_format.space_after = Pt(6)
    document.styles["Title"].font.size = Pt(22)
    document.add_paragraph("Evidence Reporter")
    document.add_paragraph(case["name"], "Title")
    if case["description"]:
        document.add_paragraph(case["description"])
    table = document.add_table(rows=0, cols=2)
    table.style = "Table Grid"
    table.autofit = False
    table.columns[0].width = Inches(1.5)
    table.columns[1].width = Inches(5.57)
    for key, value in summary(case):
        cells = table.add_row().cells
        cells[0].text, cells[1].text = str(key), str(value)
        cells[0].width, cells[1].width = Inches(1.5), Inches(5.5)
        for run in cells[0].paragraphs[0].runs:
            run.bold = True
    document.add_paragraph(case["message"])
    if case.get("attempts"):
        document.add_heading("Historial de intentos", 1)
        for attempt in [*case["attempts"], case]:
            document.add_paragraph(
                f"{display_date(attempt['started_at'])} | {attempt['status']} | {attempt['message']}"
            )
    captures_on_page = 0
    for block in blocks:
        if block.get("id"):
            document.add_page_break()
            captures_on_page = 0
        document.add_heading(block["title"], 1)
        if block["description"]:
            description = document.add_paragraph(block["description"])
            description.paragraph_format.keep_with_next = True
        for event in block["events"]:
            if event.get("_image_bytes"):
                if captures_on_page == 2:
                    document.add_page_break()
                    captures_on_page = 0
                captures_on_page += 1
            document.add_heading(event_text(event), 2)
            if event.get("description"):
                description = document.add_paragraph(event["description"])
                description.paragraph_format.keep_with_next = bool(event.get("_image_bytes"))
            if event.get("_image_bytes"):
                stream, (width, height) = printable_image(event)
                scale = min(6.9 / width, 3.15 / height, 1 / 96)
                p = document.add_paragraph()
                p.paragraph_format.keep_with_next = True
                p.add_run().add_picture(stream, width=Inches(width * scale), height=Inches(height * scale))
                document.add_paragraph(display_date(event["captured_at"]))
            if event.get("reason"):
                document.add_paragraph(event["reason"])
    footer = section.footer.paragraphs[0]
    footer.add_run("Evidence Reporter | Página ")
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)
    document.core_properties.title = case["name"]
    document.core_properties.author = "Evidence Reporter"
    document.save(target)
