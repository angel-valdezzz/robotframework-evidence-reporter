"""CLI shares the public Python generators and merge operation."""

import argparse
import sys

from .builder import build_reports
from .merge import merge_results


def main():
    parser = argparse.ArgumentParser(
        prog="rf-evidence", description="Reportes individuales de evidencias de negocio"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="Generar HTML, PDF o Word por caso y manifest.json")
    build.add_argument("results_dir")
    build.add_argument("--language", choices=("en", "es"), default="en", help="Report language (default: en)")
    build.add_argument("--output", "-o", default="evidence-reports")
    build.add_argument(
        "--formats", nargs="+", default=["html"], help="html pdf docx; también separados por comas"
    )
    build.add_argument("--max-image-width", type=int, help="Ancho máximo en píxeles; conserva proporciones")
    build.add_argument("--image-quality", type=int, help="Calidad WebP 1-100; conserva los originales")
    merge = commands.add_parser("merge", help="Combinar ejecuciones en orden, prevalece la última")
    merge.add_argument("results_dirs", nargs="+")
    merge.add_argument("--output", "-o", required=True)
    args = parser.parse_args()
    try:
        if args.command == "merge":
            paths = merge_results(args.results_dirs, args.output)
        else:
            formats = [value for group in args.formats for value in group.split(",")]
            paths = build_reports(
                args.results_dir,
                args.output,
                formats=formats,
                language=args.language,
                max_image_width=args.max_image_width,
                image_quality=args.image_quality,
            )
        for path in paths:
            print(path)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"No se pudo completar {args.command}: {error}", file=sys.stderr)
        return 1
    return 0
