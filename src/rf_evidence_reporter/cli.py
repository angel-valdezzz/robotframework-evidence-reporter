"""CLI shares the public Python generator."""

import argparse
import sys

from .builder import build_reports


def main():
    parser = argparse.ArgumentParser(
        prog="rf-evidence", description="HTML individual de evidencias de negocio"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="Generar un HTML autocontenido por caso")
    build.add_argument("results_dir")
    build.add_argument("--output", "-o", default="evidence-reports")
    args = parser.parse_args()
    try:
        for path in build_reports(args.results_dir, args.output):
            print(path)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"No se pudo generar el reporte: {error}", file=sys.stderr)
        return 1
    return 0
