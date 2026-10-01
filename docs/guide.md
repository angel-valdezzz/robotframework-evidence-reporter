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

## Estatus de evidencia y presentación

Las cuatro keywords de captura aceptan `status=INFO` (por defecto), `PASS`, `WARN` o `FAIL`. No aceptan `SKIP`; un valor inválido produce `INVALID_CAPTURE_STATUS`. El estatus describe la evidencia y no modifica el resultado de Robot. Si la captura falla, se registra una advertencia independientemente del estatus solicitado.

```robotframework
Capture Page Evidence    Error mostrado por la aplicación    status=FAIL
Capture Element Evidence    css:.confirmation    Alta confirmada    status=PASS
```

El HTML tiene pestañas **Resumen**, **Pasos** y **Logs**. Resumen muestra una sola insignia de estatus de ejecución (`SKIP` en amarillo). Pasos presenta capturas e hitos; sus logs son plegables. Logs agrupa mensajes y advertencias en bloques plegables, con bordes por nivel y fondo neutro. El switch permite elegir modo claro u oscuro; conserva la preferencia cuando el navegador permite almacenamiento local.

Las fechas visibles incluyen día/mes/año y hora con segundos. La zona horaria se indica al pie y el JSON conserva el timestamp completo. Los registros anteriores sin estatus de captura se presentan como `INFO`. No hay botón de impresión; PDF y Word quedan para una etapa posterior.
