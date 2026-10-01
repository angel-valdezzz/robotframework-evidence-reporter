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
| Capture Page Evidence | `title`, `description=`, `milestone_id=`, `strict=`, `status=INFO` | ID o `None` si falla en modo WARN |
| Capture Element Evidence | `locator`, `title`, `description=`, `milestone_id=`, `strict=`, `status=INFO` | ID o `None` |
| Capture Desktop Evidence | `title`, `description=`, `milestone_id=`, `strict=`, `status=INFO` | ID o `None` |
| Attach Image Evidence | `path`, `title`, `description=`, `milestone_id=`, `strict=`, `status=INFO` | ID o `None` |

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

## Estatus de evidencia y presentación

Las cuatro keywords de captura aceptan `status=INFO` (por defecto), `PASS`, `WARN` o `FAIL`. No aceptan `SKIP`; un valor inválido produce `INVALID_CAPTURE_STATUS`. El estatus describe la evidencia y no modifica el resultado de Robot. Si la captura falla, se registra una advertencia independientemente del estatus solicitado.

```robotframework
Capture Page Evidence    Error mostrado por la aplicación    status=FAIL
Capture Element Evidence    css:.confirmation    Alta confirmada    status=PASS
```

El HTML tiene pestañas **Resumen**, **Pasos** y **Logs**. Resumen muestra una sola insignia de estatus de ejecución (`SKIP` en amarillo). Pasos presenta capturas e hitos; sus logs son plegables. Logs agrupa mensajes y advertencias en bloques plegables, con bordes por nivel y fondo neutro. El switch permite elegir modo claro u oscuro; conserva la preferencia cuando el navegador permite almacenamiento local.

Las fechas visibles incluyen día/mes/año y hora con segundos. La zona horaria se indica al pie y el JSON conserva el timestamp completo. Los registros anteriores sin estatus de captura se presentan como `INFO`. No hay botón de impresión; PDF y Word quedan para una etapa posterior.
