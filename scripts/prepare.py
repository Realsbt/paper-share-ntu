#!/usr/bin/env python3
"""Inspect optional tools or copy the original SUSTech Beamer starter with NTU metadata without overwriting."""
import argparse
import importlib.util
import json
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    init = sub.add_parser("init")
    init.add_argument("paper_dir", type=Path)
    args = parser.parse_args()
    if args.command == "doctor":
        print(json.dumps({
            "tools": {name: (shutil.which(name) or (shutil.which("static_" + name) if name in {"ffmpeg", "ffprobe"} else None)) for name in
                      ("xelatex", "pdftoppm", "pdftotext", "pdfinfo", "ffmpeg", "ffprobe", "edge-tts")},
            "optional_python_modules": {name: importlib.util.find_spec(name) is not None
                                        for name in ("mineru", "pymupdf", "pypdf")},
            "note": "Slides need XeLaTeX and PDF inspection tools; video tools are optional."
        }, ensure_ascii=False, indent=2))
        return
    deck = args.paper_dir.resolve() / "slides-beamer"
    deck.mkdir(parents=True, exist_ok=True)
    template = Path(__file__).resolve().parents[1] / "assets" / "main.tex"
    logo = template.parent / "ntu-logo.png"
    if not logo.is_file():
        parser.exit(1, f"Required NTU logo is missing: {logo}\n")
    if (deck / "main.tex").exists() or (deck / "ntu-logo.png").exists() or (deck / "fonts").exists() or (deck / "sustech-theme").exists() or (deck / "latexmkrc").exists():
        parser.exit(1, f"Existing template files preserved: {deck}\n")
    try:
        with (deck / "main.tex").open("x", encoding="utf-8") as output:
            output.write(template.read_text(encoding="utf-8"))
    except FileExistsError:
        parser.exit(1, f"Existing source preserved: {deck / 'main.tex'}\n")
    (deck / "figures").mkdir(exist_ok=True)
    shutil.copy2(logo, deck / "ntu-logo.png")
    shutil.copytree(template.parent / "fonts", deck / "fonts")
    shutil.copytree(template.parent / "sustech-theme", deck / "sustech-theme")
    shutil.copy2(template.parent / "latexmkrc", deck / "latexmkrc")
    print(deck / "main.tex")


if __name__ == "__main__":
    main()
