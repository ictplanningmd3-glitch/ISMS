"""Validate and embed the whole-standard radar map; leave native taxonomies unchanged."""
from pathlib import Path
from collections import Counter
import json, csv, io

ROOT=Path(__file__).resolve().parent.parent
def load_groups():
    groups=json.loads((ROOT/'src/radar-taxonomy-v16.json').read_text())['groups']
    native=json.loads((ROOT/'src/taxonomy-v13.json').read_text())
    expected={id for group in native['groups'] for id in group['controls']}|{id for group in native['clauses'] for id in group['itemIds']}
    ids=[id for group in groups for id in group['itemIds']]
    if len(groups)!=10 or len({g['id'] for g in groups})!=10 or set(ids)!=expected or len(ids)!=123 or any(n!=1 for n in Counter(ids).values()):
        raise RuntimeError('The whole-standard radar must partition all 123 items into 10 disjoint domains.')
    return groups

def write_assets(taxonomy_module):
    groups=load_groups()
    rows=[['شناسه الزام / کنترل','حوزه تحلیلی کل استاندارد','Whole-standard analytical domain','نوع / Type']]
    for group in groups:
        for id in group['itemIds']:rows.append([id,group['title'],group['english'],'Annex A Control' if id.startswith('A.') else 'Requirement'])
    summary=[['حوزه / Domain','تعداد الزامات','تعداد کنترل‌ها','جمع']]
    for group in groups:
        clauses=sum(not id.startswith('A.') for id in group['itemIds'])
        summary.append([group['title'],clauses,len(group['itemIds'])-clauses,len(group['itemIds'])])
    basis=[['مشخصه','مقدار','Reference',''],['کاربرد','فقط حالت کل استاندارد در دو رادار','Whole-standard mode in both radars only',''],['مبنای نگاشت','نگاشت تحلیلی بر اساس موضوع هر بند / کنترل','Analytical mapping, not an official ISO taxonomy',''],['منبع','src/radar-taxonomy-v16.json','Version 16',''],['حوزه‌های مستقل','۸ حوزه الزامات و ۱۰ حوزه کنترل مطابق نگاشت کاربر حفظ شده‌اند','Separate user-provided taxonomies unchanged','']]
    taxonomy_module._workbook(ROOT/'assets/Whole_Standard_Radar_Domains.xlsx',rows,summary,basis)
    buffer=io.StringIO(newline='');csv.writer(buffer,lineterminator='\n').writerows(rows)
    (ROOT/'assets/Whole_Standard_Radar_Domains.csv').write_text(buffer.getvalue(),encoding='utf-8-sig')

def integrate(base):
    # This legend is outside the radar component in the native management panel.
    base=base.replace('توازن پیاده‌سازی در دامنه‌ها','توازن پیاده‌سازی در حوزه‌ها')
    old='children:"بندهای اصلی استاندارد ISO 27001"'
    if base.count(old)!=1:
        raise RuntimeError('The implementation radar subtitle integration anchor changed.')
    base=base.replace(old,'children:"الزامات، کنترل‌های Annex A یا کل استاندارد"',1)
    return base
