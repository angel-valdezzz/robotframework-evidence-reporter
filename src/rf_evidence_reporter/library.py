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
    """Registra evidencias de negocio independientes por caso de Robot Framework.

    Las capturas y los mensajes se guardan junto con los datos de ejecución en
    JSON. El HTML se genera después con ``rf-evidence build``; no se genera
    durante las keywords. Los hitos son opcionales: las evidencias sin
    ``milestone_id`` pertenecen directamente al caso.

    = Importación =
    | Library | rf_evidence_reporter.EvidenceReporter | output_dir=${OUTPUTDIR}/evidence | strict=${False} |

    = Argumentos comunes de captura =
    - ``title``: título de negocio visible en el reporte.
    - ``description``: descripción opcional de la evidencia.
    - ``milestone_id``: ID devuelto por `Create Milestone` dentro del mismo caso.
      Si se omite, la evidencia se registra directamente en el caso.
    - ``strict``: si se omite, hereda la configuración de importación.
      Con ``${False}``, un fallo de captura registra WARN y devuelve ``None``.
      Con ``${True}``, conserva la advertencia y falla con ``CAPTURE_FAILED``.
    - ``status``: INFO (predeterminado), PASS, WARN o FAIL. Describe la evidencia;
      no modifica el resultado de ejecución. SKIP solo pertenece a la ejecución.

    = Errores =
    | Código | Motivo |
    | BROWSER_UNAVAILABLE | SeleniumLibrary no importada o navegador no activo. |
    | ELEMENT_NOT_FOUND | El locator no pudo resolverse. |
    | SCREENSHOT_FAILED | El navegador o elemento no pudo producir la imagen. |
    | DESKTOP_UNAVAILABLE | El backend no pudo capturar el escritorio. |
    | IMAGE_UNAVAILABLE | La imagen solicitada no pudo leerse. |
    | INVALID_IMAGE | Archivo inválido o formato distinto de PNG, JPEG y WEBP. |
    | STORAGE_ERROR | No se pudo guardar el archivo. |

    Los errores anteriores producen advertencias por defecto. En modo estricto,
    ``CAPTURE_FAILED`` incluye el código y motivo originales. ``NO_ACTIVE_CASE``,
    ``UNKNOWN_MILESTONE``, ``INVALID_LEVEL`` e ``INVALID_CAPTURE_STATUS`` son
    errores de uso y siempre se propagan. Los errores inesperados también se
    propagan; no se convierten silenciosamente en advertencias.

    = Ejemplo =
    | ${hito}= | Create Milestone | Cliente registrado | Alta confirmada. |
    | Capture Page Evidence | Confirmación de registro | milestone_id=${hito} | status=PASS |
    | Add Evidence Message | Se confirmó el alta del cliente. | milestone_id=${hito} |

    Cada caso tiene su propio directorio e identificadores, también en Pabot.
    Las capturas se solicitan explícitamente; la librería no decide cuándo
    capturar ni oculta información sensible de las imágenes.
    """

    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, output_dir=None, strict: bool = False):
        """Configura el directorio de evidencias y la política de errores de captura.

        ``output_dir`` admite una ruta absoluta o relativa al directorio de
        ejecución. Si se omite, utiliza ``${OUTPUTDIR}/evidence`` de Robot.
        ``strict`` es falso por defecto; puede sobrescribirse en cada captura.
        La importación no abre un navegador ni genera reportes HTML.
        """
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
        """Crea un hito de negocio dentro del caso activo y devuelve su ID.

        ``title`` identifica el hito; ``description`` añade contexto opcional.
        Pasa el ID a las capturas o mensajes mediante ``milestone_id``. No hay
        un hito implícitamente activo: omitir el ID registra evidencia directa.

        | ${hito}= | Create Milestone | Cuentas consultadas | Saldos disponibles. |
        | Capture Page Evidence | Lista de cuentas | milestone_id=${hito} |
        """
        return self._active().milestone(title, description)

    @keyword
    def set_report_metadata(self, **metadata):
        """Añade campos personalizados a la tabla de información del caso.

        Recibe argumentos nombrados ``etiqueta=valor`` y los guarda como texto.
        Si se repite una etiqueta personalizada, conserva el último valor.
        Los campos automáticos de ejecución se mantienen separados. No devuelve
        un valor; falla con ``NO_ACTIVE_CASE`` fuera de un caso activo.

        | Set Report Metadata | Aplicación=ParaBank | Requerimiento=QA-123 |
        """
        self._active().metadata(metadata)

    @keyword
    def add_evidence_message(self, message: str, level: str = "INFO", milestone_id=None):
        """Registra un mensaje de negocio y devuelve el ID del evento.

        ``message`` es el texto del mensaje. ``level`` admite INFO
        (predeterminado), WARN y ERROR, sin distinguir mayúsculas. No modifica
        el resultado del caso. ``milestone_id`` es opcional; debe pertenecer al
        caso activo. Un nivel inválido falla con ``INVALID_LEVEL``.

        | Add Evidence Message | Se consultaron las cuentas del cliente. |
        | Add Evidence Message | Saldo pendiente de confirmar. | level=WARN |
        """
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
        """Captura el área visible de la página en el navegador activo.

        Reutiliza la sesión de SeleniumLibrary (Chrome, Edge o Firefox).
        No incluye barras del navegador, escritorio ni la página completa.
        Guarda URL y título de página cuando están disponibles.

        Consulta los argumentos comunes y errores en la introducción.
        Devuelve el ID del evento, o ``None`` si falla sin modo estricto.
        Sin sesión disponible registra ``BROWSER_UNAVAILABLE``.

        | Capture Page Evidence | Error mostrado por la aplicación | status=FAIL |
        """

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
        """Captura un elemento de la sesión activa de SeleniumLibrary.

        ``locator`` utiliza la sintaxis de SeleniumLibrary, por ejemplo
        ``css:.confirmation`` o ``id:registrationForm``. Guarda URL y título de
        página cuando están disponibles. No abre una sesión nueva.

        Consulta los argumentos comunes y errores en la introducción.
        Devuelve el ID del evento, o ``None`` si falla sin modo estricto.
        Un locator no resuelto registra ``ELEMENT_NOT_FOUND``.

        | Capture Element Evidence | css:.confirmation | Alta confirmada | status=PASS |
        """

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
        """Captura el escritorio del entorno donde se ejecuta Robot.

        Utiliza Pillow ImageGrab y no necesita SeleniumLibrary. Requiere un
        entorno gráfico/backend compatible y los permisos del sistema.
        No captura el escritorio de una máquina remota de Selenium Grid.
        En headless, CI o paralelo, el usuario decide si esta captura es útil:
        puede incluir otras ventanas y no se sustituye por una captura de página.

        Consulta los argumentos comunes y errores en la introducción.
        Devuelve el ID del evento, o ``None`` si falla sin modo estricto.
        Un backend no disponible registra ``DESKTOP_UNAVAILABLE``.

        | Capture Desktop Evidence | Escritorio al confirmar la operación | status=INFO |
        """

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
        """Copia una imagen existente al directorio de evidencias del caso.

        ``path`` admite una ruta absoluta o relativa al directorio de ejecución.
        Acepta PNG, JPEG y WEBP; valida el contenido real de la imagen. El archivo
        original no se modifica y puede moverse después de una copia exitosa.
        No necesita navegador ni entorno gráfico.

        Consulta los argumentos comunes y errores en la introducción.
        Devuelve el ID del evento, o ``None`` si falla sin modo estricto.
        Una ruta ilegible registra ``IMAGE_UNAVAILABLE``; contenido inválido,
        ``INVALID_IMAGE``.

        | Attach Image Evidence | ${EXECDIR}/data/confirmacion.png | Confirmación externa | status=PASS |
        """

        def producer():
            try:
                return Path(path).read_bytes(), {}
            except OSError as error:
                raise CaptureError("IMAGE_UNAVAILABLE", str(error)) from error

        return self._capture(title, producer, "attachment", milestone_id, strict, description, status)
