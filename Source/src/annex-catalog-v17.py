"""Build-time validation of the user-supplied Annex A control reference."""
from pathlib import Path
import json, re

ROOT=Path(__file__).resolve().parent.parent

def load_controls():
    catalog=json.loads((ROOT/'src/annex-controls-v17.json').read_text())
    controls=catalog['controls']
    expected=[f'A.{domain}.{n}' for domain,count in [(5,37),(6,8),(7,14),(8,34)] for n in range(1,count+1)]
    if [row['id'] for row in controls]!=expected:
        raise RuntimeError('Annex A reference must contain all 93 controls exactly once in standard order.')
    for row in controls:
        for field in ['titleEn','titleFa','textEn','textFa']:
            value=row.get(field)
            if not isinstance(value,str) or not value.strip() or any(c in value for c in ['\n','\r','\x00','\ufeff']):
                raise RuntimeError(f'{row["id"]}: invalid bilingual reference field {field}.')
        if not re.search(r'\bshall\b',row['textEn']) or 'باید' not in row['textFa']:
            raise RuntimeError(f'{row["id"]}: mandatory control wording is missing.')
        source=row.get('source',{})
        if source.get('standard')!='ISO/IEC 27001:2022' or source.get('annex')!='A' or source.get('table')!='A.1' or source.get('printedPage') not in range(11,19) or source.get('pdfPage')!=source['printedPage']+6:
            raise RuntimeError(f'{row["id"]}: invalid source reference.')
    return {row['id']:row for row in controls}
