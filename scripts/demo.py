"""Generate public examples with synthetic data and clearly labelled mock screenshots."""

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from rf_evidence_reporter import EvidenceRecorder, build_reports

root = Path("results/demo")
if root.exists():
    shutil.rmtree(root)
root.mkdir(parents=True)
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
        "Reporte de ejemplo con datos ficticios. Las imágenes son ilustrativas.",
    )
    recorder.metadata({"Aplicación": "Portal de clientes", "Ambiente": "Demo", "Requerimiento": "DEMO-001"})
    recorder.event("Se inició la validación de negocio.")
    milestone = recorder.milestone("Cliente registrado", "Confirmación del alta y acceso habilitado.")
    image.save(recorder.case_dir / "registration.png")
    recorder.event(
        "Confirmación de registro",
        kind="capture",
        capture_type="page",
        milestone_id=milestone,
        description="Captura ilustrativa del resultado esperado.",
        image="registration.png",
        width=1200,
        height=650,
        url="https://example.test/clientes",
        page_title="Portal ficticio",
    )
    recorder.event(
        "El escritorio no estaba disponible en esta demostración.",
        kind="capture_warning",
        level="WARN",
        reason="DESKTOP_UNAVAILABLE: ejemplo de advertencia sin afectar el caso.",
    )
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
    paths = build_reports(recorder.case_dir, root / "html")
    shutil.copyfile(paths[0], Path("docs/demo") / filename)
