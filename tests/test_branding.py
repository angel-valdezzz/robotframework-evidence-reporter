"""Institution branding is portable and never changes recorded data or semantic states."""

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from rf_evidence_reporter.branding import load_branding


class BrandingTests(unittest.TestCase):
    def test_relative_logo_and_accessible_palette(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            Image.new("RGB", (900, 300), "#164e63").save(root / "logo.png")
            config = root / "brand.json"
            config.write_text(
                json.dumps(
                    {"name": "Institution <QA>", "logo": "logo.png", "palette": {"primary": "#164e63"}}
                )
            )
            brand = load_branding(config)
            self.assertEqual(brand["name"], "Institution <QA>")
            self.assertTrue(brand["logo_data"].startswith("data:image/png;base64,"))
            self.assertEqual(brand["palette"]["primary"], "#164e63")
            from io import BytesIO

            with Image.open(BytesIO(brand["logo_bytes"])) as image:
                self.assertEqual(image.size, (512, 171))

    def test_invalid_and_low_contrast_configuration_is_rejected(self):
        for config in (
            {"palette": {"primary": "#ffffff"}},
            {"palette": {"primary_dark": "#151d32"}},
            {"palette": {"primary": "red;display:none"}},
            {"palette": {"fail": "#164e63"}},
            {"name": ""},
            {"extra": True},
        ):
            with self.subTest(config=config), self.assertRaisesRegex(ValueError, "INVALID_BRANDING"):
                load_branding(config)

    def test_rebuild_all_formats_preserves_case_and_status(self):
        from rf_evidence_reporter import EvidenceRecorder, build_reports
        from pypdf import PdfReader
        from docx import Document

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            recorder = EvidenceRecorder(root / "raw")
            recorder.start("Branded execution")
            recorder.event("Warning", level="WARN")
            recorder.finish("FAIL", 1, "Expected failure")
            source = recorder.case_dir / "case.json"
            before = source.read_bytes()
            paths = build_reports(
                root / "raw",
                root / "reports",
                formats=("html", "pdf", "docx"),
                brand_config={"name": "Institution <QA>", "palette": {"primary": "#164e63"}},
            )
            html = next(p for p in paths if p.suffix == ".html").read_text()
            self.assertIn("Institution &lt;QA&gt;", html)
            self.assertIn("#164e63", html)
            self.assertIn("FAIL", html)
            self.assertIn("WARN", html)
            pdf = PdfReader(next(p for p in paths if p.suffix == ".pdf"))
            self.assertIn("Institution <QA>", pdf.pages[0].extract_text())
            doc = Document(next(p for p in paths if p.suffix == ".docx"))
            self.assertIn("Institution <QA>", doc.paragraphs[0].text)
            self.assertEqual(before, source.read_bytes())
