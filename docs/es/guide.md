---
title: Guía de uso
tags:
  - Capturas
  - Reportes
---

# Guía de uso

Importa `EvidenceReporter` en las suites. La instancia incluye su listener: no necesitas registrar también `--listener`.

El ciclo es: Robot/Pabot registra JSON e imágenes → termina la ejecución → `rf-evidence build` genera un HTML por caso. Estos ejemplos completos usan `example.com`; guarda cada uno como un archivo `.robot` y ejecútalo desde la raíz de tu proyecto.

## Hitos opcionales

Las líneas resaltadas crean un hito y le asignan una captura y un mensaje. La última captura se registra directamente en el caso porque no recibe el ID.

```robotframework linenums="1" hl_lines="10-12"
*** Settings ***
Library    SeleniumLibrary
Library    EvidenceReporter
Test Teardown    Close All Browsers

*** Test Cases ***
Consultar Portal Con Un Hito
    Open Browser    https://example.com    headlesschrome
    Wait Until Element Is Visible    css:h1
    ${milestone}=    Create Milestone    Portal consultado    Página de ejemplo disponible.
    Capture Page Evidence    Portal disponible    milestone_id=${milestone}    status=PASS
    Add Evidence Message    Se confirmó el acceso.    milestone_id=${milestone}
    Capture Page Evidence    Evidencia directa sin hito
```

El ID pertenece exclusivamente al caso actual. No hay un hito actual implícito. Las evidencias directas se muestran en su bloque; los hitos se muestran en el orden de creación y sus evidencias en el orden registrado.

## Tabla configurable

La línea resaltada agrega etiquetas a la tabla de información del reporte. No necesitas un navegador para registrar metadatos o mensajes.

```robotframework linenums="1" hl_lines="6"
*** Settings ***
Library    EvidenceReporter

*** Test Cases ***
Registrar Contexto De Negocio
    Set Report Metadata    Aplicación=ParaBank    Ambiente=Demo    Ticket=QA-123
    Add Evidence Message    Contexto del caso registrado.
```

Añade tantas etiquetas como necesites. Los campos automáticos (nombre, estado, tiempos) se conservan aunque una etiqueta personalizada tenga el mismo texto.

## Resultado y mensajes

El estado final se registra después del teardown. INFO es azul, WARN naranja y ERROR rojo. El nivel de un mensaje no cambia por sí mismo el resultado de Robot. Las capturas tienen un estatus explícito que describe su contenido; si no se obtienen, se registra una advertencia.

No se captura cada clic ni se copian argumentos de keywords automáticamente. Esto evita saturar el reporte y registrar contraseñas introducidas durante el flujo. Las imágenes y notas explícitas pueden contener datos sensibles; el usuario controla lo que registra.

## Estatus de evidencia y presentación

Las cuatro keywords de captura aceptan `status=INFO` (por defecto), `PASS`, `WARN` o `FAIL`. No aceptan `SKIP`; un valor inválido produce `INVALID_CAPTURE_STATUS`. El estatus describe la evidencia y no modifica el resultado de Robot. Si la captura falla, se registra una advertencia independientemente del estatus solicitado.

Este ejemplo clasifica dos evidencias explícitamente. La segunda usa `FAIL` para demostrar su presentación; no representa un error real de `example.com` y no hace fallar el caso.

```robotframework linenums="1" hl_lines="11-12"
*** Settings ***
Library    SeleniumLibrary
Library    EvidenceReporter
Test Teardown    Close All Browsers

*** Test Cases ***
Clasificar Evidencias Del Portal
    Open Browser    https://example.com    headlesschrome
    Wait Until Element Is Visible    css:h1
    Element Text Should Be    css:h1    Example Domain
    Capture Element Evidence    css:h1    Título confirmado    status=PASS
    Capture Page Evidence    Diagnóstico ilustrativo    status=FAIL
```

El HTML tiene pestañas **Resumen**, **Pasos** y **Logs**. Resumen muestra una sola insignia de estatus de ejecución (`SKIP` en amarillo). Pasos presenta capturas e hitos; sus logs son plegables. Logs agrupa mensajes y advertencias en bloques plegables, con bordes por nivel y fondo neutro. El switch permite elegir modo claro u oscuro; conserva la preferencia cuando el navegador permite almacenamiento local.

Las fechas visibles incluyen día/mes/año y hora con segundos. La zona horaria se indica al pie y el JSON conserva el timestamp completo. Los registros anteriores sin estatus de captura se presentan como `INFO`. No hay botón de impresión; PDF y Word se generan desde la CLI con `--formats pdf docx`.

## Casos omitidos (SKIP)

- Con la etiqueta `robot:skip`, Robot no ejecuta el cuerpo del caso. Se registra su estado y motivo, sin capturas ni mensajes del cuerpo.
- Con `Skip` o `Skip If` durante la ejecución, se conservan las evidencias ya registradas. Las keywords posteriores no se ejecutan.
- `--skip` y `--skiponfailure` también dependen del momento en que Robot omite el caso: solo aparecen las evidencias que realmente se registraron.
- Los casos excluidos con `--exclude` no se ejecutan ni generan un reporte.

```robotframework linenums="1" hl_lines="6 11"
*** Settings ***
Library    EvidenceReporter

*** Test Cases ***
Omitido Desde El Inicio
    [Tags]    robot:skip
    Add Evidence Message    Este mensaje no se ejecuta.

Omitido Durante La Ejecución
    Add Evidence Message    Se comprobó que el ambiente no aplica.
    Skip    Funcionalidad no disponible en este ambiente.
    Add Evidence Message    Este mensaje tampoco se ejecuta.
```

!!! note "Evidencias anteriores a la omisión"
    Si antes de `Skip` llamaste una keyword de captura, su imagen permanece en el reporte. Un caso `SKIP` puede tener evidencias válidas anteriores a la omisión; una captura nunca recibe estatus `SKIP`. Los teardowns que Robot llegue a ejecutar también pueden registrar evidencias si las solicitas explícitamente.

## Consultar bloques y hitos

!!! tip "Capturas primero"
    En **Pasos**, las evidencias directas empiezan plegadas. Su cabecera muestra capturas, logs y advertencias. Al abrir el bloque puedes elegir **Evidencias** o **Logs del bloque**.

Los hitos empiezan abiertos y se pueden contraer individualmente. **Expandir todos los hitos** y **Contraer todos los hitos** actúan solo sobre los hitos, sin modificar las evidencias directas. Los controles funcionan con teclado; no cambian los JSON ni los resultados.

??? example "Dos hitos en el mismo caso"
    El ejemplo toma una captura de página y una de elemento, cada una asignada a un hito distinto.

    ```robotframework linenums="1" hl_lines="10-13"
    *** Settings ***
    Library    SeleniumLibrary
    Library    EvidenceReporter
    Test Teardown    Close All Browsers

    *** Test Cases ***
    Consultar Portal Y Su Título
        Open Browser    https://example.com    headlesschrome
        Wait Until Element Is Visible    css:h1
        ${portal}=    Create Milestone    Portal consultado
        Capture Page Evidence    Página disponible    milestone_id=${portal}    status=PASS
        ${heading}=    Create Milestone    Título validado
        Capture Element Evidence    css:h1    Título del portal    milestone_id=${heading}    status=PASS
    ```

Consulta las firmas y los argumentos completos en la [referencia Libdoc](reference/keywords.html).

## PDF Word merge e inventario de archivos

Genera los formatos que necesites desde los mismos JSON e imágenes de evidencia:

```bash
rf-evidence build results/evidence --output reports --formats html pdf docx
rf-evidence build results/evidence --output reports --formats html,pdf,docx --max-image-width 1600 --image-quality 85
```

HTML sigue siendo el formato predeterminado. PDF y Word conservan el resumen del caso, metadatos, estado final, evidencias directas, hitos, mensajes y advertencias. Las imágenes completas se ajustan sin recortar, con un máximo de dos capturas por página. Los formatos de impresión son documentos estáticos; las pestañas y controles interactivos pertenecen al HTML.

Cada paso se presenta en un marco propio con cabecera de color y numeración dentro de su bloque. Los hitos usan violeta; PASS verde, FAIL y ERROR rojo, WARN, SKIP e INCOMPLETE ámbar, e INFO azul, con la misma paleta del HTML. El estado general también se destaca en el resumen.

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

```python hl_lines="3-6"
from rf_evidence_reporter import build_reports, merge_results

merge_results(["results/run/evidence", "results/rerun/evidence"], "results/merged")
paths = build_reports(
    "results/merged", "reports", formats=("html", "pdf", "docx"),
    max_image_width=1600, image_quality=85,
)
```


## Idioma del reporte

El idioma predeterminado es inglés. Usa `--language es` para generar HTML, PDF y Word en español. Los nombres de casos, metadata y mensajes conservan su texto original.

```bash
rf-evidence build results/evidence --output reports/es --language es --formats html pdf docx
```
