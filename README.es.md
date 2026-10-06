# Robot Framework Evidence Reporter

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-wordmark-dark.svg">
  <img src="docs/assets/logo-wordmark.svg" alt="Evidence Reporter" width="380">
</picture>

**Reportes de evidencia de negocio en HTML, PDF y Word por caso de Robot Framework.**

[English](README.md) · **Español**

[Manual de usuario ↗](https://angel-valdezzz.github.io/robotframework-evidence-reporter/es/) · [Referencia de keywords ↗](https://angel-valdezzz.github.io/robotframework-evidence-reporter/es/reference/keywords.html) · [PyPI ↗](https://pypi.org/project/robotframework-evidence-reporter/) · [Ejemplos visuales ↗](https://angel-valdezzz.github.io/robotframework-evidence-reporter/es/demo/passed.html)


[![PyPI](https://img.shields.io/pypi/v/robotframework-evidence-reporter?logo=pypi)](https://pypi.org/project/robotframework-evidence-reporter/)
![Python](https://img.shields.io/pypi/pyversions/robotframework-evidence-reporter?logo=python)
![Robot Framework](https://img.shields.io/badge/Robot_Framework-compatible-00A6A6?logo=robotframework)
[![License](https://img.shields.io/github/license/angel-valdezzz/robotframework-evidence-reporter)](LICENSE)
[![CI](https://github.com/angel-valdezzz/robotframework-evidence-reporter/actions/workflows/ci.yml/badge.svg)](https://github.com/angel-valdezzz/robotframework-evidence-reporter/actions/workflows/ci.yml)

## Funcionalidades

- Capturas explícitas de página, elemento, escritorio e imágenes existentes.
- Hitos opcionales, mensajes de negocio y metadatos configurables.
- HTML sin conexión, salida PDF/Word y temas claro/oscuro.
- Registro paralelo, combinación de ejecución/reejecución y manifiesto con SHA-256.

## Instalación

Python 3.12+ y Robot Framework 7. SeleniumLibrary solo se exige para capturas del navegador y reutiliza su sesión activa.

```bash
pip install robotframework-evidence-reporter robotframework-seleniumlibrary
```

## Uso rápido

```robotframework
*** Settings ***
Library    SeleniumLibrary
Library    EvidenceReporter
Test Teardown    Close All Browsers

*** Test Cases ***
Portal evidence
    Open Browser    https://example.com    headlesschrome
    Wait Until Element Is Visible    css:h1
    Element Text Should Be    css:h1    Example Domain
    Set Report Metadata    Application=Example    Environment=Demo
    Capture Page Evidence    Portal available    status=PASS
```

El listener incluido registra JSON e imágenes durante la ejecución. Genera después los formatos que necesites:

```bash
robot --outputdir results evidence.robot
rf-evidence build results/evidence --output reports --formats html pdf docx
```

Los hitos son opcionales. La evidencia sin `milestone_id` pertenece directamente al caso.

## Configuración y limitaciones

Normalmente omite `output_dir`: las evidencias usan `${OUTPUTDIR}/evidence` de Robot, controlado por `--outputdir`. Para otra ubicación, usa `--variable EVIDENCE_OUTPUT_DIR:artifacts/evidence`. El argumento explícito `output_dir` tiene prioridad sobre esa variable y luego el valor predeterminado. Configura `strict` al importar cuando lo necesites. Los fallos de captura generan WARN por defecto sin cambiar el resultado; `strict=${True}` exige una captura exitosa. La evidencia admite INFO/PASS/WARN/FAIL; SKIP pertenece solo a la ejecución.

Usa una carpeta nueva por ejecución. Pabot guarda evidencias dentro de la salida de cada proceso; al terminar todos, genera recursivamente con `rf-evidence build results/pabot_results --output reports`. Los casos usan directorios UUID independientes. La captura de escritorio exige un entorno gráfico compatible y captura el escritorio local del proceso, no el remoto de Selenium Grid. No se admite página completa.

Las imágenes y notas no se censuran automáticamente. Los errores de uso e inesperados se propagan. PDF/Word son estáticos; HTML incluye controles interactivos. `manifest.json` es el inventario de este paquete, no resultados Allure.

## Ejemplos

El [ejemplo Selenium](https://github.com/angel-valdezzz/robot-framework-selenium-testing) muestra el registro de evidencia de negocio. Las demos públicas usan datos ficticios e imágenes ilustrativas identificadas. Consulta el manual para merge, tamaños de imagen, inventarios y errores de captura.

## Desarrollo y contribución

```bash
poetry install
poetry run ruff check src tests scripts
poetry run ruff format --check src tests scripts
poetry run python -m unittest discover -s tests -v
poetry run python scripts/validate.py
poetry run python docs/scripts/build_docs.py
poetry build
```

Envía los cambios mediante un pull request con verificaciones aprobadas. Actualiza ambos idiomas. Las traducciones de Libdoc viven en `docs/translations/es/libdoc.json`; la compilación rechaza entradas faltantes o desactualizadas.

## Licencia

MIT. Consulta [LICENSE](LICENSE).

## Idioma del reporte

Inglés por defecto; usa `--language es` para HTML, PDF y Word en español.

```bash
rf-evidence build results/evidence --output reports --language es --formats html pdf docx
```
