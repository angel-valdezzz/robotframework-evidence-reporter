---
hide:
  - toc
---

<div class="hero" markdown>
<div class="project-brand">
<img class="project-brand-light" src="assets/logo-wordmark.svg" alt="Evidence Reporter">
<img class="project-brand-dark" src="assets/logo-wordmark-dark.svg" alt="Evidence Reporter">
</div>

<span class="eyebrow">Robot Framework · Evidencias de negocio</span>

# Lo que validaste, listo para compartir

Un **HTML por caso**, con el resultado de ejecución, capturas, hitos y mensajes que explican qué ocurrió. Sin perderse entre los detalles técnicos de cada clic.

[Empezar](getting-started.md){ .md-button .md-button--primary }
[Ver reporte](demo/passed.html){ .md-button }
</div>

<div class="grid cards" markdown>

-   :material-camera-outline:{ .card-icon } **Captura lo que importa**

    ---

    Página visible, elemento o escritorio. Tú decides cuándo registrar una evidencia y cómo describirla.

    [Elegir una captura →](keywords.md)

-   :material-view-dashboard-outline:{ .card-icon } **Lee el resultado del caso**

    ---

    Resumen, Pasos y Logs. Hitos plegables, temas claro/oscuro e imágenes que puedes ampliar.

    [Explorar la demo →](demo.md)

-   :material-file-code-outline:{ .card-icon } **Genera después de ejecutar**

    ---

    Robot guarda JSON e imágenes; la CLI o Python los convierten en reportes autocontenidos.

    [Generar HTML →](generation.md)

-   :material-call-split:{ .card-icon } **Ejecuta en paralelo**

    ---

    Directorios independientes por caso para trabajar con Pabot sin sobrescribir evidencias.

    [Configurar Pabot →](parallel.md)

</div>

## Del flujo de negocio al reporte

1. **Ejecuta** el caso con Robot o Pabot.
2. **Registra** capturas y mensajes con keywords explícitas.
3. **Genera** un HTML individual y compártelo como archivo.

!!! info "Dos resultados diferentes"
    El **estatus de ejecución** viene de Robot. El **estatus de evidencia** lo eliges para describir una captura. Documentar un error con `status=FAIL` no cambia por sí mismo el resultado del caso.

## Una vista del reporte

[![Resumen de un caso en modo claro](assets/images/report-light.png){ .report-preview }](demo/passed.html)

La imagen ilustra la demo con datos ficticios. Abre el reporte para cambiar de tema, consultar los hitos y ampliar las evidencias.
