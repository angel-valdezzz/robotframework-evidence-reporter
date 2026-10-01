"""Check the installed wheel outside the editable project/source directory."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

wheel = next(Path("dist").glob("*.whl")).resolve()
with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    target = root / "installed"
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-deps", "--target", str(target), str(wheel)],
        check=True,
    )
    # sys.path starts at the wheel contents, not the checkout or Poetry's editable package.
    code = """
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import EvidenceReporter
import rf_evidence_reporter
from robot.libdocpkg import LibraryDocumentation
assert Path(EvidenceReporter.__file__).is_relative_to(Path(sys.argv[1]))
assert Path(rf_evidence_reporter.__file__).is_relative_to(Path(sys.argv[1]))
spec = LibraryDocumentation('EvidenceReporter')
assert len(spec.keywords) == 7
spec.save(sys.argv[2], format='JSON')
from robot import run
assert run(sys.argv[3], outputdir=sys.argv[4]) == 0
"""
    suite = root / "smoke.robot"
    suite.write_text(
        "*** Settings ***\nLibrary    EvidenceReporter\n"
        "*** Test Cases ***\nImportar Librería Publicada\n"
        "    Add Evidence Message    Importación corta desde el wheel.\n",
        encoding="utf-8",
    )
    subprocess.run(
        [
            sys.executable,
            "-c",
            code,
            str(target),
            str(root / "libdoc.json"),
            str(suite),
            str(root / "results"),
        ],
        cwd=root,
        check=True,
    )
    cases = list((root / "results/evidence").rglob("case.json"))
    assert len(cases) == 1
    assert json.loads(cases[0].read_text())["status"] == "PASS"
print("Installed wheel passed: EvidenceReporter import, seven keywords, listener and packaged code.")
