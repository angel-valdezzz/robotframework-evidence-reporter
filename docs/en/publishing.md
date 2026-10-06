# Development and publishing

## GitHub Pages

`docs.yml` generates demos, English/Spanish Libdoc and both MkDocs builds, then publishes via GitHub Actions. Configure **Settings → Pages → Source: GitHub Actions**.

### Generate documentation locally

From the project root:

```bash
poetry run python docs/scripts/build_docs.py
poetry run python -m http.server 8000 --directory site
```

English sources live in `docs/en/` and publish at the root; Spanish sources live in `docs/es/` and publish under `/es/`. Shared assets and demo outputs are copied into both builds. Keep counterpart filenames identical so language selection retains the page.

Open `/keywords/` for the reference entry page or `/reference/keywords.html` for Libdoc directly. Spanish counterparts have `/es/` prefixes. Generated Libdoc HTML is rebuilt rather than committed.

When changing a keyword, update its English docstring and Spanish translation in `docs/translations/es/libdoc.json`, including the source SHA-256. Builds reject missing or stale translations. Keep signatures in the library instead of maintaining another table manually. The native Libdoc language menu switches controls and descriptions.

Preview the complete site with `poetry run python -m http.server 8000 --directory site` after building. The selector links to production URLs, so verify it on Pages as well.

## PyPI

The package is published on PyPI. Trusted Publishing uses this configuration:

| Field | Value |
| --- | --- |
| Project name | `robotframework-evidence-reporter` |
| Owner | `angel-valdezzz` |
| Repository | `robotframework-evidence-reporter` |
| Workflow | `release.yml` |
| Environment | Empty; the workflow defines no environment |

A `pyproject.toml` change integrated into `main` activates publication. A release with a matching version tag can also trigger it. The workflow validates release versions, builds wheel/sdist and uses `pypa/gh-action-pypi-publish` with OIDC. No PyPI token is stored in the repository; publisher configuration belongs to the owner's PyPI account.

Before publishing, the workflow verifies `Library    EvidenceReporter` from the installed wheel and retains distribution artifacts even if PyPI authentication fails.

Published versions are immutable: increment the version for another release. Use `poetry install` for source development, or `poetry build` and `pip install dist/*.whl` for local distributions.
