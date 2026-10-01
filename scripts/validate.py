"""Robot/Pabot acceptance checks, including an intentionally failing teardown."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

from rf_evidence_reporter import build_reports


def run(arguments, expected=0):
    result = subprocess.run([sys.executable, "-m", *arguments], check=False)
    if result.returncode != expected:
        raise SystemExit(f"Expected exit {expected}, got {result.returncode}: {arguments}")


for directory in ["results/integration", "results/parallel", "results/parallel-evidence"]:
    shutil.rmtree(directory, ignore_errors=True)

run(["robot", "--outputdir", "results/integration", "tests/integration.robot"], expected=1)
cases = [json.loads(p.read_text()) for p in Path("results/integration/evidence").rglob("case.json")]
assert len(cases) == 5, cases
by_name = {case["name"]: case for case in cases}
assert by_name["Estado Final Incluye Teardown"]["status"] == "FAIL"
assert by_name["Caso Omitido"]["status"] == "SKIP"
assert by_name["Evidencias Directas"]["status"] == "PASS"
assert by_name["Evidencias Directas"]["events"][-1]["level"] == "WARN"
assert len(build_reports("results/integration/evidence", "results/integration/html")) == 5
run(
    [
        "pabot.pabot",
        "--no-pabotlib",
        "--processes",
        "2",
        "--testlevelsplit",
        "--outputdir",
        "results/parallel",
        "tests/parallel.robot",
    ]
)
cases = [json.loads(p.read_text()) for p in Path("results/parallel-evidence").rglob("case.json")]
assert len(cases) == 4, cases
assert all(case["status"] == "PASS" for case in cases)
assert len({case["process_id"] for case in cases}) >= 2
assert len(build_reports("results/parallel-evidence", "results/parallel/html")) == 4
print("Robot/Pabot acceptance passed: final teardown status, SKIP, warnings and isolated writers.")
