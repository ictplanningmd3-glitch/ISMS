"""Offline v18 QA: repeatable corrective indicators and genuine Word reports."""
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from io import BytesIO
from docx import Document
from openpyxl import load_workbook
from xml.etree import ElementTree as ET
import argparse, json, os

parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://127.0.0.1:8778/Didban_Amniat_Offline.html')
parser.add_argument('--artifacts',default='/tmp/didban-v18-qa/reports')
args=parser.parse_args();art=Path(args.artifacts);art.mkdir(parents=True,exist_ok=True)
W={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
TITLE='اصلاح & <دسترسی> "ویژه"'
INDICATORS=['کاهش <دسترسی> & پایش','تکمیل شواهد']
LEGACY='پروژه قدیمی تکمیل شده';FUTURE='پروژه آینده'

def read_docx(path):
 data=path.read_bytes();assert data[:2]==b'PK',path
 with ZipFile(BytesIO(data)) as archive:
  assert archive.testzip() is None
  assert {'[Content_Types].xml','_rels/.rels','word/document.xml'}.issubset(archive.namelist())
  for name in archive.namelist():
   if name.endswith('.xml') or name.endswith('.rels'):ET.fromstring(archive.read(name))
  tree=ET.fromstring(archive.read('word/document.xml'))
  text='\n'.join(node.text or '' for node in tree.findall('.//w:t',W))
  assert tree.findall('.//w:bidi',W),'Persian paragraph direction missing'
  assert tree.findall('.//w:tbl',W),'Expected genuine Word tables'
  raw=archive.read('word/document.xml').decode()
  assert '<html' not in raw.lower()
 # A separate reader must recognize the generated document, paragraphs and tables.
 document=Document(BytesIO(data));assert document.paragraphs and document.tables
 return text,tree,raw

def table_value(tree,label):
 for row in tree.findall('.//w:tr',W):
  cells=[''.join(node.text or '' for node in cell.findall('.//w:t',W)) for cell in row.findall('w:tc',W)]
  if cells and cells[0]==label:return cells[1] if len(cells)>1 else ''
 raise AssertionError('Missing Word table label: '+label)

with TemporaryDirectory() as temp,sync_playwright() as pw:
 out=Path(temp)
 browser=pw.chromium.launch(executable_path=os.environ.get('DIDBAN_CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 ctx=browser.new_context(viewport={'width':1536,'height':1050},accept_downloads=True)
 page=ctx.new_page();errors=[];requests=[]
 page.on('pageerror',lambda error:errors.append(str(error)))
 page.on('request',lambda request:requests.append(request.url))
 page.goto(args.url)
 assert page.locator('meta[name="didban-version"]').get_attribute('content')=='18'
 def main(name):page.locator('aside nav>button').filter(has_text=name).click()
 def projects():main('اقدامات اصلاحی');page.locator('[data-v13-corrective-tab=projects]:visible').first.click()
 def raw(key):return page.evaluate("suffix=>{const k=Object.keys(localStorage).find(k=>k.endsWith(':'+suffix));return k?JSON.parse(localStorage.getItem(k)):null;}",key)
 def capture(locator,name):
  style=page.add_style_tag(content='body .shell>main>header,body .toast{visibility:hidden!important}')
  locator.screenshot(path=str(art/name));style.evaluate('e=>e.remove()')
 def expand(root,text):
  summary=root.locator('summary').filter(has_text=text)
  if not summary.evaluate('e=>e.parentElement.open'):summary.click()
 def edit(title):
  page.get_by_role('button',name='ویرایش پروژه '+title,exact=True).click()
  return page.get_by_role('dialog')
 def save(form):form.get_by_role('button',name='ذخیره پروژه',exact=True).click();expect(form).to_have_count(0)
 def seed_extra_records():
  page.evaluate("""payload=>{const reg=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default')),prefix='didban-project:default:'+reg.activeId+':',key=prefix+'didban-isms-improvements-v1';const projects=JSON.parse(localStorage.getItem(key));projects.push(...payload.projects);localStorage.setItem(key,JSON.stringify(projects));const audits=Object.fromEntries(payload.audits.map(([id,compliance])=>[id,{id,status:2,compliance,applicable:true,reason:'',documents:'شواهد آزمون '+id,observations:'یافته آزمون',owner:'مالک',action:'بررسی',due:'2027-01-01',reviewer:'ممیز',correctiveAction:'',previousCompliance:'',updated:'2026-11-07T08:00:00Z'}]));localStorage.setItem(prefix+'didban-isms-offline-v1',JSON.stringify(audits));}""",{'projects':[
   {'id':'legacy18','title':LEGACY,'goal':'هدف قدیمی','owner':'مالک قدیمی','resources':'تیم قدیمی','notes':'پرونده کامل','updated':'2026-11-01T08:00:00Z','start':'2026-01-01','due':'2026-03-01','months':2,'priority':'medium','status':'completed','progress':100,'mappedIds':['4.1'],'scopeIds':[]},
   {'id':'future18','title':FUTURE,'goal':'هدف آینده','owner':'مالک آینده','resources':'تیم آینده','notes':'منتظر شروع','updated':'2026-11-01T08:00:00Z','start':'2027-01-01','due':'2027-04-01','months':3,'priority':'low','status':'planned','progress':0,'mappedIds':['A.7.1'],'scopeIds':[],'indicators':['پیگیری آینده']}
  ],'audits':[['A.5.16',1],['A.5.17',2],['4.1',3],['A.5.1',4]]})
  page.reload()
 # Create through the actual form, including middle-row removal and blank normalization.
 projects();page.get_by_role('button',name='تعریف اقدام بهبود',exact=True).click();form=page.get_by_role('dialog')
 for label,value in [('عنوان اقدام یا پروژه',TITLE),('مسئول پیگیری','مسئول & <تیم>'),('هدف و نتیجه مورد انتظار','کاهش ریسک & <نمونه>'),('منابع لازم','تیم ممیزی'),('یادداشت پیشرفت یا مانع اجرا','خط اول\nخط دوم & <شرح>')]:form.get_by_label(label,exact=True).fill(value)
 form.get_by_label('گروه زمانی پروژه',exact=True).select_option('1')
 form.get_by_label('وضعیت پروژه',exact=True).select_option('active')
 form.get_by_label('پیشرفت (درصد)',exact=True).fill('25')
 form.get_by_label('تاریخ شروع پروژه',exact=True).fill('2026-01-01')
 assert form.locator('[data-v18-indicator-input]').count()==1
 form.get_by_label('شاخص اقدام اصلاحی 1',exact=True).fill('  '+INDICATORS[0]+'  ')
 form.get_by_role('button',name='افزودن ردیف شاخص',exact=True).click();expect(form.get_by_label('شاخص اقدام اصلاحی 2',exact=True)).to_be_focused()
 form.get_by_label('شاخص اقدام اصلاحی 2',exact=True).fill('شاخص قابل حذف')
 form.get_by_role('button',name='افزودن ردیف شاخص',exact=True).click();expect(form.get_by_label('شاخص اقدام اصلاحی 3',exact=True)).to_be_focused()
 form.get_by_label('شاخص اقدام اصلاحی 3',exact=True).fill(INDICATORS[1])
 form.get_by_role('button',name='حذف شاخص 2',exact=True).click();expect(form.get_by_label('شاخص اقدام اصلاحی 2',exact=True)).to_have_value(INDICATORS[1]);expect(form.get_by_label('شاخص اقدام اصلاحی 2',exact=True)).to_be_focused()
 form.get_by_role('button',name='افزودن ردیف شاخص',exact=True).click();expect(form.get_by_label('شاخص اقدام اصلاحی 3',exact=True)).to_be_focused()
 expand(form,'ارتباط دقیق با الزامات و کنترل‌ها')
 for id in ['A.5.16','4.1']:form.get_by_label('ارتباط پروژه '+id,exact=True).check()
 expand(form,'بودجه اقدام اصلاحی');form.get_by_label('بودجه مصوب اقدام اصلاحی',exact=True).fill('1000');form.get_by_label('تاریخ تصویب بودجه',exact=True).fill('2026-01-01')
 for i,(amount,date) in enumerate([('100','2026-01-02'),('250','2026-01-03')],1):
  form.get_by_role('button',name='افزودن ردیف تخصیص بودجه',exact=True).click();form.get_by_label('میزان بودجه تخصیص داده شده '+str(i),exact=True).fill(amount);form.get_by_label('تاریخ تخصیص بودجه '+str(i),exact=True).fill(date)
 capture(form.locator('[data-v18-project-indicators]'),'indicators-light.png');save(form)
 stored=raw('didban-isms-improvements-v1');assert len(stored)==1 and stored[0]['indicators']==INDICATORS;project_id=stored[0]['id']
 assert stored[0]['start']=='2026-01-01' and stored[0]['due']=='2026-02-01'
 form=edit(TITLE);assert form.locator('[data-v18-indicator-input]').count()==2
 for i,value in enumerate(INDICATORS,1):expect(form.get_by_label('شاخص اقدام اصلاحی '+str(i),exact=True)).to_have_value(value)
 form.get_by_role('button',name='بستن پروژه',exact=True).click()
 seed_extra_records();projects();assert page.locator('[data-improvement-project]').count()==3
 # Old projects acquire an empty optional collection; deleting all rows remains a valid edit.
 form=edit(LEGACY);expect(form.get_by_label('شاخص اقدام اصلاحی 1',exact=True)).to_have_value('')
 form.get_by_role('button',name='حذف شاخص 1',exact=True).click();expect(form.locator('[data-v18-add-indicator]')).to_be_focused();assert form.locator('[data-v18-indicator-input]').count()==0
 save(form);assert next(p for p in raw('didban-isms-improvements-v1') if p['id']=='legacy18')['indicators']==[]
 print('PASS repeatable indicator add/remove/focus, blank trimming, real save/reopen, legacy defaults and budget retention',flush=True)
 # Report tests below are wired to the production dialog after its API is finalized.
 main('پشتیبانی سایت')
 with page.expect_download() as event:page.get_by_role('button',name='دریافت JSON پروژه فعال',exact=True).click()
 event.value.save_as(str(out/'backup.json'));backup=json.loads((out/'backup.json').read_text())
 assert len(backup['projects'])==3
 assert next(p for p in backup['projects'] if p['id']==project_id)['indicators']==INDICATORS
 assert next(p for p in backup['projects'] if p['id']=='legacy18')['indicators']==[]
 page.get_by_label('بارگذاری نسخه JSON',exact=True).set_input_files(str(out/'backup.json'))
 page.get_by_label('نام سازمان واردشده',exact=True).fill('بازیابی شاخص‌های نسخه۱۸')
 page.get_by_role('button',name='واردکردن پروژه',exact=True).click();expect(page.get_by_role('dialog')).to_have_count(0)
 page.reload();projects();form=edit(TITLE)
 assert form.locator('[data-v18-indicator-input]').evaluate_all('xs=>xs.map(e=>e.value)')==INDICATORS
 form.get_by_role('button',name='بستن پروژه',exact=True).click()
 main('پشتیبانی سایت');page.get_by_role('button',name='گزارش Word و Excel',exact=True).click()
 page.get_by_label('نام سازمان',exact=True).fill('سازمان & <آزمون> نسخه۱۸')
 page.get_by_label('نوع ممیزی',exact=True).select_option(label='ممیزی داخلی')
 page.get_by_label('نام ممیز / بررسی‌کننده',exact=True).fill('ممیز & <گزارش>')
 with page.expect_download() as event:page.get_by_role('button',name='دریافت Excel (.xlsx)',exact=True).click()
 event.value.save_as(str(art/'native-audit.xlsx'));workbook=load_workbook(art/'native-audit.xlsx')
 sheet=workbook['اقدامات بهبود'];headers=[cell.value for cell in sheet[1]]
 assert 'شاخص‌های اقدام اصلاحی' in headers
 row=next(row for row in list(sheet.values)[1:] if row[headers.index('عنوان')]==TITLE)
 assert all(value in row[headers.index('شاخص‌های اقدام اصلاحی')] for value in INDICATORS)
 assert 'شاخص قابل حذف' not in str(row)
 print('PASS full JSON backup/restore and native Excel indicators with special characters',flush=True)
 # The existing Word dialog passes its current, unsaved report metadata directly.
 embedded=page.locator('[data-v18-reports-entry="word"]');expect(embedded).to_have_count(1)
 if not embedded.evaluate('e=>e.open'):embedded.locator('summary').click()
 ctx.set_offline(True)
 reports=[]
 def make_report(root,kind,name,expected_count):
  root.get_by_label('نوع گزارش اقدامات اصلاحی',exact=True).select_option(kind)
  if kind=='project':root.get_by_label('پروژهٔ گزارش اقدامات اصلاحی',exact=True).select_option(project_id)
  expect(root.locator('[data-v18-report-selection]')).to_have_attribute('data-count',str(expected_count))
  with page.expect_download() as event:root.get_by_role('button',name='دریافت گزارش Word اقدامات اصلاحی',exact=True).click()
  download=event.value;assert download.suggested_filename.endswith('.docx') and 'Didban_Corrective_' in download.suggested_filename
  path=art/name;download.save_as(str(path));text,tree,xml=read_docx(path)
  assert table_value(tree,'تعداد پروژه‌های گزارش')==str(expected_count).translate(str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹'))
  expect(root.locator('[role=status]')).to_contain_text('دانلود شد')
  assert root.locator('[role=alert]').count()==0
  reports.append({'kind':kind,'filename':download.suggested_filename,'bytes':path.stat().st_size,'projects':expected_count})
  return text,tree,xml
 for kind,count in [('executive',3),('register',3),('project',1),('followup',2)]:
  text,tree,xml=make_report(embedded,kind,kind+'.docx',count)
  assert 'سازمان & <آزمون> نسخه۱۸' in text and 'ممیز & <گزارش>' in text
  assert TITLE in text
  for indicator in INDICATORS:assert indicator in text
  assert '&amp;' in xml and '&lt;' in xml and '&gt;' in xml
  assert 'شاخص قابل حذف' not in text
  assert '2026-01-01' not in text and '2026-02-01' not in text
  if kind in ['executive','register']:
   assert LEGACY in text and FUTURE in text and 'پیگیری آینده' in text
  if kind=='executive':
   assert table_value(tree,'کل اقدامات اصلاحی گزارش')=='۳'
   assert table_value(tree,'شاخص‌های تعریف‌شده')=='۳'
   assert table_value(tree,'تمام بندها و کنترل‌های نیازمند اقدام در دفتر ممیزی فعال')=='۴'
   assert table_value(tree,'موارد دارای پروژهٔ مرتبط در محدودهٔ این گزارش')=='۲'
   assert table_value(tree,'درصد پوشش')=='۵۰٪'
  if kind in ['register','project']:
   assert '۱۴۰۴/۱۰/۱۱' in text and '۱۴۰۴/۱۱/۱۲' in text
  if kind=='register':assert 'شاخصی برای این پروژه ثبت نشده است.' in text
  if kind=='project':
   assert LEGACY not in text and FUTURE not in text
   assert 'A.5.16' in text and '4.1' in text
   digits=lambda value:int(value.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹','0123456789')).replace('٬','').replace(',',''))
   assert digits(table_value(tree,'بودجه مصوب (ریال)'))==1000
   assert digits(table_value(tree,'جمع تخصیص (ریال)'))==350
   assert digits(table_value(tree,'ماندهٔ بودجه (ریال)'))==650
   assert 'خط اول' in text and 'خط دوم & <شرح>' in text
   assert 'شواهد آزمون A.5.16' in text
  if kind=='followup':assert LEGACY not in text and FUTURE in text
 capture(embedded,'reports-native-word-entry-light.png')
 print('PASS all four genuine DOCX reports, independent XML/python-docx readers, live native metadata, RTL/tables/Jalali dates, indicators/XML escaping, scope counts/coverage and project budget/findings',flush=True)
 # Status and group filters constrain both preview and actual output, including explicit empty states.
 embedded.get_by_label('وضعیت پروژه‌های گزارش اقدامات اصلاحی',exact=True).select_option('completed')
 embedded.get_by_label('گروه زمانی گزارش اقدامات اصلاحی',exact=True).select_option('B')
 text,tree,_=make_report(embedded,'register','completed-group-b.docx',1)
 assert LEGACY in text and TITLE not in text and FUTURE not in text
 text,tree,_=make_report(embedded,'followup','empty-followup.docx',0)
 assert 'پروژه‌ای با معیارهای انتخاب‌شده ثبت نشده است.' in text
 assert TITLE not in text and LEGACY not in text and FUTURE not in text
 embedded.get_by_label('وضعیت پروژه‌های گزارش اقدامات اصلاحی',exact=True).select_option('blocked')
 embedded.get_by_label('نوع گزارش اقدامات اصلاحی',exact=True).select_option('project')
 expect(embedded.locator('[data-v18-report-export]')).to_be_disabled()
 expect(embedded.locator('[data-v18-report-selection]')).to_have_attribute('data-count','0')
 embedded.get_by_label('نوع گزارش اقدامات اصلاحی',exact=True).select_option('followup')
 embedded.get_by_label('وضعیت پروژه‌های گزارش اقدامات اصلاحی',exact=True).select_option('all')
 embedded.get_by_label('گروه زمانی گزارش اقدامات اصلاحی',exact=True).select_option('all')
 embedded.get_by_label('فقط پروژه‌های سررسیدگذشته',exact=True).check()
 text,_,_=make_report(embedded,'followup','overdue-only.docx',1)
 assert TITLE in text and LEGACY not in text and FUTURE not in text
 page.get_by_label('بستن گزارش',exact=True).click();projects()
 # The project-page launcher exposes the same functioning picker, with keyboard close/focus.
 launcher=page.locator('[data-v18-reports-entry="projects"]');launcher.click()
 picker=page.locator('[data-v18-report-dialog]');expect(picker).to_be_visible()
 picker.get_by_label('وضعیت پروژه‌های گزارش اقدامات اصلاحی',exact=True).select_option('active')
 picker.get_by_label('گروه زمانی گزارش اقدامات اصلاحی',exact=True).select_option('A')
 text,tree,_=make_report(picker,'register','project-page-active-a.docx',1)
 assert TITLE in text and LEGACY not in text and FUTURE not in text
 capture(picker,'reports-project-page-light.png');page.keyboard.press('Escape');expect(picker).to_have_count(0);expect(launcher).to_be_focused()
 page.get_by_label('پوسته سایت',exact=True).select_option('dark');launcher.click();picker=page.locator('[data-v18-report-dialog]')
 capture(picker,'reports-project-page-dark.png');picker.get_by_label('بستن گزارش اقدامات اصلاحی',exact=True).click()
 page.set_viewport_size({'width':390,'height':844});assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 launcher.click();picker=page.locator('[data-v18-report-dialog]');assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 capture(picker,'reports-project-page-mobile.png');picker.get_by_label('بستن گزارش اقدامات اصلاحی',exact=True).click()
 form=edit(TITLE);capture(form.locator('[data-v18-project-indicators]'),'indicators-mobile-dark.png')
 assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 assert form.locator('[data-v18-indicator-input]').evaluate_all('xs=>xs.map(e=>e.value)')==INDICATORS
 form.get_by_role('button',name='بستن پروژه',exact=True).click()
 assert not errors,errors
 assert all(url.split('#')[0]==args.url for url in requests),requests
 (art/'result.json').write_text(json.dumps({'result':'PASS','errors':errors,'requests':requests,'reports':reports,'indicators':INDICATORS,'project_count':3,'coverage':{'required':4,'covered':2,'percentage':50}},ensure_ascii=False,indent=2))
 print('PASS report filters/empty state/overdue-only, both entry routes, focus restoration, light/dark/mobile and offline without JS errors or external requests.',flush=True)
 browser.close()
