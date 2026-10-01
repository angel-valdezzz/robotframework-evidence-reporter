*** Settings ***
Documentation    Validación de evidencias explícitas, estados y aislamiento por caso.

Library          EvidenceReporter


*** Test Cases ***
Evidencias Directas
    [Documentation]    Evidencias Directas.
    Set Report Metadata    Aplicación=Demo    Ambiente=QA
    Add Evidence Message    Validación de negocio registrada.
    Capture Page Evidence    Captura sin navegador

Hitos Opcionales
    [Documentation]    Hitos Opcionales.
    ${milestone}=    Create Milestone    Cliente registrado    Confirmación del alta.
    Add Evidence Message    Alta confirmada    milestone_id=${milestone}
    Add Evidence Message    Nota directa del caso

Caso Omitido
    [Documentation]    Caso Omitido.
    Add Evidence Message    Se registra el motivo antes de omitir.
    Skip    No aplica en este ambiente.

Fallo De Captura Estricto Controlado
    [Documentation]    Fallo De Captura Estricto Controlado.
    Run Keyword And Expect Error    *CAPTURE_FAILED*
    ...    Capture Page Evidence    Evidencia obligatoria    strict=${True}

Estado Final Incluye Teardown
    [Documentation]    Estado Final Incluye Teardown.
    Add Evidence Message    El cuerpo pasa; el teardown determina FAIL.
    [Teardown]    Fallar Teardown


*** Keywords ***
Fallar Teardown
    [Documentation]    Fallar Teardown.
    Fail    Fallo esperado del teardown para validar el resultado definitivo.
