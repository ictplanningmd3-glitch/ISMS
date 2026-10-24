"""Dashboard/audit/BCMS recovery integration QA; development-only dependencies."""
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import argparse, json, os
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8767/Didban_Amniat_Offline.html');p.add_argument('--artifacts',default='/tmp/didban-v10-qa');args=p.parse_args();art=Path(args.artifacts);art.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.environ.get('DIDBAN_CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage']);ctx=b.new_context(viewport={'width':1536,'height':1100},accept_downloads=True);page=ctx.new_page();errors=[];requests=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url));page.goto(args.url)
 def main(name):page.locator('aside nav>button').filter(has_text=name).click()
 def tab(i):page.locator('aside .v7-subnav button').nth(i).click()
 def raw(kind):return page.evaluate("kind=>{const key=Object.keys(localStorage).find(k=>k.endsWith(':didban-'+kind+'-independent-v2'));return key?JSON.parse(localStorage.getItem(key)):null;}",kind)
 page.evaluate("()=>{const reg=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default')),key='didban-project:default:'+reg.activeId+':didban-isms-offline-v1',ids=['A.5.1','A.5.2','A.5.3','A.5.4','A.5.5'];localStorage.setItem(key,JSON.stringify(Object.fromEntries(ids.map((id,i)=>[id,{id,status:i,compliance:[2,1,4,3,0][i],applicable:true,documents:'',observations:'',owner:'',action:'',due:'',reason:''}]))));}");page.reload()
 assert page.get_by_text('نمودار عنکبوتی',exact=True).count()==0
 assert page.locator('.v10-implementation-radar-figure svg').bounding_box()['height']>350
 assert page.locator('[data-implementation-slice]').count()==6
 assert page.locator('[data-implementation-slice="0"]').get_attribute('d').startswith('M160 160 L')
 assert page.locator('.v10-implementation-legend b').all_text_contents()==['۱','۱','۱','۱','۱','۱۱۸']
 palette=page.locator('[data-implementation-slice]').evaluate_all('els=>els.map(e=>getComputedStyle(e).fill)');assert len(set(palette))==6,palette
 assert palette==['rgb(220, 38, 38)','rgb(250, 204, 21)','rgb(20, 184, 166)','rgb(22, 163, 74)','rgb(196, 181, 253)','rgb(203, 213, 225)'],palette
 assert page.locator('[data-compliance-domain]').count()==66
 assert page.locator('.v10-compliance-dashboard svg').count()==1
 colors=page.locator('.v10-compliance-table thead [data-compliance-column]').evaluate_all('els=>els.map(e=>getComputedStyle(e).backgroundColor)');assert len(set(colors))==6,colors
 assert page.locator('.v10-compliance-table tbody td strong').first.evaluate('e=>+getComputedStyle(e).fontWeight')>=700
 assert page.locator('.ds-banner-art path[d^="M300 39"]').count()==1
 assert 'gradient' in page.locator('.ds-audit-banner').evaluate('e=>getComputedStyle(e).backgroundImage');assert page.locator('.ds-banner-pause svg').count()==1
 page.locator('.ds-audit-banner').screenshot(path=str(art/'banner-light.png'));page.locator('.charts').first.screenshot(path=str(art/'implementation-charts-light.png'));page.locator('.v10-compliance-dashboard').screenshot(path=str(art/'compliance-bars-light.png'))
 # Implementation badges across the register use the same separate five hues.
 main('کنترل‌های Annex A')
 for i in range(5):assert page.locator('[data-implementation="'+str(i)+'"]').count()>=1
 # Audit reviewer belongs to this audit, outside the prior-audit fields, for both item types.
 for id,name in [('A.5.1','ممیز کنترل'),('4.1','ممیز الزام')]:
  main('داشبورد مدیریتی')
  if id.startswith('A.'):page.locator('[data-standard-dot="'+id+'"]').focus();page.keyboard.press('Enter')
  else:
   main('الزامات استاندارد');page.get_by_placeholder('جستجوی عنوان، شناسه یا مسئول…').fill(id);page.get_by_role('row').filter(has=page.get_by_text(id,exact=True)).click()
  dialog=page.get_by_role('dialog');dialog.get_by_text('اطلاعات ممیزی قبلی (در صورت وجود)',exact=True).click();assert dialog.locator('.ds-audit-extra label').count()==2;assert dialog.locator('.ds-audit-extra input[aria-label="نام ممیز"]').count()==0
  assert dialog.get_by_label('نام ممیز',exact=True).evaluate("e=>!!(e.compareDocumentPosition(document.querySelector('select[aria-label=\"انطباق با استاندارد\"]'))&Node.DOCUMENT_POSITION_FOLLOWING)")
  dialog.get_by_label('نام ممیز',exact=True).fill(name);dialog.get_by_label('وضعیت انطباق در ممیزی قبلی',exact=True).select_option('1');dialog.get_by_role('button',name='ذخیره ارزیابی',exact=True).click();expect(page.get_by_role('dialog')).to_have_count(0)
 print('PASS dashboard charts, global implementation palette, compliance columns and current/previous auditor fields',flush=True)
 main('تداوم کسب‌وکار');page.get_by_role('button',name='ارزیابی جدید',exact=True).click()
 for label,value in [('نام خدمت / فعالیت','پرداخت آنلاین'),('واحد سازمانی','مالی'),('مالک فعالیت','مالک پرداخت'),('ظرفیت عادی','100'),('حداقل ظرفیت قابل قبول','40'),('ظرفیت اضطراری فعلی (%)','50'),('RTO هدف','2'),('قابلیت فعلی RTO','1.5'),('RPO هدف','1'),('قابلیت فعلی RPO','0.5'),('WRT هدف برای بازگشت کامل','1'),('WRT قابلیت فعلی','1'),('سناریوی اصلی وقفه (KDS)','قطع مرکز داده'),('بازنگری بعدی','۱۴۰۶/۱۲/۰۱')]:page.get_by_label(label,exact=True).fill(value)
 for el in page.locator('.v8-impact tbody select').all():el.select_option('1')
 page.get_by_label('عملیاتی 8 ساعت',exact=True).select_option('4');page.get_by_label('وجود BCP',exact=True).select_option('yes');page.get_by_label('وضعیت برنامه',exact=True).select_option('approved');page.get_by_label('برنامه آزمون شده است',exact=True).check();page.get_by_label('تاریخ آخرین تمرین',exact=True).fill('۱۴۰۵/۰۸/۰۱');page.get_by_label('نتیجه اعلام‌شده',exact=True).select_option('pass')
 for label,value in [('زمان واقعی بازیابی','1'),('از دست رفتن واقعی داده','0.25'),('ظرفیت واقعی در تمرین (%)','50'),('WRT واقعی تمرین','0.5')]:page.get_by_label(label,exact=True).fill(value)
 expect(page.locator('.v8-badge').first).to_contain_text('آماده')
 page.get_by_label('WRT قابلیت فعلی',exact=True).fill('-1');expect(page.locator('.v8-badge').first).to_contain_text('بحرانی');assert raw('bcms')['records']['assessments'][0]['currentWrt']==60;page.get_by_label('WRT قابلیت فعلی',exact=True).fill('1');expect(page.locator('.v8-badge').first).to_contain_text('آماده')
 page.get_by_text('گام‌های واقعی بازیابی (اختیاری)',exact=True).click()
 for i,(minutes,capacity) in enumerate([(60,50),(75,80),(90,100)],1):
  page.get_by_role('button',name='افزودن گام واقعی',exact=True).click();page.get_by_label('عنوان گام بازیابی '+str(i),exact=True).fill('گام '+str(i));page.get_by_label('زمان گام بازیابی '+str(i),exact=True).fill(str(minutes));page.get_by_label('ظرفیت گام بازیابی '+str(i),exact=True).fill(str(capacity))
 expect(page.locator('.v8-badge').first).to_contain_text('آماده');record=raw('bcms')['records']['assessments'][0];assert len(record['recoverySteps'])==3
 chart=page.locator('[data-bcp-activity]');assert chart.count()==1;chart.get_by_label('منبع نمودار BCP '+record['code'],exact=True).select_option('actual');assert chart.locator('[data-bcp-curve="actual"]').count()==1
 assert chart.locator('[data-bcp-curve="actual"]').get_attribute('d').count(' V ')==3
 assert chart.locator('[data-bcp-mtpd]').get_attribute('data-bcp-mtpd')=='480'
 assert chart.locator('.v10-bcp-metrics tbody tr').count()==6
 chart.screenshot(path=str(art/'bcp-activity-actual.png'));page.get_by_role('button',name='بازگشت به فهرست',exact=True).click();page.get_by_role('button',name='تکثیر',exact=True).click();page.get_by_label('نام خدمت / فعالیت',exact=True).fill('ثبت سفارش');page.get_by_label('WRT قابلیت فعلی',exact=True).fill('7');expect(page.locator('.v8-badge').first).to_contain_text('بحرانی');page.get_by_role('button',name='بازگشت به فهرست',exact=True).click();tab(0)
 assert page.locator('.v10-bcp-gallery [data-bcp-activity]').count()==2
 problems=page.locator('.v10-bcp-problems');assert 'ثبت سفارش' in problems.inner_text();assert problems.get_by_role('button',name='پرداخت آنلاین',exact=True).count()==0
 assert 'MTPD' in problems.inner_text() or 'WRT' in problems.inner_text();page.locator('.v10-bcp-dashboard').screenshot(path=str(art/'bcp-dashboard-light.png'))
 # Live source switching, state persistence, mobile and offline.
 page.get_by_label('پوسته سایت',exact=True).select_option('dark');page.locator('.v10-bcp-gallery [data-bcp-activity]').first.screenshot(path=str(art/'bcp-dark.png'));page.reload();main('تداوم کسب‌وکار');assert page.locator('.v10-bcp-gallery [data-bcp-activity]').count()==2
 ctx.set_offline(True);page.set_viewport_size({'width':390,'height':844});page.locator('.v8-module>.v7-subnav button').first.click();assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');page.locator('.v10-bcp-gallery [data-bcp-activity]').first.screenshot(path=str(art/'bcp-mobile.png'))
 main('داشبورد مدیریتی');assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');page.locator('.ds-audit-banner').screenshot(path=str(art/'banner-mobile.png'));assert not errors,errors;assert all(r==args.url for r in requests),requests
 (art/'result.json').write_text(json.dumps({'result':'PASS','implementation_colors':palette,'errors':errors,'requests':requests},indent=2));print('PASS per-activity BCP staircase, RPO/RTO/WRT/MTPD metrics, real recovery steps, independent dashboard issue detection, dark/mobile/offline; no browser errors or external requests.');b.close()
