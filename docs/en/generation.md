# CLI and Python

=== "CLI"

    ```bash
    rf-evidence build results/evidence --output reports
    ```

=== "Python"

    ```python
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
