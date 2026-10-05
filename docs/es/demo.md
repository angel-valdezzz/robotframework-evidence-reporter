# Ejemplos visuales

## Ejemplo PDF

[Ver PDF de ejemplo](demo/passed.pdf){ .md-button .md-button--primary target="_blank" rel="noopener" }

Este PDF se genera con el motor de exportación de Evidence Reporter a partir del mismo caso aprobado de la demo HTML. Incluye datos ficticios, hitos, capturas y estados de evidencia. El enlace abre el archivo estático en otra pestaña; el navegador puede mostrarlo o descargarlo según su configuración.

## Ejemplos HTML

Estos son HTML reales, autocontenidos, generados por el mismo motor del paquete. Los datos y las imágenes son ficticios y están identificados como demostración.

- [Abrir reporte aprobado](demo/passed.html)
- [Abrir reporte fallido](demo/failed.html)
- [Abrir reporte omitido](demo/skipped.html)
- [Abrir ejecución incompleta](demo/incomplete.html)

Pulsa una imagen para ampliarla. Puedes descargar el HTML y abrirlo sin conexión. La demo aprobada contiene evidencias directas, dos hitos y una advertencia de captura. La demo omitida representa un caso saltado desde el inicio: tiene estado y motivo, pero no capturas. Si se omite durante el flujo, se conservan las evidencias anteriores; consulta [casos omitidos](guide.md#casos-omitidos-skip).

El ejemplo `examples/browser.robot` toma imágenes reales de una aplicación local ficticia y se valida con Chrome en el workflow de CI, bajo Xvfb. Sus reportes se conservan como artefactos; no se confunden con las imágenes ilustrativas de estas demos.

Las demos incluyen Resumen, Pasos y Logs, switch claro/oscuro y los cuatro estatus de evidencia. Son ejemplos visuales: una evidencia `FAIL` no cambia el resultado del caso. `SKIP` corresponde únicamente a la ejecución y se muestra en amarillo.

## Prueba los controles

1. Abre **Pasos**: el bloque de evidencias directas está plegado y los dos hitos están abiertos.
2. Contrae todos los hitos y vuelve a expandirlos. Las evidencias directas conservan su estado.
3. Abre las evidencias directas y cambia entre **Evidencias** y **Logs del bloque**.
4. Consulta **Cliente registrado** y **Cuentas consultadas**: tienen imágenes y mensajes distintos.
5. Cambia a modo oscuro o amplía una captura para revisar sus detalles.

!!! info "Datos ilustrativos"
    Los saldos y las cuentas de la demo son ficticios. Los reportes se generan con el mismo motor que usa la librería.
