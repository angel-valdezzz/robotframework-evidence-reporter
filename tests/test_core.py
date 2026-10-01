import json
import tempfile
import unittest
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from rf_evidence_reporter import EvidenceRecorder, EvidenceReporter, build_reports


def record_worker(root):
    recorder = EvidenceRecorder(root)
    identifier = recorder.start("Mismo nombre", "Paralelo")
    recorder.event("Evento independiente")
    recorder.finish("PASS", 1)
    return identifier


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.recorder = EvidenceRecorder(self.root / "raw")
        self.recorder.start('<script>alert("x")</script>', "Demo")

    def test_persistence_incomplete_and_escaping(self):
        self.recorder.event("<img onerror=alert(1)>")
        report = build_reports(self.root / "raw", self.root / "html")[0].read_text()
        self.assertIn("INCOMPLETE", report)
        self.assertIn("&lt;script&gt;", report)
        self.assertNotIn("<img onerror=", report)

    def test_warning_default_and_strict(self):
        library = EvidenceReporter()
        library.recorder = self.recorder
        missing = str(self.root / "missing.png")
        self.assertIsNone(library.attach_image_evidence(missing, "No existe"))
        self.assertEqual(self.recorder.case["events"][-1]["level"], "WARN")
        with self.assertRaisesRegex(RuntimeError, "CAPTURE_FAILED"):
            library.attach_image_evidence(missing, "Obligatoria", strict=True)
        self.assertEqual(self.recorder.case["status"], "INCOMPLETE")

    def test_browser_and_desktop_errors(self):
        library = EvidenceReporter()
        library.recorder = self.recorder
        library.capture_page_evidence("Sin navegador")
        self.assertIn("BROWSER_UNAVAILABLE", self.recorder.case["events"][-1]["reason"])
        with patch("rf_evidence_reporter.library.ImageGrab.grab", side_effect=OSError("no display")):
            library.capture_desktop_evidence("Sin escritorio")
        self.assertIn("DESKTOP_UNAVAILABLE", self.recorder.case["events"][-1]["reason"])

    def test_copy_embed_and_missing_image(self):
        image = self.root / "source.png"
        Image.new("RGB", (120, 80), "teal").save(image)
        library = EvidenceReporter()
        library.recorder = self.recorder
        milestone = library.create_milestone("Registro")
        library.attach_image_evidence(str(image), "Confirmación", milestone_id=milestone)
        image.unlink()
        self.recorder.finish("PASS", 2.5)
        report = build_reports(self.root / "raw", self.root / "html")[0].read_text()
        self.assertIn("data:image/png;base64,", report)
        self.assertIn("Registro", report)
        copied = next((self.root / "raw").rglob("*.png"))
        copied.unlink()
        with self.assertWarns(UserWarning):
            report = build_reports(self.root / "raw", self.root / "html")[0].read_text()
        self.assertIn("IMAGE_UNAVAILABLE", report)

    def test_path_traversal_not_embedded(self):
        self.recorder.event("Fuera del caso", kind="capture", image="../secret.png")
        with self.assertWarns(UserWarning):
            report = build_reports(self.root / "raw", self.root / "html")[0].read_text()
        self.assertIn("fuera del directorio", report)

    def test_metadata_and_unknown_milestone(self):
        self.recorder.metadata({"Estado": "Texto de negocio"})
        self.assertEqual(self.recorder.case["status"], "INCOMPLETE")
        with self.assertRaisesRegex(ValueError, "UNKNOWN_MILESTONE"):
            self.recorder.event("No válido", milestone_id="missing")

    def test_parallel_duplicate_names(self):
        with ProcessPoolExecutor(max_workers=4) as pool:
            identifiers = list(pool.map(record_worker, [str(self.root / "parallel")] * 8))
        self.assertEqual(len(set(identifiers)), 8)
        self.assertEqual(len(build_reports(self.root / "parallel", self.root / "reports")), 8)

    def test_no_cases_fails(self):
        with self.assertRaisesRegex(ValueError, "NO_CASES"):
            build_reports(self.root / "empty", self.root / "reports")

    def test_final_status_persisted(self):
        self.recorder.finish("SKIP", 1, "No aplica")
        case = json.loads(next((self.root / "raw").rglob("case.json")).read_text())
        self.assertEqual(case["status"], "SKIP")
        self.assertEqual(case["duration_seconds"], 1)

    def test_capture_status_independent_and_legacy_reports(self):
        image = self.root / "sample.png"
        Image.new("RGB", (40, 30), "blue").save(image)
        library = EvidenceReporter()
        library.recorder = self.recorder
        for status in ["INFO", "PASS", "WARN", "FAIL"]:
            library.attach_image_evidence(str(image), status, status=status.lower())
            self.assertEqual(self.recorder.case["events"][-1]["status"], status)
        with self.assertRaisesRegex(ValueError, "INVALID_CAPTURE_STATUS"):
            library.attach_image_evidence(str(image), "No válido", status="SKIP")
        self.assertEqual(len(self.recorder.case["events"]), 4)
        self.recorder.case["events"][0].pop("status")
        self.recorder.finish("PASS", 1)
        report = build_reports(self.root / "raw", self.root / "html")[0].read_text()
        self.assertIn('data-status="FAIL"', report)
        self.assertIn('data-status="INFO"', report)
        self.assertIn("execution-status PASS", report)
        self.assertNotIn("Estado de Robot", report)
        self.assertNotIn("Imprimir", report)
        self.assertIn("Estatus de ejecución", report)
        self.assertEqual(report.count('class="badge execution-status'), 1)

    def test_date_display_preserves_raw_timestamp(self):
        self.recorder.case["started_at"] = "2026-10-01T13:29:32.456-06:00"
        self.recorder.save()
        report = build_reports(self.root / "raw", self.root / "html")[0].read_text()
        self.assertIn("01/10/2026 · 13:29:32", report)
        self.assertIn("UTC-06:00", report)
        case = json.loads(next((self.root / "raw").rglob("case.json")).read_text())
        self.assertEqual(case["started_at"], "2026-10-01T13:29:32.456-06:00")
