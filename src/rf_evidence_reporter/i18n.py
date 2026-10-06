"""Report interface translations. Caller-provided content is never translated."""

from ._version import __version__


EN = {
    "Ver advertencias": "View warnings",
    "Expandir todo": "Expand all",
    "Contraer todo": "Collapse all",
    "Buscar en mensajes": "Search messages",
    "Todos": "All",
    "Sin mensajes para este filtro.": "No messages match this filter.",
    "No registrado": "Not recorded",
    "Sin zona horaria": "Timezone unspecified",
    "Resumen": "Summary",
    "Pasos": "Steps",
    "Logs": "Logs",
    "Resumen del caso": "Case summary",
    "Estatus de ejecución": "Execution status",
    "Historial de intentos": "Attempt history",
    "Duración": "Duration",
    "Sin finalizar": "Unfinished",
    "Capturas obtenidas": "Screenshots",
    "Advertencias": "Warnings",
    "Información del caso": "Case information",
    "Caso de prueba": "Test case",
    "Suite": "Suite",
    "Inicio de ejecución": "Execution started",
    "Fin de ejecución": "Execution ended",
    "Resultado": "Outcome",
    "Inicio": "Started",
    "Fin": "Ended",
    "Zona horaria": "Timezone",
    "Resultado del caso": "Case outcome",
    "Evidencias del caso": "Case evidence",
    "Mensaje registrado": "Recorded message",
    "Paso": "Step",
    "Página": "Page",
    "Modo oscuro": "Dark mode",
    "Modo claro": "Light mode",
    "Secciones del reporte": "Report sections",
    "Ejecución incompleta: se muestran las evidencias conservadas, sin atribuir un resultado final.": "Incomplete execution: preserved evidence is shown without assigning a final outcome.",
    "Ampliar": "Enlarge",
    "Página visible": "Visible page",
    "Elemento": "Element",
    "Escritorio": "Desktop",
    "Imagen adjunta": "Attached image",
    "Ampliar imagen": "Enlarge image",
    "Evidencia no disponible": "Evidence unavailable",
    "Sin capturas en este bloque.": "No screenshots in this block.",
    "Controles de hitos": "Milestone controls",
    "hitos de negocio": "business milestones",
    "Expandir todos los hitos": "Expand all milestones",
    "Contraer todos los hitos": "Collapse all milestones",
    "Hito de negocio": "Business milestone",
    "Evidencias directas": "Direct evidence",
    "capturas": "screenshots",
    "logs": "logs",
    "advertencias": "warnings",
    "Contenido de evidencias directas": "Direct evidence content",
    "Evidencias": "Evidence",
    "Logs del bloque": "Block logs",
    "Sin mensajes registrados en este bloque.": "No messages recorded in this block.",
    "Sin evidencias registradas": "No evidence recorded",
    "El resultado se conserva aunque no se hayan llamado keywords de evidencia.": "The outcome is preserved even when no evidence keywords were called.",
    "Registro de mensajes": "Message log",
    "Logs de negocio": "Business logs",
    "Mensajes explícitos y advertencias de captura. Despliega el bloque que quieras consultar.": "Explicit messages and capture warnings. Expand a block to inspect it.",
    "Sin logs registrados.": "No logs recorded.",
    "Vista ampliada de evidencia": "Enlarged evidence",
    "Cerrar": "Close",
}


def translator(language):
    if language not in {"en", "es"}:
        raise ValueError("INVALID_LANGUAGE: expected en or es")
    return lambda text: EN.get(text, text) if language == "en" else text


def footer_text(language):
    translator(language)
    prefix = "Generated with" if language == "en" else "Generado con"
    return f"{prefix} Evidence Reporter · v{__version__}"
