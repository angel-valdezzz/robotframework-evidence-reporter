"""Build the English root and Spanish subtree from matching source pages."""

import shutil
import subprocess
import sys
from pathlib import Path


def build(root: Path, shared: tuple[str, ...] = ("assets",)) -> None:
    pages = [
        {str(p.relative_to(root / "docs" / lang)) for p in (root / "docs" / lang).rglob("*.md")}
        for lang in ("en", "es")
    ]
    if pages[0] != pages[1]:
        raise ValueError(f"Documentation pages differ between languages: {pages[0] ^ pages[1]}")
    for language in ("en", "es"):
        for directory in shared:
            source = root / "docs" / directory
            if source.is_dir():
                shutil.copytree(source, root / "docs" / language / directory, dirs_exist_ok=True)
    for config in ("mkdocs.yml", "docs/config/es.yml"):
        subprocess.run(
            [sys.executable, "-m", "mkdocs", "build", "--strict", "-f", config], cwd=root, check=True
        )
    shutil.copytree(root / "build/site-es", root / "site/es", dirs_exist_ok=True)
