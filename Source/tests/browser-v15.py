"""Offline v15 QA: implementation distribution/drilldown and clearer BCMS forms."""
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
from tempfile import TemporaryDirectory
from openpyxl import load_workbook
from zipfile import ZipFile
import argparse, json, os

parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://127.0.0.1:8775/Didban_Amniat_Offline.html')
parser.add_argument('--artifacts',default='/tmp/didban-v15-qa')
args=parser.parse_args();art=Path(args.artifacts);art.mkdir(parents=True,exist_ok=True)
taxonomy=json.loads(Path('src/taxonomy-v13.json').read_text())
clauses=taxonomy['clauses'];groups=taxonomy['groups'];statuses=['0','1','2','3','4','unknown']
assert len(clauses)==8 and len(groups)==10

with TemporaryDirectory() as temp, sync_playwright() as pw:
 out=Path(temp)
 browser=pw.chromium.launch(executable_path=os.environ.get('DIDBAN_CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 ctx=browser.new_context(viewport={'width':1536,'height':1050},accept_downloads=True)
 page=ctx.new_page();errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:requests.append(r.url))
 page.goto(args.url)
 def main(name):page.locator('aside nav>button').filter(has_text=name).click()
 def raw(key):return page.evaluate("suffix=>{const k=Object.keys(localStorage).find(k=>k.endsWith(':'+suffix));return k?JSON.parse(localStorage.getItem(k)):null;}",key)
 def capture(locator,name):
  style=page.add_style_tag(content='body .shell>main>header,body .toast{visibility:hidden!important}')
  locator.screenshot(path=str(art/name));style.evaluate('e=>e.remove()')
 def stat(key):return page.locator('[data-v15-implementation-stat="'+str(key)+'"]')
 def listing():return page.locator('[data-v15-implementation-list]')
 def item_ids():return listing().locator('[data-v15-implementation-item]').evaluate_all('xs=>xs.map(x=>x.dataset.v15ImplementationItem)')
 def count_cards(expected):
  assert page.locator('[data-v15-implementation-stat]').evaluate_all('xs=>xs.map(x=>x.dataset.v15ImplementationStat)')==statuses
  for key,count in expected.items():assert int(stat(key).get_attribute('data-count'))==count,(key,count)
 def close_list():page.get_by_role('button',name='بستن فهرست وضعیت پیاده‌سازی',exact=True).click();expect(listing()).to_have_count(0)
 def seed():
  audits=[('A.5.1',0,5,True),('A.5.2',1,0,True),('A.5.3',2,4,True),('A.5.4',3,3,True),('A.5.5',4,2,True),('A.5.6',4,1,False),('4.1',0,2,True),('4.2',1,1,True),('4.3',2,0,True),('4.4',3,5,True),('5.1',4,2,True)]
  page.evaluate("""rows=>{const reg=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default')),prefix='didban-project:default:'+reg.activeId+':';localStorage.setItem(prefix+'didban-isms-offline-v1',JSON.stringify(Object.fromEntries(rows.map(([id,status,compliance,applicable])=>[id,{id,status,compliance,applicable,reason:applicable?'':'خارج از دامنه آزمون',documents:'شواهد ثبت‌شده '+id,observations:'نتیجه بررسی '+id,owner:'مالک آزمون',action:'تصمیم ممیزی',due:'2027-12-01',reviewer:'ممیز آزمون',correctiveAction:'',previousCompliance:'',updated:'2026-10-27T08:00:00Z'}]))));}""",audits)
  page.reload()
 # The addition is below the existing final compliance table and all category data remains shared.
 section=page.locator('[data-v15-implementation-dashboard]')
 expect(section).to_have_count(1)
 assert page.evaluate("()=>Boolean(document.querySelector('.v10-compliance-table').compareDocumentPosition(document.querySelector('[data-v15-implementation-dashboard]')) & Node.DOCUMENT_POSITION_FOLLOWING)")
 assert page.locator('[data-standard-dot]').count()==93
 assert page.locator('[data-v13-implementation-axis]').count()==8
 assert page.locator('[data-v13-compliance-group]').count()==18
 assert page.locator('[data-v15-implementation-chart="clause"] [data-v15-implementation-group]').count()==8
 assert page.locator('[data-v15-implementation-chart="control"] [data-v15-implementation-group]').count()==10
 count_cards({'0':0,'1':0,'2':0,'3':0,'4':0,'unknown':123})
 for row in section.locator('[data-v15-implementation-group]').all():
  assert row.locator('[data-v15-implementation-segment]').count()==1
  assert row.locator('[data-v15-implementation-segment]').get_attribute('data-v15-implementation-segment')=='unknown'
  assert float(row.locator('[data-v15-implementation-segment]').get_attribute('data-percentage'))==100
 for link in page.locator('.ds-quick a').all():
  target=link.get_attribute('href');assert target and page.locator('[id="'+target[1:]+'"]').count()==1,target
 assert page.locator('.ds-quick a').count()==7
 seed();section=page.locator('[data-v15-implementation-dashboard]')
 count_cards({'0':2,'1':2,'2':2,'3':2,'4':2,'unknown':112})
 assert '۱۲۲' in section.locator('.v15-eligible-total').inner_text()
 for row in section.locator('[data-v15-implementation-group]').all():
  values=row.locator('[data-v15-implementation-segment]').evaluate_all('xs=>xs.map(x=>({n:+x.dataset.count,p:+x.dataset.percentage,w:parseFloat(x.style.width)}))')
  assert sum(v['n'] for v in values)==int(row.get_attribute('data-total'))
  assert abs(sum(v['p'] for v in values)-100)<.001
  assert all(abs(v['p']-v['w'])<.001 for v in values)
 governance=section.locator('[data-v15-implementation-group="annex:governance"]')
 assert governance.get_attribute('data-total')=='14'
 assert governance.locator('[data-v15-implementation-segment]').evaluate_all('xs=>xs.map(x=>x.dataset.v15ImplementationSegment)')==statuses
 assert governance.locator('[data-v15-implementation-segment]').evaluate_all('xs=>xs.map(x=>+x.dataset.count)')==[1,1,1,1,1,9]
 context=section.locator('[data-v15-implementation-group="clause:context"]')
 assert context.get_attribute('data-total')=='4'
 assert context.locator('[data-v15-implementation-segment]').evaluate_all('xs=>xs.map(x=>+x.dataset.percentage)')==[25]*4
 capture(section,'implementation-overview-light.png')
 # Summary cards bring both kinds into one list. Kind, scope and search filters are cumulative.
 stat(0).click();expect(listing()).to_be_visible();assert set(item_ids())=={'A.5.1','4.1'}
 assert listing().locator('h3').evaluate('e=>e===document.activeElement')
 page.get_by_label('نوع موارد فهرست پیاده‌سازی',exact=True).select_option('control');assert item_ids()==['A.5.1']
 page.get_by_label('نوع موارد فهرست پیاده‌سازی',exact=True).select_option('clause');assert item_ids()==['4.1']
 page.get_by_label('نوع موارد فهرست پیاده‌سازی',exact=True).select_option('all')
 page.get_by_label('جستجوی فهرست پیاده‌سازی',exact=True).fill('A.5.1');assert item_ids()==['A.5.1']
 page.get_by_role('button',name='بازکردن ممیزی A.5.1',exact=True).click();dialog=page.get_by_role('dialog')
 assert dialog.locator('.audit-entry .formgrid select').input_value()=='0'
 assert dialog.get_by_label('انطباق با استاندارد',exact=True).input_value()=='5'
 assert dialog.get_by_label('شواهد و مستندات بررسی‌شده',exact=True).input_value()=='شواهد ثبت‌شده A.5.1'
 dialog.get_by_role('button',name='بستن',exact=True).click();expect(dialog).to_have_count(0)
 capture(listing(),'implementation-list-light.png');close_list();expect(stat(0)).to_be_focused()
 stat(1).click();page.keyboard.press('Escape');expect(listing()).to_have_count(0);expect(stat(1)).to_be_focused()
 # A chart segment narrows the same list by both domain and status.
 governance.locator('[data-v15-implementation-segment="unknown"]').click()
 assert page.get_by_label('حوزه فهرست پیاده‌سازی',exact=True).input_value()=='annex:governance'
 assert page.get_by_label('نوع موارد فهرست پیاده‌سازی',exact=True).input_value()=='control'
 assert len(item_ids())==9 and 'A.5.6' not in item_ids()
 close_list()
 # An unassessed item opens the real audit form, and saving updates the cards, stacks and list immediately.
 stat('unknown').click();assert len(item_ids())==112
 page.get_by_label('جستجوی فهرست پیاده‌سازی',exact=True).fill('A.5.7');assert item_ids()==['A.5.7']
 page.get_by_role('button',name='بازکردن ممیزی A.5.7',exact=True).click();dialog=page.get_by_role('dialog')
 dialog.locator('.audit-entry .formgrid select').select_option('2')
 dialog.get_by_label('انطباق با استاندارد',exact=True).select_option('5')
 dialog.get_by_label('نام ممیز',exact=True).fill('ممیز جدید')
 dialog.get_by_label('شواهد و مستندات بررسی‌شده',exact=True).fill('شواهد واقعی جدید')
 dialog.get_by_role('button',name='ذخیره ارزیابی',exact=True).click();expect(dialog).to_have_count(0)
 assert raw('didban-isms-offline-v1')['A.5.7']['status']==2
 assert raw('didban-isms-offline-v1')['A.5.7']['compliance']==5
 count_cards({'0':2,'1':2,'2':3,'3':2,'4':2,'unknown':111});assert not item_ids()
 close_list();stat(2).click();assert set(item_ids())=={'A.5.3','A.5.7','4.3'};close_list()
 page.reload();count_cards({'0':2,'1':2,'2':3,'3':2,'4':2,'unknown':111})
 print('PASS both implementation stacks, exact status totals/100% shares, NA exclusion, independent compliance, clickable filters/audit details and reactive unassessed-save',flush=True)
 # Existing project navigation continues to work; the new controls have no network dependency.
 for name in ['الزامات استاندارد','کنترل‌های Annex A','اقدامات اصلاحی','روش ارزیابی','مدیریت ریسک','پشتیبانی سایت','داشبورد مدیریتی']:
  main(name);assert page.locator('aside>nav>button.active').count()==1
 main('داشبورد مدیریتی');page.get_by_label('پوسته سایت',exact=True).select_option('dark')
 capture(page.locator('[data-v15-implementation-dashboard]'),'implementation-overview-dark.png')
 stat('unknown').click();capture(listing(),'implementation-list-dark.png');close_list()
 # Seed one complete BIA record, retaining known readiness, goals and actual values through the presentation change.
 page.evaluate("""()=>{const reg=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default')),key='didban-project:default:'+reg.activeId+':didban-bcms-independent-v2';const impacts=Object.fromEntries(['operational','financial','legal','customer','hse'].map(k=>[k,Object.fromEntries([60,240,480,1440,4320,10080].map(t=>[t,t>=480?4:1]))]));const b={id:'bia15',code:'BIA-015',title:'پرداخت آفلاین',department:'مالی',owner:'مالک فعالیت',description:'فعالیت نمونه برای آزمون فرم',assessedAt:'2026-10-27',lastReview:'2026-10-27',nextReview:'2027-12-01',impacts,threshold:4,normalCapacity:100,minimumCapacity:40,capacityUnit:'درخواست',emergencyCapacity:50,rto:120,currentRto:60,rpo:60,currentRpo:30,rpoNA:false,bcp:'yes',bcpName:'برنامه پرداخت',bcpOwner:'مالک برنامه',bcpReview:'2027-12-01',bcpStatus:'approved',tested:true,testDate:'2026-10-27',testType:'tabletop',testResult:'pass',actualRto:60,actualRpo:15,actualCapacity:50,scenario:'Data centre outage',disruptionCapacity:0,lastBackupAge:15,wrt:60,currentWrt:30,actualWrt:30,targetRecoverySteps:[],currentRecoverySteps:[],recoverySteps:[]};localStorage.setItem(key,JSON.stringify({version:2,revision:1,records:{assessments:[b]},settings:{threshold:4},audit:[]}));}""")
 page.reload();main('تداوم کسب‌وکار');page.get_by_role('button',name='بازکردن طرح پرداخت آفلاین',exact=True).click()
 form=page.locator('.v15-bcms-form');expect(form).to_have_count(1)
 assert form.locator(':scope>details').count()==5
 assert all(form.locator(':scope>details').evaluate_all('xs=>xs.map(x=>x.open)'))
 assert form.locator('[data-v15-bcms-section]').evaluate_all('xs=>xs.map(x=>x.dataset.v15BcmsSection)')==['basic','impact','recovery','bcp','result']
 expect(form.locator('[data-v15-bcms-guide]')).to_be_visible()
 assert form.locator('.v15-field-hint').count()>=12
 assert form.locator('.v15-section-intro').count()>=3
 for kind in ['target','current']:assert form.locator('[data-v15-recovery-group="'+kind+'"]').count()==1
 assert form.locator('.v11-bcms-field [lang=en]').count()>=20
 assert form.locator('.v8-badge.ready').count()>=1
 assert page.get_by_label('RTO هدف',exact=True).input_value()=='2'
 page.get_by_label('واحد RTO هدف',exact=True).select_option('1');assert page.get_by_label('RTO هدف',exact=True).input_value()=='120'
 page.get_by_label('RTO هدف',exact=True).fill('180');assert raw('didban-bcms-independent-v2')['records']['assessments'][0]['rto']==180
 page.get_by_label('واحد RTO هدف',exact=True).select_option('60');assert page.get_by_label('RTO هدف',exact=True).input_value()=='3'
 page.get_by_label('حداقل ظرفیت قابل قبول',exact=True).fill('50');assert raw('didban-bcms-independent-v2')['records']['assessments'][0]['minimumCapacity']==50
 assert form.locator('.v8-badge.ready').count()>=1
 capture(form.locator('[data-v15-bcms-section="recovery"]'),'bcms-recovery-fields-dark.png')
 page.get_by_label('RPO برای این فعالیت نامرتبط است',exact=True).check();assert page.get_by_label('فاصلهٔ آخرین پشتیبان سازگار تا رخداد',exact=True).count()==0
 page.get_by_label('RPO برای این فعالیت نامرتبط است',exact=True).uncheck()
 assert page.get_by_label('نوع آزمون',exact=True).is_visible()
 page.get_by_label('وجود BCP',exact=True).select_option('no')
 assert page.get_by_label('وضعیت برنامه',exact=True).count()==0
 assert page.get_by_label('نوع آزمون',exact=True).count()==0
 assert not raw('didban-bcms-independent-v2')['records']['assessments'][0]['tested']
 page.get_by_label('وجود BCP',exact=True).select_option('yes');page.get_by_label('وضعیت برنامه',exact=True).select_option('draft')
 assert not page.get_by_label('برنامه آزمون شده است',exact=True).is_checked()
 page.get_by_label('پوسته سایت',exact=True).select_option('light')
 capture(form,'bcms-form-light.png')
 ctx.set_offline(True);page.get_by_label('نام خدمت / فعالیت',exact=True).fill('پرداخت آفلاین جدید')
 assert raw('didban-bcms-independent-v2')['records']['assessments'][0]['title']=='پرداخت آفلاین جدید'
 page.set_viewport_size({'width':390,'height':844});assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 capture(form.locator('[data-v15-bcms-section="recovery"]'),'bcms-recovery-mobile.png')
 page.get_by_role('button',name='بازگشت به فهرست',exact=True).click();main('داشبورد مدیریتی')
 assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 stat(2).click();assert set(item_ids())=={'A.5.3','A.5.7','4.3'}
 capture(listing(),'implementation-list-mobile.png')
 page.get_by_role('button',name='بازکردن ممیزی 4.3',exact=True).click();expect(page.get_by_role('dialog')).to_have_count(1)
 page.get_by_role('dialog').get_by_role('button',name='بستن',exact=True).click();close_list()
 capture(page.locator('[data-v15-implementation-dashboard]'),'implementation-overview-mobile.png')
 assert not errors,errors
 assert all(url.split('#')[0]==args.url for url in requests),requests
 (art/'result.json').write_text(json.dumps({'result':'PASS','errors':errors,'requests':requests,'catalog':123,'eligible':122,'statuses':statuses},indent=2))
 print('PASS BCMS five-section form/hints, target/current units and live autosave/readiness, conditional BCP/RPO, navigation, both themes/mobile/offline with no JS errors or external requests.');browser.close()
