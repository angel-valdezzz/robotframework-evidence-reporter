# Publicación

## GitHub Pages

El workflow `docs.yml` construye MkDocs Material y genera la demo HTML desde Python. Publica mediante GitHub Actions. Configura **Settings → Pages → Source: GitHub Actions**.

## PyPI

Antes de la primera release registra un **pending trusted publisher** en PyPI:

| Campo | Valor |
| --- | --- |
| Project name | `robotframework-evidence-reporter` |
| Owner | `angel-valdezzz` |
| Repository | `robotframework-evidence-reporter` |
| Workflow | `release.yml` |
| Environment | Dejar vacío; el workflow no define environment |

Una release publicada con tag `v0.1.0` verifica la versión, construye wheel/sdist y usa `pypa/gh-action-pypi-publish` con OIDC. No almacena un token PyPI en el repositorio. La configuración del publisher se realiza en la cuenta PyPI del propietario.

Cada versión publicada es inmutable: aumenta la versión antes de otra release. Para validar el paquete desde fuente: `poetry install`. Para distribución local: `poetry build` y `pip install dist/*.whl`.
