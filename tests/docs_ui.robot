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
    Click Element    css:label[for="__search"]
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


*** Keywords ***
Abrir Documentación
    [Documentation]    Abre el sitio servido localmente por CI en un navegador aislado.
    Open Browser    http://localhost:8765/    headlesschrome
    ...    options=add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage")
    Set Window Size    1440    1000
