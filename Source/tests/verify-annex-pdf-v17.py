#!/usr/bin/env python3
"""Dev-only verification of the 93 English controls against a user-supplied PDF.

Requires Poppler's pdftotext; no PDF, PDF parser, or external resource is needed
by the offline application. This independent raw-text check deliberately does
not use the coordinate-based extraction that produced the source catalog.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess


def raw_controls(pdf):
    result = subprocess.run(
        ['pdftotext', '-raw', str(pdf), '-'],
        check=True, capture_output=True, encoding='utf-8',
    ).stdout
    controls = {}
    for pdf_page, page in enumerate(result.split('\f'), 1):
        if not 17 <= pdf_page <= 24:
            continue
        starts = list(re.finditer(r'(?m)^([5-8]\.\d+)\s+(.+)', page))
        for position, match in enumerate(starts):
            stop = starts[position + 1].start() if position + 1 < len(starts) else len(page)
            row = page[match.start():stop]
            title, body = row.split('Control', 1)
            title = title[len(match[1]):].strip()
            lines = []
            for line in body.splitlines():
                line = line.strip()
                if (
                    line.startswith('Table A.1') or '© ISO/IEC' in line
                    or re.fullmatch(r'\d+', line)
                    or re.match(r'^[5-8] (People|Physical|Technological|Organizational) controls', line)
                ):
                    break
                if line.startswith('--`') or line in ['\ufeff', '\b', '\b\ufeff']:
                    continue
                lines.append(line)
            control_id = 'A.' + match[1]
            assert control_id not in controls, f'Duplicate PDF control: {control_id}'
            controls[control_id] = {'title': title, 'body': ' '.join(lines), 'pdfPage': pdf_page}
    return controls


def layout_neutral(text):
    # PDF table extraction merges some justified words and wraps other words
    # with visible hyphens. All letters, case and punctuation remain checked.
    return re.sub(r'[\s\-\ufeff\b]', '', text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', type=Path, required=True)
    parser.add_argument('--catalog', type=Path, required=True)
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding='utf-8'))
    entries = catalog['controls'] if isinstance(catalog, dict) and 'controls' in catalog else catalog
    if isinstance(entries, dict):
        entries = list(entries.values())
    expected = [f'A.{domain}.{n}' for domain, count in [(5, 37), (6, 8), (7, 14), (8, 34)] for n in range(1, count + 1)]
    assert [entry['id'] for entry in entries] == expected, 'Expected all 93 controls in standard order'
    source = raw_controls(args.pdf)
    assert set(source) == set(expected), 'Expected all 93 controls in the source PDF'
    for entry in entries:
        control_id = entry['id']
        original = source[control_id]
        assert layout_neutral(entry['titleEn']) == layout_neutral(original['title']), f'{control_id}: title differs'
        assert layout_neutral(entry['textEn']) == layout_neutral(original['body']), f'{control_id}: body differs'
        assert entry['textEn'].endswith('.') and 'shall' in entry['textEn'], f'{control_id}: mandatory wording missing'
        assert not re.search(r'\bshould\b', entry['textEn']), f'{control_id}: advisory wording substituted'
        reference = entry['source']
        assert reference['standard'] == 'ISO/IEC 27001:2022' and reference['annex'] == 'A' and reference['table'] == 'A.1', control_id
        assert reference['pdfPage'] == original['pdfPage'], f'{control_id}: incorrect PDF page'
        assert reference['printedPage'] == original['pdfPage'] - 6, f'{control_id}: incorrect printed page'
    indexed = {entry['id']: entry for entry in entries}
    assert indexed['A.5.16']['titleEn'] == 'Identity management'
    assert indexed['A.5.16']['textEn'] == 'The full life cycle of identities shall be managed.'
    assert indexed['A.6.8']['titleEn'] == 'Information security event reporting', 'PDF wrap re-porting must be joined'
    if isinstance(catalog, dict) and catalog.get('sourceSha256'):
        assert catalog['sourceSha256'] == hashlib.sha256(args.pdf.read_bytes()).hexdigest(), 'Source PDF checksum differs'
    print('PASS: 93 English titles and Control statements match the supplied 27001 PDF; all references and mandatory wording verified.')


if __name__ == '__main__':
    main()
