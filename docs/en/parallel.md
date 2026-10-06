# Parallel execution and CI/CD

Save this as `tests/portal.robot`. Robot's output directory also controls the evidence location; no import argument is needed.

```robotframework linenums="1" hl_lines="10"
*** Settings ***
Library    SeleniumLibrary
Library    EvidenceReporter
Test Teardown    Close All Browsers

*** Test Cases ***
Consultar Portal En Paralelo
    Open Browser    https://example.com    headlesschrome
    Wait Until Element Is Visible    css:h1
    Capture Page Evidence    Portal disponible    status=PASS
```

```bash
pabot --processes 4 --testlevelsplit --outputdir results tests
rf-evidence build results/pabot_results --output reports
```

Pabot gives each worker an output directory under `results/pabot_results`; its evidence is saved in that worker’s `evidence` subdirectory. The generator searches recursively after all workers finish. For serial Robot execution, use `results/evidence`.

Use the directory for one execution only. Processes write cases to separate UUID directories without a common manifest. JSON is replaced atomically after each event.

Generate after all processes finish. In GitHub Actions use `if: always()` for generation and artifact upload. In Python use `try/finally` to generate after Robot, while preserving the tests' exit code.

Desktop capture is explicit and can show another window when browsers share a desktop. The library does not infer which window belongs to the case. In parallel/headless execution use visible-page or element captures unless desktops are isolated.

## Interruptions

Saved events survive interruption. Without `end_test`, the report remains INCOMPLETE. This does not recover unwritten data or guarantee capture during forced termination. Initial/final listener write errors appear in Robot and must be checked in CI.

!!! warning "Shared desktop"
    A desktop capture may show another process's window. Use page or element captures, or explicitly isolate desktops.

??? tip "Generate even when tests fail"
    Separate execution from generation and retain reports as artifacts:

    ```yaml hl_lines="2-3 5 8"
    - run: poetry run robot --outputdir results tests
    - if: always()
      run: poetry run rf-evidence build results/evidence --output reports
    - if: always()
      uses: actions/upload-artifact@v4
      with:
        name: business-reports
        path: reports/
    ```
