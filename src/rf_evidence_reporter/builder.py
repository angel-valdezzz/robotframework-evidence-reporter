"""Generate portable HTML from recorded JSON without a browser or Robot execution."""

import base64
import json
import warnings
from pathlib import Path
from datetime import datetime

from jinja2 import Environment, PackageLoader, select_autoescape

from .recorder import slug, timestamp


def display_date(value):
    if not value:
        return "No registrado"
    return datetime.fromisoformat(value).strftime("%d/%m/%Y · %H:%M:%S")


def timezone_label(value):
    offset = datetime.fromisoformat(value).strftime("%z")
    return "UTC" + offset[:3] + ":" + offset[3:] if offset else "Sin zona horaria"


def build_reports(results_dir, output_dir):
    """Return generated HTML Paths. One HTML per recorded case, never a global dashboard.

    Invalid case files fail generation clearly. Missing/invalid images become visible warnings.
    Input image references must remain inside their case directory.
    """
    root = Path(results_dir).resolve()
    files = sorted(root.rglob("case.json"))
    if not files:
        raise ValueError(f"NO_CASES: no hay archivos case.json en {root}")
    destination = Path(output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    environment = Environment(
        loader=PackageLoader("rf_evidence_reporter", "templates"), autoescape=select_autoescape(["html"])
    )
    environment.filters["display_date"] = display_date
    environment.filters["timezone_label"] = timezone_label
    template = environment.get_template("report.html")
    generated = []
    for source in files:
        case = json.loads(source.read_text(encoding="utf-8"))
        if case.get("schema_version") != 1:
            raise ValueError(f"UNSUPPORTED_SCHEMA: {source}")
        # Validate the minimum identity needed for a reliable report filename.
        if not isinstance(case.get("id"), str) or not case["id"] or not isinstance(case.get("name"), str):
            raise ValueError(f"INVALID_CASE: {source}")
        if case.get("status") not in {"PASS", "FAIL", "SKIP", "INCOMPLETE"}:
            raise ValueError(f"INVALID_STATUS: {source}")
        for event in case["events"]:
            event.setdefault("status", "WARN" if event["kind"] == "capture_warning" else "INFO")
            if event["status"] not in {"INFO", "PASS", "WARN", "FAIL"}:
                raise ValueError(f"INVALID_CAPTURE_STATUS: {source}")
            if event.get("image"):
                path = (source.parent / event["image"]).resolve()
                try:
                    if not path.is_relative_to(source.parent.resolve()):
                        raise ValueError("referencia fuera del directorio del caso")
                    from PIL import Image

                    with Image.open(path) as image:
                        image.verify()
                        mime = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}[image.format]
                    event["image_data"] = f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"
                except (OSError, ValueError, KeyError) as error:
                    event.update(
                        kind="capture_warning",
                        level="WARN",
                        status="WARN",
                        reason=f"IMAGE_UNAVAILABLE: {error}",
                    )
                    warnings.warn(f"{source}: {event['reason']}", stacklevel=2)
        case["warning_count"] = sum(
            event.get("level") == "WARN" or event.get("status") == "WARN" for event in case["events"]
        )
        blocks = []
        # Blocks follow first evidence appearance; evidence within each block retains its order.
        direct = [event for event in case["events"] if not event.get("milestone_id")]
        if direct:
            blocks.append({"title": "Evidencias del caso", "description": "", "events": direct})
        for milestone in case["milestones"]:
            blocks.append(
                {
                    **milestone,
                    "events": [
                        event for event in case["events"] if event.get("milestone_id") == milestone["id"]
                    ],
                }
            )
        name = f"{slug(case['name'])}-{slug(case['id'])}.html"
        target = destination / name
        target.write_text(
            template.render(case=case, blocks=blocks, generated_at=timestamp()), encoding="utf-8"
        )
        generated.append(target)
    return generated
