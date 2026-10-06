"""Locale changes interface text without changing evidence or metadata."""

import tempfile
import unittest
from pathlib import Path
from docx import Document
from pypdf import PdfReader
from rf_evidence_reporter import EvidenceRecorder, build_reports


class LocaleTests(unittest.TestCase):
    def test_rebuild_same_case_in_both_languages_and_all_formats(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            recorder = EvidenceRecorder(root / "raw")
            recorder.start("Resumen — caller content", "Suite")
            recorder.metadata({"Application": "Resumen"})
            recorder.event("Advertencias — caller content")
            recorder.finish("PASS", 1)
            before = (recorder.case_dir / "case.json").read_bytes()
            for lang, label, footer in [
                ("en", "Execution status", "Generated with"),
                ("es", "Estatus de ejecución", "Generado con"),
            ]:
                paths = build_reports(
                    root / "raw", root / lang, language=lang, formats=("html", "pdf", "docx")
                )
                html = next(p for p in paths if p.suffix == ".html").read_text()
                self.assertIn(f'lang="{lang}"', html)
                self.assertIn(label, html)
                self.assertIn(footer, html)
                self.assertIn("Resumen — caller content", html)
                self.assertIn("Advertencias — caller content", html)
                self.assertNotIn("Reporte individual de evidencias de negocio", html)
                pdf = PdfReader(next(p for p in paths if p.suffix == ".pdf"))
                self.assertIn(footer, " ".join(page.extract_text() for page in pdf.pages))
                doc = Document(next(p for p in paths if p.suffix == ".docx"))
                self.assertIn(footer, doc.sections[0].footer.paragraphs[0].text)
            self.assertEqual(before, (recorder.case_dir / "case.json").read_bytes())
            with self.assertRaisesRegex(ValueError, "INVALID_LANGUAGE"):
                build_reports(root / "raw", root / "bad", language="fr")
            self.assertFalse((root / "bad").exists())
