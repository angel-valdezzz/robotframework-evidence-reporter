# CLI y Python

=== "CLI"

    ```bash
    rf-evidence build results/evidence --output reports
    ```

=== "Python"

    ```python
    from rf_evidence_reporter import build_reports

    reports = build_reports("results/evidence", "reports")
    ```

Salida: rutas de los HTML generados. Código 0: generación completada. Código 1: entrada inválida o error de generación. Un caso FAIL no hace fallar el generador: son resultados válidos para reportar. Una imagen ausente produce advertencia y una tarjeta visible en el reporte.

No requiere una sesión Robot ni un navegador para generar. `EvidenceRecorder` también es público para registrar desde Python: `start`, `milestone`, `metadata`, `event` y `finish`. El contrato de datos se versiona con `schema_version`.

La generación no cambia los JSON originales. Se puede volver a generar con otra versión de la plantilla. No combina reintentos: cada ejecución de un caso genera su propio reporte. El UUID del archivo evita sobrescrituras de casos homónimos.

No hay dashboard ni índice agregado de ejecuciones. Cada HTML tiene su resumen individual. Las fechas de ejecución y generación se presentan por separado, con zona horaria.

!!! tip "Regenera sin volver a ejecutar"
    Puedes usar los mismos JSON e imágenes con una plantilla nueva. Genera a otra carpeta para conservar el reporte original.

??? warning "Imagen no disponible"
    La generación muestra una advertencia junto a la evidencia ausente. No convierte el caso en fallido ni cambia el resultado registrado por Robot.
