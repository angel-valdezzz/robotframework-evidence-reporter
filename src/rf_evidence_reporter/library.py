"""Robot adapter: explicit evidence keywords and automatic final test metadata."""

import io
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageGrab
from robot.api import logger
from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn

from .recorder import EvidenceRecorder


class CaptureError(RuntimeError):
    def __init__(self, code, reason):
        self.code = code
        super().__init__(f"{code}: {reason}")


@library(scope="GLOBAL", auto_keywords=False)
class EvidenceReporter:
    """Record each test independently. Capture failures warn unless strict=True.

    output_dir defaults to Robot's OUTPUTDIR/evidence. Import as
    Library    rf_evidence_reporter.EvidenceReporter
    """

    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, output_dir=None, strict: bool = False):
        self.ROBOT_LIBRARY_LISTENER = self
        self.output_dir = output_dir
        self.strict = strict
        self.recorder = None

    def start_test(self, data, result):
        root = self.output_dir or Path(BuiltIn().get_variable_value("${OUTPUTDIR}")) / "evidence"
        self.recorder = EvidenceRecorder(root)
        self.recorder.start(result.name, result.parent.full_name, str(data.doc), result.tags)

    def end_test(self, data, result):
        if self.recorder and self.recorder.case:
            self.recorder.finish(result.status, result.elapsed_time.total_seconds(), result.message)

    def _active(self, milestone_id=None):
        if self.recorder is None:
            raise RuntimeError("NO_ACTIVE_CASE: no existe un caso de prueba activo.")
        self.recorder.validate_milestone(milestone_id)
        return self.recorder

    @keyword
    def create_milestone(self, title: str, description: str = ""):
        """Return an optional block ID; evidence without an ID belongs directly to the case."""
        return self._active().milestone(title, description)

    @keyword
    def set_report_metadata(self, **metadata):
        """Add custom label=value fields without overriding automatic Robot fields."""
        self._active().metadata(metadata)

    @keyword
    def add_evidence_message(self, message: str, level: str = "INFO", milestone_id=None):
        """Record an explicit business note. INFO, WARN and ERROR are supported."""
        level = level.upper()
        if level not in {"INFO", "WARN", "ERROR"}:
            raise ValueError("INVALID_LEVEL: utiliza INFO, WARN o ERROR.")
        return self._active(milestone_id).event(message, level=level, milestone_id=milestone_id)

    def _driver(self):
        try:
            selenium = BuiltIn().get_library_instance("SeleniumLibrary")
            return selenium.driver
        except Exception as error:
            raise CaptureError(
                "BROWSER_UNAVAILABLE", "SeleniumLibrary no está importada o no hay navegador activo."
            ) from error

    def _context(self, driver):
        context = {}
        for field, attribute in (("url", "current_url"), ("page_title", "title")):
            try:
                context[field] = getattr(driver, attribute)
            except Exception:
                context[field] = ""
        return context

    def _image(self, content):
        try:
            with Image.open(io.BytesIO(content)) as image:
                if image.format not in {"PNG", "JPEG", "WEBP"}:
                    raise ValueError("solo se admite PNG, JPEG o WEBP")
                image.load()
                return image.format.lower(), image.size
        except Exception as error:
            raise CaptureError("INVALID_IMAGE", str(error)) from error

    def _capture(self, title, producer, kind, milestone_id, strict, description, context=None):
        recorder = self._active(milestone_id)
        try:
            content, details = producer()
            extension, size = self._image(content)
            path = recorder.case_dir / f"{uuid4().hex}.{extension}"
            try:
                path.write_bytes(content)
            except OSError as error:
                raise CaptureError("STORAGE_ERROR", str(error)) from error
            return recorder.event(
                title,
                kind="capture",
                milestone_id=milestone_id,
                capture_type=kind,
                description=description,
                image=path.name,
                width=size[0],
                height=size[1],
                **details,
            )
        except CaptureError as error:
            reason = str(error)
        except OSError as error:
            reason = f"STORAGE_ERROR: {error}"
        # Unexpected programming errors deliberately propagate.
        try:
            recorder.event(
                title,
                kind="capture_warning",
                level="WARN",
                milestone_id=milestone_id,
                capture_type=kind,
                description=description,
                reason=reason,
                **(context or {}),
            )
        except OSError as error:
            logger.warn(f"STORAGE_ERROR: tampoco se pudo guardar la advertencia: {error}")
        logger.warn(f"No se obtuvo la evidencia '{title}'. {reason}")
        if self.strict if strict is None else strict:
            raise CaptureError("CAPTURE_FAILED", reason)
        return None

    @keyword
    def capture_page_evidence(
        self, title: str, description: str = "", milestone_id=None, strict: bool | None = None
    ):
        """Capture the browser viewport; does not include browser chrome or desktop."""

        def producer():
            driver = self._driver()
            try:
                return driver.get_screenshot_as_png(), self._context(driver)
            except Exception as error:
                raise CaptureError("SCREENSHOT_FAILED", str(error)) from error

        return self._capture(title, producer, "page", milestone_id, strict, description)

    @keyword
    def capture_element_evidence(
        self, locator: str, title: str, description: str = "", milestone_id=None, strict: bool | None = None
    ):
        """Capture one element using SeleniumLibrary locator syntax."""

        def producer():
            driver = self._driver()
            try:
                element = BuiltIn().get_library_instance("SeleniumLibrary").find_element(locator)
            except Exception as error:
                raise CaptureError("ELEMENT_NOT_FOUND", f"{locator}: {error}") from error
            try:
                return element.screenshot_as_png, self._context(driver)
            except Exception as error:
                raise CaptureError("SCREENSHOT_FAILED", str(error)) from error

        return self._capture(title, producer, "element", milestone_id, strict, description)

    @keyword
    def capture_desktop_evidence(
        self, title: str, description: str = "", milestone_id=None, strict: bool | None = None
    ):
        """Capture the desktop of this Robot process with Pillow ImageGrab.

        Caller chooses when suitable. No detection of headless, remote browsers or parallelism.
        Linux requires a supported graphical display/capture backend; macOS may require permissions.
        """

        def producer():
            try:
                image = ImageGrab.grab()
                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                return buffer.getvalue(), {}
            except Exception as error:
                raise CaptureError("DESKTOP_UNAVAILABLE", str(error)) from error

        return self._capture(title, producer, "desktop", milestone_id, strict, description)

    @keyword
    def attach_image_evidence(
        self, path: str, title: str, description: str = "", milestone_id=None, strict: bool | None = None
    ):
        """Copy an existing PNG/JPEG/WEBP image into this case; original can then be moved."""

        def producer():
            try:
                return Path(path).read_bytes(), {}
            except OSError as error:
                raise CaptureError("IMAGE_UNAVAILABLE", str(error)) from error

        return self._capture(title, producer, "attachment", milestone_id, strict, description)
