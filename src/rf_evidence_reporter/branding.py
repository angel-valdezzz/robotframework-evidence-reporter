"""Portable, optional report branding. Semantic status colors stay independent."""

import base64
import json
import re
from importlib.resources import files
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image


def load_branding(config: str | Path | dict[str, Any] | None = None) -> dict[str, Any]:
    """Read a JSON file or mapping; resolve logo paths relative to the JSON file."""
    root = Path.cwd()
    if isinstance(config, (str, Path)):
        path = Path(config).resolve()
        root = path.parent
        config = json.loads(path.read_text(encoding="utf-8"))
    if config is None:
        config = {}
    if not isinstance(config, dict) or set(config) - {"name", "logo", "palette"}:
        raise ValueError("INVALID_BRANDING: expected name, logo and palette")
    palette = dict(DEFAULT_PALETTE)
    values = config.get("palette", {})
    if not isinstance(values, dict) or set(values) - set(palette):
        raise ValueError("INVALID_BRANDING_PALETTE: unknown color role")
    for key, value in values.items():
        if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise ValueError("INVALID_BRANDING_COLOR: use #RRGGBB")
        palette[key] = value
    # Headers and selected controls use white text; dark controls use dark ink.
    for key in ("primary", "primary_dark"):
        foreground = "#ffffff" if key == "primary" else "#151d32"
        if contrast(palette[key], foreground) < 4.5:
            raise ValueError(f"INVALID_BRANDING_CONTRAST: {key} requires contrast >= 4.5")
    name = config.get("name", DEFAULT_NAME)
    if not isinstance(name, str) or not name.strip() or len(name) > 100:
        raise ValueError("INVALID_BRANDING_NAME: use 1 to 100 characters")
    logo = config.get("logo")
    if logo is not None:
        if not isinstance(logo, str):
            raise ValueError("INVALID_BRANDING_LOGO: expected a local image path")
        content = (root / logo).read_bytes()
        if len(content) > 5 * 1024 * 1024:
            raise ValueError("INVALID_BRANDING_LOGO: maximum 5 MiB")
        with Image.open(BytesIO(content)) as image:
            image.load()
            image.thumbnail((512, 512))
            output = BytesIO()
            image.convert("RGBA").save(output, format="PNG")
            png = output.getvalue()
        data = "data:image/png;base64," + base64.b64encode(png).decode("ascii")
    else:
        png = files(PACKAGE).joinpath("assets/logo.png").read_bytes()
        content = files(PACKAGE).joinpath("assets/logo.svg").read_bytes()
        data = "data:image/svg+xml;base64," + base64.b64encode(content).decode("ascii")
    return {"name": name.strip(), "palette": palette, "logo_data": data, "logo_bytes": png}


def contrast(first: str, second: str) -> float:
    def luminance(color: str) -> float:
        values = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
        values = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in values]
        return sum(v * weight for v, weight in zip(values, (0.2126, 0.7152, 0.0722), strict=True))

    high, low = sorted((luminance(first), luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


PACKAGE = "rf_evidence_reporter"
DEFAULT_NAME = "Evidence Reporter"
DEFAULT_PALETTE = {
    "primary": "#5744cc",
    "accent": "#007c91",
    "primary_dark": "#b1a3ff",
    "accent_dark": "#5de0ed",
}
