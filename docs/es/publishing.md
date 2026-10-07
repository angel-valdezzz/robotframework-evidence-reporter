---
title: Publicación
tags:
  - Desarrollo
---

# Publicación

## GitHub Pages

El workflow `docs.yml` genera la demo HTML y la referencia de keywords con Libdoc desde los docstrings de la librería, y después construye MkDocs Material. Publica mediante GitHub Actions. Configura **Settings → Pages → Source: GitHub Actions**.

### Generar la documentación localmente

Desde la raíz del proyecto:

```bash
poetry run python docs/scripts/build_docs.py
poetry run python -m http.server 8000 --directory site
```

Abre `/keywords/` para acceder a la referencia o `/reference/keywords.html` para consultar Libdoc directamente. El HTML generado se publica en Pages, pero no se versiona: cada compilación lo reconstruye desde el código. Al cambiar una keyword, actualiza su docstring; no mantengas otra tabla de firmas en MkDocs.

## PyPI

Antes de la primera release registra un **pending trusted publisher** en PyPI:

| Campo | Valor |
| --- | --- |
| Project name | `robotframework-evidence-reporter` |
| Owner | `angel-valdezzz` |
| Repository | `robotframework-evidence-reporter` |
| Workflow | `release.yml` |
| Environment | Dejar vacío; el workflow no define environment |

Un cambio de `pyproject.toml` integrado en `main` activa la publicación. También puede activarse con una release cuyo tag coincida con la versión (por ejemplo, `v0.1.0`). El workflow verifica la versión en las releases, construye wheel/sdist y usa `pypa/gh-action-pypi-publish` con OIDC. No almacena un token PyPI en el repositorio. La configuración del publisher se realiza en la cuenta PyPI del propietario.

Antes de publicar, el workflow prueba la importación `Library    EvidenceReporter` desde el wheel instalado y conserva wheel/sdist como artefactos, incluso si el paso posterior de PyPI no puede autenticarse.

Cada versión publicada es inmutable: aumenta la versión antes de otra release. Para validar el paquete desde fuente: `poetry install`. Para distribución local: `poetry build` y `pip install dist/*.whl`.

## Mantener los idiomas

El inglés vive en `docs/en/` y se publica en la raíz. El español vive en `docs/es/`
y se publica bajo `/es/`. Conserva los mismos nombres de páginas en ambos idiomas.
Las traducciones de Libdoc viven en `docs/translations/es/libdoc.json`; la compilación
rechaza entradas faltantes o desactualizadas. El selector nativo de Libdoc cambia los controles y las descripciones. Actualiza ambos textos y el SHA-256 del original cuando cambie una keyword.

## Piloto de documentación

La portada utiliza `docs/overrides/home.html`, estilos propios en `docs/assets/stylesheets/landing.css` y una animación Canvas pequeña en `docs/assets/landing.js`. Se pausa fuera de pantalla y en pestañas en segundo plano, respeta el movimiento reducido y muestra el contenido completo sin JavaScript. La suscripción de navegación instantánea de Material libera los observers antes de montar otra escena.

La construcción bilingüe activa búsqueda, etiquetas, tarjetas sociales, privacidad y optimización de imágenes. Mermaid 11.12.0 y las fuentes DejaVu Sans con licencia se incluyen localmente. `build_docs.py` prepara la caché de fuentes de tarjetas sociales para evitar descargarlas. Instala `pngquant` antes de construir (en Ubuntu: `sudo apt-get install pngquant`); CI lo instala automáticamente. Poetry incluye las dependencias de imágenes de Material.

Agrega páginas equivalentes en `docs/en` y `docs/es`, selecciona etiquetas útiles y prioriza componentes Markdown nativos. La animación de portada es una demo explicativa; los reportes de ejemplo se generan con el paquete. Analytics, comentarios y despliegue versionado quedan como decisiones futuras separadas.
