# CLI y Python

```bash
rf-evidence build results/evidence --output reports
```

Salida: rutas de los HTML generados. Código 0: generación completada. Código 1: entrada inválida o error de generación. Un caso FAIL no hace fallar el generador: son resultados válidos para reportar. Una imagen ausente produce advertencia y una tarjeta visible en el reporte.

```python
from rf_evidence_reporter import build_reports

reports = build_reports("results/evidence", "reports")
```

No requiere una sesión Robot ni un navegador para generar. `EvidenceRecorder` también es público para registrar desde Python: `start`, `milestone`, `metadata`, `event` y `finish`. El contrato de datos se versiona con `schema_version`.

La generación no cambia los JSON originales. Se puede volver a generar con otra versión de la plantilla. No combina reintentos: cada ejecución de un caso genera su propio reporte. El UUID del archivo evita sobrescrituras de casos homónimos.

No hay dashboard ni índice agregado de ejecuciones. Cada HTML tiene su resumen individual. Las fechas de ejecución y generación se presentan por separado, con zona horaria.
