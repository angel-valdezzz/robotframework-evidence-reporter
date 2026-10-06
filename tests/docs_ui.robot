*** Settings ***
Documentation     Verifica identidad, temas y búsqueda de la documentación publicada.

Library           SeleniumLibrary

Suite Setup       Abrir Documentación
Suite Teardown    Close All Browsers
Test Setup        Go To    http://localhost:8765/


*** Test Cases ***
Consultar Portada En Ambos Temas
    [Documentation]    Comprueba logo propio, tarjetas y cambio de tema en Material.
    ${logo}=    Get Element Attribute    css:.md-logo img    src
    Should Contain    ${logo}    assets/logo.svg
    Page Should Contain Element    css:.grid.cards
    Capture Page Screenshot    ${OUTPUTDIR}/docs-light.png
    Click Element    css:label[for="__palette_1"]
    Wait For Condition    return document.body.getAttribute('data-md-color-scheme') === 'slate';
    Capture Page Screenshot    ${OUTPUTDIR}/docs-dark.png
    Click Element    css:label[for="__palette_0"]
    Wait For Condition    return document.body.getAttribute('data-md-color-scheme') === 'default';

Buscar Keywords En La Documentación
    [Documentation]    Comprueba que el índice de búsqueda entrega resultados útiles.
    Click Element    css:input[data-md-component="search-query"]
    Wait Until Element Is Visible    css:input[data-md-component="search-query"]
    Input Text    css:input[data-md-component="search-query"]    Capture Page Evidence
    Wait Until Element Is Visible    css:.md-search-result__link
    Element Should Contain    css:.md-search-result__list    Capture

Consultar Ejemplos Por Pestañas
    [Documentation]    Valida alternativas de instalación y el enlace al reporte vivo.
    Go To    http://localhost:8765/getting-started/
    Click Element    css:.tabbed-labels label:nth-child(2)
    Element Should Contain    css:.tabbed-block:nth-child(2)    pip install
    Go To    http://localhost:8765/demo/passed.html
    Element Text Should Be    css:.execution-status    ✓ PASS
    Click Element    id:tab-steps
    Page Should Contain    Cuentas consultadas

Consultar Referencia Libdoc
    [Documentation]    Comprueba que MkDocs enlaza la referencia generada de la librería.
    Click Link    css:a[href="reference/keywords.html"]
    Switch Window    NEW
    Location Should Be    http://localhost:8765/reference/keywords.html
    Wait Until Page Contains    EvidenceReporter
    Wait Until Page Contains    Capture Page Evidence
    Page Should Contain    Create Milestone
    Page Should Contain    INVALID_CAPTURE_STATUS

Consultar Ejemplos Resaltados
    [Documentation]    Comprueba contexto Robot completo y líneas resaltadas en la guía.
    Go To    http://localhost:8765/guide/
    Page Should Contain    *** Settings ***
    Page Should Contain    *** Test Cases ***
    Page Should Contain Element    css:.highlight .hll
    Capture Page Screenshot    ${OUTPUTDIR}/docs-guide.png

Cambiar Idioma En Libdoc
    [Documentation]    Cambia controles y descripciones desde el menú nativo, conservando la keyword.
    Go To    http://localhost:8765/reference/keywords.html#Capture%20Page%20Evidence
    Elegir Idioma De Libdoc    Español
    Location Should Be    http://localhost:8765/es/reference/keywords.html#Capture%20Page%20Evidence
    Wait Until Page Contains    Introducción
    Page Should Contain    Captura el área visible de la página
    Element Should Contain    css:#language-container button    Idioma: Español
    Elegir Idioma De Libdoc    English
    Location Should Be    http://localhost:8765/reference/keywords.html#Capture%20Page%20Evidence
    Wait Until Page Contains    Capture the visible page area


*** Keywords ***
Abrir Documentación
    [Documentation]    Abre el sitio servido localmente por CI en un navegador aislado.
    Open Browser    http://localhost:8765/    headlesschrome
    ...    options=add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage")
    Set Window Size    1440    1000

Elegir Idioma De Libdoc
    [Documentation]    Usa el selector nativo para abrir la referencia del idioma elegido.
    [Arguments]    ${idioma}
    Click Element    css:#language-container button
    Click Link    ${idioma}
