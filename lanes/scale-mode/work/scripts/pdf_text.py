"""Extract text from a PDF (untrusted data) with pypdf. usage: pdf_text.py IN.pdf OUT.txt"""
import sys
from pypdf import PdfReader
r = PdfReader(sys.argv[1])
with open(sys.argv[2], 'w') as f:
    for i, p in enumerate(r.pages):
        f.write(f'\n===== page {i+1} =====\n')
        f.write(p.extract_text() or '')
print('pages', len(r.pages), 'meta', dict(r.metadata or {}))
