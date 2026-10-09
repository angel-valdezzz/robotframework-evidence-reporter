# Robot Framework Evidence Reporter

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-wordmark-dark.svg">
  <img src="docs/assets/logo-wordmark.svg" alt="Evidence Reporter" width="380">
</picture>

**Screenshots, milestones and results to document your test executions in HTML, PDF and Word.**

**English** · [Español](README.es.md)

[User guide](https://angel-valdezzz.github.io/robotframework-evidence-reporter/) · [Keyword reference](https://angel-valdezzz.github.io/robotframework-evidence-reporter/reference/keywords.html) · [PyPI](https://pypi.org/project/robotframework-evidence-reporter/) · [Visual examples](https://angel-valdezzz.github.io/robotframework-evidence-reporter/demo/passed.html)


[![PyPI](https://img.shields.io/pypi/v/robotframework-evidence-reporter?logo=pypi)](https://pypi.org/project/robotframework-evidence-reporter/)
![Python](https://img.shields.io/pypi/pyversions/robotframework-evidence-reporter?logo=python)
![Robot Framework](https://img.shields.io/badge/Robot_Framework-compatible-00A6A6?logo=robotframework)
[![License](https://img.shields.io/github/license/angel-valdezzz/robotframework-evidence-reporter)](LICENSE)
[![CI](https://github.com/angel-valdezzz/robotframework-evidence-reporter/actions/workflows/ci.yml/badge.svg)](https://github.com/angel-valdezzz/robotframework-evidence-reporter/actions/workflows/ci.yml)

## Features

- Explicit page, element, desktop and existing-image captures.
- Optional milestones, business messages and configurable metadata.
- Offline HTML, PDF/Word output and light/dark report themes.
- Parallel recording, execution/rerun merging and a SHA-256 file manifest.

## Installation

Python 3.12+ and Robot Framework 7. SeleniumLibrary is required only for browser captures and reuses its active browser.

```bash
pip install robotframework-evidence-reporter robotframework-seleniumlibrary
```

## Quick start

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

The included listener records JSON and images during execution. Generate the requested formats afterwards:

```bash
robot --outputdir results evidence.robot
rf-evidence build results/evidence --output reports --formats html pdf docx
```

Milestones are optional. Evidence without `milestone_id` belongs directly to the case.

## Configuration and limitations

Normally omit `output_dir`: evidence uses Robot's `${OUTPUTDIR}/evidence`, controlled by `--outputdir`. For an alternative location, use `--variable EVIDENCE_OUTPUT_DIR:artifacts/evidence`. An explicit import `output_dir` takes precedence over that variable, then the default. Configure `strict` on import when needed. Capture failures produce WARN by default without changing test status; `strict=${True}` requires a successful capture. Evidence accepts INFO/PASS/WARN/FAIL; SKIP belongs only to execution.

Use a new evidence directory per execution. Pabot stores evidence inside each worker’s output directory; after all workers finish, generate recursively with `rf-evidence build results/pabot_results --output reports`. Cases use independent UUID directories. Desktop capture requires a compatible graphical environment and captures the local process desktop, not a remote Selenium Grid desktop. Full-page capture is unsupported.

Images and notes are not automatically redacted. Usage errors and unexpected errors propagate. PDF/Word are static; HTML contains interactive controls. `manifest.json` is this package's inventory, not Allure results.

## Examples

The [Selenium example](https://github.com/angel-valdezzz/robot-framework-selenium-testing) demonstrates business evidence recording. Public visual demos use clearly labeled fictitious data and illustrative images. See the manual for merge, image sizing, file inventories and capture errors.

## Development and contribution

```bash
poetry install
poetry run ruff check src tests scripts
poetry run ruff format --check src tests scripts
poetry run python -m unittest discover -s tests -v
poetry run python scripts/validate.py
poetry run python docs/scripts/build_docs.py
poetry build
```

Submit changes through a pull request with passing checks. Update both documentation languages. Libdoc translations live in `docs/translations/es/libdoc.json`; builds reject missing or stale entries.

## License

MIT. See [LICENSE](LICENSE).

## Report language

English by default; use `--language es` for Spanish HTML, PDF and Word.

```bash
rf-evidence build results/evidence --output reports --language es --formats html pdf docx
```

## Report branding

Optional institution name, local logo and accessible brand colors are free. See the user guide for `brand_config` and the executable `examples/brand.json` configuration. Existing imports and capture keywords remain compatible.
