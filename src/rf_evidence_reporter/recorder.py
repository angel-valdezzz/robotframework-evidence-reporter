"""Append evidence to independent, atomically replaced case files."""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from uuid import uuid4


def timestamp():
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def slug(text):
    return re.sub(r"[^\w-]+", "-", text, flags=re.UNICODE).strip("-")[:80] or "case"


class EvidenceRecorder:
    """One writer per case; no shared manifests, counters or browser state."""

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir).resolve()
        self.case = None
        self.case_dir = None

    def start(self, name, suite="", description="", tags=()):
        identifier = uuid4().hex
        self.case_dir = self.output_dir / f"{slug(name)}-{identifier}"
        self.case_dir.mkdir(parents=True, exist_ok=False)
        self.case = {
            "schema_version": 1,
            "id": identifier,
            "name": str(name),
            "suite": str(suite),
            "description": str(description),
            "tags": list(tags),
            "process_id": os.getpid(),
            "started_at": timestamp(),
            "ended_at": None,
            "duration_seconds": None,
            "status": "INCOMPLETE",
            "message": "",
            "metadata": {},
            "milestones": [],
            "events": [],
        }
        self.save()
        return identifier

    def require_case(self):
        if self.case is None:
            raise RuntimeError("NO_ACTIVE_CASE: la evidencia debe registrarse dentro de un caso de prueba.")

    def save(self):
        self.require_case()
        target = self.case_dir / "case.json"
        temporary = target.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.case, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(target)

    def milestone(self, title, description=""):
        self.require_case()
        identifier = uuid4().hex
        self.case["milestones"].append(
            {"id": identifier, "title": str(title), "description": str(description)}
        )
        self.save()
        return identifier

    def validate_milestone(self, identifier):
        self.require_case()
        if identifier and not any(item["id"] == identifier for item in self.case["milestones"]):
            raise ValueError("UNKNOWN_MILESTONE: el hito no pertenece al caso activo.")

    def metadata(self, values):
        self.require_case()
        self.case["metadata"].update({str(key): str(value) for key, value in values.items()})
        self.save()

    def event(self, title, kind="message", level="INFO", milestone_id=None, **fields):
        self.validate_milestone(milestone_id)
        event = {
            "id": uuid4().hex,
            "title": str(title),
            "kind": kind,
            "level": level,
            "milestone_id": milestone_id,
            "captured_at": timestamp(),
            **fields,
        }
        self.case["events"].append(event)
        self.save()
        return event["id"]

    def finish(self, status, duration_seconds, message=""):
        self.require_case()
        if status not in {"PASS", "FAIL", "SKIP"}:
            raise ValueError(f"Unsupported Robot status: {status}")
        self.case.update(
            status=status,
            duration_seconds=float(duration_seconds),
            message=str(message),
            ended_at=timestamp(),
        )
        self.save()
        self.case = None
