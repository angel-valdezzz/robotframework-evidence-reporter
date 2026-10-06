"""Generate portable HTML from recorded JSON without a browser or Robot execution."""

import base64
import json
import warnings
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from .branding import load_branding
from .i18n import footer_text, translator
from .images import image_bytes
from .manifest import file_entry, write_manifest
from .recorder import slug, timestamp


def display_date(value, language="en"):
    if not value:
        return translator(language)("No registrado")
    return datetime.fromisoformat(value).strftime("%d/%m/%Y · %H:%M:%S")


def timezone_label(value, language="en"):
    offset = datetime.fromisoformat(value).strftime("%z")
    return "UTC" + offset[:3] + ":" + offset[3:] if offset else translator(language)("Sin zona horaria")


def build_reports(
    results_dir,
    output_dir,
    *,
    formats=("html",),
    max_image_width=None,
    image_quality=None,
    language="en",
    brand_config=None,
):
    """Return generated HTML Paths. One HTML per recorded case, never a global dashboard.

    Invalid case files fail generation clearly. Missing/invalid images become visible warnings.
    Input image references must remain inside their case directory.
    """
    t = translator(language)
    branding = load_branding(brand_config)
    if isinstance(formats, str):
        formats = formats.split(",")
    formats = tuple(dict.fromkeys(item.strip().lower() for item in formats))
    if not formats or any(item not in {"html", "pdf", "docx"} for item in formats):
        raise ValueError("INVALID_FORMAT: formatos válidos html,pdf,docx")
    if max_image_width is not None and (not isinstance(max_image_width, int) or max_image_width < 1):
        raise ValueError("INVALID_IMAGE_WIDTH: se requiere un entero positivo")
    if image_quality is not None and (not isinstance(image_quality, int) or not 1 <= image_quality <= 100):
        raise ValueError("INVALID_IMAGE_QUALITY: rango 1 a 100")
    root = Path(results_dir).resolve()
    files = sorted(root.rglob("case.json"))
    if not files:
        raise ValueError(f"NO_CASES: no hay archivos case.json en {root}")
    destination = Path(output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    environment = Environment(
        loader=PackageLoader("rf_evidence_reporter", "templates"), autoescape=select_autoescape(["html"])
    )
    environment.filters["display_date"] = lambda value: display_date(value, language)
    environment.filters["timezone_label"] = lambda value: timezone_label(value, language)
    template = environment.get_template("report.html")
    logo_data = branding["logo_data"]
    generated = []
    records = []
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
                    content, mime, size = image_bytes(path, max_image_width, image_quality)
                    event["image_data"] = f"data:{mime};base64,{base64.b64encode(content).decode()}"
                    event["_image_bytes"] = content
                    event["export_width"], event["export_height"] = size
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
            blocks.append({"title": t("Evidencias del caso"), "description": "", "events": direct})
        for milestone in case["milestones"]:
            blocks.append(
                {
                    **milestone,
                    "events": [
                        event for event in case["events"] if event.get("milestone_id") == milestone["id"]
                    ],
                }
            )
        for block in blocks:
            block["log_events"] = [
                e for e in block["events"] if e["kind"] != "capture" or e["status"] == "WARN"
            ]
            times = [
                datetime.fromisoformat(e["captured_at"]) for e in block["events"] if e.get("captured_at")
            ]
            block["duration_seconds"] = (max(times) - min(times)).total_seconds() if len(times) > 1 else None
            block["warning_count"] = sum(
                event.get("level") == "WARN" or event.get("status") == "WARN" for event in block["events"]
            )
        stem = f"{slug(case['name'])}-{slug(case['id'])}"
        outputs = []
        for format_name in formats:
            target = destination / f"{stem}.{format_name}"
            if format_name == "html":
                target.write_text(
                    template.render(
                        logo_data=logo_data,
                        branding=branding,
                        case=case,
                        blocks=blocks,
                        generated_at=timestamp(),
                        t=t,
                        language=language,
                        footer=footer_text(language),
                    ),
                    encoding="utf-8",
                )
            else:
                from .documents import render_document

                render_document(case, blocks, target, format_name, language=language, branding=branding)
            generated.append(target)
            outputs.append(file_entry(target, destination, format_name))
        assets = [file_entry(source, destination, "case_json")]
        images = set()
        for attempt in [*case.get("attempts", []), case]:
            for event in attempt["events"]:
                if event.get("image"):
                    path = (source.parent / event["image"]).resolve()
                    if path.is_relative_to(source.parent) and path.is_file():
                        images.add(path)
        assets.extend(file_entry(path, destination, "image") for path in sorted(images))
        records.append(
            {
                "id": case["id"],
                "name": case["name"],
                "suite": case["suite"],
                "status": case["status"],
                "attempt_count": len(case.get("attempts", [])) + 1,
                "files": [*outputs, *assets],
            }
        )
    write_manifest(destination, records)
    return generated
