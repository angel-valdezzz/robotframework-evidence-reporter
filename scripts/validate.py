"""Robot/Pabot acceptance checks, including an intentionally failing teardown."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image
from rf_evidence_reporter import build_reports


def run(arguments, expected=0):
    result = subprocess.run([sys.executable, "-m", *arguments], check=False)
    if result.returncode != expected:
        raise SystemExit(f"Expected exit {expected}, got {result.returncode}: {arguments}")


for directory in [
    "results/integration",
    "results/parallel",
    "results/parallel/pabot_results",
    "results/skip",
]:
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
cases = [json.loads(p.read_text()) for p in Path("results/parallel/pabot_results").rglob("case.json")]
assert len(cases) == 4, cases
assert all(case["status"] == "PASS" for case in cases)
assert len({case["process_id"] for case in cases}) >= 2
assert len(build_reports("results/parallel/pabot_results", "results/parallel/html")) == 4
print("Robot/Pabot acceptance passed: final teardown status, SKIP, warnings and isolated writers.")

fixture = Path("results/skip-fixture.png").resolve()
Image.new("RGB", (20, 20), "white").save(fixture)
run(["robot", "--variable", f"IMAGE_PATH:{fixture}", "--outputdir", "results/skip", "tests/skip.robot"])
cases = [json.loads(p.read_text()) for p in Path("results/skip/evidence").rglob("case.json")]
assert len(cases) == 4, cases
assert all(case["status"] == "SKIP" for case in cases)
for case in cases:
    if case["name"] == "Omitido Después De Capturar":
        assert len(case["events"]) == 1
        assert case["events"][0]["kind"] == "capture"
        assert case["events"][0]["status"] == "INFO"
    else:
        assert case["events"] == [], case
assert len(build_reports("results/skip/evidence", "results/skip/html")) == 4
print("SKIP acceptance passed: empty initial omissions and preserved earlier capture.")
