# Paralelo y CI/CD

```robotframework
Library    rf_evidence_reporter.EvidenceReporter    output_dir=${EXECDIR}/results/evidence
```

```bash
pabot --processes 4 --testlevelsplit --outputdir results tests
rf-evidence build results/evidence --output reports
```

La carpeta debe pertenecer a una sola ejecución. Cada proceso escribe casos en directorios con UUID, sin un manifiesto común. Los JSON se reemplazan de forma atómica después de cada evento.

Genera después de esperar a todos los procesos. En GitHub Actions usa `if: always()` para generación y subida de artefactos. Si ejecutas desde Python, usa `try/finally` para generar tras Robot, y conserva el código de salida de las pruebas.

La captura del escritorio es explícita y puede mostrar otra ventana si varios navegadores comparten un escritorio. La librería no determina cuál corresponde al caso. Para paralelo/headless usa página visible o elemento, salvo que hayas aislado los escritorios.

## Interrupciones

Los eventos ya guardados sobreviven a una interrupción. Si no se registra `end_test`, el reporte queda `INCOMPLETE`. Esto no recupera datos nunca escritos ni garantiza captura durante un cierre forzado. Los errores de escritura inicial/final del listener aparecen en Robot y deben revisarse en el pipeline.
