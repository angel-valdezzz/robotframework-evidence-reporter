# Tu primera evidencia

Registra una captura en un caso de Robot y genera el HTML al terminar. Necesitas **Python 3.12 o superior**, Robot Framework 7 y SeleniumLibrary para las capturas del navegador.

## 1. Instala la librería

!!! note "Publicación en PyPI pospuesta"
    Por ahora instala desde la revisión Git publicada. Los comandos de PyPI estarán disponibles después de la primera publicación.

=== "Poetry"

    ```bash
    poetry add "git+https://github.com/angel-valdezzz/robotframework-evidence-reporter.git@main"
    poetry add robotframework-seleniumlibrary
    ```

=== "pip"

    ```bash
    pip install "git+https://github.com/angel-valdezzz/robotframework-evidence-reporter.git@main"
    pip install robotframework-seleniumlibrary
    ```

Estos comandos instalan la rama `main`. En un proyecto de equipo, fija una revisión Git en el archivo de dependencias para hacer reproducible la instalación. Consulta el [repositorio](https://github.com/angel-valdezzz/robotframework-evidence-reporter) para el código actualizado.

## 2. Registra una captura

Guarda este ejemplo como `evidence.robot`. Usa `BROWSER:chrome` para abrir una ventana o conserva `headlesschrome` para ejecutarlo sin interfaz visible.

```robotframework
*** Settings ***
Library    SeleniumLibrary
Library    rf_evidence_reporter.EvidenceReporter
Test Teardown    Close All Browsers

*** Variables ***
${BROWSER}    headlesschrome

*** Test Cases ***
Consultar El Portal
    Open Browser    https://example.com    ${BROWSER}
    Set Report Metadata    Aplicación=Portal de ejemplo    Ambiente=Demo
    Wait Until Element Is Visible    css:h1
    Element Text Should Be    css:h1    Example Domain
    Capture Page Evidence    Portal disponible    status=PASS
```

!!! tip "Empieza sin hitos"
    Las evidencias directas funcionan sin crear bloques. Añade [hitos opcionales](guide.md#hitos-opcionales) cuando necesites agrupar un flujo de negocio.

## 3. Ejecuta y genera

=== "Poetry"

    ```bash
    poetry run robot --outputdir results evidence.robot
    poetry run rf-evidence build results/evidence --output reports
    ```

=== "pip"

    ```bash
    robot --outputdir results evidence.robot
    rf-evidence build results/evidence --output reports
    ```

Abre el archivo de `reports/` en tu navegador. El HTML incluye las imágenes, estilos y controles; no necesita conexión a Internet para consultarlo.

!!! warning "Una carpeta por ejecución"
    El generador incluye todos los `case.json` que encuentre. Usa una carpeta nueva por ejecución para no mezclar resultados anteriores.

[Continuar con hitos y metadatos](guide.md){ .md-button }
[Ver el reporte completo](demo/passed.html){ .md-button .md-button--primary }
