# Guía de uso

Importa `rf_evidence_reporter.EvidenceReporter` en las suites. La instancia incluye su listener: no necesitas registrar también `--listener`.

El ciclo es: Robot/Pabot registra JSON e imágenes → termina la ejecución → `rf-evidence build` genera un HTML por caso.

## Hitos opcionales

```robotframework
${milestone}=    Create Milestone    Cliente registrado    Confirmación del alta.
Capture Page Evidence    Registro exitoso    milestone_id=${milestone}
Add Evidence Message    Cuenta habilitada    milestone_id=${milestone}
Capture Page Evidence    Evidencia directa sin hito
```

El ID pertenece exclusivamente al caso actual. No hay un hito actual implícito. Las evidencias directas se muestran en su bloque; los hitos se muestran en el orden de creación y sus evidencias en el orden registrado.

## Tabla configurable

```robotframework
Set Report Metadata    Aplicación=ParaBank    Ambiente=Demo    Ticket=QA-123
```

Añade tantas etiquetas como necesites. Los campos automáticos (nombre, estado, tiempos) se conservan aunque una etiqueta personalizada tenga el mismo texto.

## Resultado y mensajes

El estado final se registra después del teardown. INFO es azul, WARN naranja y ERROR rojo. El nivel de un mensaje no cambia por sí mismo el resultado de Robot. No se inventan estados para capturas: una captura está disponible o genera una advertencia.

No se captura cada clic ni se copian argumentos de keywords automáticamente. Esto evita saturar el reporte y registrar contraseñas introducidas durante el flujo. Las imágenes y notas explícitas pueden contener datos sensibles; el usuario controla lo que registra.
