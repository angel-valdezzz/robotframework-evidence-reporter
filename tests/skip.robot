*** Settings ***
Documentation    Comprueba omisiones iniciales y conservación de evidencias previas.

Library          EvidenceReporter


*** Test Cases ***
Omitido Por Etiqueta
    [Documentation]    Robot no ejecuta el cuerpo marcado robot:skip.
    [Tags]    robot:skip
    Fail    El cuerpo no debe ejecutarse.

Omitido En Primera Keyword
    [Documentation]    Skip inicial no crea capturas ni mensajes.
    Skip    No aplica en este ambiente.
    Fail    El cuerpo posterior no debe ejecutarse.

Omitido Después De Capturar
    [Documentation]    Una imagen anterior a Skip se conserva.
    Attach Image Evidence    ${IMAGE_PATH}    Evidencia previa    status=INFO
    Skip    Se documentó el contexto antes de omitir.
    Fail    El cuerpo posterior no debe ejecutarse.

Omitido Por Condición
    [Documentation]    Skip If verdadero evita las siguientes keywords.
    Skip If    ${True}    Condición de omisión confirmada.
    Fail    El cuerpo posterior no debe ejecutarse.
