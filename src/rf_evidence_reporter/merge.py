"""Merge ordered executions using stable business identity and portable evidence."""

import copy
import json
import shutil

from .recorder import slug
from pathlib import Path


def identity(case):
    return (case["suite"], case["name"])


def merge_results(inputs, output_dir):
    """Later input wins, including SKIP/INCOMPLETE; never concatenate test attempts.

    Match exact suite + test name. Duplicate identities inside one execution are ambiguous
    and rejected. All earlier attempt data and images remain in the selected case history.
    The output directory must be absent or empty and outside every input directory.
    """
    roots = [Path(root).resolve() for root in inputs]
    if len(roots) < 2:
        raise ValueError("MERGE_INPUTS: se requieren al menos dos ejecuciones")
    target = Path(output_dir).resolve()
    if any(target == root or target.is_relative_to(root) or root.is_relative_to(target) for root in roots):
        raise ValueError("MERGE_OVERLAP: entrada y salida deben estar separadas")
    if target.exists() and any(target.iterdir()):
        raise ValueError("MERGE_NOT_EMPTY: el directorio de salida debe estar vacío")
    groups = {}
    for root in roots:
        files = sorted(root.rglob("case.json"))
        if not files:
            raise ValueError(f"NO_CASES: {root}")
        seen = set()
        for source in files:
            case = json.loads(source.read_text(encoding="utf-8"))
            if (
                case.get("schema_version") != 1
                or not isinstance(case.get("suite"), str)
                or not isinstance(case.get("name"), str)
            ):
                raise ValueError(f"INVALID_CASE: {source}")
            key = identity(case)
            if key in seen:
                raise ValueError(f"AMBIGUOUS_CASE: suite y nombre repetidos en {root}: {key}")
            seen.add(key)
            groups.setdefault(key, []).append((source, case))
    # Validate all referenced assets before any writes; missing captures stay visible warnings.
    for attempts in groups.values():
        for source, case in attempts:
            for attempt in [*case.get("attempts", []), case]:
                for event in attempt.get("events", []):
                    if event.get("image"):
                        path = (source.parent / event["image"]).resolve()
                        if not path.is_relative_to(source.parent):
                            raise ValueError("INVALID_IMAGE_PATH: referencia fuera del caso")
    target.mkdir(parents=True, exist_ok=True)
    generated = []
    for index, attempts in enumerate(groups.values()):
        selected = copy.deepcopy(attempts[-1][1])
        directory = target / f"case-{index + 1}-{slug(selected['id'])}"
        directory.mkdir()
        history = []
        for number, (source, case) in enumerate(attempts):
            snapshots = [*case.get("attempts", []), case]
            for nested, snapshot in enumerate(snapshots):
                snapshot = copy.deepcopy(snapshot)
                snapshot.pop("attempts", None)
                for event_number, event in enumerate(snapshot.get("events", [])):
                    if not event.get("image"):
                        continue
                    image = (source.parent / event["image"]).resolve()
                    relative = Path("images") / f"{number}-{nested}-{event_number}{image.suffix}"
                    event["image"] = relative.as_posix()
                    if image.is_file():
                        (directory / relative).parent.mkdir(exist_ok=True)
                        shutil.copyfile(image, directory / relative)
                history.append(snapshot)
        selected = history.pop()
        selected["attempts"] = history
        selected["merge_identity"] = {"suite": selected["suite"], "name": selected["name"]}
        path = directory / "case.json"
        path.write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
        generated.append(path)
    return generated
