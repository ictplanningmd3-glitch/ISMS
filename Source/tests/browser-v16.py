"""Offline v16 QA: three radar scopes and traceable corrective-action coverage."""
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import argparse, json, math, os

parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://127.0.0.1:8776/Didban_Amniat_Offline.html')
parser.add_argument('--artifacts',default='/tmp/didban-v16-qa')
args=parser.parse_args();art=Path(args.artifacts);art.mkdir(parents=True,exist_ok=True)
taxonomy=json.loads(Path('src/taxonomy-v13.json').read_text())
clause_ids={item for group in taxonomy['clauses'] for item in group['itemIds']}
control_ids={item for group in taxonomy['groups'] for item in group['controls']}
assert len(clause_ids)==30 and len(control_ids)==93

with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=os.environ.get('DIDBAN_CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 ctx=browser.new_context(viewport={'width':1536,'height':1050},accept_downloads=True)
 page=ctx.new_page();errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:requests.append(r.url))
 page.goto(args.url)
 def main(name):page.locator('aside nav>button').filter(has_text=name).click()
 def tab(value):page.locator('[data-v13-corrective-tab="'+value+'"]:visible').first.click()
 def dashboard():main('اقدامات اصلاحی');tab('gaps')
 def raw(key):return page.evaluate("suffix=>{const k=Object.keys(localStorage).find(k=>k.endsWith(':'+suffix));return k?JSON.parse(localStorage.getItem(k)):null;}",key)
 def capture(locator,name):
  style=page.add_style_tag(content='body .shell>main>header,body .toast{visibility:hidden!important}')
  locator.screenshot(path=str(art/name));style.evaluate('e=>e.remove()')
 def radar():return page.locator('[data-v16-radar-mode]')
 def impl():return page.locator('[data-v16-implementation-mode]')
 def mode(which,value):page.get_by_label('دامنه رادار انطباق' if which=='compliance' else 'دامنه توازن پیاده‌سازی',exact=True).select_option(value)
 def dots():return page.locator('[data-standard-dot]').evaluate_all('xs=>xs.map(x=>x.dataset.standardDot)')
 def close_audit():page.get_by_role('dialog').get_by_role('button',name='بستن',exact=True).click();expect(page.get_by_role('dialog')).to_have_count(0)
 def expand_summary(root,text):
  summary=root.locator('summary').filter(has_text=text)
  if not summary.evaluate('e=>e.parentElement.open'):summary.click()
 def coverage(required,defined,covered):
  chart=page.locator('[data-v16-coverage-chart]');kpi=page.locator('[data-v16-coverage-kpi]')
  for key,value in [('required',required),('defined',defined),('covered',covered),('uncovered',required-covered)]:assert chart.get_attribute('data-'+key)==str(value),(key,value)
  for key,value in [('required',required),('defined',defined),('covered',covered)]:assert page.locator('[data-v16-coverage-count="'+key+'"]').get_attribute('data-count')==str(value),(key,value)
  pct=kpi.get_attribute('data-percentage')
  if required:assert abs(float(pct)-covered/required*100)<1e-9,(pct,covered,required)
  else:assert pct=='none' and '—' in kpi.inner_text()
  return chart
 # Defaults preserve existing main-page scope; each mode contains the complete correct catalog once.
 assert radar().get_attribute('data-v16-radar-mode')=='control'
 assert impl().get_attribute('data-v16-implementation-mode')=='clause'
 assert page.locator('[data-v13-implementation-axis]').count()==8
 for value,expected,groups in [('control',control_ids,10),('clause',clause_ids,8),('all',clause_ids|control_ids,10)]:
  mode('compliance',value)
  assert radar().get_attribute('data-v16-radar-mode')==value
  ids=dots();assert len(ids)==len(expected) and set(ids)==expected,(value,ids)
  assert radar().locator('[data-compliance-group]').count()==groups
  assert radar().locator('[data-compliance-divider]').count()==groups
  assert sum(map(int,radar().locator('[data-v16-group-count]').evaluate_all('xs=>xs.map(x=>x.dataset.v16GroupCount)')))==len(expected)
  assert radar().locator('[lang=en]').count()>0
  assert radar().locator('.v8-scope svg>g>text').evaluate_all('xs=>xs.every(e=>{const b=e.getBBox(),v=e.ownerSVGElement.viewBox.baseVal;return b.x>=v.x&&b.x+b.width<=v.x+v.width;})'),value
  assert all(float(point.get_attribute('cx'))>=0 for point in radar().locator('[data-standard-dot]').all())
  mode('implementation',value)
  assert impl().get_attribute('data-v16-implementation-mode')==value
  assert impl().locator('[data-v13-implementation-axis]').count()==groups
  assert impl().locator('[data-v13-implementation-score]').count()==groups
  assert all(x=='0' for x in impl().locator('[data-v13-implementation-score]').evaluate_all('xs=>xs.map(x=>x.dataset.score)'))
  capture(radar(),'compliance-'+value+'-empty-light.png')
 # Four actionable items plus independent positive, N/A and unassessed records.
 audits=[('4.1',4,2,True),('4.2',0,3,True),('4.3',2,5,True),('4.4',4,0,True),('5.1',4,0,True),('A.5.1',4,1,True),('A.5.2',0,4,True),('A.5.3',4,2,False),('A.6.1',2,5,True)]
 page.evaluate("""rows=>{const reg=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default')),prefix='didban-project:default:'+reg.activeId+':';localStorage.setItem(prefix+'didban-isms-offline-v1',JSON.stringify(Object.fromEntries(rows.map(([id,status,compliance,applicable])=>[id,{id,status,compliance,applicable,reason:applicable?'':'خارج از دامنه آزمون',documents:'شواهد '+id,observations:'نتیجه بررسی '+id,owner:'مالک آزمون',action:'تصمیم ممیزی',due:'2027-12-01',reviewer:'ممیز آزمون',correctiveAction:'',previousCompliance:'',updated:'2026-10-30T08:00:00Z'}]))));localStorage.setItem(prefix+'didban-isms-improvements-v1','[]');}""",audits)
 page.reload();mode('implementation','clause')
 scores=lambda:dict(impl().locator('[data-v13-implementation-score]').evaluate_all('xs=>xs.map(x=>[x.dataset.v13ImplementationScore,+x.dataset.score])'))
 assert scores()['clause:context']==63
 assert scores()['clause:leadership']==33
 assert all(value==0 for key,value in scores().items() if key not in ['clause:context','clause:leadership'])
 mode('implementation','control');assert scores()['annex:governance']==7 and scores()['annex:people']==6
 mode('implementation','all');assert len(scores())==10
 mode('compliance','all')
 for item,rank in [('4.1','5'),('4.2','3'),('4.3','0'),('4.4','1'),('A.5.1','4'),('A.5.2','2'),('A.6.1','0')]:assert page.locator('[data-standard-dot="'+item+'"]').get_attribute('data-compliance-rank')==rank
 assert page.locator('[data-standard-dot="A.8.34"]').get_attribute('data-compliance-rank')=='outside'
 # Side-card hover and focus highlight the matching sector; drilldown opens the real audit form.
 for value,item in [('clause','4.1'),('control','A.5.1'),('all','4.1')]:
  mode('compliance',value)
  dot=page.locator('[data-standard-dot="'+item+'"]')
  group_id=dot.locator('..').locator('[data-compliance-divider]').get_attribute('data-compliance-divider')
  card=radar().locator('[data-compliance-group="'+group_id+'"]')
  card.hover();assert 'active' in dot.get_attribute('class')
  card.focus();assert 'active' in dot.get_attribute('class')
  card.press('Enter');listing=page.locator('[data-v16-radar-list]');expect(listing).to_be_visible()
  assert listing.get_attribute('data-v16-radar-list')==group_id
  assert listing.locator('[data-v16-radar-item="'+item+'"]').count()==1
  listing.locator('[data-v16-radar-item="'+item+'"]').click();dialog=page.get_by_role('dialog')
  expect(dialog).to_be_visible();assert dialog.get_by_label('شواهد و مستندات بررسی‌شده',exact=True).input_value()=='شواهد '+item
  close_audit();page.get_by_role('button',name='بستن فهرست حوزه رادار',exact=True).click();expect(listing).to_have_count(0);expect(card).to_be_focused()
  dot.focus();dot.press('Enter');expect(page.get_by_role('dialog')).to_be_visible();close_audit()
  capture(radar(),'compliance-'+value+'-light.png')
 # Selectors remain independent.
 assert impl().get_attribute('data-v16-implementation-mode')=='all'
 mode('implementation','clause');assert radar().get_attribute('data-v16-radar-mode')=='all'
 capture(impl(),'implementation-clause-light.png');mode('implementation','control');capture(impl(),'implementation-control-light.png');mode('implementation','all');capture(impl(),'implementation-all-light.png')
 print('PASS three exhaustive scopes in both radars, canonical 8/10 and combined10 domains, native scores, N/A/unknown handling, independent compliance, hover/focus, keyboard dot audit and group drilldown',flush=True)
 # The coverage ratio counts distinct actionable items; project count is a separate unit.
 dashboard();coverage(4,0,0)
 assert set(page.locator('[data-v14-action-row]').evaluate_all('xs=>xs.map(x=>x.dataset.v14ActionRow)'))=={'4.1','4.2','A.5.1','A.5.2'}
 tab('projects');page.get_by_role('button',name='تعریف اقدام بهبود',exact=True).click();form=page.get_by_role('dialog')
 for label,value in [('عنوان اقدام یا پروژه','پوشش مشترک دو بند'),('مسئول پیگیری','مسئول پوشش'),('هدف و نتیجه مورد انتظار','رفع دو یافته'),('منابع لازم','تیم اجرا')]:form.get_by_label(label,exact=True).fill(value)
 form.get_by_label('گروه زمانی پروژه',exact=True).select_option('1')
 form.get_by_label('وضعیت پروژه',exact=True).select_option('active')
 form.get_by_label('پیشرفت (درصد)',exact=True).fill('25')
 form.get_by_label('تاریخ شروع پروژه',exact=True).fill('2026-10-01')
 expand_summary(form,'ارتباط دقیق با الزامات و کنترل‌ها')
 for item in ['4.1','A.5.1']:form.get_by_label('ارتباط پروژه '+item,exact=True).check()
 form.get_by_role('button',name='ذخیره پروژه',exact=True).click();expect(form).to_have_count(0)
 tab('gaps');chart=coverage(4,1,2)
 assert chart.locator('[data-v16-coverage-segment=covered]').get_attribute('data-percentage')=='50'
 assert chart.locator('[data-v16-coverage-segment=uncovered]').get_attribute('data-percentage')=='50'
 capture(page.locator('[data-v13-corrective-dashboard]'),'coverage-fifty-percent-light.png')
 chart.locator('summary').filter(has_text='جزئیات محاسبه و موارد تحت پوشش').click()
 project_id=raw('didban-isms-improvements-v1')[0]['id']
 assert chart.locator('[data-v16-coverage-project="'+project_id+'"]').get_attribute('data-count')=='2'
 chart.get_by_role('button',name='بازکردن مورد بدون پوشش 4.2',exact=True).click();expect(page.get_by_role('dialog')).to_be_visible();close_audit()
 chart.get_by_role('button',name='مشاهده پوشش پروژه پوشش مشترک دو بند',exact=True).click();form=page.get_by_role('dialog');expect(form).to_be_visible()
 form.get_by_label('وضعیت پروژه',exact=True).select_option('completed');form.get_by_role('button',name='ذخیره پروژه',exact=True).click();expect(form).to_have_count(0)
 coverage(4,1,2);assert page.locator('[data-v14-action-row="4.1"]').get_attribute('data-v14-action-status')=='done'
 assert raw('didban-isms-offline-v1')['4.1']['compliance']==2
 # A heading plus exact links broadens coverage once for each item; the exact4.1 overlap adds no duplicate.
 page.locator('[data-v14-action-row="4.1"]').get_by_role('button',name='بازکردن پروژه مرتبط پوشش مشترک دو بند',exact=True).click();form=page.get_by_role('dialog')
 form.get_by_label('حوزه پروژه شناخت سازمان، دامنه و ذینفعان',exact=True).check()
 expand_summary(form,'ارتباط دقیق با الزامات و کنترل‌ها')
 form.get_by_label('ارتباط پروژه A.5.2',exact=True).check()
 form.get_by_role('button',name='ذخیره پروژه',exact=True).click();expect(form).to_have_count(0)
 coverage(4,1,4);page.reload();dashboard();coverage(4,1,4)
 assert page.locator('[data-v14-action-row]').count()==4
 # Main dashboard links, all modules and the earlier implementation drilldown remain usable.
 main('داشبورد مدیریتی')
 for link in page.locator('.ds-quick a').all():
  target=link.get_attribute('href');assert target and page.locator('[id="'+target[1:]+'"]').count()==1,target
 for name in ['الزامات استاندارد','کنترل‌های Annex A','اقدامات اصلاحی','Risk Treatment Plan','روش ارزیابی','مدیریت ریسک','تداوم کسب‌وکار','پشتیبانی سایت','داشبورد مدیریتی']:
  main(name);assert page.locator('aside>nav>button.active').count()==1
 page.locator('[data-v15-implementation-stat="4"]').click();expect(page.locator('[data-v15-implementation-list]')).to_be_visible()
 page.get_by_role('button',name='بستن فهرست وضعیت پیاده‌سازی',exact=True).click()
 ctx.set_offline(True)
 page.get_by_label('پوسته سایت',exact=True).select_option('dark');mode('compliance','all');mode('implementation','all')
 capture(radar(),'compliance-all-dark.png');capture(impl(),'implementation-all-dark.png')
 dashboard();coverage(4,1,4);capture(page.locator('[data-v16-coverage-chart]'),'coverage-full-dark.png')
 page.set_viewport_size({'width':390,'height':844});main('داشبورد مدیریتی');mode('compliance','all');mode('implementation','all')
 assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 capture(radar(),'compliance-all-mobile.png');capture(impl(),'implementation-all-mobile.png')
 radar().locator('[data-compliance-group]').first.click();capture(page.locator('[data-v16-radar-list]'),'radar-list-mobile.png')
 assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 page.get_by_role('button',name='بستن فهرست حوزه رادار',exact=True).click()
 dashboard();coverage(4,1,4);assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 capture(page.locator('[data-v16-coverage-chart]'),'coverage-mobile.png')
 # Zero baseline is displayed as unavailable, not fabricated 100% coverage.
 page.evaluate("""()=>{const reg=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default')),prefix='didban-project:default:'+reg.activeId+':';const rows=JSON.parse(localStorage.getItem(prefix+'didban-isms-offline-v1'));for(const row of Object.values(rows))row.compliance=0;localStorage.setItem(prefix+'didban-isms-offline-v1',JSON.stringify(rows));}""")
 ctx.set_offline(False);page.reload();dashboard();coverage(0,1,0);ctx.set_offline(True)
 assert not errors,errors
 assert all(url.split('#')[0]==args.url for url in requests),requests
 (art/'result.json').write_text(json.dumps({'result':'PASS','errors':errors,'requests':requests,'catalog':123,'compliance_modes':{'clause':30,'control':93,'all':123},'implementation_modes':{'clause':8,'control':10,'all':10},'coverage_example':{'required':4,'projects':1,'covered':2,'percent':50}},indent=2))
 print('PASS 4needs/1project/2covered=50%, live edits/completion/scope overlap/persistence, traceable item audit/project links, zero baseline, all navigation, both themes/mobile/offline with no JS errors or external requests.',flush=True)
 browser.close()
