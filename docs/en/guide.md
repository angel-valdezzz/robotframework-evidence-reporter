# User guide

Import `EvidenceReporter` in your suites. Its listener is included; do not also register `--listener`.

The flow is: Robot/Pabot records JSON and images → execution ends → `rf-evidence build` generates one report per case. The complete examples use `example.com`; save each as a `.robot` file and run from the project root. Business labels in the examples are Spanish and can use any language.

<span id="hitos-opcionales"></span>

## Optional milestones

Highlighted lines create a milestone and associate a capture and message. The last capture belongs directly to the case because no milestone ID is provided.

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

IDs belong only to the current case. There is no implicit current milestone. Direct evidence has its own block; milestones appear in creation order and their evidence in recorded order.

## Configurable information table

The highlighted line adds labels to the report information table. Metadata and messages require no browser.

```robotframework linenums="1" hl_lines="6"
*** Settings ***
Library    EvidenceReporter

*** Test Cases ***
Registrar Contexto De Negocio
    Set Report Metadata    Aplicación=ParaBank    Ambiente=Demo    Ticket=QA-123
    Add Evidence Message    Contexto del caso registrado.
```

Add as many labels as needed. Automatic fields (name, status and times) remain separate even if a custom label has the same text.

## Results and messages

Final test status is recorded after teardown. INFO is blue, WARN amber and ERROR red. A message level alone does not change Robot's result. Captures have an explicit evidence status; unavailable captures produce warnings.

Clicks and keyword arguments are not automatically recorded. This avoids excessive technical detail and automatically copying passwords entered during a flow. Explicit images and notes can still contain sensitive data; users control what they record.

<span id="estatus-de-evidencia-y-presentacion"></span>

## Evidence status and presentation

The four capture keywords accept `status=INFO` (default), `PASS`, `WARN` or `FAIL`. SKIP is invalid and produces `INVALID_CAPTURE_STATUS`. Evidence status does not change execution status. A capture failure records a warning regardless of requested status.

This example classifies two captures. FAIL demonstrates presentation; it is not a real `example.com` error and does not fail the case.

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

HTML includes Summary (Resumen), Steps (Pasos) and Logs. Summary shows one execution status badge, with SKIP amber. Steps presents captures and milestones with collapsible logs. Logs groups messages and warnings in collapsible blocks with level borders and neutral backgrounds. Light/dark selection is remembered when browser storage is available.

Visible dates include day/month/year and time with seconds. The time zone appears in the footer; JSON retains the full timestamp. Older records without capture status display INFO. There is no print button; CLI generates PDF and Word with `--formats pdf docx`.

<span id="casos-omitidos-skip"></span>

## Skipped cases (SKIP)

- `robot:skip` prevents the test body from running. Status and reason are recorded without body captures or messages.
- `Skip` or `Skip If` during execution retain earlier evidence. Later keywords do not execute.
- `--skip` and `--skiponfailure` depend on when Robot skips: only actually recorded evidence appears.
- Cases excluded with `--exclude` do not execute or generate a report.

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

!!! note "Evidence before skipping"
    Captures recorded before `Skip` remain in the report. A SKIP case can have valid earlier evidence; capture status is never SKIP. Teardowns that Robot executes can also record explicitly requested evidence.

## Explore blocks and milestones

!!! tip "Captures first"
    In **Pasos**, direct evidence starts collapsed. Its header shows capture, log and warning counts. Expand it to select **Evidencias** or **Logs del bloque**.

Milestones start expanded and can be collapsed individually. Expand/Collapse all milestones only affects milestones, preserving direct evidence state. Controls support the keyboard and do not change JSON or results.

??? example "Two milestones in one case"
    Capture a page and element, each associated with its own milestone.

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

See full signatures and arguments in the [Libdoc reference](reference/keywords.html).

## PDF, Word, merge and file inventory

Generate required formats from the same evidence JSON and images:

```bash
rf-evidence build results/evidence --output reports --formats html pdf docx
rf-evidence build results/evidence --output reports --formats html,pdf,docx --max-image-width 1600 --image-quality 85
```

HTML is the default. PDF and Word preserve the case summary, metadata, final status, direct evidence, milestones, messages and warnings. Full images fit without cropping, with up to two captures per page. Print formats are static; tabs and interactive controls belong to HTML.

Each step has its own frame, colored header and numbering within its block. Milestones are violet; PASS green, FAIL/ERROR red, WARN/SKIP/INCOMPLETE amber and INFO blue, matching HTML. The overall status is highlighted in the summary.

`--max-image-width` reduces width proportionally without enlarging small images. `--image-quality` accepts 1–100 and exports compressed WebP; PDF/DOCX convert it to PNG for engine compatibility. Without these options, original resolution is retained. Original JSON and captures remain unchanged.

#<span id="combinar-ejecucion-y-reejecucion"></span>

## Combine execution and rerun

```bash
rf-evidence merge results/run/evidence results/rerun/evidence --output results/merged
rf-evidence build results/merged --output reports --formats html pdf docx
```

Identity is the **suite and full case name**, which must remain stable between runs. The last listed input wins regardless of date or status, including a final SKIP or INCOMPLETE. Cases not rerun remain. Duplicate identities within an input fail with `AMBIGUOUS_CASE`; use unique names per data row.

Each result retains complete previous attempts in `attempts`, including images, and shows status history in all three formats. The merged directory is independent of inputs, which can be moved or removed afterwards. Output must be empty and separate from inputs.

### File manifest

Each `build` creates `manifest.json`, with case ID, suite, name, status, number of attempts and a `files` list of reports, JSON and original/prior-attempt images. Each file records its path relative to the manifest, type, byte size and SHA-256. Existing files are referenced without duplication. Preserve relative directory relationships when moving the set; individual reports contain their own images.

This is Evidence Reporter's own inventory schema for integration and evidence uploads. It is not `allure-results` and cannot be sent directly to Allure.

```python hl_lines="3-6"
from rf_evidence_reporter import build_reports, merge_results

merge_results(["results/run/evidence", "results/rerun/evidence"], "results/merged")
paths = build_reports(
    "results/merged", "reports", formats=("html", "pdf", "docx"),
    max_image_width=1600, image_quality=85,
)
```


## Report language

English is the default. Generate Spanish reports with `--language es`; this applies to HTML, PDF and Word. Case names, metadata and evidence messages retain their original text.

```bash
rf-evidence build results/evidence --output reports/es --language es --formats html pdf docx
```
