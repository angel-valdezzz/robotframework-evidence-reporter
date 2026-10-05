"""Build the bilingual manual and keyword reference."""

import subprocess
import sys
from pathlib import Path

from bilingual_libdoc import generate
from bilingual_site import build

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    subprocess.run([sys.executable, "scripts/demo.py"], cwd=ROOT, check=True)
    generate(
        "EvidenceReporter",
        ROOT,
        "reference/keywords.html",
        "https://angel-valdezzz.github.io/robotframework-evidence-reporter/",
    )
    build(ROOT, ("assets", "demo"))


if __name__ == "__main__":
    main()
