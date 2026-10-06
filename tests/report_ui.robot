*** Settings ***
Documentation     Verifica el reporte HTML navegable con Selenium en Chrome headless.

Library           SeleniumLibrary

Suite Setup       Abrir Reporte
Suite Teardown    Close All Browsers
Test Setup        Cargar Demo


*** Test Cases ***
Cambiar Tema Del Reporte
    [Documentation]    Valida los temas y el resumen sin estatus duplicado ni impresión.
    Element Text Should Be    css:.execution-status    ✓ PASS
    Page Should Not Contain    Estado de Robot
    Page Should Not Contain    Imprimir
    Elegir Tema    light
    Capture Page Screenshot    ${OUTPUTDIR}/report-light.png
    Click Element    id:theme-toggle
    Tema Debe Ser    dark
    Capture Page Screenshot    ${OUTPUTDIR}/report-dark-summary.png

Consultar Capturas Y Ampliarlas
    [Documentation]    Comprueba los estatus de evidencia y el visualizador de imágenes.
    Elegir Tema    dark
    Click Element    id:tab-steps
    Element Should Not Be Visible    id:summary
    FOR    ${status}    IN    INFO    PASS    WARN    FAIL
        Page Should Contain Element    css:.capture[data-status="${status}"]
    END
    Capture Page Screenshot    ${OUTPUTDIR}/report-dark.png
    Click Element    css:#steps .image-button
    Element Should Be Visible    id:viewer
    Click Element    css:#viewer .close
    Element Should Not Be Visible    id:viewer

Desplegar Logs Y Navegar Con Teclado
    [Documentation]    Verifica bloques plegables y navegación accesible entre pestañas.
    Click Element    id:tab-logs
    Element Should Be Visible    id:logs
    Element Should Not Be Visible    id:steps
    Element Should Be Visible    css:#logs details[open] .log-list
    Press Keys    id:tab-logs    ARROW_LEFT
    Element Should Be Visible    id:steps

Consultar Reporte En Pantalla Móvil
    [Documentation]    Comprueba que el reporte no desborda horizontalmente en un viewport estrecho.
    Elegir Tema    light
    Set Window Size    390    844
    ${fits}=    Execute Javascript    return document.documentElement.scrollWidth <= window.innerWidth;
    Should Be True    ${fits}
    Capture Page Screenshot    ${OUTPUTDIR}/report-mobile.png

Mostrar Estatus De Ejecución
    [Documentation]    Valida casos fallidos, omitidos e incompletos sin capturas SKIP.
    FOR    ${file}    ${status}    IN    failed    FAIL    skipped    SKIP    incomplete    INCOMPLETE
        Go To    file://${EXECDIR}/docs/demo/${file}.html
        Element Should Contain    css:.execution-status    ${status}
        Click Element    id:tab-steps
        Page Should Not Contain Element    css:.capture[data-status="SKIP"]
    END

Contraer Y Expandir Hitos
    [Documentation]    Valida el estado inicial y los controles globales sin abrir evidencias directas.
    Click Element    id:tab-steps
    Element Should Not Be Visible    css:details[data-block-kind="direct"] .events
    Contar Hitos Abiertos    1
    Click Element    id:collapse-milestones
    Contar Hitos Abiertos    0
    Click Element    id:expand-milestones
    Contar Hitos Abiertos    2
    Element Should Be Visible    css:details[data-block-kind="direct"] .events
    Capture Page Screenshot    ${OUTPUTDIR}/report-milestones.png

Filtrar Advertencias Y Buscar Mensajes
    [Documentation]    Comprueba filtros globales, búsqueda y resultado vacío sin logs dentro de pasos.
    Click Element    id:view-warnings
    Element Should Be Visible    id:logs
    ${levels}=    Execute Javascript
    ...    return Array.from(document.querySelectorAll('#logs .log'))
    ...    .filter(e => !e.hidden).map(e => e.dataset.level).join(',');
    Should Not Contain    ${levels}    INFO
    Should Contain    ${levels}    WARN
    Input Text    id:log-search    mensaje-inexistente
    Element Should Be Visible    id:logs-empty
    Click Element    id:tab-steps
    Page Should Not Contain Element    css:#steps .log-list


*** Keywords ***
Abrir Reporte
    [Documentation]    Abre el HTML generado sin depender de servicios externos.
    Open Browser    file://${EXECDIR}/docs/demo/passed.html    headlesschrome
    ...    options=add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage")
    Set Window Size    1440    1000

Elegir Tema
    [Documentation]    Selecciona explícitamente el tema para obtener capturas reproducibles.
    [Arguments]    ${theme}
    ${current}=    Execute Javascript    return document.documentElement.dataset.theme;
    IF    $current != $theme    Click Element    id:theme-toggle
    Tema Debe Ser    ${theme}

Tema Debe Ser
    [Documentation]    Comprueba el tema y el estado accesible del switch.
    [Arguments]    ${theme}
    ${current}=    Execute Javascript    return document.documentElement.dataset.theme;
    Should Be Equal    ${current}    ${theme}

Cargar Demo
    [Documentation]    Restablece el reporte y el tamaño antes de cada verificación.
    Go To    file://${EXECDIR}/docs/demo/passed.html
    Set Window Size    1440    1000

Contar Hitos Abiertos
    [Documentation]    Verifica todos los hitos, no solo el primer bloque visible.
    [Arguments]    ${expected}
    ${count}=    Execute Javascript
    ...    return document.querySelectorAll('details[data-block-kind="milestone"][open]').length;
    Should Be Equal As Integers    ${count}    ${expected}
