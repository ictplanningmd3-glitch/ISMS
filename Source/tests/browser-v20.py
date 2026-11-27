from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from zipfile import ZipFile
from docx import Document
from openpyxl import load_workbook
from xml.etree import ElementTree as E
import json,os,argparse
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8790/Didban_Amniat_Offline.html');parser.add_argument('--artifacts',default='/workspace/isms-build/v20/validation');args=parser.parse_args();out=Path(args.artifacts);out.mkdir(parents=True,exist_ok=True)
W={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
colors=['4FAE66','E87945','C83E50','D6A13D','3C91CF','168B78'];audit_ids=['4.1','4.2','A.5.1','A.5.2','A.5.3','A.5.4']
bia={'id':'old19-bia','code':'BIA-019','title':'طرح قدیمی نسخه نوزده','department':'عملیات','owner':'مالک طرح','description':'شرح محفوظ','assessedAt':'2026-11-01','lastReview':'2026-11-01','nextReview':'2027-12-01','threshold':4,'impacts':{k:{str(t):(4 if k=='operational' and t>=480 else 0) for t in [60,240,480,1440,4320,10080]} for k in ['operational','financial','legal','customer','hse']},'normalCapacity':100,'minimumCapacity':50,'capacityUnit':'درخواست در ساعت','emergencyCapacity':60,'rto':180,'currentRto':240,'rpo':60,'currentRpo':90,'rpoNA':False,'bcp':'yes','bcpName':'طرح مصوب','bcpOwner':'مسئول طرح','bcpReview':'2026-11-01','bcpStatus':'approved','tested':True,'testDate':'2026-11-01','testType':'technical','testResult':'pass','actualRto':210,'actualRpo':75,'actualCapacity':55,'scenario':'BCMS_PRIVATE_SCENARIO','disruptionCapacity':0,'wrt':120,'currentWrt':120,'actualWrt':150,'recoverySteps':[{'id':'s1','title':'مرحله قدیمی','minutes':300,'capacity':80},{'id':'s2','title':'بازگشت کامل','minutes':360,'capacity':100}],'targetRecoverySteps':[],'currentRecoverySteps':[],'lastBackupAge':30,'legacyCustom':{'keep':'untouched'}}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.environ.get('DIDBAN_CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage']);context=browser.new_context(viewport={'width':1536,'height':1050},accept_downloads=True);page=context.new_page();page.set_default_timeout(8000);errors=[];external=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:external.append(r.url) if not r.url.startswith(('http://127.0.0.1:8790','blob:','data:')) else None);page.goto(args.url);assert page.locator('meta[name=didban-version]').get_attribute('content')=='20'
 def main(text):page.locator('aside nav>button').filter(has_text=text).click()
 def raw(key):return page.evaluate("suffix=>{const reg=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default'));return localStorage.getItem('didban-project:default:'+reg.activeId+':'+suffix)}",key)
 audit={}
 for i,code in enumerate(audit_ids):audit[code]={'id':code,'status':i%5,'compliance':i,'applicable':True,'reason':'','documents':'شاهد ویژه '+code+' & <سند> <script>window.INJECTED=true</script>','observations':'','owner':'','action':'','due':'','reviewer':'ممیز ردیف','correctiveAction':'','previousCompliance':'','updated':'2026-11-27T08:00:00Z'}
 audit['A.5.5']={'id':'A.5.5','status':0,'compliance':None,'applicable':True,'reason':'','documents':'','observations':'','owner':'','action':'','due':'','reviewer':'','correctiveAction':'','previousCompliance':''}
 seed={'didban-isms-offline-v1':audit,'didban-isms-improvements-v1':[{'id':'p-secret','title':'CORRECTIVE_PRIVATE_PROJECT','goal':'بدون تغییر','owner':'مالک اقدام','resources':'منبع خصوصی','notes':'','updated':'','start':'2026-11-01','due':'2026-12-01','months':1,'priority':'high','status':'planned','progress':0,'mappedIds':['4.1'],'indicators':[]}],'didban-risk-independent-v1':{'context':{'scope':'RISK_PRIVATE_SCOPE','stakeholders':'','criteria':'','accept':4,'owner':'','review':''},'assets':[],'risks':[]},'didban-rtp-independent-v2':{'version':2,'revision':0,'records':{'projects':[],'activities':[],'payments':[]},'settings':{'privateSentinel':'RTP_PRIVATE_DATA'},'audit':[]},'didban-bcms-independent-v2':{'version':2,'revision':8,'records':{'assessments':[bia]},'settings':{'threshold':4},'audit':[]},'didban-report-meta':{'organization':'سازمان گزارش آزمون','auditType':'ممیزی داخلی','auditor':'ممیز اصلی','reportNumber':'AUDIT-20','date':'2026-11-27'}}
 page.evaluate("payload=>{const reg=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default'));for(const [k,v] of Object.entries(payload))localStorage.setItem('didban-project:default:'+reg.activeId+':'+k,JSON.stringify(v))}",seed);page.reload();before={k:raw(k) for k in seed if k!='didban-report-meta'}
 # Audit report exports do not read other modules, even a broken risk file cannot block them.
 page.evaluate("()=>{const reg=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default'));localStorage.setItem('didban-project:default:'+reg.activeId+':didban-risk-independent-v1','BROKEN_RISK_SHOULD_NOT_BLOCK_AUDIT')}")
 page.get_by_role('button',name='گزارش Word و Excel',exact=True).click();dialog=page.get_by_role('dialog');assert dialog.locator('[data-v18-corrective-reports]').count()==0
 for name,file in [('دریافت Word (.docx)','audit.docx'),('دریافت Excel (.xlsx)','audit.xlsx'),('دریافت گزارش HTML','audit.html')]:
  with page.expect_download() as dl:dialog.get_by_role('button',name=name,exact=True).click()
  dl.value.save_as(str(out/file))
 dialog.get_by_role('button',name='بستن گزارش',exact=True).click()
 assert raw('didban-isms-offline-v1')==before['didban-isms-offline-v1'];assert raw('didban-bcms-independent-v2')==before['didban-bcms-independent-v2'];assert raw('didban-isms-improvements-v1')==before['didban-isms-improvements-v1'];assert raw('didban-rtp-independent-v2')==before['didban-rtp-independent-v2']
 page.evaluate("payload=>{const r=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default'));localStorage.setItem('didban-project:default:'+r.activeId+':didban-risk-independent-v1',payload)}",before['didban-risk-independent-v1'])
 print('PASS audit exports work independently of all other modules and preserve data',flush=True)
 # Exported HTML itself is a usable offline artifact.
 report=context.new_page();report.on('pageerror',lambda e:errors.append(str(e)));report.route('**/audit.html',lambda r:r.fulfill(content_type='text/html',body=(out/'audit.html').read_text()));report.goto('http://127.0.0.1:8790/audit.html');assert report.locator('tbody tr').count()==123;assert report.locator('.report-nav nav a').count()==6;assert report.locator('#implementation svg').count()==2;assert report.locator('.group').count()==18;assert report.evaluate('window.INJECTED') is None
 for secret in ['CORRECTIVE_PRIVATE_PROJECT','BCMS_PRIVATE_SCENARIO','RISK_PRIVATE_SCOPE','RTP_PRIVATE_DATA']:assert secret not in (out/'audit.html').read_text(),secret
 description=report.locator('tr[data-audit-id="4.1"] td').last.inner_text();assert 'شواهد و مستندات ممیزی' in description;assert all(x not in description for x in ['ثبت نشده','مسئول پیگیری','مشاهدات و نتیجه بررسی','اقدامات پیشنهادی','مهلت اقدام','دلیل / مبنای کاربرد'])
 report.get_by_label('جستجوی گزارش ممیزی').fill('شاهد ویژه A.5.1');assert report.locator('tbody tr:visible').count()==1;report.get_by_label('جستجوی گزارش ممیزی').fill('');report.get_by_label('وضعیت انطباق گزارش').select_option('5');assert report.locator('tbody tr:visible').count()==1;report.get_by_label('وضعیت انطباق گزارش').select_option('all');report.get_by_label('نوع بند').select_option('clause');assert report.locator('tbody tr:visible').count()==30;report.get_by_label('نوع بند').select_option('all');report.screenshot(path=str(out/'audit-report.png'));report.pdf(path=str(out/'audit-report.pdf'),format='A4',print_background=True)
 report.set_viewport_size({'width':390,'height':844});assert report.evaluate('document.documentElement.scrollWidth<=innerWidth');report.screenshot(path=str(out/'audit-report-mobile.png'))
 print('PASS standalone HTML navigation, SVG charts, filters, search, escaping, responsive layout and PDF',flush=True)
 # Existing BIA data is mounted and switching tabs is a presentation-only operation.
 main('BCMS');page.get_by_role('button',name='بازکردن طرح '+bia['title'],exact=True).click();tabs=page.get_by_role('tab');assert tabs.count()==9;old=raw('didban-bcms-independent-v2')
 for tab in tabs.all():tab.click();assert page.get_by_role('tabpanel').count()==1
 assert raw('didban-bcms-independent-v2')==old
 page.get_by_role('tab',name='نمای گرافیکی',exact=True).click();values={k:page.locator('[data-v20-bcp-value="'+k+'"]').inner_text() for k in ['RPO','RTO','MBCO','MTPD','KDS']};assert values=={'RPO':'1 h','RTO':'3 h','MBCO':'50%','MTPD':'8 h','KDS':bia['scenario']},values
 page.get_by_label('منبع نمودار BCP '+bia['code'],exact=True).select_option('actual');assert page.locator('[data-v20-bcp-value=RTO]').inner_text()=='3.5 h';page.get_by_label('منبع نمودار BCP '+bia['code'],exact=True).select_option('target')
 assert page.evaluate("()=>Boolean(document.querySelector('.v10-bcp-card').compareDocumentPosition(document.querySelector('[data-v20-review]'))&Node.DOCUMENT_POSITION_FOLLOWING)")
 page.get_by_role('tab',name='اهداف و قابلیت بازیابی',exact=True).click();page.get_by_label('واحد RTO هدف',exact=True).select_option('1');assert page.get_by_label('RTO هدف',exact=True).input_value()=='180';page.get_by_role('tab',name='اطلاعات اصلی',exact=True).click();page.get_by_role('tab',name='اهداف و قابلیت بازیابی',exact=True).click();assert page.get_by_label('RTO هدف',exact=True).input_value()=='180';assert raw('didban-bcms-independent-v2')==old
 # New optional contacts/resources/document fields are round-trippable, without changing any old property.
 page.get_by_role('tab',name='ماتریس ارتباطات و وظایف',exact=True).click();page.get_by_role('button',name='افزودن فرد پاسخگو').click()
 for name,value in [('نام فرد','پاسخگوی اول'),('روش تماس','تماس تلفنی'),('شماره تماس','+98 021 00123'),('سمت','مدیر بحران'),('روش احراز هویت','تماس برگشتی با شماره ثبت‌شده'),('وظایف در شرایط اضطراری','هماهنگی بازیابی')]:page.get_by_label(name+' اضطراری 1',exact=True).fill(value)
 page.get_by_role('tab',name='منابع و دارایی‌های طرح',exact=True).click();page.get_by_role('button',name='افزودن منبع طرح').click();page.get_by_label('نام منبع / دارایی طرح 1',exact=True).fill('سرور جایگزین');page.get_by_label('تعداد / مقدار موردنیاز طرح 1',exact=True).fill('۲ دستگاه')
 page.get_by_role('tab',name='طرح، مستندات و روش کار',exact=True).click();page.get_by_label('مستندات طرح',exact=True).fill('مرجع سند BCP-01');page.get_by_label('روش کار و دستورالعمل اجرای طرح',exact=True).fill('فرایند اجرای طرح')
 updated=json.loads(raw('didban-bcms-independent-v2'));row=updated['records']['assessments'][0];assert updated['version']==2
 for key,value in bia.items():assert row[key]==value,(key,row[key],value)
 assert row['emergencyContacts'][0]['contactNumber']=='+98 021 00123';assert row['planResources'][0]['quantity']=='۲ دستگاه';assert row['planDocuments']=='مرجع سند BCP-01'
 page.get_by_role('tab',name='آزمون',exact=True).click();expect(page.get_by_label('زمان واقعی بازیابی',exact=True)).to_have_value('3.5');page.get_by_role('tab',name='سناریو و مراحل بازیابی',exact=True).click();expect(page.get_by_label('سناریوی اصلی وقفه (KDS)',exact=True)).to_have_value(bia['scenario']);assert page.get_by_label('RTO هدف',exact=True).is_hidden()
 page.get_by_role('tab',name='نمای گرافیکی',exact=True).click();page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(out/'bcms-graphic.png'));page.get_by_label('پوسته سایت').select_option('dark');page.screenshot(path=str(out/'bcms-dark.png'))
 page.get_by_role('tab',name='اطلاعات اصلی',exact=True).click();page.get_by_role('tab',name='اطلاعات اصلی',exact=True).focus();page.keyboard.press('End');expect(page.get_by_role('tab',name='نمای گرافیکی',exact=True)).to_be_focused();assert page.get_by_role('tab',name='نمای گرافیکی',exact=True).get_attribute('aria-selected')=='true'
 page.reload();main('BCMS');page.get_by_role('button',name='بازکردن طرح '+bia['title'],exact=True).click();page.get_by_role('tab',name='ماتریس ارتباطات و وظایف',exact=True).click();expect(page.get_by_label('نام فرد اضطراری 1',exact=True)).to_have_value('پاسخگوی اول');page.get_by_role('tab',name='منابع و دارایی‌های طرح',exact=True).click();expect(page.get_by_label('نام منبع / دارایی طرح 1',exact=True)).to_have_value('سرور جایگزین')
 # Standard project JSON remains the same version and captures the new optional values.
 main('پشتیبانی');
 with page.expect_download() as dl:page.get_by_role('button',name='دریافت JSON پروژه فعال',exact=True).click()
 dl.value.save_as(str(out/'project.json'));backup=json.loads((out/'project.json').read_text());assert backup['bcms']['version']==2;assert backup['bcms']['records']['assessments'][0]==row;assert backup['assessments']==audit
 page.get_by_label('بارگذاری نسخه JSON',exact=True).set_input_files(str(out/'project.json'));imp=page.get_by_role('dialog',name='واردکردن پروژه JSON');imp.get_by_label('عنوان پروژه واردشده',exact=True).fill('بازخوانی نسخه ۲۰')
 with page.expect_navigation(wait_until='domcontentloaded'):imp.get_by_role('button',name='واردکردن پروژه',exact=True).click()
 main('BCMS');page.get_by_role('button',name='بازکردن طرح '+bia['title'],exact=True).click();page.get_by_role('tab',name='ماتریس ارتباطات و وظایف',exact=True).click();expect(page.get_by_label('نام فرد اضطراری 1',exact=True)).to_have_value('پاسخگوی اول')
 page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(out/'bcms-mobile.png'));assert not errors,errors;assert not external,external
 print('PASS BCMS nine tabs, unchanged v19 data and calculations, unit state, numeric cards, contacts/resources, keyboard, JSON import/export, mobile and no external requests',flush=True)
 browser.close()
# Inspect actual Office files with readers independent of the browser generator.
with ZipFile(out/'audit.docx') as z:
 assert z.testzip() is None
 for name in z.namelist():
  if name.endswith(('.xml','.rels')):E.fromstring(z.read(name))
 root=E.fromstring(z.read('word/document.xml'))
doc=Document(out/'audit.docx');table=doc.tables[2];assert len(table.rows)==124
for i,code in enumerate(audit_ids):
 rows=[r for r in table.rows[1:] if r.cells[2].text==code];assert len(rows)==1;desc=rows[0].cells[6].text;assert 'شاهد ویژه '+code in desc
 for missing in ['ثبت نشده','دلیل / مبنای کاربرد','مسئول پیگیری','مشاهدات و نتیجه بررسی','اقدامات پیشنهادی','مهلت اقدام']:assert missing not in desc,(code,missing,desc)
 fills=rows[0].cells[5]._tc.findall('.//w:shd',W);assert any(fill.get('{'+W['w']+'}fill')==colors[i] for fill in fills),(code,colors[i])
text='\n'.join(p.text for p in doc.paragraphs)+'\n'+'\n'.join(c.text for t in doc.tables for r in t.rows for c in r.cells)
for secret in ['CORRECTIVE_PRIVATE_PROJECT','RTP_PRIVATE_DATA','RISK_PRIVATE_SCOPE','BCMS_PRIVATE_SCENARIO','ضمائم — اقدامات بهبود']:assert secret not in text,secret
wb=load_workbook(out/'audit.xlsx');assert wb.sheetnames==['اطلاعات گزارش','ممیزی استاندارد','خلاصه وضعیت'];assert wb['ممیزی استاندارد'].max_row==124
print('PASS actual DOCX/XLSX: all 123 audit items, populated fields only, six native status colors, no unrelated-module appendices',flush=True)
