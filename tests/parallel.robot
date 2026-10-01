*** Settings ***
Documentation    Validación de evidencias explícitas, estados y aislamiento por caso.

Library          rf_evidence_reporter.EvidenceReporter    output_dir=${EXECDIR}/results/parallel-evidence


*** Test Cases ***
Cliente Uno
    [Documentation]    Cliente Uno.
    Add Evidence Message    Evidencia independiente del primer cliente.

Cliente Dos
    [Documentation]    Cliente Dos.
    ${milestone}=    Create Milestone    Registro
    Add Evidence Message    Evidencia independiente del segundo cliente.    milestone_id=${milestone}

Cliente Tres
    [Documentation]    Cliente Tres.
    Capture Page Evidence    Advertencia sin navegador.

Cliente Cuatro
    [Documentation]    Cliente Cuatro.
    Set Report Metadata    Aplicación=Ejemplo paralelo
    Add Evidence Message    Evidencia independiente del cuarto cliente.
