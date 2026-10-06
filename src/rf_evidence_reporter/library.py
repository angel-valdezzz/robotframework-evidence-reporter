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
    """Record independent business evidence for each Robot Framework case.

    Screenshots and messages are stored with execution data as JSON. Generate HTML afterwards with ``rf-evidence build``, not during keywords. Milestones are optional: evidence without ``milestone_id`` belongs directly to the case.

    = Importing =
    | Library | EvidenceReporter |

    Robot's ``--outputdir`` sets the base directory; evidence goes into ``${OUTPUTDIR}/evidence``. To select a separate evidence directory, set the optional Robot variable ``${EVIDENCE_OUTPUT_DIR}`` with ``--variable EVIDENCE_OUTPUT_DIR:path``. An explicit import ``output_dir`` takes precedence for compatibility. With Pabot, each worker uses its own output directory; generate reports from the parent ``results/pabot_results`` after execution.

    = Common capture arguments =
    - ``title``: business title displayed in the report.
    - ``description``: optional evidence description.
    - ``milestone_id``: ID returned by `Create Milestone` in the same case. Omit it for direct evidence.
    - ``strict``: inherits the import setting when omitted. With ``${False}``, capture failure records WARN and returns ``None``. With ``${True}``, it preserves the warning and fails with ``CAPTURE_FAILED``.
    - ``status``: INFO (default), PASS, WARN or FAIL. Describes evidence without changing execution status. SKIP belongs only to execution.

    = Errors =
    | Code | Reason |
    | BROWSER_UNAVAILABLE | SeleniumLibrary not imported or no active browser. |
    | ELEMENT_NOT_FOUND | The locator could not be resolved. |
    | SCREENSHOT_FAILED | The browser or element could not produce an image. |
    | DESKTOP_UNAVAILABLE | The backend could not capture the desktop. |
    | IMAGE_UNAVAILABLE | The requested image could not be read. |
    | INVALID_IMAGE | Invalid file or format other than PNG, JPEG and WEBP. |
    | STORAGE_ERROR | The file could not be saved. |

    These errors produce warnings by default. In strict mode, ``CAPTURE_FAILED`` includes the original code and reason. ``NO_ACTIVE_CASE``, ``UNKNOWN_MILESTONE``, ``INVALID_LEVEL`` and ``INVALID_CAPTURE_STATUS`` are usage errors and always propagate. Unexpected errors also propagate rather than silently becoming warnings.

    = Example =
    | ${milestone}= | Create Milestone | Customer registered | Registration confirmed. |
    | Capture Page Evidence | Registration confirmation | milestone_id=${milestone} | status=PASS |
    | Add Evidence Message | Customer registration confirmed. | milestone_id=${milestone} |

    Each case has its own directory and identifiers, including with Pabot. Captures are explicit: the library does not decide when to capture or hide sensitive information in images."""

    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, output_dir=None, strict: bool = False):
        """Configure the evidence directory and capture error policy.

        ``output_dir`` accepts an absolute path or a path relative to the execution directory. Resolution order: explicit ``output_dir``, optional Robot variable ``${EVIDENCE_OUTPUT_DIR}``, then ``${OUTPUTDIR}/evidence``. Normally omit this argument and configure Robot's ``--outputdir``. ``strict`` defaults to false and can be overridden per capture. Importing does not open a browser or generate HTML reports."""
        self.ROBOT_LIBRARY_LISTENER = self
        self.output_dir = output_dir
        self.strict = strict
        self.recorder = None

    def start_test(self, data, result):
        robot = BuiltIn()
        root = (
            self.output_dir
            or robot.get_variable_value("${EVIDENCE_OUTPUT_DIR}")
            or Path(robot.get_variable_value("${OUTPUTDIR}")) / "evidence"
        )
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
        """Create a business milestone in the active case and return its ID.

        ``title`` identifies the milestone; ``description`` adds optional context. Pass its ID to captures or messages using ``milestone_id``. There is no implicit active milestone: omitting the ID records direct evidence.

        | ${milestone}= | Create Milestone | Accounts queried | Balances available. |
        | Capture Page Evidence | Account list | milestone_id=${milestone} |"""
        return self._active().milestone(title, description)

    @keyword
    def set_report_metadata(self, **metadata):
        """Add custom fields to the case information table.

        Accepts named ``label=value`` arguments and stores them as text. Repeated custom labels retain the last value. Automatic execution fields stay separate. Returns nothing; fails with ``NO_ACTIVE_CASE`` outside an active case.

        | Set Report Metadata | Application=ParaBank | Requirement=QA-123 |"""
        self._active().metadata(metadata)

    @keyword
    def add_evidence_message(self, message: str, level: str = "INFO", milestone_id=None):
        """Record a business message and return its event ID.

        ``message`` is the message text. ``level`` accepts INFO (default), WARN and ERROR, case-insensitively. It does not change test status. Optional ``milestone_id`` must belong to the active case. An invalid level fails with ``INVALID_LEVEL``.

        | Add Evidence Message | Customer accounts queried. |
        | Add Evidence Message | Balance pending confirmation. | level=WARN |"""
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

    def _capture(self, title, producer, kind, milestone_id, strict, description, status="INFO", context=None):
        status = status.upper()
        if status not in {"INFO", "PASS", "WARN", "FAIL"}:
            raise ValueError("INVALID_CAPTURE_STATUS: utiliza INFO, PASS, WARN o FAIL; SKIP no es válido.")
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
                status=status,
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
                status="WARN",
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
        self,
        title: str,
        description: str = "",
        milestone_id=None,
        strict: bool | None = None,
        status: str = "INFO",
    ):
        """Capture the visible page area in the active browser.

        Reuses the SeleniumLibrary session (Chrome, Edge or Firefox). Does not include browser toolbars, desktop or the full page. Stores page URL and title when available.

        See common arguments and errors in the introduction. Returns the event ID, or ``None`` on failure without strict mode. No available session records ``BROWSER_UNAVAILABLE``.

        | Capture Page Evidence | Error shown by the application | status=FAIL |"""

        def producer():
            driver = self._driver()
            try:
                return driver.get_screenshot_as_png(), self._context(driver)
            except Exception as error:
                raise CaptureError("SCREENSHOT_FAILED", str(error)) from error

        return self._capture(title, producer, "page", milestone_id, strict, description, status)

    @keyword
    def capture_element_evidence(
        self,
        locator: str,
        title: str,
        description: str = "",
        milestone_id=None,
        strict: bool | None = None,
        status: str = "INFO",
    ):
        """Capture an element in SeleniumLibrary's active session.

        ``locator`` uses SeleniumLibrary syntax, such as ``css:.confirmation`` or ``id:registrationForm``. Stores page URL and title when available. Does not open a new session.

        See common arguments and errors in the introduction. Returns the event ID, or ``None`` on failure without strict mode. An unresolved locator records ``ELEMENT_NOT_FOUND``.

        | Capture Element Evidence | css:.confirmation | Registration confirmed | status=PASS |"""

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

        return self._capture(title, producer, "element", milestone_id, strict, description, status)

    @keyword
    def capture_desktop_evidence(
        self,
        title: str,
        description: str = "",
        milestone_id=None,
        strict: bool | None = None,
        status: str = "INFO",
    ):
        """Capture the desktop of the environment where Robot runs.

        Uses Pillow ImageGrab without SeleniumLibrary. Requires a compatible graphical environment/backend and system permissions. Does not capture a remote Selenium Grid machine's desktop. In headless, CI or parallel execution, the user decides whether this is useful: it can include other windows and is not replaced by a page screenshot.

        See common arguments and errors in the introduction. Returns the event ID, or ``None`` on failure without strict mode. An unavailable backend records ``DESKTOP_UNAVAILABLE``.

        | Capture Desktop Evidence | Desktop after confirming the operation | status=INFO |"""

        def producer():
            try:
                image = ImageGrab.grab()
                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                return buffer.getvalue(), {}
            except Exception as error:
                raise CaptureError("DESKTOP_UNAVAILABLE", str(error)) from error

        return self._capture(title, producer, "desktop", milestone_id, strict, description, status)

    @keyword
    def attach_image_evidence(
        self,
        path: str,
        title: str,
        description: str = "",
        milestone_id=None,
        strict: bool | None = None,
        status: str = "INFO",
    ):
        """Copy an existing image into the case's evidence directory.

        ``path`` accepts an absolute path or a path relative to the execution directory. Accepts PNG, JPEG and WEBP and validates actual image content. The original is unchanged and can be moved after a successful copy. No browser or graphical environment is required.

        See common arguments and errors in the introduction. Returns the event ID, or ``None`` on failure without strict mode. An unreadable path records ``IMAGE_UNAVAILABLE``; invalid content records ``INVALID_IMAGE``.

        | Attach Image Evidence | ${EXECDIR}/data/confirmation.png | External confirmation | status=PASS |"""

        def producer():
            try:
                return Path(path).read_bytes(), {}
            except OSError as error:
                raise CaptureError("IMAGE_UNAVAILABLE", str(error)) from error

        return self._capture(title, producer, "attachment", milestone_id, strict, description, status)
