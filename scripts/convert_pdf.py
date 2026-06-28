#!/usr/bin/env python3
"""
PDF -> Markdown raw extraction stage for the `pdf-to-llm` skill/plugin.

Uses opendataloader-pdf (https://github.com/opendataloader-project/opendataloader-pdf)
to extract text, tables, layout and images from a PDF. Runs entirely locally.

This script ONLY does the deterministic extraction step. The vision-enrichment
step (describing every figure/diagram/chart/table inline) is performed by Claude
afterwards, per the instructions in SKILL.md.

It manages a self-contained, isolated virtual environment in the user's home
directory so it never disturbs the system / global Python packages, and so the
same environment is reused across machines and across plugin updates.

Usage:
    python convert_pdf.py "<input.pdf>" ["<output_dir>"]

Prints a JSON summary to stdout, e.g.:
    {"markdown": ".../doc.md", "output_dir": "...", "image_count": 41, "images": [...]}
"""
import json
import os
import subprocess
import sys
import venv
from pathlib import Path

# Shared, install-location-independent venv so the same environment is reused
# whether this script is invoked from the local skill or an installed plugin.
VENV_DIR = Path.home() / ".pdf-to-llm" / "venv"


def venv_python(vdir: Path) -> Path:
    if os.name == "nt":
        return vdir / "Scripts" / "python.exe"
    return vdir / "bin" / "python"


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def check_java() -> None:
    from shutil import which
    if which("java") is None:
        log(
            "ERROR: Java runtime not found on PATH. opendataloader-pdf requires "
            "Java 11+ (JDK or JRE). Install it (e.g. Temurin/Adoptium or Microsoft "
            "OpenJDK) and ensure `java` is on PATH, then retry."
        )
        sys.exit(2)


def ensure_venv() -> Path:
    py = venv_python(VENV_DIR)
    if not py.exists():
        log(f"Creating isolated virtual environment at {VENV_DIR} ...")
        VENV_DIR.parent.mkdir(parents=True, exist_ok=True)
        venv.create(VENV_DIR, with_pip=True)
    # Is opendataloader-pdf importable?
    probe = subprocess.run(
        [str(py), "-c", "import opendataloader_pdf"],
        capture_output=True,
    )
    if probe.returncode != 0:
        log("Installing opendataloader-pdf into the skill venv (first run only) ...")
        subprocess.run(
            [str(py), "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
        )
        subprocess.run(
            [str(py), "-m", "pip", "install", "-U", "opendataloader-pdf"],
            check=True,
        )
    return py


def run_conversion(py: Path, pdf: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    # Paths passed as argv (not interpolated) to avoid any quoting/escaping issues.
    runner = (
        "import sys, opendataloader_pdf; "
        "opendataloader_pdf.convert("
        "input_path=[sys.argv[1]], output_dir=sys.argv[2], format='markdown')"
    )
    subprocess.run([str(py), "-c", runner, str(pdf), str(out_dir)], check=True)


def main() -> None:
    if len(sys.argv) < 2:
        log('Usage: python convert_pdf.py "<input.pdf>" ["<output_dir>"]')
        sys.exit(1)

    pdf = Path(sys.argv[1]).expanduser().resolve()
    if not pdf.exists():
        log(f"ERROR: input PDF not found: {pdf}")
        sys.exit(1)

    out_dir = (
        Path(sys.argv[2]).expanduser().resolve()
        if len(sys.argv) > 2
        else pdf.parent / f"{pdf.stem}_odl"
    )

    check_java()
    py = ensure_venv()
    run_conversion(py, pdf, out_dir)

    md = next(iter(sorted(out_dir.glob("*.md"))), None)
    images = sorted(
        str(p)
        for p in out_dir.rglob("*")
        if p.suffix.lower() in (".png", ".jpg", ".jpeg")
    )
    summary = {
        "markdown": str(md) if md else None,
        "output_dir": str(out_dir),
        "image_count": len(images),
        "images": images,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
