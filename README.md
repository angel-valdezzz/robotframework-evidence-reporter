# Robot Framework Evidence Reporter

Reportes HTML, PDF y Word por caso de Robot Framework, orientado a evidencias de negocio. Registra capturas explícitas, mensajes y metadatos durante la ejecución; genera los documentos después, desde CLI o Python.

[PyPI](https://pypi.org/project/robotframework-evidence-reporter/) · [Documentación](https://angel-valdezzz.github.io/robotframework-evidence-reporter/) · [Documentación de keywords](https://angel-valdezzz.github.io/robotframework-evidence-reporter/reference/keywords.html) · [Ver reporte HTML](https://angel-valdezzz.github.io/robotframework-evidence-reporter/demo/passed.html)

## Estado de publicación

La versión 0.1.0 está publicada en [PyPI](https://pypi.org/project/robotframework-evidence-reporter/). El código, la documentación y la demo HTML también están publicados. Las nuevas versiones se publican mediante GitHub Actions con Trusted Publishing.

## Instalación

```bash
pip install robotframework-evidence-reporter
poetry add robotframework-evidence-reporter

# Instalación alternativa desde el repositorio
pip install "git+https://github.com/angel-valdezzz/robotframework-evidence-reporter.git@main"
```

Python 3.12 o superior y Robot Framework 7. Para capturar páginas o elementos instala también SeleniumLibrary. La librería reutiliza su navegador activo: no abre otra sesión ni depende de un navegador concreto.

## Uso en Robot

```robotframework
*** Settings ***
Library    SeleniumLibrary
Library    EvidenceReporter

*** Test Cases ***
Registrar Cliente
    Open Browser    https://example.test    chrome
    Set Report Metadata    Aplicación=Portal    Ambiente=QA    Ticket=QA-123
    Capture Page Evidence    Formulario de alta
    ${milestone}=    Create Milestone    Cliente registrado
    Capture Element Evidence    css:.confirmation    Confirmación    milestone_id=${milestone}
    Add Evidence Message    El alta fue confirmada.    milestone_id=${milestone}
    [Teardown]    Close All Browsers
```

Los hitos son opcionales. Sin `milestone_id`, la evidencia se añade directamente al caso. No se registran automáticamente argumentos ni todos los logs técnicos; añade los mensajes de negocio que necesites.

```bash
robot --outputdir results tests
rf-evidence build results/evidence --output reports
```

Cada caso conserva su estado final de Robot (`PASS`, `FAIL`, `SKIP`), inicio, fin y duración, incluidos fallos del teardown. Un proceso interrumpido antes de guardar el resultado final conserva `INCOMPLETE`. Las fechas incluyen el offset horario del proceso que las registra.

## Capturas y errores

| Keyword | Captura |
| --- | --- |
| `Capture Page Evidence` | Página visible del navegador activo |
| `Capture Element Evidence` | Elemento usando un locator SeleniumLibrary |
| `Capture Desktop Evidence` | Escritorio de la máquina donde corre Robot |
| `Attach Image Evidence` | Copia una imagen PNG, JPEG o WEBP existente |

Las capturas fallidas producen **WARN por defecto**, se registran en el HTML y no cambian el estado del caso. Usa `strict=${True}` por keyword o `strict=${True}` al importar la librería para exigir una captura. `strict=${False}` por keyword permite sobrescribir esa configuración global.

El usuario elige cuándo usar el escritorio. No hay detección automática de headless, remoto ni paralelismo. Pillow ImageGrab necesita un entorno gráfico compatible; en Linux puede requerir un backend de captura, y en macOS permisos de pantalla. La captura corresponde al escritorio del proceso, no necesariamente al navegador remoto. No se implementa página completa en esta versión.

Errores definidos: `BROWSER_UNAVAILABLE`, `ELEMENT_NOT_FOUND`, `SCREENSHOT_FAILED`, `DESKTOP_UNAVAILABLE`, `IMAGE_UNAVAILABLE`, `INVALID_IMAGE`, `STORAGE_ERROR`. Argumentos incorrectos, hitos ajenos al caso y errores internos no se silencian. Si falla el almacenamiento inicial o final del listener, Robot registra el error del listener; comprueba también que se hayan generado los JSON esperados.

## Python y paralelo

```python
from rf_evidence_reporter import build_reports

paths = build_reports("results/evidence", "reports")
```

Cada caso usa un UUID y un directorio propio. Para Pabot proporciona un directorio compartido de esta ejecución, por ejemplo `output_dir=${EXECDIR}/results/evidence`. Genera los HTML después de que terminen todos los procesos. Usa un directorio nuevo por ejecución: el generador incluye todos los `case.json` encontrados y conserva cada intento separado.

## Desarrollo

```bash
poetry install
poetry run ruff check src tests scripts
poetry run ruff format --check src tests scripts
poetry run robocop check tests examples
poetry run python -m unittest discover -s tests -v
poetry run python scripts/validate.py
poetry run python scripts/demo.py
poetry run python -m robot.libdoc --name "Evidence Reporter" EvidenceReporter docs/reference/keywords.html
poetry run mkdocs build --strict
poetry build
```

`scripts/validate.py` verifica Robot y Pabot, incluyendo un caso con fallo deliberado en teardown. Las pruebas del núcleo usan unittest de Python; las pruebas de integración usan Robot. La demo pública utiliza datos e imágenes ficticios, indicados en el propio reporte.

El HTML incluye imágenes, CSS y JavaScript sin recursos externos. Su visualizador funciona sin conexión y es navegable con teclado. Jira puede permitir adjuntarlo sin ofrecer vista previa; se puede descargar y abrir en un navegador. El contenido y las imágenes no se censuran automáticamente: registra solo datos apropiados para el destino del reporte.

## Publicación

GitHub Actions valida los cambios. `main` publica MkDocs y la demo en GitHub Pages. Un cambio de `pyproject.toml` en `main`, o una release `vX.Y.Z` cuya versión coincida con el paquete, publica wheel y sdist en PyPI mediante Trusted Publishing. Consulta `docs/publishing.md` para el registro inicial del publisher.

Licencia MIT.

## Estatus de evidencia y presentación

Las cuatro keywords de captura aceptan `status=INFO` (por defecto), `PASS`, `WARN` o `FAIL`. No aceptan `SKIP`; un valor inválido produce `INVALID_CAPTURE_STATUS`. El estatus describe la evidencia y no modifica el resultado de Robot. Si la captura falla, se registra una advertencia independientemente del estatus solicitado.

Consulta los [ejemplos completos con estatus de evidencia](https://angel-valdezzz.github.io/robotframework-evidence-reporter/guide/#estatus-de-evidencia-y-presentacion).

El HTML tiene pestañas **Resumen**, **Pasos** y **Logs**. Resumen muestra una sola insignia de estatus de ejecución (`SKIP` en amarillo). Pasos presenta capturas e hitos; sus logs son plegables. Logs agrupa mensajes y advertencias en bloques plegables, con bordes por nivel y fondo neutro. El switch permite elegir modo claro u oscuro; conserva la preferencia cuando el navegador permite almacenamiento local.

Las fechas visibles incluyen día/mes/año y hora con segundos. La zona horaria se indica al pie y el JSON conserva el timestamp completo. Los registros anteriores sin estatus de captura se presentan como `INFO`. No hay botón de impresión; PDF y Word se generan desde la CLI con `--formats pdf docx`.

## Navegación del reporte

En Pasos, las evidencias directas empiezan plegadas y tienen pestañas Evidencias/Logs del bloque. Los hitos empiezan abiertos; puedes contraerlos individualmente o usar Expandir/Contraer todos los hitos. Los controles globales no modifican el bloque directo.

La documentación comparte logo, colores y temas con el reporte. Consulta [Primera evidencia](https://angel-valdezzz.github.io/robotframework-evidence-reporter/getting-started/) para ejemplos de instalación y ejecución.

## PDF Word merge e inventario de archivos

Genera los formatos que necesites desde los mismos JSON e imágenes de evidencia:

```bash
rf-evidence build results/evidence --output reports --formats html pdf docx
rf-evidence build results/evidence --output reports --formats html,pdf,docx --max-image-width 1600 --image-quality 85
```

HTML sigue siendo el formato predeterminado. PDF y Word conservan el resumen del caso, metadatos, estado final, evidencias directas, hitos, mensajes y advertencias. Las imágenes completas se ajustan sin recortar, con un máximo de dos capturas por página. Los formatos de impresión son documentos estáticos; las pestañas y controles interactivos pertenecen al HTML.

`--max-image-width` reduce el ancho conservando la proporción y sin ampliar imágenes pequeñas. `--image-quality` acepta valores 1–100 y comprime la imagen exportada como WebP; PDF y DOCX la convierten a PNG para compatibilidad de sus motores. Sin estas opciones se conserva la resolución original. Los JSON y capturas originales nunca se modifican.

### Combinar ejecución y reejecución

```bash
rf-evidence merge results/run/evidence results/rerun/evidence --output results/merged
rf-evidence build results/merged --output reports --formats html pdf docx
```

La identidad es la **suite y el nombre completo del caso**. Los nombres deben conservarse entre ejecuciones. La última entrada indicada prevalece, independientemente de su fecha o estado: un último SKIP o INCOMPLETE también reemplaza el resultado anterior. Los casos no reejecutados se conservan. Si una ejecución contiene dos casos con la misma identidad, el merge falla con `AMBIGUOUS_CASE`; usa nombres distintos para cada fila de datos.

Cada resultado conserva los intentos anteriores completos en `attempts`, junto con sus imágenes, y muestra su historial de estados en los tres formatos. El directorio combinado es independiente de las entradas: se pueden mover o retirar las carpetas originales después del merge. La salida debe estar vacía y separada de las entradas.

### Manifest de archivos

Cada `build` genera `manifest.json` con una entrada por caso: ID, suite, nombre, estado, número de intentos y una lista `files` con los reportes, JSON e imágenes originales y de intentos anteriores. Cada archivo incluye ruta relativa al manifiesto, tipo, tamaño en bytes y SHA-256. El inventario referencia los archivos existentes sin duplicarlos. Para mover el conjunto conserva la relación entre las carpetas; los reportes individuales contienen sus imágenes.

Este es el esquema propio de Evidence Reporter para integraciones y subida de evidencias. No es el formato `allure-results` ni se puede enviar directamente a Allure.

```python
from rf_evidence_reporter import build_reports, merge_results

merge_results(["results/run/evidence", "results/rerun/evidence"], "results/merged")
paths = build_reports(
    "results/merged", "reports", formats=("html", "pdf", "docx"),
    max_image_width=1600, image_quality=85,
)
```
