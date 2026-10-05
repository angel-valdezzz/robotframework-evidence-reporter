# Parallel execution and CI/CD

Save this as `tests/portal.robot`. The highlighted line configures the evidence directory shared by this execution's processes.

```robotframework linenums="1" hl_lines="3"
*** Settings ***
Library    SeleniumLibrary
Library    EvidenceReporter    output_dir=${EXECDIR}/results/evidence
Test Teardown    Close All Browsers

*** Test Cases ***
Consultar Portal En Paralelo
    Open Browser    https://example.com    headlesschrome
    Wait Until Element Is Visible    css:h1
    Capture Page Evidence    Portal disponible    status=PASS
```

```bash
pabot --processes 4 --testlevelsplit --outputdir results tests
rf-evidence build results/evidence --output reports
```

Use the directory for one execution only. Processes write cases to separate UUID directories without a common manifest. JSON is replaced atomically after each event.

Generate after all processes finish. In GitHub Actions use `if: always()` for generation and artifact upload. In Python use `try/finally` to generate after Robot, while preserving the tests' exit code.

Desktop capture is explicit and can show another window when browsers share a desktop. The library does not infer which window belongs to the case. In parallel/headless execution use visible-page or element captures unless desktops are isolated.

## Interruptions

Saved events survive interruption. Without `end_test`, the report remains INCOMPLETE. This does not recover unwritten data or guarantee capture during forced termination. Initial/final listener write errors appear in Robot and must be checked in CI.

!!! warning "Shared desktop"
    A desktop capture may show another process's window. Use page or element captures, or explicitly isolate desktops.

??? tip "Generate even when tests fail"
    Separate execution from generation and retain reports as artifacts:

    ```yaml
    - run: poetry run robot --outputdir results tests
    - if: always()
      run: poetry run rf-evidence build results/evidence --output reports
    - if: always()
      uses: actions/upload-artifact@v4
      with:
        name: business-reports
        path: reports/
    ```
