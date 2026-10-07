---
title: CLI y Python
tags:
  - Reportes
  - Configuración
---

# CLI y Python

=== "CLI"

    ```bash
    rf-evidence build results/evidence --output reports
    ```

=== "Python"

    ```python hl_lines="3"
    from rf_evidence_reporter import build_reports

    reports = build_reports("results/evidence", "reports")
    ```

Salida: rutas de los HTML generados. Código 0: generación completada. Código 1: entrada inválida o error de generación. Un caso FAIL no hace fallar el generador: son resultados válidos para reportar. Una imagen ausente produce advertencia y una tarjeta visible en el reporte.

No requiere una sesión Robot ni un navegador para generar. `EvidenceRecorder` también es público para registrar desde Python: `start`, `milestone`, `metadata`, `event` y `finish`. El contrato de datos se versiona con `schema_version`.

La generación no cambia los JSON originales. Se puede volver a generar con otra versión de la plantilla. Cada ejecución de un caso genera su propio reporte. Para combinar reintentos usa el [comando merge](guide.md#combinar-ejecucion-y-reejecucion). El UUID del archivo evita sobrescrituras de casos homónimos.

No hay dashboard ni índice agregado de ejecuciones. Cada HTML tiene su resumen individual. Las fechas de ejecución y generación se presentan por separado, con zona horaria.

!!! tip "Regenera sin volver a ejecutar"
    Puedes usar los mismos JSON e imágenes con una plantilla nueva. Genera a otra carpeta para conservar el reporte original.

??? warning "Imagen no disponible"
    La generación muestra una advertencia junto a la evidencia ausente. No convierte el caso en fallido ni cambia el resultado registrado por Robot.

## Diseño del reporte y marca institucional

Los reportes comparten navegación, etiquetas de estado compactas y control claro/oscuro. Evidence muestra capturas en Pasos y mensajes en Logs, con filtros por nivel y búsqueda. Request abre la primera petición capturada; Fallos lleva directamente a la validación afectada. PDF y Word comparten la tabla de metadatos, bandas de hitos suaves y marcos de evidencia con acento de estado.

La personalización es opcional y gratuita. Cambia la presentación, sin alterar metadatos ni validaciones. Sin configuración conserva nombre, logo y paleta originales.

```json
{
  "name": "Example QA",
  "palette": {
    "primary": "#164e63",
    "accent": "#155e75",
    "primary_dark": "#67e8f9",
    "accent_dark": "#7dd3fc"
  }
}
```

Parte del archivo ejecutable `examples/brand.json`. Agrega `"logo": "logo.png"` para usar una imagen local PNG, JPEG o WebP; la ruta es relativa al JSON. El logo se incrusta, admite hasta 5 MiB y se reduce a un máximo de 512 px. El reporte se consulta sin peticiones externas. Los colores usan hexadecimal de seis dígitos. Los colores primarios deben alcanzar contraste 4.5:1 frente al texto de controles seleccionados; una configuración inválida falla con un mensaje claro. PASS, FAIL, WARN y los estados HTTP conservan su significado.

```bash
rf-evidence build results/evidence --output results/reports --formats html pdf docx --brand-config examples/brand.json
```

```python hl_lines="1 7"
from rf_evidence_reporter import build_reports

build_reports(
    "results/evidence",
    "results/reports",
    formats=("html", "pdf", "docx"),
    brand_config="examples/brand.json",
)
```

## Elige un formato de salida

| Capacidad | HTML | PDF | DOCX |
| --- | --- | --- | --- |
| Resumen individual del caso | Sí | Sí | Sí |
| Imágenes e hitos | Sí | Sí | Sí |
| Ampliar capturas y filtrar logs | Interactivo | Estático | Estático |
| Selector claro/oscuro | Sí | No | No |
| Documento editable | No | No | Sí |
| Leer sin un servidor de reportes | Sí | Sí | Sí |

=== "English"

    ```bash
    rf-evidence build results/evidence --output reports/en --language en --formats html pdf docx
    ```

=== "Español"

    ```bash
    rf-evidence build results/evidence --output reports/es --language es --formats html pdf docx
    ```

!!! tip "Una grabación, varios entregables"
    Genera formatos e idiomas desde las mismas entradas. Las capturas, nombres de casos y mensajes del usuario conservan su contenido original.
