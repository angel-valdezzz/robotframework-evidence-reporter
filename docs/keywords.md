# Keywords

Importación:

```robotframework
Library    rf_evidence_reporter.EvidenceReporter    output_dir=${EXECDIR}/results/evidence    strict=${False}
```

| Keyword | Argumentos principales | Retorno |
| --- | --- | --- |
| Create Milestone | `title`, `description=` | ID del hito |
| Set Report Metadata | `**metadata` (`etiqueta=valor`) | Ninguno |
| Add Evidence Message | `message`, `level=INFO`, `milestone_id=` | ID del evento |
| Capture Page Evidence | `title`, `description=`, `milestone_id=`, `strict=` | ID o `None` si falla en modo WARN |
| Capture Element Evidence | `locator`, `title`, `description=`, `milestone_id=`, `strict=` | ID o `None` |
| Capture Desktop Evidence | `title`, `description=`, `milestone_id=`, `strict=` | ID o `None` |
| Attach Image Evidence | `path`, `title`, `description=`, `milestone_id=`, `strict=` | ID o `None` |

`strict` por keyword sobrescribe el valor de importación. Si se omite, hereda el valor global (por defecto falso).

## Errores de captura

| Código | Motivo |
| --- | --- |
| BROWSER_UNAVAILABLE | SeleniumLibrary no importada o navegador no activo |
| ELEMENT_NOT_FOUND | El locator no pudo resolverse |
| SCREENSHOT_FAILED | El navegador/elemento no pudo producir la imagen |
| DESKTOP_UNAVAILABLE | El backend no pudo capturar el escritorio |
| IMAGE_UNAVAILABLE | La imagen solicitada no pudo leerse |
| INVALID_IMAGE | Archivo incompatible o inválido |
| STORAGE_ERROR | No se pudo guardar el archivo |

Con modo estricto la keyword falla con `CAPTURE_FAILED` y conserva el motivo original. `NO_ACTIVE_CASE`, `UNKNOWN_MILESTONE` e `INVALID_LEVEL` son errores de uso que siempre se propagan.

La librería admite locators de SeleniumLibrary y reutiliza su sesión activa en Chrome, Edge o Firefox. El escritorio utiliza Pillow ImageGrab y requiere un entorno compatible; no se sustituye silenciosamente por otra captura.
