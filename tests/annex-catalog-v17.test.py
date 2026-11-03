"""Bilingual reference integrity and build-integration checks, without the source PDF."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util, hashlib, json

ROOT=Path(__file__).resolve().parent.parent
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

loader=module('annex_catalog','src/annex-catalog-v17.py')
integration=module('annex_integration','src/annex-integration-v17.py')
catalog=json.loads((ROOT/'src/annex-controls-v17.json').read_text())
rows=catalog['controls'];controls=loader.load_controls();checks=0
def test(name,fn):
    global checks
    fn();checks+=1;print('✓',name)

def coverage():
    expected=[f'A.{domain}.{n}' for domain,count in [(5,37),(6,8),(7,14),(8,34)] for n in range(1,count+1)]
    assert list(controls)==expected
    assert len(rows)==len({row['id'] for row in rows})==93
test('all 93 Annex A controls appear once in standard order, with no requirement clauses',coverage)

def english():
    content='\n'.join('\t'.join([row['id'],row['titleEn'],row['textEn']]) for row in rows).encode()
    # Independently compared with the supplied PDF using verify-annex-pdf-v17.py.
    assert hashlib.sha256(content).hexdigest()=='1d9530523310c8bca683341a917633bdf769cb9b11a10253c1935a7edcaf32f3'
    assert catalog['sourceSha256']=='843a6728009540947b2c5531f94b4cf1fb698d5bf3b51b324c8801e3e01c5b78'
    assert all('shall' in row['textEn'] and 'should' not in row['textEn'] for row in rows)
test('every English title and mandatory statement retains the PDF-verified content digest',english)

def example():
    row=controls['A.5.16']
    assert row['titleEn']=='Identity management' and row['titleFa']=='مدیریت هویت'
    assert row['textEn']=='The full life cycle of identities shall be managed.'
    assert row['textFa']=='چرخهٔ کامل عمر هویت‌ها باید مدیریت شود.'
    assert controls['A.6.8']['titleEn']=='Information security event reporting'
test('A.5.16 matches the requested example and PDF-only hyphenation is normalized',example)

def translations():
    for row in rows:
        assert row['titleFa'] and row['textFa'] and 'باید' in row['textFa']
        assert any('\u0600'<=ch<='\u06ff' for ch in row['titleFa'])
        source=row['source'];assert source['standard']=='ISO/IEC 27001:2022'
        assert source['annex']=='A' and source['table']=='A.1'
        assert 11<=source['printedPage']<=18 and source['pdfPage']==source['printedPage']+6
    assert 'پوشان‌سازی' in controls['A.8.11']['titleFa'] and 'رمزنگاری' in controls['A.8.24']['titleFa']
    assert 'رویداد' in controls['A.5.25']['titleFa'] and 'رخداد' in controls['A.5.26']['titleFa']
test('all translations are mandatory, complete and linked to the correct standard pages',translations)

def rejects_incomplete():
    original=loader.ROOT
    with TemporaryDirectory() as temp:
        loader.ROOT=Path(temp);folder=loader.ROOT/'src';folder.mkdir()
        mutations=[lambda j:j['controls'].pop(),lambda j:j['controls'][0].update(textFa=''),lambda j:j['controls'][0]['source'].update(standard='ISO/IEC 27005:2022'),lambda j:j['controls'][0].update(textEn=j['controls'][0]['textEn'].replace('shall','should'))]
        try:
            for mutate in mutations:
                bad=json.loads(json.dumps(catalog));mutate(bad);(folder/'annex-controls-v17.json').write_text(json.dumps(bad))
                try:loader.load_controls()
                except RuntimeError:pass
                else:raise AssertionError('Incomplete or misattributed reference accepted')
        finally:loader.ROOT=original
test('build refuses missing controls, empty translations, wrong sources and advisory substitutions',rejects_incomplete)

def original_form():
    native=(ROOT/'src/base-v6.html').read_text();built=integration.integrate(native)
    original='(0,i.jsxs)("h2",{id:"audit-title",children:[J.find(c=>c.id===n.id)?.title," ",(0,i.jsxs)("span",{className:"english-title",lang:"en",dir:"ltr",children:["(",J.find(c=>c.id===n.id)?.english,")"]})]})'
    assert 'V17AnnexControls[n.id]?DH(V17AnnexAuditTitle,{id:n.id}):'+original in built
    assert built.count('DH(V17AnnexReference,{id:n.id})')==1
    for anchor in ['onSubmit:pL','value:n.documents','value:n.observations','value:n.status','onClick:()=>L(null)']:
        assert built.count(anchor)==native.count(anchor)
test('only the control title/reference is inserted; clause header and audit input anchors remain intact',original_form)
print(str(checks)+' Annex A reference checks passed')
