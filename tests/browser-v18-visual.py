"""Offline v18 visual QA: audit palette, uniform compliance table and brand marks."""
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import argparse, json, os

parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://127.0.0.1:8778/Didban_Amniat_Offline.html')
parser.add_argument('--artifacts',default='/tmp/didban-v18-qa/visual')
args=parser.parse_args();art=Path(args.artifacts);art.mkdir(parents=True,exist_ok=True)
taxonomy=json.loads(Path('src/taxonomy-v13.json').read_text())
groups=[dict(g,id='clause:'+g['id'],kind='clause') for g in taxonomy['clauses']]+[dict(g,id='annex:'+g['id'],kind='control',itemIds=g['controls']) for g in taxonomy['groups']]
ids=[id for g in groups for id in g['itemIds']]
order=[5,0,4,3,1,2,6]
palette={5:'#168B78',0:'#4FAE66',4:'#3C91CF',3:'#D6A13D',1:'#E87945',2:'#C83E50'}
tokens={5:'good-point',0:'conformity',4:'improvement',3:'observation',1:'minor',2:'major'}
states=[5,0,4,3,1,2,None]
audits={id:dict(id=id,status=i%5,compliance=states[i%7],applicable=id not in ['A.5.36','A.5.37'],reason='' if id not in ['A.5.36','A.5.37'] else 'خارج از دامنهٔ آزمون',documents='شواهد '+id,observations='نتیجهٔ آزمون '+id,owner='مسئول آزمون',action='',due='2027-12-01',reviewer='ممیز آزمون',correctiveAction='',previousCompliance='',updated='2026-11-07T08:00:00Z') for i,id in enumerate(ids)}
audits['A.5.16']['compliance']=5
digits=str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩','01234567890123456789')
def number(text):return int(text.translate(digits).replace(',','').replace('٬','').strip())
def rgb(hex):return 'rgb('+', '.join(str(int(hex[i:i+2],16)) for i in (1,3,5))+')'
def expected_counts(item_ids):return {code:sum(audits[id]['applicable'] and (audits[id]['compliance'] if audits[id]['compliance'] is not None else 6)==code for id in item_ids) for code in order}

with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=os.environ.get('DIDBAN_CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 ctx=browser.new_context(viewport={'width':1536,'height':1050},accept_downloads=True)
 page=ctx.new_page();errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:requests.append(r.url))
 page.goto(args.url)
 assert page.locator('meta[name="didban-version"]').get_attribute('content')=='18'
 page.evaluate("""rows=>{const reg=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default')),prefix='didban-project:default:'+reg.activeId+':';localStorage.setItem(prefix+'didban-isms-offline-v1',JSON.stringify(rows));}""",audits)
 page.reload();ctx.set_offline(True)
 def main(name):page.locator('aside nav>button').filter(has_text=name).click()
 def capture(locator,name):
  style=page.add_style_tag(content='body .shell>main>header,body .toast{visibility:hidden!important}')
  locator.screenshot(path=str(art/name));style.evaluate('e=>e.remove()')
 def close_audit():page.get_by_role('dialog').get_by_role('button',name='بستن',exact=True).click();expect(page.get_by_role('dialog')).to_have_count(0)
 def css_tokens(theme):
  expected={'light':['#DC2626','#FACC15','#14B8A6','#16A34A','#C4B5FD','#CBD5E1'],'dark':['#F87171','#FACC15','#2DD4BF','#4ADE80','#C4B5FD','#CBD5E1']}[theme]
  names=['none','planned','partial','implemented','effective','unknown']
  values=page.evaluate("names=>names.map(name=>getComputedStyle(document.documentElement).getPropertyValue('--impl-'+name).trim().toUpperCase())",names)
  assert values==expected,(theme,values)
  generic=page.evaluate("()=>Object.fromEntries(['success','critical','info'].map(name=>[name,getComputedStyle(document.documentElement).getPropertyValue('--'+name).trim().toUpperCase()]))")
  assert generic==({'success':'#15803D','critical':'#DC2626','info':'#2563EB'} if theme=='light' else {'success':'#4ADE80','critical':'#F87171','info':'#60A5FA'}),generic
  for code,token in tokens.items():
   value=page.evaluate("name=>getComputedStyle(document.documentElement).getPropertyValue('--audit-'+name).trim().toUpperCase()",token)
   assert value==palette[code],(code,value)
 def table():
  page.mouse.move(1,1)
  root=page.locator('.v10-compliance-table');expect(root).to_have_count(1)
  assert root.locator('[data-v13-compliance-group]').count()==18
  headers=root.locator('thead [data-compliance-column]')
  assert headers.evaluate_all('xs=>xs.map(x=>+x.dataset.complianceColumn)')==order
  widths=headers.evaluate_all('xs=>xs.map(x=>x.getBoundingClientRect().width)')
  assert max(widths)-min(widths)<1,(widths,'numeric header widths differ')
  for g in groups:
   row=root.locator('[data-v13-compliance-group="'+g['id']+'"]');cells=row.locator('[data-compliance-column]');expected=expected_counts(g['itemIds'])
   assert cells.evaluate_all('xs=>xs.map(x=>+x.dataset.complianceColumn)')==order
   for cell,code in zip(cells.all(),order):
    assert number(cell.inner_text())==expected[code],(g['id'],code,cell.inner_text(),expected[code])
    assert cell.locator('strong').evaluate('e=>+getComputedStyle(e).fontWeight')>=600
   cell_widths=cells.evaluate_all('xs=>xs.map(x=>x.getBoundingClientRect().width)')
   assert max(cell_widths)-min(cell_widths)<1,cell_widths
  totals=root.locator('tfoot [data-compliance-column]')
  assert totals.count()==7
  expected=expected_counts(ids)
  for cell,code in zip(totals.all(),order):assert number(cell.inner_text())==expected[code],(code,cell.inner_text(),expected[code])
  assert headers.evaluate_all('xs=>xs.every(e=>e.scrollWidth<=e.clientWidth+1)'), 'headers overflow'
  backgrounds=root.locator('[data-v13-compliance-group]').first.locator('[data-compliance-column]').evaluate_all('xs=>xs.map(x=>getComputedStyle(x).backgroundColor)')
  assert len(set(backgrounds))==7,backgrounds
  assert all(backgrounds[i]!=rgb(palette[code]) for i,code in enumerate(order) if code in palette),'table cells must use a pale tint'
  for color,code in zip(backgrounds,order):
   expected=page.evaluate("fill=>{const e=document.createElement('span');e.style.backgroundColor='color-mix(in srgb,'+fill+' 7%,var(--surface))';document.body.append(e);const result=getComputedStyle(e).backgroundColor;e.remove();return result;}",palette.get(code,'var(--audit-unknown)'))
   assert color==expected,(code,color,expected)
  return root
 def badge_colors(required=None):
  seen=set()
  for badge in page.locator('[data-audit-status]').all():
   raw=badge.get_attribute('data-audit-status')
   if raw and raw.isdigit() and int(raw) in palette:
    code=int(raw);seen.add(code)
    assert badge.evaluate('e=>getComputedStyle(e,"::before").backgroundColor')==rgb(palette[code])
  if required:assert set(required)<=seen,(required,seen)
 def summary_contrast():
  values=page.locator('.v10-compliance-dashboard .dc-summary>article').evaluate_all('''xs=>xs.map(e=>{const num=e.querySelector('strong'),parse=s=>{if(s.startsWith('color(srgb'))return s.match(/[\\d.]+/g).slice(0,3).map(Number);return s.match(/[\\d.]+/g).slice(0,3).map(n=>+n/255);},lum=rgb=>{const a=rgb.map(c=>c<=.04045?c/12.92:((c+.055)/1.055)**2.4);return a[0]*.2126+a[1]*.7152+a[2]*.0722;},a=lum(parse(getComputedStyle(e).backgroundColor)),b=lum(parse(getComputedStyle(num).color));return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);})''')
  assert all(v>=4.5 for v in values),values
 def radar():
  for mode,n,total in [('clause',8,30),('control',10,93),('all',10,123)]:
   page.get_by_label('دامنه رادار انطباق',exact=True).select_option(mode)
   root=page.locator('[data-v16-radar-mode]');assert root.locator('[data-standard-dot]').count()==total
   assert root.locator('[data-compliance-divider]').count()==n
   for dot in root.locator('[data-standard-dot]').all():
    id=dot.get_attribute('data-standard-dot');code=audits[id]['compliance']
    if code is not None:
     actual=dot.evaluate('e=>getComputedStyle(e).fill')
     assert actual==rgb(palette[code]),(id,code,actual,rgb(palette[code]),dot.get_attribute('fill'))
   for legend,code in zip(root.locator('.v9-radar-legend>span').all(),order):
    if code in palette:assert legend.locator('i').evaluate('e=>getComputedStyle(e).backgroundColor')==rgb(palette[code])
  page.get_by_label('دامنه رادار انطباق',exact=True).select_option('control')
 def audit_chart():
  for kind in ['control','clause']:
   page.get_by_label('دامنه توزیع نتایج ممیزی',exact=True).select_option(kind)
   for segment in page.locator('[data-v14-audit-series]').all():
    code=int(segment.get_attribute('data-v14-audit-series'))
    assert segment.evaluate('e=>getComputedStyle(e).backgroundColor')==rgb(palette[code])
  for legend in page.locator('[data-v14-audit-legend]').all():
   code=int(legend.get_attribute('data-v14-audit-legend'))
   assert legend.locator('i').evaluate('e=>getComputedStyle(e).backgroundColor')==rgb(palette[code])
 def marks():
  assert page.locator('[data-v18-brand-mark="sidebar"]').count()==1
  assert page.locator('[data-v18-brand-mark="banner"]').count()==1
  all_ids=page.locator('[data-v18-brand-mark] [id]').evaluate_all('xs=>xs.map(x=>x.id)')
  assert len(set(all_ids))==len(all_ids)
  for mark in page.locator('[data-v18-brand-mark]').all():
   box=mark.bounding_box();assert box and box['width']>40 and box['height']>40
   assert mark.locator('path').count()>=4 and mark.locator('circle').count()>=2
  assert page.locator('.ds-banner-art').count()==1
  assert 'دیدبان امنیت' in page.locator('.ds-brand').inner_text()
 for theme in ['light','dark']:
  page.get_by_label('پوسته سایت',exact=True).select_option(theme)
  css_tokens(theme);radar();audit_chart();root=table();marks();badge_colors(palette);summary_contrast()
  capture(page.locator('.v10-compliance-dashboard'),'compliance-table-'+theme+'.png')
  capture(page.locator('[data-v16-radar-mode]'),'compliance-radar-'+theme+'.png')
  capture(page.locator('.ds-brand'),'brand-sidebar-'+theme+'.png')
  capture(page.locator('.ds-audit-banner'),'brand-banner-'+theme+'.png')
  # Native selectors remain plain even when Good Point is selected.
  dot=page.locator('[data-standard-dot="A.5.16"]');dot.focus();dot.press('Enter');dialog=page.get_by_role('dialog')
  assert dialog.locator('[data-v17-text-en]').inner_text()=='The full life cycle of identities shall be managed.'
  current=dialog.get_by_label('انطباق با استاندارد',exact=True);assert current.input_value()=='5'
  previous=dialog.get_by_label('وضعیت انطباق در ممیزی قبلی',exact=True)
  for selector in [current,previous]:
   assert selector.locator('option').evaluate_all('xs=>xs.every(e=>!e.getAttribute("style")&&!e.getAttribute("class"))')
   backgrounds=selector.locator('option').evaluate_all('xs=>xs.map(e=>getComputedStyle(e).backgroundColor)')
   assert len(set(backgrounds))==1,backgrounds
  capture(dialog.locator('[data-v17-annex-reference]'),'annex-reference-'+theme+'.png');close_audit()
 print('PASS exact six-color audit palette in both themes, all radar modes/stacks, plain selectors, 18-domain uniform table and truthful totals, preserved implementation/alert colors and Annex A text',flush=True)
 # Corrective-action stacks and badges use the same palette.
 main('اقدامات اصلاحی');page.locator('[data-v13-corrective-tab="gaps"]:visible').first.click()
 for segment in page.locator('[data-v14-finding-status]').all():
  code=int(segment.get_attribute('data-v14-finding-status'))
  assert segment.evaluate('e=>getComputedStyle(e).backgroundColor')==rgb(palette[code])
 badge_colors([4,3,1,2])
 main('داشبورد مدیریتی');page.emulate_media(reduced_motion='reduce');marks()
 assert page.locator('[data-v18-brand-mark] *').evaluate_all('xs=>xs.every(e=>getComputedStyle(e).animationName==="none")')
 page.set_viewport_size({'width':390,'height':844})
 for theme in ['light','dark']:
  page.get_by_label('پوسته سایت',exact=True).select_option(theme);root=table();marks()
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),theme
  wrapper=root.locator('..');assert wrapper.evaluate('e=>e.scrollWidth>=e.clientWidth')
  capture(wrapper,'compliance-table-mobile-'+theme+'.png')
  assert wrapper.evaluate('e=>{e.scrollLeft=-e.scrollWidth;return e.scrollLeft<0;}'),'RTL table must scroll to all status columns'
  capture(wrapper,'compliance-table-mobile-scrolled-'+theme+'.png')
  capture(page.locator('.ds-brand'),'brand-sidebar-mobile-'+theme+'.png')
  capture(page.locator('.ds-audit-banner'),'brand-banner-mobile-'+theme+'.png')
 for link in page.locator('.ds-quick a').all():
  target=link.get_attribute('href');assert target and page.locator('[id="'+target[1:]+'"]').count()==1,target
 assert page.locator('.ds-quick a').count()==7
 for name in ['الزامات استاندارد','کنترل‌های Annex A','اقدامات اصلاحی','Risk Treatment Plan','روش ارزیابی','مدیریت ریسک','تداوم کسب‌وکار','پشتیبانی سایت','داشبورد مدیریتی']:
  main(name);assert page.locator('aside>nav>button.active').count()==1
 assert not errors,errors
 assert all(url.split('#')[0]==args.url for url in requests),requests
 (art/'result.json').write_text(json.dumps({'result':'PASS','palette':palette,'groups':18,'eligible':121,'order':order,'errors':errors,'requests':requests},ensure_ascii=False,indent=2))
 print('PASS consistent corrective stacks/badges, both brand marks, reduced motion, mobile light/dark, 9 menus/7 bookmarks and offline operation with no JavaScript errors or external requests.',flush=True)
 browser.close()
