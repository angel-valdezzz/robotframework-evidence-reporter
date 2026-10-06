"""Generate public examples with synthetic data and clearly labelled mock screenshots."""

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from rf_evidence_reporter import EvidenceRecorder, build_reports

root = Path("results/demo")
if root.exists():
    shutil.rmtree(root)
root.mkdir(parents=True)
Path("docs/demo").mkdir(parents=True, exist_ok=True)
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font = ImageFont.truetype(font_path, 22) if Path(font_path).exists() else ImageFont.load_default(size=22)
large = ImageFont.truetype(font_path, 34) if Path(font_path).exists() else ImageFont.load_default(size=34)
image = Image.new("RGB", (1200, 650), "#eef4f8")
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, 1200, 90), fill="#15314b")
draw.text((45, 28), "Portal de clientes | DEMO CON DATOS FICTICIOS", font=font, fill="white")
draw.rounded_rectangle((140, 145, 1060, 545), radius=18, fill="white")
draw.text((190, 195), "Cliente registrado correctamente", font=large, fill="#146b42")
draw.text((190, 280), "Cliente: Ana Pruebas", font=font, fill="#18354c")
draw.text((190, 330), "El acceso al portal quedo habilitado.", font=font, fill="#52657c")
draw.text((190, 435), "Imagen ilustrativa; no corresponde a una ejecucion real.", font=font, fill="#52657c")
for status, filename in [
    ("PASS", "passed.html"),
    ("FAIL", "failed.html"),
    ("SKIP", "skipped.html"),
    ("INCOMPLETE", "incomplete.html"),
]:
    recorder = EvidenceRecorder(root)
    recorder.start(
        "Registrar cliente y consultar sus cuentas",
        "Demostración",
        "",
    )
    if status == "SKIP":
        recorder.finish("SKIP", 0.0, "Caso omitido antes de ejecutar el cuerpo (ejemplo de robot:skip).")
        paths = build_reports(recorder.case_dir, root / "html")
        shutil.copyfile(paths[0], Path("docs/demo") / filename)
        continue
    recorder.metadata({"Aplicación": "Portal de clientes", "Ambiente": "Demo", "Requerimiento": "DEMO-001"})
    recorder.event("Se inició la validación de negocio.")
    milestone = recorder.milestone("Cliente registrado", "Confirmación del alta y acceso habilitado.")
    image.save(recorder.case_dir / "registration.png")
    recorder.event(
        "Confirmación de registro",
        kind="capture",
        capture_type="page",
        status="PASS",
        milestone_id=milestone,
        description="Captura ilustrativa del resultado esperado.",
        image="registration.png",
        width=1200,
        height=650,
        url="https://example.test/clientes",
        page_title="Portal ficticio",
    )
    for evidence_status, title in [
        ("INFO", "Contexto del formulario"),
        ("WARN", "Datos que requieren revisión"),
        ("FAIL", "Error documentado en la aplicación"),
    ]:
        recorder.event(
            title,
            kind="capture",
            capture_type="element",
            status=evidence_status,
            description="Ejemplo visual de estatus de evidencia; no determina el resultado del caso.",
            image="registration.png",
            width=1200,
            height=650,
            milestone_id=milestone,
        )
    recorder.event("Mensaje de negocio que requiere revisión.", level="WARN", milestone_id=milestone)
    recorder.event("Error documentado para diagnóstico.", level="ERROR", milestone_id=milestone)
    recorder.event(
        "El escritorio no estaba disponible en esta demostración.",
        kind="capture_warning",
        level="WARN",
        reason="DESKTOP_UNAVAILABLE: ejemplo de advertencia sin afectar el caso.",
    )
    accounts = recorder.milestone(
        "Cuentas consultadas", "Verificación de la identidad y disponibilidad de cuentas."
    )
    account_image = Image.new("RGB", (1200, 650), "#f0f4fb")
    account_draw = ImageDraw.Draw(account_image)
    account_draw.rectangle((0, 0, 1200, 90), fill="#33277d")
    account_draw.text((45, 28), "Cuentas | DEMO CON DATOS FICTICIOS", font=font, fill="white")
    account_draw.rounded_rectangle((140, 145, 1060, 545), radius=18, fill="white")
    account_draw.text((190, 190), "Cuentas de Ana Pruebas", font=large, fill="#5744cc")
    account_draw.text((190, 290), "Cuenta de demostracion: DEMO-001", font=font, fill="#18354c")
    account_draw.text((190, 345), "Saldo ficticio: $1,250.00 MXN", font=font, fill="#146b42")
    account_draw.text(
        (190, 440), "Imagen ilustrativa; no es informacion bancaria real.", font=font, fill="#52657c"
    )
    account_image.save(recorder.case_dir / "accounts.png")
    recorder.event(
        "Cuentas disponibles",
        kind="capture",
        capture_type="page",
        status="PASS",
        milestone_id=accounts,
        image="accounts.png",
        width=1200,
        height=650,
        description="Segunda evidencia de negocio, con una imagen diferente.",
        url="https://example.test/cuentas",
        page_title="Cuentas ficticias",
    )
    recorder.event("La consulta devolvió la cuenta de demostración esperada.", milestone_id=accounts)
    if status != "INCOMPLETE":
        recorder.finish(
            status,
            12.48,
            "Saldo esperado no coincide con el observado."
            if status == "FAIL"
            else "Ejemplo de caso omitido."
            if status == "SKIP"
            else "",
        )
    formats = ("html", "pdf") if status == "PASS" else ("html",)
    paths = build_reports(recorder.case_dir, root / "html", formats=formats)
    shutil.copyfile(paths[0], Path("docs/demo") / filename)
    if status == "PASS":
        shutil.copyfile(paths[1], Path("docs/demo/passed.pdf"))

# Spanish interface preview from the same recorded cases, including PDF and Word.
spanish = Path("docs/demo/es")
spanish.mkdir(parents=True, exist_ok=True)
for case_file in root.rglob("case.json"):
    import json

    case = json.loads(case_file.read_text())
    filename = {"PASS": "passed", "FAIL": "failed", "SKIP": "skipped", "INCOMPLETE": "incomplete"}[
        case["status"]
    ]
    outputs = build_reports(
        case_file.parent, root / "html-es", formats=("html", "pdf", "docx"), language="es"
    )
    for source in outputs:
        shutil.copyfile(source, spanish / (filename + source.suffix))
