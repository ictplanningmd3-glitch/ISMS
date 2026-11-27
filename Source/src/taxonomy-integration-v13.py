"""One shared conceptual taxonomy for radar, filters, project scopes and reports.
The ten Annex A domains and eight requirements domains follow the user mapping
and the requested context/scope and risk-management merges in version 14.
"""
from pathlib import Path
from collections import Counter
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import csv, io, json

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'src' / 'taxonomy-v13.json'
CLAUSE_IDS = ['4.1','4.2','4.3','4.4','5.1','5.2','5.3','6.1.1','6.1.2','6.1.3','6.2','6.3','7.1','7.2','7.3','7.4','7.5.1','7.5.2','7.5.3','8.1','8.2','8.3','9.1','9.2.1','9.2.2','9.3.1','9.3.2','9.3.3','10.1','10.2']

def load_taxonomy():
    taxonomy = json.loads(SOURCE.read_text())
    expected = {f'A.{domain}.{n}' for domain, count in [(5,37),(6,8),(7,14),(8,34)] for n in range(1,count+1)}
    for key,item_key,item_ids,label,domain_count in [('groups','controls',expected,'Annex A',10),('clauses','itemIds',set(CLAUSE_IDS),'standard requirements',8)]:
        groups=taxonomy[key]
        items=[item for group in groups for item in group[item_key]]
        if len(groups)!=domain_count or len({g['id'] for g in groups})!=domain_count:
            raise RuntimeError(f'The canonical {label} taxonomy must contain {domain_count} unique domains.')
        if len(items)!=len(item_ids) or set(items)!=item_ids or any(n!=1 for n in Counter(items).values()):
            raise RuntimeError(f'The taxonomy must assign all {label} items exactly once.')
        for group in groups:
            if any(not isinstance(group.get(k),str) or not group[k].strip() for k in ['id','title','short','english']):
                raise RuntimeError('Every domain requires a title and stable id.')
    return taxonomy

def _sheet(rows):
    def cell(value,column,row):
        name=''
        while column:
            column,remainder=divmod(column-1,26)
            name=chr(65+remainder)+name
        if isinstance(value,(int,float)):
            return f'<c r="{name}{row}"><v>{value}</v></c>'
        return f'<c r="{name}{row}" t="inlineStr"><is><t xml:space="preserve">{escape(str(value))}</t></is></c>'
    body=''.join('<row r="'+str(i)+'">'+''.join(cell(v,j,i) for j,v in enumerate(row,1))+'</row>' for i,row in enumerate(rows,1))
    return '<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0" rightToLeft="1"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols><col min="1" max="1" width="16" customWidth="1"/><col min="2" max="2" width="48" customWidth="1"/><col min="3" max="3" width="58" customWidth="1"/><col min="4" max="4" width="90" customWidth="1"/></cols><sheetData>'+body+'</sheetData><autoFilter ref="A1:D'+str(len(rows))+'"/></worksheet>'

def _workbook(path,rows,summary,basis):
    with ZipFile(path,'w',ZIP_DEFLATED) as archive:
        def write(name,value):
            entry=ZipInfo(name,date_time=(2026,1,1,0,0,0))
            entry.compress_type=ZIP_DEFLATED
            entry.external_attr=0o100644 << 16
            archive.writestr(entry,value)
        write('[Content_Types].xml','<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/worksheets/sheet3.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
        write('_rels/.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        write('xl/workbook.xml','<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Item mapping" sheetId="1" r:id="rId1"/><sheet name="Domain summary" sheetId="2" r:id="rId2"/><sheet name="Basis" sheetId="3" r:id="rId3"/></sheets></workbook>')
        write('xl/_rels/workbook.xml.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet3.xml"/></Relationships>')
        write('xl/worksheets/sheet1.xml',_sheet(rows))
        write('xl/worksheets/sheet2.xml',_sheet(summary))
        write('xl/worksheets/sheet3.xml',_sheet(basis))

def write_assets(taxonomy,native):
    start=native.index('GS={')+3
    finish=native.index(',Yl=[',start)
    names=json.loads(native[start:finish])
    basis=[['مشخصه','مقدار','Reference',''],['مبنای نام و ترتیب حوزه‌ها','تقسیم‌بندی کامل ارسالی مستقیم کاربر','Authoritative mapping supplied directly by the user',''],['مبنای نگاشت بندها و کنترل‌ها','فهرست ده حوزهٔ کنترل و هشت حوزهٔ الزامات، با ادغام‌های درخواستی نسخهٔ ۱۴','User assignments with the version-14 requirements-domain merges',''],['منبع واحد','src/taxonomy-v13.json','Canonical source',''],['مستندات','docs/ANNEX-A-MAPPING.md','Mapping documentation','']]
    for filename,key,item_key in [('Annex_A_Domains','groups','controls'),('Clause_Domains','clauses','itemIds')]:
        groups=taxonomy[key]
        rows=[['Item ID','حوزه مفهومی','Domain','Item title']]
        for group in groups:
            rows.extend([[item,group['title'],group['english'],names[item]] for item in group[item_key]])
        summary=[['Domain ID','حوزه مفهومی','Domain','Item count']]+[[g['id'],g['title'],g['english'],len(g[item_key])] for g in groups]
        text=io.StringIO(newline='')
        csv.writer(text,lineterminator='\n').writerows(rows)
        (ROOT/'assets'/(filename+'.csv')).write_text('\ufeff'+text.getvalue(),newline='')
        _workbook(ROOT/'assets'/(filename+'.xlsx'),rows,summary,basis)

def integrate(base):
    taxonomy=load_taxonomy()
    start=base.index('Yl=[')+len('Yl=')
    end=base.index('],J=Yp.map(',start)+1
    if base.count('Yl=[')!=1:
        raise RuntimeError('The canonical Annex A integration anchor changed.')
    write_assets(taxonomy,base)
    serialize=lambda value:json.dumps(value,ensure_ascii=False,separators=(',',':'))
    base=base[:start]+serialize(taxonomy['groups'])+',V13ClauseGroups='+serialize(taxonomy['clauses'])+base[end:]
    original_j='J=Yp.map(a=>({...a,english:GS[a.id],concept:Yl.find(e=>e.controls.includes(a.id))?.id}))'
    updated_j='J=Yp.map(a=>{const annex=Yl.find(e=>e.controls.includes(a.id)),clause=V13ClauseGroups.find(e=>e.itemIds.includes(a.id)),scope=annex||clause;return {...a,english:GS[a.id],concept:annex?.id,clauseConcept:clause?.id,conceptLabel:scope?.title,conceptEnglish:scope?.english}})'
    if base.count(original_j)!=1:
        raise RuntimeError('The canonical control metadata integration anchor changed.')
    base=base.replace(original_j,updated_j,1)
    if base.count('item.group||item.domain')!=2:
        raise RuntimeError('The canonical audit finding/report group anchors changed.')
    base=base.replace('item.group||item.domain','item.conceptLabel||item.group||item.domain')
    original_row='item.english,item.domain,a?.applicable'
    if base.count(original_row)!=1:
        raise RuntimeError('The canonical audit spreadsheet group anchor changed.')
    base=base.replace(original_row,'item.english,item.conceptLabel||item.group||item.domain,a?.applicable',1)
    original_search='item.id,item.title,item.english,item.group,dsFlatten'
    if base.count(original_search)!=1:
        raise RuntimeError('The canonical audit search metadata anchor changed.')
    base=base.replace(original_search,'item.id,item.title,item.english,item.conceptLabel,item.conceptEnglish,item.group,dsFlatten',1)
    # Retain official domain codes in a separate reference filter; conceptual grouping
    # for both pages follows the corresponding shared user taxonomy.
    original_filter='(0,i.jsxs)("select",{"aria-label":"حوزه مفهومی",value:H,onChange:c=>ja(c.target.value),disabled:a==="clauses",children:[(0,i.jsx)("option",{value:"all",children:"تمام حوزه‌های مفهومی"}),Yl.map(c=>(0,i.jsx)("option",{value:c.id,children:c.title},c.id))]})'
    updated_filter='DH("select",{"aria-label":"حوزه مفهومی",value:H,onChange:c=>ja(c.target.value)},DH("option",{value:"all"},"تمام حوزه‌های مفهومی"),...V13StandardGroups().filter(c=>c.kind===(a==="clauses"?"clause":"control")).map(c=>DH("option",{key:c.id,value:c.domain},c.title)))'
    if base.count(original_filter)!=1:
        raise RuntimeError('The canonical conceptual filter anchor changed.')
    base=base.replace(original_filter,updated_filter,1)
    if base.count('(H==="all"||c.concept===H)')!=1:
        raise RuntimeError('The canonical conceptual row filter anchor changed.')
    base=base.replace('(H==="all"||c.concept===H)','(H==="all"||(a==="clauses"?c.clauseConcept:c.concept)===H)',1)
    original_reference='(0,i.jsxs)("select",{value:s,onChange:c=>m(c.target.value),children:[(0,i.jsx)("option",{value:"all",children:"تمام حوزه‌ها"}),Qs.map(c=>(0,i.jsxs)("option",{value:c,children:[c," — ",J.find(y=>y.domain===c)?.group]},c))]})'
    updated_reference='DH("select",{"aria-label":"بند مرجع استاندارد",value:s,onChange:c=>m(c.target.value)},DH("option",{value:"all"},"تمام بندهای مرجع"),...Qs.filter(c=>J.some(y=>y.domain===c&&y.kind===(a==="clauses"?"clause":"control"))).map(c=>DH("option",{key:c,value:c},c)))'
    if base.count(original_reference)!=1:
        raise RuntimeError('The official reference filter anchor changed.')
    base=base.replace(original_reference,updated_reference,1)
    original_caption='children:[c.group,c.concept?" \\xB7 "+Yl.find(y=>y.id===c.concept)?.title:""]'
    if base.count(original_caption)!=1:
        raise RuntimeError('The canonical registry group caption anchor changed.')
    base=base.replace(original_caption,'children:[c.conceptLabel||c.group," \\xB7 ",c.domain]',1)
    helper="function V13StandardGroups(){return V13ClauseGroups.map(s=>({id:'clause:'+s.id,domain:s.id,title:s.title,short:s.short,english:s.english,kind:'clause',itemIds:[...s.itemIds]})).concat(Yl.map(s=>({id:'annex:'+s.id,domain:s.id,title:s.title,short:s.short,english:s.english,kind:'control',itemIds:[...s.controls]})));}\n"
    if base.count('function js(){')!=1:
        raise RuntimeError('The canonical standard group helper anchor changed.')
    return base.replace('function js(){',helper+'function js(){',1)
