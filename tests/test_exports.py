"""Contracts for portable exports, ordered reruns and original evidence retention."""

import base64
import hashlib
import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from docx import Document
from PIL import Image
from pypdf import PdfReader

from rf_evidence_reporter import EvidenceRecorder, EvidenceReporter, build_reports, merge_results


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def case(self, run, status="PASS", name="Registrar cliente", suite="Portal"):
        recorder = EvidenceRecorder(self.root / run)
        recorder.start(name, suite, "Reporte de negocio con datos ficticios")
        recorder.metadata({"Aplicación": "Portal de clientes", "Requerimiento": "QA-123"})
        image = self.root / "image.png"
        Image.new("RGBA", (2400, 1200), "#15314b").save(image)
        library = EvidenceReporter()
        library.recorder = recorder
        milestone = recorder.milestone("Cliente registrado", "Confirmación de alta")
        library.attach_image_evidence(str(image), "Confirmación", milestone_id=milestone, status="PASS")
        recorder.event("Mensaje de negocio", milestone_id=milestone)
        recorder.finish(status, 1.5, f"Resultado {status}")
        return recorder.case_dir

    def test_formats_preserve_hierarchy_and_manifest_checksums(self):
        directory = self.case("run")
        output = self.root / "reports"
        paths = build_reports(directory, output, formats=("html", "pdf", "docx"))
        self.assertEqual({p.suffix for p in paths}, {".html", ".pdf", ".docx"})
        pdf = PdfReader(next(p for p in paths if p.suffix == ".pdf"))
        text = "\n".join(page.extract_text() for page in pdf.pages)
        doc = Document(next(p for p in paths if p.suffix == ".docx"))
        doc_text = "\n".join(p.text for p in doc.paragraphs)
        for expected in ["Cliente registrado", "Confirmación", "Mensaje de negocio"]:
            self.assertIn(expected, text)
            self.assertIn(expected, doc_text)
        self.assertEqual(len(doc.inline_shapes), 1)
        manifest = json.loads((output / "manifest.json").read_text())
        record = manifest["cases"][0]
        self.assertEqual(record["status"], "PASS")
        self.assertEqual({f["type"] for f in record["files"]}, {"html", "pdf", "docx", "case_json", "image"})
        for item in record["files"]:
            path = output / item["path"]
            self.assertEqual(path.stat().st_size, item["size_bytes"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), item["sha256"])

    def test_resize_keeps_original_and_full_aspect_ratio(self):
        directory = self.case("run")
        original = next(directory.glob("*.png"))
        before = original.read_bytes()
        html = build_reports(directory, self.root / "reports", max_image_width=600, image_quality=80)[
            0
        ].read_text()
        payload = html.split("data:image/webp;base64,")[1].split('"')[0]
        with Image.open(BytesIO(base64.b64decode(payload))) as image:
            self.assertEqual(image.size, (600, 300))
        self.assertEqual(original.read_bytes(), before)
        with self.assertRaisesRegex(ValueError, "INVALID_IMAGE_QUALITY"):
            build_reports(directory, self.root / "bad", image_quality=101)

    def test_merge_last_input_wins_and_history_is_portable(self):
        self.case("run", "FAIL")
        self.case("run", "PASS", "Otro caso")
        self.case("rerun", "PASS")
        result = merge_results([self.root / "run", self.root / "rerun"], self.root / "merged")
        self.assertEqual(len(result), 2)
        selected = next(p for p in result if json.loads(p.read_text())["name"] == "Registrar cliente")
        case = json.loads(selected.read_text())
        self.assertEqual(case["status"], "PASS")
        self.assertEqual(case["attempts"][0]["status"], "FAIL")
        self.assertNotEqual(case["events"][0]["image"], case["attempts"][0]["events"][0]["image"])
        import shutil

        shutil.rmtree(self.root / "run")
        shutil.rmtree(self.root / "rerun")
        for attempt in [case, *case["attempts"]]:
            for event in attempt["events"]:
                if event.get("image"):
                    self.assertTrue((selected.parent / event["image"]).is_file())
        outputs = build_reports(self.root / "merged", self.root / "reports", formats="html,pdf,docx")
        self.assertEqual(len(outputs), 6)
        self.assertIn(
            "Historial de intentos",
            next(p for p in outputs if p.suffix == ".html" and "Registrar" in p.name).read_text(),
        )

    def test_merge_rejects_duplicates_overlap_and_nonempty_output(self):
        self.case("run")
        self.case("run")
        self.case("rerun")
        with self.assertRaisesRegex(ValueError, "AMBIGUOUS_CASE"):
            merge_results([self.root / "run", self.root / "rerun"], self.root / "merged")
        self.assertFalse((self.root / "merged").exists())
        with self.assertRaisesRegex(ValueError, "MERGE_OVERLAP"):
            merge_results([self.root / "run", self.root / "rerun"], self.root / "run" / "merged")

    def test_later_skip_wins_and_cases_from_other_suites_stay_distinct(self):
        self.case("run", "FAIL")
        self.case("run", "PASS", suite="Otro portal")
        self.case("rerun", "SKIP")
        merged = merge_results([self.root / "run", self.root / "rerun"], self.root / "merged")
        records = [json.loads(p.read_text()) for p in merged]
        self.assertEqual(len(records), 2)
        self.assertEqual(next(c for c in records if c["suite"] == "Portal")["status"], "SKIP")
        self.assertEqual(next(c for c in records if c["suite"] == "Otro portal")["status"], "PASS")
