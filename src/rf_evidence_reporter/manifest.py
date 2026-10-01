"""File inventory generated after all writers finish."""

import hashlib
import json
import os
from pathlib import Path

from .recorder import timestamp


def file_entry(path, root, kind):
    path = Path(path).resolve()
    return {
        "path": Path(os.path.relpath(path, root)).as_posix(),
        "type": kind,
        "size_bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def write_manifest(destination, records):
    destination = Path(destination).resolve()
    payload = {"schema_version": 1, "generated_at": timestamp(), "cases": records}
    target = destination / "manifest.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(target)
    return target
