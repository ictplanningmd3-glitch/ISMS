"""Offline v19 QA: long corrective plans, structured indicators and portfolio/compliance dashboards."""
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
parser.add_argument('--url',default='http://127.0.0.1:8781/Didban_Amniat_Offline.html')
parser.add_argument('--artifacts',default='/tmp/didban-v19-qa/corrective')
args=parser.parse_args();art=Path(args.artifacts);art.mkdir(parents=True,exist_ok=True)
W={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
TITLE='طرح جامع اصلاح & <دسترسی> نسخه۱۹'
LONG_GOAL=('شرح برنامهٔ کامل اصلاح دسترسی و نتیجهٔ مورد انتظار؛ حفظ شواهد، مسئولیت‌ها و خروجی‌ها.\n'*180)+'پایان طرح کامل'
assert 10000<len(LONG_GOAL)<50000
INDICATORS=[{'title':'پوشش <کنترل> & هویت‌ها','reviewPeriod':'ماهانه','owner':'مدیریت امنیت'},
            {'title':'زمان رفع یافته','reviewPeriod':'پس از هر آزمون','owner':'تیم اجرایی'}]
LEGACY='پروژه قدیمی دوماهه';FUTURE='پروژه آینده سه‌ماهه';BLOCKED='پروژه متوقف یک‌ماهه'
taxonomy=json.loads(Path('src/taxonomy-v13.json').read_text())
all_ids=[id for g in taxonomy['clauses'] for id in g['itemIds']]+[id for g in taxonomy['groups'] for id in g['controls']]
palette={5:'#168B78',0:'#4FAE66',4:'#3C91CF',3:'#D6A13D',1:'#E87945',2:'#C83E50'}
digits=str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩','01234567890123456789')

def read_docx(path):
 with ZipFile(path) as z:
  assert z.testzip() is None and 'word/document.xml' in z.namelist()
  for name in z.namelist():
   if name.endswith('.xml') or name.endswith('.rels'):ET.fromstring(z.read(name))
  tree=ET.fromstring(z.read('word/document.xml'));text='\n'.join(n.text or '' for n in tree.findall('.//w:t',W))
 document=Document(BytesIO(path.read_bytes()));assert document.tables and document.paragraphs
 return text

with TemporaryDirectory() as temp,sync_playwright() as pw:
 out=Path(temp)
 browser=pw.chromium.launch(executable_path=os.environ.get('DIDBAN_CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 ctx=browser.new_context(viewport={'width':1536,'height':1050},accept_downloads=True)
 page=ctx.new_page();errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:requests.append(r.url))
 page.goto(args.url);assert page.locator('meta[name="didban-version"]').get_attribute('content')=='19'
 def main(name):page.locator('aside>nav>button').filter(has_text=name).click()
 def projects():main('اقدامات اصلاحی');page.locator('[data-v13-corrective-tab="projects"]:visible').first.click()
 def dashboard():main('اقدامات اصلاحی');page.locator('[data-v13-corrective-tab="gaps"]:visible').first.click()
 def raw(key):return page.evaluate("suffix=>{const k=Object.keys(localStorage).find(k=>k.endsWith(':'+suffix));return k?JSON.parse(localStorage.getItem(k)):null;}",key)
 def capture(locator,name):
  style=page.add_style_tag(content='body .shell>main>header,body .toast{visibility:hidden!important}')
  locator.screenshot(path=str(art/name));style.evaluate('e=>e.remove()')
 def expand(root,text):
  summary=root.locator('summary').filter(has_text=text)
  if not summary.evaluate('e=>e.parentElement.open'):summary.click()
 def edit(title):page.get_by_role('button',name='ویرایش پروژه '+title,exact=True).click();return page.get_by_role('dialog')
 def save(form):form.get_by_role('button',name='ذخیره پروژه',exact=True).click();expect(form).to_have_count(0)
 def close_project(form):form.get_by_role('button',name='بستن پروژه',exact=True).click()
 def field(form,label,index):return form.get_by_label(label+' '+str(index),exact=True)
 def fill_indicator(form,index,values):
  for key,label in [('title','عنوان شاخص'),('reviewPeriod','دوره بازبینی'),('owner','متولی اجرایی')]:field(form,label,index).fill(values[key])
 def seed(project_rows,audits):
  page.evaluate("""payload=>{const reg=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default')),p='didban-project:default:'+reg.activeId+':';if(payload.projects!==null)localStorage.setItem(p+'didban-isms-improvements-v1',JSON.stringify(payload.projects));localStorage.setItem(p+'didban-isms-offline-v1',JSON.stringify(payload.audits));}""",{'projects':project_rows,'audits':audits})
  page.reload()
 # The real form accepts a complete plan without inventing a mandatory resource value.
 projects();page.get_by_role('button',name='تعریف اقدام بهبود',exact=True).click();form=page.get_by_role('dialog')
 form.get_by_label('عنوان اقدام یا پروژه',exact=True).fill(TITLE)
 form.get_by_label('مسئول پیگیری',exact=True).fill('مسئول طرح')
 goal=form.get_by_label('هدف و نتیجه مورد انتظار',exact=True);assert goal.get_attribute('maxlength')=='50000';goal.fill(LONG_GOAL)
 assert goal.evaluate('e=>e.getBoundingClientRect().height')>=220
 resources=form.get_by_label('منابع لازم',exact=True);assert not resources.evaluate('e=>e.required');resources.fill('')
 fill_indicator(form,1,{key:'  '+value+'  ' for key,value in INDICATORS[0].items()})
 form.get_by_role('button',name='افزودن ردیف شاخص',exact=True).click();expect(field(form,'عنوان شاخص',2)).to_be_focused()
 fill_indicator(form,2,{'title':'قابل حذف','reviewPeriod':'روزانه','owner':'فرد حذف‌شده'})
 form.get_by_role('button',name='افزودن ردیف شاخص',exact=True).click();fill_indicator(form,3,INDICATORS[1])
 form.get_by_role('button',name='حذف شاخص 2',exact=True).click();expect(field(form,'عنوان شاخص',2)).to_have_value(INDICATORS[1]['title']);expect(field(form,'عنوان شاخص',2)).to_be_focused()
 form.get_by_role('button',name='افزودن ردیف شاخص',exact=True).click()
 form.get_by_label('گروه زمانی پروژه',exact=True).select_option('1');form.get_by_label('تاریخ شروع پروژه',exact=True).fill('2026-01-01')
 form.get_by_label('وضعیت پروژه',exact=True).select_option('active');form.get_by_label('پیشرفت (درصد)',exact=True).fill('25')
 expand(form,'ارتباط دقیق با الزامات و کنترل‌ها')
 for id in ['A.5.16','4.1']:form.get_by_label('ارتباط پروژه '+id,exact=True).check()
 capture(form.locator('[data-v19-structured-indicators]'),'structured-indicators-light.png');capture(goal,'large-goal-light.png');save(form)
 stored=raw('didban-isms-improvements-v1');assert len(stored)==1;created=stored[0];project_id=created['id']
 assert created['goal']==LONG_GOAL and created['resources']=='' and created['indicators']==INDICATORS
 form=edit(TITLE);expect(form.get_by_label('هدف و نتیجه مورد انتظار',exact=True)).to_have_value(LONG_GOAL)
 for i,row in enumerate(INDICATORS,1):
  for key,label in [('title','عنوان شاخص'),('reviewPeriod','دوره بازبینی'),('owner','متولی اجرایی')]:expect(field(form,label,i)).to_have_value(row[key])
 close_project(form)
 # Keep old strings/old projects and stress card dimensions with long goals and123 links.
 common={'owner':'مالک نمونه','resources':'','notes':'یادداشت وضعیت','updated':'2026-11-11T08:00:00Z','priority':'medium','scopeIds':[]}
 legacy=dict(common,id='legacy19',title=LEGACY,goal='هدف قدیمی',start='2026-01-01',due='2026-03-01',months=2,status='completed',progress=100,mappedIds=['4.2'],indicators=['شاخص قدیمی'])
 future=dict(common,id='future19',title=FUTURE,goal=LONG_GOAL,start='2027-01-01',due='2027-04-01',months=3,status='planned',progress=0,mappedIds=all_ids,indicators=[])
 blocked=dict(common,id='blocked19',title=BLOCKED,goal='هدف متوقف',start='2026-11-01',due='2026-12-01',months=1,status='blocked',progress=5,mappedIds=['A.5.17'],indicators=[])
 fixture=[created,legacy,future,blocked]
 audits={}
 for id,compliance in [('4.1',5),('4.2',0),('4.3',4),('4.4',3),('A.5.16',1),('A.5.17',2),('A.5.36',0),('A.5.37',None)]:
  audits[id]=dict(id=id,status=2,compliance=compliance,applicable=id not in ['A.5.36','A.5.37'],reason='' if id not in ['A.5.36','A.5.37'] else 'خارج از دامنهٔ آزمون',documents='شاهد '+id,observations='نتیجهٔ آزمون',owner='مالک',action='',due='2027-01-01',reviewer='ممیز',correctiveAction='',previousCompliance='',updated='2026-11-11T08:00:00Z')
 seed(fixture,audits);projects()
 cards=page.locator('[data-v19-fixed-card]');assert cards.count()==4
 heights=cards.evaluate_all('xs=>xs.map(e=>e.getBoundingClientRect().height)');assert max(heights)-min(heights)<=1 and 390<=min(heights)<=420,heights
 for card in cards.all():
  button=card.locator('.project-edit');assert button.is_visible();assert button.evaluate('e=>{const a=e.getBoundingClientRect(),b=e.closest("[data-v19-fixed-card]").getBoundingClientRect();return a.bottom<=b.bottom+1;}')
 capture(page.locator('.project-grid'),'fixed-project-cards-light.png')
 form=edit(LEGACY);expect(field(form,'عنوان شاخص',1)).to_have_value('شاخص قدیمی');expect(field(form,'دوره بازبینی',1)).to_have_value('');expect(field(form,'متولی اجرایی',1)).to_have_value('');save(form)
 assert next(p for p in raw('didban-isms-improvements-v1') if p['id']=='legacy19')['indicators']==[{'title':'شاخص قدیمی','reviewPeriod':'','owner':''}]
 print('PASS complete long plan, optional resources, three indicator fields/add/delete/focus, legacy string migration and fixed-height project cards',flush=True)
 # Transfer the active project using the existing public backup route.
 main('پشتیبانی سایت')
 with page.expect_download() as event:page.get_by_role('button',name='دریافت JSON پروژه فعال',exact=True).click()
 event.value.save_as(str(out/'backup.json'));backup=json.loads((out/'backup.json').read_text());assert len(backup['projects'])==4
 assert next(p for p in backup['projects'] if p['id']==project_id)['indicators']==INDICATORS
 page.get_by_label('بارگذاری نسخه JSON',exact=True).set_input_files(str(out/'backup.json'));page.get_by_label('نام سازمان واردشده',exact=True).fill('بازآوری شاخص‌های نسخه۱۹');page.get_by_role('button',name='واردکردن پروژه',exact=True).click();expect(page.get_by_role('dialog')).to_have_count(0)
 page.reload();projects();form=edit(TITLE);expect(form.get_by_label('هدف و نتیجه مورد انتظار',exact=True)).to_have_value(LONG_GOAL);expect(field(form,'متولی اجرایی',1)).to_have_value(INDICATORS[0]['owner']);close_project(form)
 main('پشتیبانی سایت');page.get_by_role('button',name='گزارش Word و Excel',exact=True).click()
 page.get_by_label('نام سازمان',exact=True).fill('سازمان نسخه۱۹');page.get_by_label('نوع ممیزی',exact=True).select_option(label='ممیزی داخلی');page.get_by_label('نام ممیز / بررسی‌کننده',exact=True).fill('ممیز نسخه۱۹')
 with page.expect_download() as event:page.get_by_role('button',name='دریافت Excel (.xlsx)',exact=True).click()
 event.value.save_as(str(art/'structured-indicators.xlsx'));workbook=load_workbook(art/'structured-indicators.xlsx');sheet=workbook['اقدامات بهبود'];headers=[c.value for c in sheet[1]]
 row=next(row for row in list(sheet.values)[1:] if row[headers.index('عنوان')]==TITLE);exported=row[headers.index('شاخص‌های اقدام اصلاحی')]
 for indicator in INDICATORS:
  assert all(value in exported for value in indicator.values())
 assert '[object Object]' not in exported and row[headers.index('هدف')]==LONG_GOAL
 embedded=page.locator('[data-v18-reports-entry="word"]');expand(embedded,'گزارش‌های Word اقدامات اصلاحی')
 embedded.get_by_label('نوع گزارش اقدامات اصلاحی',exact=True).select_option('project');embedded.get_by_label('پروژهٔ گزارش اقدامات اصلاحی',exact=True).select_option(project_id)
 with page.expect_download() as event:embedded.get_by_role('button',name='دریافت گزارش Word اقدامات اصلاحی',exact=True).click()
 event.value.save_as(str(art/'structured-indicators.docx'));word=read_docx(art/'structured-indicators.docx')
 for indicator in INDICATORS:assert all(value in word for value in indicator.values())
 assert LONG_GOAL in word and '[object Object]' not in word
 page.get_by_label('بستن گزارش',exact=True).click()
 print('PASS JSON transfer and genuine Word/Excel exports preserve the full plan and all three indicator fields',flush=True)
 # New portfolio and compliance assertions are below; their hooks are shared with unit-tested engines.
 dashboard();portfolio=page.locator('[data-v19-portfolio]');expect(portfolio).to_have_count(1)
 for key,count in [('all',4),('A',2),('B',1),('C',1)]:expect(portfolio.locator('[data-v19-portfolio-group="'+key+'"]').first).to_have_attribute('data-count',str(count))
 assert portfolio.locator('[data-v19-portfolio-project]').count()==4
 expected_health={project_id:'delayed','legacy19':'completed','future19':'ontrack','blocked19':'atrisk'}
 for id,health in expected_health.items():expect(portfolio.locator('[data-v19-portfolio-project="'+id+'"]')).to_have_attribute('data-v19-portfolio-health',health)
 assert portfolio.locator('[data-v19-portfolio-today]').count()==1
 assert portfolio.locator('[data-v19-duration-donut]').count()==1
 for key,count in [('A',2),('B',1),('C',1)]:expect(portfolio.locator('[data-v19-duration-segment="'+key+'"]').first).to_have_attribute('data-count',str(count))
 for segment in portfolio.locator('[data-v19-health-segment]').all():assert segment.get_attribute('data-count')=='1'
 portfolio.locator('[data-v19-portfolio-group="A"]').first.click();assert portfolio.locator('[data-v19-portfolio-project]').count()==2
 portfolio.get_by_label('گروه داشبورد پروژه‌ها',exact=True).select_option('all')
 portfolio.get_by_label('وضعیت زمان‌بندی داشبورد پروژه‌ها',exact=True).select_option('delayed');assert portfolio.locator('[data-v19-portfolio-project]').count()==1
 portfolio.get_by_label('وضعیت زمان‌بندی داشبورد پروژه‌ها',exact=True).select_option('all')
 portfolio.get_by_label('جستجوی داشبورد پروژه‌ها',exact=True).fill('طرح جامع');assert portfolio.locator('[data-v19-portfolio-project]').count()==1
 portfolio.get_by_label('جستجوی داشبورد پروژه‌ها',exact=True).fill('')
 portfolio.get_by_role('button',name='مشاهده اطلاعات پروژه '+TITLE,exact=True).click();detail=portfolio.locator('[data-v19-portfolio-detail="'+project_id+'"]')
 expect(detail).to_be_visible();assert detail.locator('.v19-portfolio-full-text').first.text_content()==LONG_GOAL
 for indicator in INDICATORS:assert all(value in detail.inner_text() for value in indicator.values())
 assert 'A.5.16' in detail.inner_text() and '4.1' in detail.inner_text()
 detail.get_by_role('button',name='ویرایش پروژه از داشبورد '+TITLE,exact=True).click();form=page.get_by_role('dialog')
 expect(form.get_by_label('هدف و نتیجه مورد انتظار',exact=True)).to_have_value(LONG_GOAL);close_project(form)
 portfolio.get_by_role('button',name='مشاهده اطلاعات پروژه '+TITLE,exact=True).click();expect(detail).to_have_count(0)
 capture(portfolio,'corrective-portfolio-light.png')
 main('داشبورد مدیریتی');summary=page.locator('[data-v19-compliance-summary]');expect(summary).to_have_count(1)
 assert page.locator('.v10-compliance-dashboard .dc-summary').count()==0
 assert page.locator('.v10-compliance-dashboard .v13-compliance-distribution').count()==0
 for code in [5,0,4,3,1,2]:expect(summary.locator('[data-v19-compliance-count="'+str(code)+'"]')).to_have_attribute('data-count','1')
 expect(summary.locator('[data-v19-compliance-count="unknown"]')).to_have_attribute('data-count','115')
 rate=summary.locator('[data-v19-compliance-rate]');assert int(rate.get_attribute('data-positive'))==4 and int(rate.get_attribute('data-total'))==121
 assert abs(float(rate.get_attribute('data-rate'))-4/121*100)<1e-7
 assert summary.locator('[data-v19-compliance-donut]').count()==1
 segments=summary.locator('[data-v19-compliance-segment]');assert sum(int(s.get_attribute('data-count')) for s in segments.all())==121
 assert abs(sum(float(s.get_attribute('data-percentage')) for s in segments.all())-100)<1e-7
 for segment in segments.all():
  code=segment.get_attribute('data-v19-compliance-segment')
  if code!='unknown':
   color=palette[int(code)];expected='rgb('+', '.join(str(int(color[i:i+2],16)) for i in (1,3,5))+')'
   assert segment.evaluate('e=>getComputedStyle(e).stroke')==expected
 assert 'ماه قبل' not in summary.inner_text()
 assert page.locator('[data-v13-compliance-group]').count()==18
 assert page.locator('[data-v15-implementation-dashboard]').count()==1
 for code,count in [('5',1),('0',1),('4',1),('3',1),('1',1),('2',1),('6',115)]:expect(page.locator('[data-v18-compliance-total="'+code+'"]')).to_have_attribute('data-count',str(count))
 expect(page.locator('[data-v15-implementation-stat="2"]')).to_have_attribute('data-count','6')
 expect(page.locator('[data-v15-implementation-stat="unknown"]')).to_have_attribute('data-count','115')
 capture(summary,'compliance-overall-light.png')
 # An empty audit ledger stays unknown; it never fabricates full compliance.
 seed(None,{});main('داشبورد مدیریتی');summary=page.locator('[data-v19-compliance-summary]');rate=summary.locator('[data-v19-compliance-rate]')
 assert rate.get_attribute('data-positive')=='0' and rate.get_attribute('data-total')=='123' and float(rate.get_attribute('data-rate'))==0
 expect(summary.locator('[data-v19-compliance-count="unknown"]')).to_have_attribute('data-count','123')
 assert 'هنوز ممیزی ثبت نشده' in summary.inner_text()
 seed(None,audits);main('داشبورد مدیریتی')
 # Existing Annex A wording and navigation remain available, while all new views work offline.
 ctx.set_offline(True)
 dot=page.locator('[data-standard-dot="A.5.16"]');dot.focus();dot.press('Enter');dialog=page.get_by_role('dialog')
 expect(dialog.locator('[data-v17-text-en]')).to_have_text('The full life cycle of identities shall be managed.')
 dialog.get_by_role('button',name='بستن',exact=True).click()
 for theme in ['light','dark']:
  page.get_by_label('پوسته سایت',exact=True).select_option(theme);main('داشبورد مدیریتی');summary=page.locator('[data-v19-compliance-summary]');capture(summary,'compliance-overall-'+theme+'.png')
  assert summary.locator('[data-v19-compliance-donut-rate]').evaluate('e=>getComputedStyle(e).fill')==({'light':'rgb(37, 106, 54)','dark':'rgb(155, 217, 170)'}[theme])
  for segment in summary.locator('[data-v19-compliance-segment]').all():
   code=segment.get_attribute('data-v19-compliance-segment')
   if code!='unknown':
    color=palette[int(code)];assert segment.evaluate('e=>getComputedStyle(e).stroke')=='rgb('+', '.join(str(int(color[i:i+2],16)) for i in (1,3,5))+')'
  dashboard();capture(page.locator('[data-v19-portfolio]'),'corrective-portfolio-'+theme+'.png')
 page.set_viewport_size({'width':390,'height':844})
 for theme in ['light','dark']:
  page.get_by_label('پوسته سایت',exact=True).select_option(theme);main('داشبورد مدیریتی');assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');capture(page.locator('[data-v19-compliance-summary]'),'compliance-overall-mobile-'+theme+'.png')
  dashboard();assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');capture(page.locator('[data-v19-portfolio]'),'corrective-portfolio-mobile-'+theme+'.png')
 projects();form=edit(TITLE);capture(form.locator('[data-v19-structured-indicators]'),'structured-indicators-mobile-dark.png');assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');close_project(form)
 main('داشبورد مدیریتی')
 for link in page.locator('.ds-quick a').all():
  target=link.get_attribute('href');assert target and page.locator('[id="'+target[1:]+'"]').count()==1,target
 assert page.locator('.ds-quick a').count()==7
 for name in ['الزامات استاندارد','کنترل‌های Annex A','اقدامات اصلاحی','Risk Treatment Plan','روش ارزیابی','مدیریت ریسک','تداوم کسب‌وکار','پشتیبانی سایت','داشبورد مدیریتی']:
  main(name);assert page.locator('aside>nav>button.active').count()==1
 assert not errors,errors
 assert all(url.split('#')[0]==args.url for url in requests),requests
 (art/'result.json').write_text(json.dumps({'result':'PASS','errors':errors,'requests':requests,'goal_chars':len(LONG_GOAL),'structured_indicators':INDICATORS,'projects':4,'positive':4,'eligible':121,'rate':4/121*100},ensure_ascii=False,indent=2))
 print('PASS portfolio/compliance dashboards, preserved audit links, light/dark/mobile and offline operation without JS errors or external requests',flush=True)
 browser.close()
