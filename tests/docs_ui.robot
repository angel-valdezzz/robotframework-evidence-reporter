*** Settings ***
Documentation     Verifica identidad, temas y búsqueda de la documentación publicada.

Library           SeleniumLibrary

Suite Setup       Abrir Documentación
Suite Teardown    Close All Browsers
Test Setup        Go To    ${DOCS_URL}


*** Variables ***
${DOCS_URL}    http://localhost:8765/robotframework-evidence-reporter/


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
    Click Element    css:.er-search-trigger
    Click Element    css:input[data-md-component="search-query"]
    Wait Until Element Is Visible    css:input[data-md-component="search-query"]
    Input Text    css:input[data-md-component="search-query"]    Capture Page Evidence
    Wait Until Element Is Visible    css:.md-search-result__link
    Element Should Contain    css:.md-search-result__list    Capture

Consultar Ejemplos Por Pestañas
    [Documentation]    Valida alternativas de instalación y el enlace al reporte vivo.
    Go To    ${DOCS_URL}getting-started/
    Click Element    css:.tabbed-labels label:nth-child(2)
    Element Should Contain    css:.tabbed-block:nth-child(2)    pip install
    Go To    ${DOCS_URL}demo/passed.html
    Element Text Should Be    css:.execution-status    ✓ PASS
    Click Element    id:tab-steps
    Page Should Contain    Cuentas consultadas

Consultar Referencia Libdoc
    [Documentation]    Comprueba que MkDocs enlaza la referencia generada de la librería.
    Click Link    css:.er-home-content a[href$="reference/keywords.html"]
    Switch Window    NEW
    Location Should Be    ${DOCS_URL}reference/keywords.html
    Wait Until Page Contains    EvidenceReporter
    Wait Until Page Contains    Capture Page Evidence
    Page Should Contain    Create Milestone
    Page Should Contain    INVALID_CAPTURE_STATUS

Consultar Ejemplos Resaltados
    [Documentation]    Comprueba contexto Robot completo y líneas resaltadas en la guía.
    Go To    ${DOCS_URL}guide/
    Page Should Contain    *** Settings ***
    Page Should Contain    *** Test Cases ***
    Page Should Contain Element    css:.highlight .hll
    Capture Page Screenshot    ${OUTPUTDIR}/docs-guide.png

Cambiar Idioma En Libdoc
    [Documentation]    Cambia controles y descripciones desde el menú nativo, conservando la keyword.
    Go To    ${DOCS_URL}reference/keywords.html#Capture%20Page%20Evidence
    Elegir Idioma De Libdoc    Español
    Location Should Be    ${DOCS_URL}es/reference/keywords.html#Capture%20Page%20Evidence
    Wait Until Page Contains    Introducción
    Page Should Contain    Captura el área visible de la página
    Element Should Contain    css:#language-container button    Idioma: Español
    Elegir Idioma De Libdoc    English
    Location Should Be    ${DOCS_URL}reference/keywords.html#Capture%20Page%20Evidence
    Wait Until Page Contains    Capture the visible page area

Controlar Movimiento Y Volver Desde La Guia
    [Documentation]    Comprueba pausa explícita y restauración de controles al volver desde la guía.
    Click Element    css:[data-er-pause]
    Element Text Should Be    css:[data-er-pause] span:last-child    Resume animation
    Comprobar Estado De Movimiento    true
    Click Element    css:[data-er-pause]
    Comprobar Estado De Movimiento    false
    Click Link    css:.er-action-primary
    Wait Until Page Contains    Your first evidence
    Volver Y Comprobar Movimiento

Consultar Portada Movil En Espanol
    [Documentation]    Comprueba CTA, scroll y ausencia de desbordamiento en español.
    Set Window Size    390    844
    Go To    ${DOCS_URL}es/
    Element Should Contain    css:#er-headline    Cada paso.
    Comprobar Portada Sin Desbordamiento
    Capturar Portada    landing-es-mobile.png
    Set Window Size    1440    1000

Capturar Diseno En Varios Viewports
    [Documentation]    Captura la composición sin demo y con cabecera transparente en EN/ES.
    Click Element    css:[data-er-pause]
    Capturar Portada    landing-en-final.png
    Go To    ${DOCS_URL}es/
    Set Window Size    1440    1167
    Click Element    css:[data-er-pause]
    Comprobar Portada Sin Desbordamiento
    Capturar Portada    landing-es-final.png
    Capturar Portada En Pantallas Pequenas

Explorar Contenido Y Hover
    [Documentation]    Comprueba iluminación de botones, ancla de scroll y ejemplos reales.
    Comprobar Iluminacion Del Boton
    Capture Page Screenshot    ${OUTPUTDIR}/landing-hover.png
    Mouse Over    css:.er-scroll-cue
    Capture Page Screenshot    ${OUTPUTDIR}/landing-scroll-hover.png
    Click Link    css:.er-scroll-cue
    Wait For Condition    return scrollY > 100;
    Page Should Contain    Evidence that explains the result
    Page Should Contain Element    css:.er-format-preview iframe
    Page Should Not Contain Element    css:.er-preview
    Capture Page Screenshot    ${OUTPUTDIR}/landing-content.png

Conservar Idioma Tema Y Encabezado
    [Documentation]    Comprueba idioma, tema y sincronía del fondo del encabezado y navegación.
    Click Link    css:.er-action-primary
    Click Element    css:label[for="__palette_1"]
    Wait For Condition    return document.body.getAttribute('data-md-color-scheme') === 'slate';
    Click Element    css:.md-select button
    Click Link    Español
    Location Should Be    ${DOCS_URL}es/getting-started/
    Wait For Condition    return document.body.getAttribute('data-md-color-scheme') === 'slate';
    ${animated}=    Execute Javascript
    ...    const header=document.querySelector('.md-header'),tabs=document.querySelector('.md-tabs');
    ...    const a=getComputedStyle(header),b=getComputedStyle(tabs);
    ...    return a.animationName==='er-header-flow' && b.animationName===a.animationName &&
    ...    a.backgroundImage===b.backgroundImage && a.backgroundPosition===b.backgroundPosition &&
    ...    Math.abs(header.getAnimations()[0].currentTime-tabs.getAnimations()[0].currentTime)<1;
    Should Be True    ${animated}
    Capture Page Screenshot    ${OUTPUTDIR}/docs-es-header.png


*** Keywords ***
Volver Y Comprobar Movimiento
    [Documentation]    Comprueba que la portada restaura su control al volver desde la guía.
    Click Link    css:.md-logo
    Wait Until Element Is Visible    css:[data-er-pause]
    Click Element    css:[data-er-pause]
    Comprobar Estado De Movimiento    true
    Click Element    css:[data-er-pause]

Capturar Portada En Pantallas Pequenas
    [Documentation]    Captura portátil, móvil y tableta con sus controles visibles.
    Set Window Size    1366    768
    Comprobar Portada Sin Desbordamiento
    Capturar Portada    landing-es-laptop.png
    Set Window Size    390    844
    Comprobar Portada Sin Desbordamiento
    Capturar Portada    landing-es-mobile-top.png
    Set Window Size    820    1180
    Comprobar Portada Sin Desbordamiento
    Capturar Portada    landing-es-tablet.png
    Set Window Size    1440    1000

Comprobar Iluminacion Del Boton
    [Documentation]    Comprueba que el hover ilumina el contorno.
    Mouse Over    css:.er-action-primary
    ${shadow}=    Execute Javascript
    ...    return getComputedStyle(document.querySelector('.er-action-primary')).boxShadow;
    Should Not Be Equal    ${shadow}    none

Capturar Portada
    [Documentation]    Captura la portada desde arriba.
    [Arguments]    ${archivo}
    Execute Javascript    window.scrollTo(0,0);
    Capture Page Screenshot    ${OUTPUTDIR}/${archivo}

Comprobar Estado De Movimiento
    [Documentation]    La pausa solicitada se aplica a la animación ambiental.
    [Arguments]    ${estado}
    ${actual}=    Get Element Attribute    css:body    data-er-motion-paused
    Should Be Equal    ${actual}    ${estado}

Comprobar Portada Sin Desbordamiento
    [Documentation]    Comprueba ancho, acciones y separación de idioma/búsqueda.
    Execute Javascript    window.scrollTo(0,0);
    ${overflow}=    Execute Javascript
    ...    return document.documentElement.scrollWidth > innerWidth ||
    ...    document.querySelector("#er-headline").scrollWidth > document.querySelector("#er-headline").clientWidth;
    Should Not Be True    ${overflow}
    ${visible}=    Execute Javascript
    ...    return [...document.querySelectorAll('.er-action')].every(el=>{
    ...    const b=el.getBoundingClientRect();return b.top>=0&&b.bottom<=innerHeight;});
    Should Be True    ${visible}
    Comprobar Indicacion De Scroll
    ${separate}=    Execute Javascript
    ...    const a=document.querySelector('.md-select button').getBoundingClientRect();
    ...    const b=document.querySelector('.er-search-trigger').getBoundingClientRect();
    ...    return a.right<=b.left;
    Should Be True    ${separate}
    ${transparent}=    Execute Javascript
    ...    return getComputedStyle(document.querySelector('.md-header')).backgroundColor;
    Should Be Equal    ${transparent}    rgba(0, 0, 0, 0)

Comprobar Indicacion De Scroll
    [Documentation]    Comprueba que el botón para bajar queda dentro de la portada completa.
    ${reachable}=    Execute Javascript
    ...    const hero=document.querySelector('[data-er-hero]').getBoundingClientRect();
    ...    const cue=document.querySelector('.er-scroll-cue').getBoundingClientRect();
    ...    return cue.top>=hero.top && cue.bottom<=hero.bottom;
    Should Be True    ${reachable}

Abrir Documentación
    [Documentation]    Abre el sitio servido localmente por CI en un navegador aislado.
    Open Browser    ${DOCS_URL}    headlesschrome
    ...    options=add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage")
    Set Window Size    1440    1000

Elegir Idioma De Libdoc
    [Documentation]    Usa el selector nativo para abrir la referencia del idioma elegido.
    [Arguments]    ${idioma}
    Click Element    css:#language-container button
    Click Link    ${idioma}
