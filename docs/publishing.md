# Publicación

## GitHub Pages

El workflow `docs.yml` genera la demo HTML y la referencia de keywords con Libdoc desde los docstrings de la librería, y después construye MkDocs Material. Publica mediante GitHub Actions. Configura **Settings → Pages → Source: GitHub Actions**.

### Generar la documentación localmente

Desde la raíz del proyecto:

```bash
poetry run python scripts/demo.py
poetry run python -m robot.libdoc rf_evidence_reporter.EvidenceReporter docs/reference/keywords.html
poetry run mkdocs build --strict
poetry run mkdocs serve
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

Una release publicada con tag `v0.1.0` verifica la versión, construye wheel/sdist y usa `pypa/gh-action-pypi-publish` con OIDC. No almacena un token PyPI en el repositorio. La configuración del publisher se realiza en la cuenta PyPI del propietario.

Cada versión publicada es inmutable: aumenta la versión antes de otra release. Para validar el paquete desde fuente: `poetry install`. Para distribución local: `poetry build` y `pip install dist/*.whl`.
