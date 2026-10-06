"""Output settings resolve at test start and retain import compatibility."""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from rf_evidence_reporter import EvidenceReporter


class OutputDirectoryTests(unittest.TestCase):
    def test_output_directory_precedence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for explicit, variable, expected in [
                (None, None, root / "robot" / "evidence"),
                (None, str(root / "variable"), root / "variable"),
                (str(root / "explicit"), str(root / "variable"), root / "explicit"),
            ]:
                with self.subTest(explicit=explicit, variable=variable):
                    values = {"${OUTPUTDIR}": str(root / "robot"), "${EVIDENCE_OUTPUT_DIR}": variable}
                    with patch("rf_evidence_reporter.library.BuiltIn") as builtin:
                        builtin.return_value.get_variable_value.side_effect = values.get
                        library = EvidenceReporter(output_dir=explicit)
                        library.start_test(
                            SimpleNamespace(doc=""),
                            SimpleNamespace(name="Case", parent=SimpleNamespace(full_name="Suite"), tags=[]),
                        )
                    cases = list(expected.rglob("case.json"))
                    self.assertEqual(len(cases), 1)
                    self.assertTrue(library.recorder.case_dir.is_relative_to(expected))
