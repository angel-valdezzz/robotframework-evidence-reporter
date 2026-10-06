# Paralelo y CI/CD

Guarda este caso en `tests/portal.robot`. El directorio de salida de Robot también controla las evidencias; no hace falta un argumento de importación.

```robotframework linenums="1"
*** Settings ***
Library    SeleniumLibrary
Library    EvidenceReporter
Test Teardown    Close All Browsers

*** Test Cases ***
Consultar Portal En Paralelo
    Open Browser    https://example.com    headlesschrome
    Wait Until Element Is Visible    css:h1
    Capture Page Evidence    Portal disponible    status=PASS
```

```bash
pabot --processes 4 --testlevelsplit --outputdir results tests
rf-evidence build results/pabot_results --output reports
```

Pabot asigna a cada proceso una carpeta bajo `results/pabot_results`; sus evidencias se guardan en la subcarpeta `evidence`. El generador busca recursivamente al finalizar todos los procesos. Para Robot sin paralelo, usa `results/evidence`.

La carpeta debe pertenecer a una sola ejecución. Cada proceso escribe casos en directorios con UUID, sin un manifiesto común. Los JSON se reemplazan de forma atómica después de cada evento.

Genera después de esperar a todos los procesos. En GitHub Actions usa `if: always()` para generación y subida de artefactos. Si ejecutas desde Python, usa `try/finally` para generar tras Robot, y conserva el código de salida de las pruebas.

La captura del escritorio es explícita y puede mostrar otra ventana si varios navegadores comparten un escritorio. La librería no determina cuál corresponde al caso. Para paralelo/headless usa página visible o elemento, salvo que hayas aislado los escritorios.

## Interrupciones

Los eventos ya guardados sobreviven a una interrupción. Si no se registra `end_test`, el reporte queda `INCOMPLETE`. Esto no recupera datos nunca escritos ni garantiza captura durante un cierre forzado. Los errores de escritura inicial/final del listener aparecen en Robot y deben revisarse en el pipeline.

!!! warning "Escritorio compartido"
    Una captura de escritorio puede mostrar una ventana de otro proceso. Para paralelo o headless, utiliza página visible o elemento, o aísla explícitamente cada escritorio.

??? tip "Generar aunque fallen las pruebas"
    En GitHub Actions separa la ejecución de la generación y conserva los reportes como artefactos:

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
