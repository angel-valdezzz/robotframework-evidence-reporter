# CLI and Python

=== "CLI"

    ```bash
    rf-evidence build results/evidence --output reports
    ```

=== "Python"

    ```python hl_lines="3"
    from rf_evidence_reporter import build_reports

    reports = build_reports("results/evidence", "reports")
    ```

Output contains paths to generated reports. Exit code 0 means completed; 1 means invalid input or generation error. A FAIL case does not fail the generator: it is a valid result to report. A missing image produces a warning and visible report card.

Generation requires neither a Robot session nor a browser. The public `EvidenceRecorder` API records from Python using `start`, `milestone`, `metadata`, `event` and `finish`. `schema_version` versions the data contract.

Generation leaves original JSON unchanged, so you can regenerate with another template version. Each separately recorded case normally produces its own report with a UUID preventing same-name overwrites. Use the explicit [merge command](guide.md#combine-execution-and-rerun) when combining attempts.

There is no suite dashboard or aggregate execution index. Each HTML has an individual summary. Execution and generation dates are separate and include their time zones.

!!! tip "Regenerate without rerunning tests"
    Reuse JSON and images with a new template. Write to another directory to retain the original reports.

??? warning "Unavailable image"
    Generation displays a warning beside missing evidence without changing Robot's recorded status.

## Report design and institution branding

Reports use the same navigation, compact status labels and light/dark controls. Evidence keeps captures in Steps and messages in Logs, with level filters and search. Request opens the first captured request; Failures links directly to the affected assertion. PDF and Word share a clean metadata table, light milestone bands and evidence frames with a status accent.

Branding is optional and free. It changes presentation, not case metadata or assertion behavior. With no configuration, the original tool name, logo and palette remain.

```json
{
  "name": "Example QA",
  "palette": {
    "primary": "#164e63",
    "accent": "#155e75",
    "primary_dark": "#67e8f9",
    "accent_dark": "#7dd3fc"
  }
}
```

Use `examples/brand.json` as a runnable starting point. Add `"logo": "logo.png"` to use a local PNG, JPEG or WebP image; its path is relative to the JSON file. Logos are embedded, limited to 5 MiB and resized to at most 512 px. No external request is required to view the report. Colors use six-digit hex values. Primary colors must meet 4.5:1 contrast against the selected control text; invalid configuration fails clearly. PASS, FAIL, WARN and HTTP status colors keep their semantic meaning.

```bash
rf-evidence build results/evidence --output results/reports --formats html pdf docx --brand-config examples/brand.json
```

```python hl_lines="1 7"
from rf_evidence_reporter import build_reports

build_reports(
    "results/evidence",
    "results/reports",
    formats=("html", "pdf", "docx"),
    brand_config="examples/brand.json",
)
```
