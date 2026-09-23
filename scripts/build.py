#!/usr/bin/env python3
"""Compile a deck offline with its bundled theme and one consistent TeX toolchain."""
import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('deck', type=Path, help='Directory containing main.tex')
a = p.parse_args()
deck = a.deck.resolve()
engine = shutil.which('xelatex')
if not engine:
    p.exit(1, 'XeLaTeX is missing. Install a TeX distribution with ctex and beamer.\n')
# Resolve wrapper symlink to choose the distribution, but invoke xelatex by name.
bin_dir = Path(engine).resolve().parent
candidate = bin_dir / 'xelatex'
engine = str(candidate) if candidate.exists() else engine
env = os.environ.copy()
env['PATH'] = str(bin_dir) + os.pathsep + env.get('PATH', '')
env['TEXINPUTS'] = str(deck / 'sustech-theme') + '//' + os.pathsep + env.get('TEXINPUTS', '')
if not (deck / 'main.tex').is_file():
    p.exit(1, f'Missing source: {deck / "main.tex"}\n')
for _ in range(3):
    run = subprocess.run([engine, '-no-shell-escape', '-interaction=nonstopmode', '-halt-on-error', 'main.tex'], cwd=deck, env=env, capture_output=True, text=True)
    if run.returncode:
        print(run.stdout[-6000:])
        p.exit(1, 'Compilation failed; inspect main.log.\n')
log = (deck / 'main.log').read_text(errors='replace')
problems = re.findall(r'^.*(?:Overfull \\[hv]box|Missing character:|Undefined control sequence).*$', log, re.M)
if problems:
    print('\n'.join(problems))
    p.exit(2, 'PDF compiled but needs layout/font corrections.\n')
print(deck / 'main.pdf')
