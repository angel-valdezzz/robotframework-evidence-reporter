# Demo HTML

Estos son HTML reales, autocontenidos, generados por el mismo motor del paquete. Los datos y las imágenes son ficticios y están identificados como demostración.

- [Abrir reporte aprobado](demo/passed.html)
- [Abrir reporte fallido](demo/failed.html)
- [Abrir reporte omitido](demo/skipped.html)
- [Abrir ejecución incompleta](demo/incomplete.html)

Pulsa una imagen para ampliarla. Puedes descargar el HTML y abrirlo sin conexión. La demo contiene evidencias directas, un hito y una advertencia de captura.

El ejemplo `examples/browser.robot` toma imágenes reales de una aplicación local ficticia y se valida con Chrome en el workflow de CI, bajo Xvfb. Sus reportes se conservan como artefactos; no se confunden con las imágenes ilustrativas de estas demos.

Las demos incluyen Resumen, Pasos y Logs, switch claro/oscuro y los cuatro estatus de evidencia. Son ejemplos visuales: una evidencia `FAIL` no cambia el resultado del caso. `SKIP` corresponde únicamente a la ejecución y se muestra en amarillo.
