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
    Click Link    css:.er-home-content a[href$="reference/keywords.html"]
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

Controlar La Animacion Y Volver Desde La Guia
    [Documentation]    Pausa y reinicia el hero; verifica que la navegación instantánea restaura sus controles.
    Wait Until Element Is Visible    css:[data-er-pause]
    Click Element    css:[data-er-pause]
    Element Text Should Be    css:[data-er-pause]    Resume
    Comprobar Pausa De La Animacion
    Click Element    css:[data-er-replay]
    Element Text Should Be    css:[data-er-pause]    Pause
    Volver A La Portada Desde La Guia

Consultar Portada Movil En Espanol
    [Documentation]    Comprueba traducción, CTA y ausencia de desbordamiento en un viewport estrecho.
    Set Window Size    390    844
    Go To    http://localhost:8765/es/
    Wait Until Element Is Visible    css:[data-er-pause]
    Element Should Contain    css:#er-headline    Cada paso.
    Comprobar Ancho Y Enlace En Espanol
    Capture Page Screenshot    ${OUTPUTDIR}/landing-es-mobile.png
    Set Window Size    1440    1000
    Go To    http://localhost:8765/
    Capture Page Screenshot    ${OUTPUTDIR}/landing-en-desktop.png

Explorar Pasos Y Vistas De La Demostracion
    [Documentation]    Comprueba selección de evidencia, pestañas y pausa manual.
    Seleccionar Evidencia Manualmente
    Cambiar Vistas De La Demostracion

Recorrer La Evidencia Y Capturar El Diseno
    [Documentation]    Comprueba el recorrido automático y captura el diseño final en ambos idiomas.
    Click Element    css:[data-er-replay]
    Wait For Condition    return document.querySelector('[data-er-hero]').dataset.erStep === '2';    timeout=12s
    Click Element    css:[data-er-pause]
    Capture Page Screenshot    ${OUTPUTDIR}/landing-en-final.png
    Go To    http://localhost:8765/es/
    Click Element    css:[data-er-select="2"]
    Set Window Size    1440    1120
    Comprobar Controles Dentro Del Viewport
    Capture Page Screenshot    ${OUTPUTDIR}/landing-es-final.png

Consultar Evidencia En Pantallas Pequenas
    [Documentation]    Captura portátil y móvil sin desbordamiento, manteniendo las acciones visibles.
    Go To    http://localhost:8765/es/
    Click Element    css:[data-er-select="2"]
    Set Window Size    1366    768
    Comprobar Controles Dentro Del Viewport
    Capture Page Screenshot    ${OUTPUTDIR}/landing-es-laptop.png
    Capturar Evidencia En Movil
    Set Window Size    1440    1000


*** Keywords ***
Seleccionar Evidencia Manualmente
    [Documentation]    Selecciona una captura y comprueba que se pausa el recorrido.
    Click Element    css:[data-er-select="1"]
    Element Text Should Be    css:[data-er-pause]    Resume
    Element Should Contain    css:[data-er-context="1"]    Details confirmed
    Element Should Be Visible    css:[data-er-capture="1"]
    Element Should Not Be Visible    css:[data-er-capture="0"]

Cambiar Vistas De La Demostracion
    [Documentation]    Comprueba Logs, Resumen y el reinicio en la vista Pasos.
    Click Element    css:[data-er-view="logs"]
    Element Should Be Visible    id:er-view-logs
    Element Should Not Be Visible    id:er-view-steps
    Click Element    css:[data-er-view="summary"]
    Element Should Be Visible    id:er-view-summary
    Click Element    css:[data-er-replay]
    Element Should Be Visible    id:er-view-steps

Capturar Evidencia En Movil
    [Documentation]    Captura la entrada y la evidencia seleccionada en el viewport móvil.
    Set Window Size    390    844
    Comprobar Ancho Y Enlace En Espanol
    Capture Page Screenshot    ${OUTPUTDIR}/landing-es-mobile-top.png
    Scroll Element Into View    css:.er-contexts
    Capture Page Screenshot    ${OUTPUTDIR}/landing-es-mobile-evidence.png

Comprobar Controles Dentro Del Viewport
    [Documentation]    Comprueba que las acciones principales caben en pantallas de escritorio y portátil.
    ${visible}=    Execute Javascript
    ...    return [...document.querySelectorAll('.er-action')].every(el=>{
    ...    const b=el.getBoundingClientRect();return b.top>=0&&b.bottom<=innerHeight;});
    Should Be True    ${visible}

Volver A La Portada Desde La Guia
    [Documentation]    Verifica los controles después de volver a la portada con navegación instantánea.
    Click Link    css:.er-action-primary
    Wait Until Page Contains    Your first evidence
    Click Link    css:.md-logo
    Wait Until Element Is Visible    css:[data-er-pause]
    Click Element    css:[data-er-pause]
    Element Text Should Be    css:[data-er-pause]    Resume

Comprobar Pausa De La Animacion
    [Documentation]    Comprueba que la evidencia seleccionada no avanza cuando se pausa.
    ${before}=    Get Element Attribute    css:[data-er-hero]    data-er-step
    Sleep    2s
    ${after}=    Get Element Attribute    css:[data-er-hero]    data-er-step
    Should Be Equal    ${before}    ${after}

Comprobar Ancho Y Enlace En Espanol
    [Documentation]    Verifica que el móvil no desborda y abre el reporte del idioma elegido.
    ${overflow}=    Execute Javascript    return document.documentElement.scrollWidth > window.innerWidth;
    Should Not Be True    ${overflow}
    ${report}=    Get Element Attribute    css:.er-action-secondary    href
    Should Contain    ${report}    /es/demo/es/passed.html

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
