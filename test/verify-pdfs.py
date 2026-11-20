#!/usr/bin/env python3
"""Check manually generated test PDFs. Requires Poppler tools."""
from pathlib import Path
import subprocess

results = Path(__file__).resolve().parents[1] / 'test-output' / 'results'
for name in ('file', 'stdin'):
    pdf = results / f'{name}.pdf'
    assert pdf.read_bytes().startswith(b'%PDF-'), f'{name}: invalid PDF header'
    info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
    assert '612 x 792 pts (letter)' in info, info
    text = subprocess.check_output(['pdftotext', '-enc', 'UTF-8', str(pdf), '-'], text=True)
    for expected in ('wkhtmltopdf smoke test', 'café naïve résumé', 'Ελληνικά', 'Привет мир', '0123456789', '€'):
        assert expected in text, f'{name}: missing {expected!r}'
    fonts = subprocess.check_output(['pdffonts', str(pdf)], text=True)
    for expected in ('DejaVuSans', 'LiberationSerif', 'DejaVuSansMono'):
        assert expected in fonts, f'{name}: missing font {expected}\n{fonts}'
    for row in fonts.splitlines()[2:]:
        # Font name, type (one or more words), encoding, emb, sub, uni, IDs.
        assert row.split()[-5] == 'yes', f'{name}: font is not embedded: {row}'
    print(f'{name}: Letter page, UTF-8 text and embedded fonts verified')
subprocess.run(['pdftoppm', '-f', '1', '-singlefile', '-scale-to', '1400', '-png',
                str(results / 'file.pdf'), str(results / 'preview')], check=True)
