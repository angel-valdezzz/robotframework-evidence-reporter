*** Settings ***
Documentation    Validación de evidencias explícitas, estados y aislamiento por caso.

Library          SeleniumLibrary    run_on_failure=NONE
Library          rf_evidence_reporter.EvidenceReporter    output_dir=${EXECDIR}/results/browser-evidence

Test Setup       Abrir Portal
Test Teardown    Close All Browsers


*** Variables ***
${BROWSER}    chrome


*** Test Cases ***
Registrar Cliente En Portal De Demostración
    [Documentation]    Registrar Cliente En Portal De Demostración.
    Set Report Metadata    Aplicación=Portal ficticio    Ambiente=Demostración    Requerimiento=DEMO-001
    Capture Page Evidence    Formulario de alta    strict=${True}
    ${milestone}=    Create Milestone    Cliente registrado    Confirmar el alta y acceso habilitado.
    Click Element    id:register
    Wait Until Element Is Visible    id:confirmation
    Element Should Contain    id:confirmation    Cliente registrado correctamente
    Capture Element Evidence
    ...    id:confirmation
    ...    Confirmación de registro
    ...    milestone_id=${milestone}
    ...    strict=${True}
    Capture Page Evidence    Resultado del registro    milestone_id=${milestone}    strict=${True}
    Add Evidence Message    La identidad utilizada es ficticia.    milestone_id=${milestone}
    Capture Desktop Evidence    Escritorio del runner gráfico    strict=${True}


*** Keywords ***
Abrir Portal
    [Documentation]    Abrir Portal.
    Open Browser    file://${EXECDIR}/examples/application.html    ${BROWSER}
    ...    options=add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage")
    Set Window Size    1440    1000
