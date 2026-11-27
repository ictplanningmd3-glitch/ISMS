"""Offline v19 RTP QA: card register, long project text and allocation budgets."""
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
from tempfile import TemporaryDirectory
from openpyxl import Workbook, load_workbook
import argparse, json, os

parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://127.0.0.1:8781/Didban_Amniat_Offline.html')
parser.add_argument('--artifacts',default='/tmp/didban-v19-qa/rtp')
args=parser.parse_args();art=Path(args.artifacts);art.mkdir(parents=True,exist_ok=True)
PALETTE={'none':'#C83E50','planned':'#E87945','paused':'#D6A13D','active':'#3C91CF','effective':'#4FAE66'}
LONG=('شرح کامل پروژه: دامنه، تحویل‌دادنی‌ها، برنامهٔ اجرا و معیار پذیرش & <نمونه>\n'*180)
TITLE='پروژهٔ گستردهٔ RTP & <پذیرش>'
DIGITS=str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩','01234567890123456789')
def number(text):return float(text.translate(DIGITS).replace('٬','').replace(',','').strip())

def old_project(id,code,status='none',**extra):
 row={'id':id,'code':code,'title':'پروژهٔ '+code,'strategy':'mitigate','risk':'ریسک قبلی','threat':'تهدید قبلی','vulnerability':'آسیب‌پذیری قبلی','owner':'مالک آزمون','executor':'مجری آزمون','start':'2026-01-01','due':'2026-02-01','progress':0,'status':status,'decision':'تصمیم قبلی','budget':'','allocated':'','allocationDate':'','priority':'','annex':'','soa':'','notes':'یادداشت قبلی','evidence':'','attachments':[],'effectiveness':'pending','residualRisk':'','ownerConfirmed':False,'confirmedBy':'','closed':False}
 row.update(extra);return row

LEGACY=[
 old_project('legacy-none','LEG-001',budget=1000,allocated=750,allocationDate=''),
 old_project('legacy-planned','LEG-002','planned',start='2027-01-01',due='2027-03-01',progress=10),
 old_project('legacy-active','LEG-003','active',start='2026-11-01',due='2027-01-01',progress=30),
 old_project('legacy-paused','LEG-004','paused',start='',due='',progress=20),
 old_project('legacy-effective','LEG-005','effective',progress=100,effectiveness='effective',evidence='شواهد قبلی تأیید اثربخشی')
]
STATE={'version':2,'revision':0,'records':{'projects':LEGACY,'activities':[{'id':'activity-old','project':'legacy-none','title':'فعالیت قدیمی','executor':'مجری قبلی','due':'2027-01-01','progress':10,'status':'active','decision':'شرح قبلی'}],'payments':[{'id':'payment-old','project':'legacy-none','amount':200,'status':'پرداخت قبلی','updatedAt':'2026-11-01T08:00:00Z'}]},'settings':{},'audit':[]}

with TemporaryDirectory() as temp,sync_playwright() as pw:
 out=Path(temp)
 browser=pw.chromium.launch(executable_path=os.environ.get('DIDBAN_CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 ctx=browser.new_context(viewport={'width':1536,'height':1050},accept_downloads=True)
 page=ctx.new_page();errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:requests.append(r.url))
 page.goto(args.url)
 assert page.locator('meta[name="didban-version"]').get_attribute('content')=='20'
 def main(name):page.locator('aside>nav>button').filter(has_text=name).click()
 def tab(index):
  button=page.locator('aside .v7-subnav button').nth(index)
  (button if button.is_visible() else page.locator('.v8-module .v7-subnav button').nth(index)).click()
 def raw():return page.evaluate("()=>{const reg=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default')),key='didban-project:default:'+reg.activeId+':didban-rtp-independent-v2';return JSON.parse(localStorage.getItem(key));}")
 def row(id):return next(p for p in raw()['records']['projects'] if p['id']==id)
 def capture(locator,name):
  style=page.add_style_tag(content='body .shell>main>header,body .toast{visibility:hidden!important}')
  locator.screenshot(path=str(art/name));style.evaluate('e=>e.remove()')
 def card(id):return page.locator('[data-v19-rtp-card="'+id+'"]')
 def edit(code):page.get_by_role('button',name='ویرایش پروژه RTP '+code,exact=True).click();return page.get_by_role('dialog')
 def close():page.get_by_role('dialog').get_by_role('button',name='بستن',exact=True).click();expect(page.get_by_role('dialog')).to_have_count(0)
 def expand(root,text):
  summary=root.locator('summary').filter(has_text=text)
  if not summary.evaluate('e=>e.parentElement.open'):summary.click()
 def submit(form):
  target=form.get_by_role('button',name='ثبت پروژه',exact=True)
  (target if target.count() else form.get_by_role('button',name='ذخیره پروژه RTP',exact=True)).click()
 def save(form):submit(form);expect(form).to_have_count(0)
 def paste(label,text):page.locator('[data-v19-rtp-bulk]').get_by_label(label,exact=True).evaluate("(el,text)=>{const d=new DataTransfer();d.setData('text/plain',text);el.dispatchEvent(new ClipboardEvent('paste',{clipboardData:d,bubbles:true,cancelable:true}));}",text)
 # Excel still accepts the historical column names plus the optional long description.
 workbook=Workbook();sheet=workbook.active
 sheet.append(['شناسه پروژه','عنوان پروژه','درصد پیشرفت','تاریخ شروع شمسی','موعد پایان','شرح پروژه'])
 sheet.append(['EX-019','ورود Excel نسخه۱۹',.4,'1405/01/01','1405/12/01','شرح واردشده از Excel & <نمونه>'])
 sheet['C2'].number_format='0%';workbook.save(out/'import.xlsx')
 main('Risk Treatment Plan');tab(0)
 empty=page.locator('[data-v19-rtp-dashboard]');expect(empty).to_have_count(1)
 assert empty.locator('[data-v19-rtp-dashboard-row]').count()==0
 assert empty.locator('[data-v19-rtp-slice]').count()==0
 assert number(empty.locator('.v8-kpis article').first.locator('strong').inner_text())==0
 assert 'NaN' not in empty.inner_text() and 'Infinity' not in empty.inner_text()
 tab(1)
 page.locator('.v8-file input').set_input_files(str(out/'import.xlsx'))
 expect(page.locator('[data-v19-rtp-card]')).to_have_count(1)
 imported=raw()['records']['projects'][0]
 assert imported['code']=='EX-019' and imported['progress']==40
 assert imported['description']=='شرح واردشده از Excel & <نمونه>'
 # Seed a version-18 independent store, deliberately omitting the new description/allocation fields.
 page.evaluate("""state=>{const reg=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default'));localStorage.setItem('didban-project:default:'+reg.activeId+':didban-rtp-independent-v2',JSON.stringify(state));}""",STATE)
 page.reload();main('Risk Treatment Plan');tab(1)
 expect(page.locator('[data-v19-rtp-card]')).to_have_count(5)
 for status,color in PALETTE.items():
  item=page.locator('[data-v19-rtp-card][data-status="'+status+'"]');expect(item).to_have_count(1)
  rgb=tuple(int(color[i:i+2],16) for i in (1,3,5))
  assert item.evaluate("(e,rgb)=>{const s=getComputedStyle(e);return [s.borderTopColor,s.borderRightColor,s.borderLeftColor,s.backgroundColor,s.getPropertyValue('--rtp-status'),s.getPropertyValue('--v19-rtp-status'),s.getPropertyValue('--v19-rtp-color')].some(c=>c.trim().toUpperCase()==rgb.hex||c.replace(/\\s/g,'')===rgb.rgb);}",{'hex':color,'rgb':'rgb('+','.join(map(str,rgb))+')'}),(status,color)
 assert raw()['records']['payments'][0]['amount']==200
 assert raw()['records']['activities'][0]['title']=='فعالیت قدیمی'
 # A full project description is an explicit wide text area, not a truncated table cell.
 page.get_by_role('button',name='افزودن پروژه',exact=True).click();form=page.get_by_role('dialog')
 form.get_by_label('شناسه پروژه',exact=True).fill('LONG-019')
 form.get_by_label('عنوان پروژه',exact=True).fill(TITLE)
 description=form.get_by_label('شرح پروژه',exact=True);assert description.evaluate('e=>e.tagName')=='TEXTAREA'
 assert int(description.get_attribute('maxlength'))>=100000
 description.fill(LONG)
 box=description.bounding_box();code_box=form.get_by_label('شناسه پروژه',exact=True).bounding_box()
 assert box['width']>code_box['width']*1.6 and box['height']>=160
 assert box['y']>code_box['y']
 form.get_by_label('مالک ریسک',exact=True).fill('مالک متن کامل')
 form.get_by_label('مسئول اجرا',exact=True).fill('مجری متن کامل')
 form.get_by_label('تاریخ شروع شمسی',exact=True).fill('2026-11-01')
 form.get_by_label('موعد پایان',exact=True).fill('2027-02-01')
 capture(description,'project-description-light.png');save(form)
 new=next(p for p in raw()['records']['projects'] if p['code']=='LONG-019');new_id=new['id']
 assert new['description']==LONG
 heights=page.locator('[data-v19-rtp-card]').evaluate_all('xs=>xs.map(e=>e.getBoundingClientRect().height)')
 assert max(heights)-min(heights)<2,heights
 assert card(new_id).evaluate('e=>e.scrollHeight<=e.clientHeight+1')
 form=edit('LONG-019');expect(form.get_by_label('شرح پروژه',exact=True)).to_have_value(LONG)
 form.get_by_label('شرح پروژه',exact=True).fill(LONG+'\nاصلاح نهایی');save(form)
 assert row(new_id)['description']==LONG+'\nاصلاح نهایی'
 # Manual effective status still requires real evidence; execution100 remains independent of closure.
 form=edit('LONG-019');form.get_by_label('درصد پیشرفت',exact=True).fill('100')
 form.get_by_label('آخرین وضعیت',exact=True).select_option('effective')
 submit(form);expect(form).to_have_count(1)
 assert form.locator('[role=alert]').count()>=1
 assert not row(new_id)['closed']
 form.get_by_label('آخرین وضعیت',exact=True).select_option('active');save(form)
 assert row(new_id)['progress']==100 and not row(new_id)['closed']
 # Activities and the preserved bulk grid remain functional beneath the cards.
 page.get_by_role('button',name='فعالیت‌های پروژه RTP LEG-001',exact=True).click()
 expect(page.get_by_label('عنوان فعالیت ردیف 1',exact=True)).to_have_value('فعالیت قدیمی')
 page.get_by_role('button',name='افزودن فعالیت',exact=True).click()
 page.get_by_label('عنوان فعالیت ردیف 2',exact=True).fill('فعالیت جدید RTP');page.get_by_label('عنوان فعالیت ردیف 2',exact=True).press('Tab')
 assert raw()['records']['activities'][1]['title']=='فعالیت جدید RTP'
 bulk=page.locator('[data-v19-rtp-bulk]')
 if not bulk.evaluate('e=>e.open'):bulk.locator('summary').click()
 paste('عنوان پروژه ردیف 1','عنوان اصلاح‌شده با چسباندن\n')
 assert row('legacy-none')['title']=='عنوان اصلاح‌شده با چسباندن'
 paste('درصد پیشرفت ردیف 1','101\n');assert row('legacy-none')['progress']==0
 bulk.locator('summary').click()
 with page.expect_download() as event:page.get_by_role('button',name='خروجی Excel',exact=True).click()
 event.value.save_as(str(art/'rtp-projects.xlsx'));book=load_workbook(art/'rtp-projects.xlsx')
 headers=[c.value for c in book.active[1]];assert 'شرح پروژه' in headers
 values=list(book.active.values);export_row=next(r for r in values[1:] if r[headers.index('شناسه پروژه')]=='LONG-019')
 assert export_row[headers.index('شرح پروژه')]==LONG+'\nاصلاح نهایی'
 print('PASS legacy card register, exact status colors, full long description, edit persistence, fixed heights, execution/closure distinction and activities/bulk/export',flush=True)
 # Legacy allocation is counted once and remains editable even when its old date was absent.
 tab(2);budget=page.locator('[data-v19-rtp-budget-project="legacy-none"]')
 if budget.evaluate('e=>e.tagName==="DETAILS"&&!e.open'):budget.locator('summary').click()
 assert budget.get_by_label('بودجه مصوب RTP',exact=True).input_value()=='1000'
 assert budget.get_by_label('مبلغ تخصیص RTP 1',exact=True).input_value()=='750'
 assert number(budget.locator('[data-v19-rtp-allocated]').inner_text())==750
 assert number(budget.locator('[data-v19-rtp-remaining]').inner_text())==250
 budget.get_by_label('تاریخ تصویب بودجه RTP',exact=True).fill('2026-01-01')
 budget.get_by_role('button',name='ذخیره بودجه RTP',exact=True).click()
 expect(budget.locator('[role=alert]')).to_have_count(1)
 assert 'allocations' not in row('legacy-none') and row('legacy-none')['allocated']==750
 budget.get_by_label('تاریخ تخصیص RTP 1',exact=True).fill('2026-01-02')
 budget.get_by_role('button',name='افزودن تخصیص بودجه',exact=True).click()
 budget.get_by_label('مبلغ تخصیص RTP 2',exact=True).fill('100')
 budget.get_by_label('تاریخ تخصیص RTP 2',exact=True).fill('2026-01-03')
 assert number(budget.locator('[data-v19-rtp-allocated]').inner_text())==850
 assert number(budget.locator('[data-v19-rtp-remaining]').inner_text())==150
 budget.get_by_role('button',name='ذخیره بودجه RTP',exact=True).click()
 assert row('legacy-none')['budget']==1000 and row('legacy-none')['allocated']==850
 assert len(row('legacy-none')['allocations'])==2
 assert sum(float(r['amount']) for r in row('legacy-none')['allocations'])==850
 assert raw()['records']['payments'][0]['amount']==200
 capture(budget,'budget-allocations-light.png')
 budget.get_by_role('button',name='حذف تخصیص RTP 2',exact=True).click()
 budget.get_by_role('button',name='ذخیره بودجه RTP',exact=True).click()
 assert row('legacy-none')['allocated']==750 and len(row('legacy-none')['allocations'])==1
 assert number(budget.locator('[data-v19-rtp-remaining]').inner_text())==250
 assert raw()['records']['payments'][0]['status']=='پرداخت قبلی'
 budget_card=budget.locator('..');expand(budget_card,'دفتر پرداخت‌های ثبت‌شده')
 expect(budget_card.get_by_label('میزان آخرین پرداخت ردیف 1',exact=True)).to_have_value('200')
 page.reload();main('Risk Treatment Plan');tab(1)
 form=edit('LONG-019');expect(form.get_by_label('شرح پروژه',exact=True)).to_have_value(LONG+'\nاصلاح نهایی');close()
 assert row('legacy-none')['allocated']==750
 print('PASS approved/date and repeated allocation budget, no legacy double-counting, delete/reload and preserved independent payment log',flush=True)
 # Existing full-workspace JSON transfer carries the new fields and the untouched legacy rows.
 main('پشتیبانی سایت')
 with page.expect_download() as event:page.get_by_role('button',name='دریافت JSON پروژه فعال',exact=True).click()
 event.value.save_as(str(out/'backup.json'));backup=json.loads((out/'backup.json').read_text())
 assert next(p for p in backup['rtp']['records']['projects'] if p['id']==new_id)['description']==LONG+'\nاصلاح نهایی'
 assert next(p for p in backup['rtp']['records']['projects'] if p['id']=='legacy-none')['allocated']==750
 page.get_by_label('بارگذاری نسخه JSON',exact=True).set_input_files(str(out/'backup.json'))
 page.get_by_label('نام سازمان واردشده',exact=True).fill('بازیابی RTP نسخه۱۹')
 page.get_by_role('button',name='واردکردن پروژه',exact=True).click();expect(page.get_by_role('dialog')).to_have_count(0)
 main('Risk Treatment Plan');tab(0);dashboard=page.locator('[data-v19-rtp-dashboard]')
 expect(dashboard).to_have_count(1);expect(page.locator('[data-v19-rtp-timeline]')).to_have_count(1)
 assert number(dashboard.locator('.v8-kpis article').first.locator('strong').inner_text())==6
 assert number(dashboard.locator('.v8-kpis article').last.locator('strong').inner_text())==0
 assert page.locator('[data-v19-rtp-dashboard-row]').count()==6
 assert page.locator('[data-v19-rtp-dashboard-row="legacy-paused"]').count()==1
 assert 'تاریخ شروع یا پایان کامل نیست' in page.locator('[data-v19-rtp-dashboard-row="legacy-paused"]').inner_text()
 assert page.locator('[data-v19-rtp-dashboard-row="legacy-none"] .v19-rtp-health').get_attribute('class').endswith('delayed')
 assert raw()['records']['payments'][0]['amount']==200
 capture(dashboard,'dashboard-light.png')
 ctx.set_offline(True);page.get_by_label('پوسته سایت',exact=True).select_option('dark')
 capture(dashboard,'dashboard-dark.png')
 tab(1);capture(page.locator('[data-v19-rtp-view]'),'register-dark.png')
 page.set_viewport_size({'width':390,'height':844});assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 capture(page.locator('[data-v19-rtp-view]'),'register-mobile-dark.png')
 form=edit('LONG-019');assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 expect(form.get_by_label('شرح پروژه',exact=True)).to_have_value(LONG+'\nاصلاح نهایی')
 capture(form.get_by_label('شرح پروژه',exact=True),'description-mobile-dark.png');close()
 tab(0);capture(page.locator('[data-v19-rtp-dashboard]'),'dashboard-mobile-dark.png')
 assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 assert not errors,errors
 assert all(url.split('#')[0]==args.url for url in requests),requests
 (art/'result.json').write_text(json.dumps({'result':'PASS','projects':6,'legacy_allocated':750,'description_length':len(LONG),'errors':errors,'requests':requests},ensure_ascii=False,indent=2))
 print('PASS complete JSON transfer, actual dashboard timelines and unknown dates, both themes/mobile and offline without JS errors or external requests',flush=True)
 browser.close()
