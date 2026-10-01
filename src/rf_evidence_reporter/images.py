"""Prepare portable images without modifying original evidence."""

from io import BytesIO

from PIL import Image, ImageOps


def image_bytes(path, max_width=None, quality=None):
    if max_width is not None and (not isinstance(max_width, int) or max_width < 1):
        raise ValueError("INVALID_IMAGE_WIDTH: max_width debe ser un entero positivo")
    if quality is not None and (not isinstance(quality, int) or not 1 <= quality <= 100):
        raise ValueError("INVALID_IMAGE_QUALITY: quality debe estar entre 1 y 100")
    with Image.open(path) as original:
        original.load()
        mime = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}[original.format]
        image = ImageOps.exif_transpose(original)
        if max_width is None and quality is None:
            return path.read_bytes(), mime, image.size
        if max_width and image.width > max_width:
            image.thumbnail(
                (max_width, max(1, round(image.height * max_width / image.width))), Image.Resampling.LANCZOS
            )
        stream = BytesIO()
        if quality is None:
            image.save(stream, format="PNG", optimize=True)
            mime = "image/png"
        else:
            image.save(stream, format="WEBP", quality=quality, method=6)
            mime = "image/webp"
        return stream.getvalue(), mime, image.size
