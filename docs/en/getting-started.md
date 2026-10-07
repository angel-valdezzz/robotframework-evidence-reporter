---
title: Your first evidence
tags:
  - Captures
  - Integration
---

# Your first evidence

Capture evidence in a Robot test and generate HTML afterwards. Use **Python 3.12+**, Robot Framework 7 and SeleniumLibrary for browser captures.

## 1. Install the library

The package is published on [PyPI](https://pypi.org/project/robotframework-evidence-reporter/).

=== "Poetry"

    ```bash
    poetry add robotframework-evidence-reporter
    poetry add robotframework-seleniumlibrary
    ```

=== "pip"

    ```bash
    pip install robotframework-evidence-reporter
    pip install robotframework-seleniumlibrary
    ```

Pin a package version in your team's dependency file for reproducible installation. The [repository](https://github.com/angel-valdezzz/robotframework-evidence-reporter) contains current source code.

## 2. Record a capture

Save this as `evidence.robot`. Use `BROWSER:chrome` for a visible window or keep `headlesschrome` for headless execution.

```robotframework linenums="1" hl_lines="3 15"
*** Settings ***
Library    SeleniumLibrary
Library    EvidenceReporter
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

!!! tip "Start without milestones"
    Direct evidence works without groups. Add [optional milestones](guide.md#optional-milestones) to group a business flow.

## 3. Run and generate

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

Open the file in `reports/`. Its images, styles and controls are embedded, so reading it requires no Internet connection.

!!! warning "One directory per execution"
    Generation includes every discovered `case.json`. Use a new directory for each execution to avoid mixing prior results.

[Continue with milestones and metadata](guide.md){ .md-button }
[Visual examples](demo/passed.html){ .md-button .md-button--primary }

## Output directory

Normally import `EvidenceReporter` without output arguments and run `robot --outputdir results tests`. Evidence goes into `results/evidence`. To choose a separate location, use `robot --outputdir results --variable EVIDENCE_OUTPUT_DIR:artifacts/evidence tests`. An explicit library `output_dir` still takes precedence for compatibility. For Pabot, see [parallel execution](parallel.md).

## Choose the right capture

| What you want to show | Keyword | When to use it |
| --- | --- | --- |
| Visible browser page | `Capture Page Evidence` | A completed screen or confirmation |
| One browser element | `Capture Element Evidence` | A specific result, message or component |
| Desktop | `Capture Desktop Evidence` | A desktop session where capture is available |
| Existing image file | `Attach Image Evidence` | An image produced by another tool |

Check exact arguments and environment requirements in [Keyword Reference](reference/keywords.html). Browser page capture records the viewport; it is not a full-page capture.

*[CLI]: Command-line interface
*[Pabot]: Parallel executor for Robot Framework
