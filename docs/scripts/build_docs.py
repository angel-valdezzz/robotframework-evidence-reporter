"""Build the bilingual manual and keyword reference."""

import shutil
import subprocess
import sys
from pathlib import Path

from bilingual_libdoc import generate
from bilingual_site import build

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    # Seed the documented social plugin font cache from licensed local assets.
    # Builds and browsers need no connection to Google Fonts.
    for config_dir in (ROOT, ROOT / "docs/config"):
        fonts = config_dir / ".cache/plugin/social/fonts/DejaVu Sans"
        fonts.mkdir(parents=True, exist_ok=True)
        for source in (ROOT / "docs/assets/fonts").glob("*.ttf"):
            shutil.copyfile(source, fonts / source.name)
    subprocess.run([sys.executable, "docs/scripts/demo.py"], cwd=ROOT, check=True)
    generate(
        "EvidenceReporter",
        ROOT,
        "reference/keywords.html",
        "https://angel-valdezzz.github.io/robotframework-evidence-reporter/",
    )
    build(ROOT, ("assets", "demo"))


if __name__ == "__main__":
    main()
