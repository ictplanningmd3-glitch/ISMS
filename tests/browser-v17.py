"""Offline v17 QA: exact supplied Annex A controls and compact Persian translations."""
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import argparse, json, os

parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://127.0.0.1:8777/Didban_Amniat_Offline.html')
parser.add_argument('--artifacts',default='/tmp/didban-v17-qa')
args=parser.parse_args();art=Path(args.artifacts);art.mkdir(parents=True,exist_ok=True)
catalog=json.loads(Path('src/annex-controls-v17.json').read_text())
controls={row['id']:row for row in catalog['controls']}
expected=[f'A.{domain}.{n}' for domain,count in [(5,37),(6,8),(7,14),(8,34)] for n in range(1,count+1)]
assert list(controls)==expected and len(controls)==93
assert controls['A.5.16']['titleEn']=='Identity management'
assert controls['A.5.16']['textEn']=='The full life cycle of identities shall be managed.'

with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=os.environ.get('DIDBAN_CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 ctx=browser.new_context(viewport={'width':1536,'height':1050},accept_downloads=True)
 page=ctx.new_page();errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:requests.append(r.url))
 page.goto(args.url)
 assert page.locator('meta[name="didban-version"]').get_attribute('content')=='17'
 assert page.locator('[data-standard-dot]').count()==93
 def main(name):page.locator('aside nav>button').filter(has_text=name).click()
 def dialog():return page.get_by_role('dialog')
 def close():dialog().get_by_role('button',name='بستن',exact=True).click();expect(dialog()).to_have_count(0)
 def open_dot(id):
  point=page.locator('[data-standard-dot="'+id+'"]');point.focus();point.press('Enter');expect(dialog()).to_be_visible()
 def raw(key):return page.evaluate("suffix=>{const k=Object.keys(localStorage).find(k=>k.endsWith(':'+suffix));return k?JSON.parse(localStorage.getItem(k)):null;}",key)
 def reference(id):
  row=controls[id];root=dialog();card=root.locator('[data-v17-annex-reference]')
  expect(card).to_have_count(1);expect(card).to_be_visible()
  assert card.get_attribute('data-v17-annex-reference')==id
  for hook,field in [('title-en','titleEn'),('title-fa','titleFa'),('text-en','textEn'),('text-fa','textFa')]:
   expect(root.locator('[data-v17-'+hook+']')).to_have_text(row[field])
  assert root.locator('#audit-title').count()==1
  assert root.locator('#audit-title').evaluate('e=>e.scrollWidth<=e.clientWidth+1'),id
  assert root.locator('[data-v17-title-en]').get_attribute('lang')=='en'
  assert root.locator('[data-v17-title-en]').get_attribute('dir')=='ltr'
  assert root.locator('[data-v17-title-fa]').get_attribute('lang')=='fa'
  assert root.locator('[data-v17-title-fa]').get_attribute('dir')=='rtl'
  assert card.locator('[data-v17-text-en]').evaluate('e=>e.closest("[lang]").lang')=='en'
  assert card.locator('[data-v17-text-fa]').evaluate('e=>e.closest("[lang]").lang')=='fa'
  assert card.locator('[data-v17-text-en]').evaluate('e=>getComputedStyle(e).direction')=='ltr'
  assert card.locator('[data-v17-text-fa]').evaluate('e=>getComputedStyle(e).direction')=='rtl'
  assert card.get_by_role('heading',name='Control',exact=True).count()==1
  caption=card.locator('[data-v17-source]').inner_text()
  assert 'ISO/IEC 27001:2022' in caption and 'Annex A' in caption and id in caption
  assert str(row['source']['printedPage']) in caption
  # Text is fully rendered, with wrapping and no line clamp or fixed-height clipping.
  assert card.locator('[data-v17-text-en],[data-v17-text-fa]').evaluate_all('xs=>xs.every(e=>{const s=getComputedStyle(e);return e.scrollHeight<=e.clientHeight+1&&e.scrollWidth<=e.clientWidth+1&&s.textOverflow!=="ellipsis"&&s.webkitLineClamp==="none"&&parseFloat(s.fontSize)>=10&&parseFloat(s.fontSize)<=12;})')
  assert card.locator('details').count()==0
  assert 'باید' in row['textFa'],id
  return card
 def capture(locator,name):
  style=page.add_style_tag(content='body .shell>main>header,body .toast{visibility:hidden!important}')
  locator.screenshot(path=str(art/name));style.evaluate('e=>e.remove()')
 # Every control opens via the actual native audit callback while the network is disconnected.
 ctx.set_offline(True)
 seen=[];max_height=0
 for id in expected:
  open_dot(id);card=reference(id);seen.append(id)
  max_height=max(max_height,card.bounding_box()['height'])
  if id in ['A.5.1','A.5.16','A.6.1','A.8.34']:capture(card,id.replace('.','-')+'-light.png')
  if id in ['A.5.21','A.5.31','A.5.36']:capture(dialog().locator('#audit-title'),id.replace('.','-')+'-title-light.png')
  close()
 assert max_height<320,max_height
 print('PASS all 93 control modals match exact supplied English and complete Persian translations; semantic direction, source pages and compact untruncated display',flush=True)
 # A small reference must not replace the independent auditor guidance or input fields.
 open_dot('A.5.16');reference('A.5.16')
 assert dialog().locator('.audit-guide').count()==1
 assert dialog().get_by_label('نام ممیز',exact=True).count()==1
 dialog().get_by_label('نام ممیز',exact=True).fill('ممیز متن کنترل')
 dialog().get_by_label('انطباق با استاندارد',exact=True).select_option('5')
 dialog().get_by_label('شواهد و مستندات بررسی‌شده',exact=True).fill('شواهد چرخهٔ عمر هویت')
 dialog().get_by_role('button',name='ذخیره ارزیابی',exact=True).click();expect(dialog()).to_have_count(0)
 saved=raw('didban-isms-offline-v1')['A.5.16'];assert saved['compliance']==5 and saved['reviewer']=='ممیز متن کنترل'
 assert 'textEn' not in saved and 'titleFa' not in saved
 open_dot('A.5.16');reference('A.5.16');close()
 # Clause forms retain their native header and do not acquire Annex A reference content.
 page.get_by_label('دامنه رادار انطباق',exact=True).select_option('clause')
 for id in ['4.1','10.2']:
  open_dot(id);expect(dialog().locator('[data-v17-annex-reference]')).to_have_count(0)
  expect(dialog().locator('[data-v17-title-en],[data-v17-title-fa]')).to_have_count(0)
  assert dialog().locator('#audit-title .english-title').count()==1
  assert dialog().get_by_label('انطباق با استاندارد',exact=True).count()==1
  close()
 # Group drilldown and previous implementation-list entry points display the same content.
 page.get_by_label('دامنه رادار انطباق',exact=True).select_option('all')
 page.locator('[data-compliance-group="standard:identity"]').click()
 page.locator('[data-v16-radar-item="A.5.16"]').click();reference('A.5.16');close()
 page.get_by_role('button',name='بستن فهرست حوزه رادار',exact=True).click()
 page.locator('[data-v15-implementation-stat="unknown"]').click()
 page.get_by_label('جستجوی فهرست پیاده‌سازی',exact=True).fill('A.8.34')
 page.get_by_role('button',name='بازکردن ممیزی A.8.34',exact=True).click();reference('A.8.34');close()
 page.get_by_role('button',name='بستن فهرست وضعیت پیاده‌سازی',exact=True).click()
 print('PASS unchanged clause forms, separate existing guidance, real audit save/reopen and both dashboard drilldown routes',flush=True)
 # Themes, long content, mobile stacking and print keep all reference text readable.
 page.get_by_label('پوسته سایت',exact=True).select_option('dark');open_dot('A.6.1');card=reference('A.6.1')
 capture(card,'long-control-dark.png');close()
 page.set_viewport_size({'width':390,'height':844});open_dot('A.6.1');card=reference('A.6.1')
 assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 boxes=card.locator('.v17-annex-reference-body>div').evaluate_all('xs=>xs.map(e=>({x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y,width:e.getBoundingClientRect().width}))')
 assert len(boxes)==2 and boxes[1]['y']>boxes[0]['y'] and abs(boxes[0]['x']-boxes[1]['x'])<2
 assert card.bounding_box()['height']<650
 capture(card,'long-control-mobile-dark.png');close()
 page.get_by_label('پوسته سایت',exact=True).select_option('light');open_dot('A.5.16');card=reference('A.5.16')
 capture(card,'identity-mobile-light.png')
 page.emulate_media(media='print');print_card=page.locator('.auditmodal [data-v17-annex-reference]')
 assert print_card.evaluate('e=>getComputedStyle(e).breakInside')=='avoid'
 assert print_card.locator('[data-v17-text-en]').text_content()==controls['A.5.16']['textEn']
 page.emulate_media(media='screen');close()
 # Existing links and menus remain active and point to actual on-page targets.
 for name in ['الزامات استاندارد','کنترل‌های Annex A','اقدامات اصلاحی','Risk Treatment Plan','روش ارزیابی','مدیریت ریسک','تداوم کسب‌وکار','پشتیبانی سایت','داشبورد مدیریتی']:
  main(name);assert page.locator('aside>nav>button.active').count()==1
 assert page.locator('.ds-quick a').count()==7
 for link in page.locator('.ds-quick a').all():
  href=link.get_attribute('href');assert href and href.startswith('#')
  assert page.locator('[id="'+href[1:]+'"]').count()==1,href
 assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
 assert not errors,errors
 assert all(url.split('#')[0]==args.url for url in requests),requests
 (art/'result.json').write_text(json.dumps({'result':'PASS','controls':len(seen),'ids':seen,'largest_desktop_reference_height':max_height,'errors':errors,'requests':requests},ensure_ascii=False,indent=2))
 print('PASS dark/light/mobile/print, 9 menus and 7 bookmarks; offline without external requests or JavaScript errors',flush=True)
 browser.close()
