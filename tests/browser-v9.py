"""Focused regression checks for compliance radar (including Good Point), themes, and create dialog."""
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import argparse, math, json, os
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8766/Didban_Amniat_Offline.html');p.add_argument('--artifacts',default='/tmp/didban-v9-qa');args=p.parse_args();art=Path(args.artifacts);art.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.environ.get('DIDBAN_CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage']);ctx=b.new_context(viewport={'width':1536,'height':1050},accept_downloads=True);page=ctx.new_page();errors=[];requests=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url));page.goto(args.url)
 def main(name):page.locator('aside nav>button').filter(has_text=name).click()
 def tab(i):page.locator('aside .v7-subnav button').nth(i).click()
 def modal():return page.get_by_role('dialog',name='افزودن پروژه RTP',exact=True)
 def raw():return page.evaluate("()=>{const key=Object.keys(localStorage).find(k=>k.endsWith(':didban-rtp-independent-v2'));return key?JSON.parse(localStorage.getItem(key)):null;}")
 assert page.locator('[data-compliance-group]').count()==10
 assert page.locator('[data-compliance-divider]').count()==10
 assert page.locator('[data-standard-dot]').count()==93
 assert page.locator('[data-compliance="unknown"]').count()==93
 assert page.locator('.v9-radar-legend>span').count()==7
 # Each compliance value is deliberately paired with a conflicting implementation status.
 ids=['A.5.1','A.5.2','A.5.3','A.5.4','A.5.5','A.5.6','A.5.8'];values=[2,1,4,3,0,5,None]
 page.evaluate("({ids,values})=>{const r=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default'));const key='didban-project:default:'+r.activeId+':didban-isms-offline-v1';localStorage.setItem(key,JSON.stringify(Object.fromEntries(ids.map((id,i)=>[id,{id,applicable:true,status:4-i%5,compliance:values[i],documents:'',observations:'',reason:'',owner:'',action:'',due:''}]))));}",{'ids':ids,'values':values});page.reload()
 known=[];colors=[]
 for i,id in enumerate(ids):
  dot=page.locator('[data-standard-dot="'+id+'"]');assert dot.get_attribute('data-compliance-rank')==('outside' if values[i] is None else str(i));xy=dot.evaluate("e=>[+e.getAttribute('cx'),+e.getAttribute('cy'),getComputedStyle(e).fill]");r=math.hypot(xy[0]-260,xy[1]-260);assert r>190 if values[i] is None else r<190;known.append(r);colors.append(xy[2])
 assert known[:-1]==sorted(known[:-1]);assert len(set(colors))==len(values)
 expected_counts=['۱']*(len(values)-1)+[str(93-(len(values)-1)).translate(str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹'))]
 assert [page.locator('.v9-radar-legend>span b').nth(i).inner_text() for i in range(len(values))]==expected_counts
 # Changing only implementation cannot move an audit compliance point.
 before=page.locator('[data-standard-dot="A.5.1"]').get_attribute('cy');page.evaluate("()=>{const key=Object.keys(localStorage).find(k=>k.endsWith(':didban-isms-offline-v1'));const data=JSON.parse(localStorage.getItem(key));data['A.5.1'].status=0;localStorage.setItem(key,JSON.stringify(data));}");page.reload();assert page.locator('[data-standard-dot="A.5.1"]').get_attribute('cy')==before
 page.get_by_role('button',name='توقف پویانمایی',exact=True).click();assert page.locator('.v8-sweep').evaluate("e=>getComputedStyle(e).animationPlayState")=='paused'
 page.locator('[data-compliance-group]').first.hover();assert 'active' in page.locator('[data-standard-dot="A.5.1"]').get_attribute('class')
 page.locator('[data-standard-dot="A.5.1"]').focus();page.keyboard.press('Enter');expect(page.get_by_role('dialog')).to_have_count(1);page.get_by_role('dialog').get_by_role('button',name='بستن',exact=True).click()
 # Exact foundation tokens and runtime component colors in both themes.
 palettes={'light':{'--bg':'#F6F8FC','--sidebar':'#FFFFFF','--surface':'#FFFFFF','--primary':'#2563EB'},'dark':{'--bg':'#0B1220','--sidebar':'#101A2B','--surface':'#151F30','--primary':'#60A5FA'}}
 for theme,palette in palettes.items():
  page.get_by_label('پوسته سایت',exact=True).select_option(theme);actual=page.evaluate("keys=>Object.fromEntries(keys.map(k=>[k,getComputedStyle(document.documentElement).getPropertyValue(k).trim().toUpperCase()]))",list(palette));assert actual==palette,(theme,actual)
  page.locator('.v8-concept').screenshot(path=str(art/('radar-'+theme+'.png')))
  page.reload();assert page.locator('html').get_attribute('data-theme')==theme
 page.emulate_media(color_scheme='dark');page.get_by_label('پوسته سایت',exact=True).select_option('system');assert page.locator('html').get_attribute('data-theme')=='dark';page.emulate_media(color_scheme='light');expect(page.locator('html')).to_have_attribute('data-theme','light');page.get_by_label('پوسته سایت',exact=True).select_option('light')
 main('Risk Treatment Plan');tab(1);page.get_by_role('button',name='افزودن پروژه',exact=True).click();expect(modal()).to_be_visible();assert not raw() or len(raw()['records']['projects'])==0
 form=modal();assert form.locator('form>.v8-fields>.v8-field').count()==14;form.get_by_label('عنوان پروژه',exact=True).fill('لغو شود');form.get_by_role('button',name='انصراف',exact=True).click();assert not raw() or len(raw()['records']['projects'])==0
 page.get_by_role('button',name='افزودن پروژه',exact=True).click();page.keyboard.press('Escape');expect(modal()).to_have_count(0);assert not raw() or len(raw()['records']['projects'])==0
 page.get_by_role('button',name='افزودن پروژه',exact=True).click();form=modal()
 for label,value in [('عنوان پروژه','آزمون ثبت در پنجره'),('شرح کوتاه ریسک','توقف سرویس'),('شرح کوتاه تهدید','قطعی'),('شرح کوتاه آسیب‌پذیری','تک نقطهٔ خرابی'),('مالک ریسک','مالک'),('مسئول اجرا','مجری'),('تاریخ شروع شمسی','۱۴۰۵/۰۱/۰۱'),('موعد پایان','۱۴۰۵/۱۲/۰۱'),('درصد پیشرفت','۲۵'),('آخرین وضعیت و تصمیمات','در انتظار خرید'),('بودجه مصوب','۱٬۰۰۰')]:form.get_by_label(label,exact=True).fill(value)
 form.get_by_label('استراتژی مواجهه',exact=True).select_option('mitigate');form.get_by_label('آخرین وضعیت',exact=True).select_option('active');form.screenshot(path=str(art/'project-create-light.png'));form.get_by_role('button',name='ثبت پروژه',exact=True).click();expect(modal()).to_have_count(0);p=raw()['records']['projects'][0];assert p['progress']==25 and p['budget']==1000 and p['start']=='2026-03-21' and p['title']=='آزمون ثبت در پنجره'
 expect(page.get_by_label('عنوان پروژه ردیف 1',exact=True)).to_have_value('آزمون ثبت در پنجره');page.get_by_role('button',name='افزودن فعالیت',exact=True).click();assert page.get_by_role('table',name='فعالیت‌های پروژه',exact=True).is_visible()
 page.get_by_label('عنوان فعالیت ردیف 1',exact=True).fill('فعالیت همان گرید');page.get_by_label('عنوان فعالیت ردیف 1',exact=True).press('Tab');assert len(raw()['records']['activities'])==1
 # Validation keeps the dialog open and does not append a partial project.
 page.get_by_role('button',name='افزودن پروژه',exact=True).click();form=modal();form.get_by_label('عنوان پروژه',exact=True).fill('شناسهٔ تکراری');form.get_by_label('شناسه پروژه',exact=True).fill(p['code']);form.get_by_role('button',name='ثبت پروژه',exact=True).click();assert form.get_by_role('alert').is_visible();assert len(raw()['records']['projects'])==1
 form.get_by_label('شناسه پروژه',exact=True).fill('RTP-2');form.get_by_label('درصد پیشرفت',exact=True).fill('101');form.get_by_role('button',name='ثبت پروژه',exact=True).click();assert form.get_by_role('alert').is_visible();assert len(raw()['records']['projects'])==1
 form.get_by_role('button',name='انصراف',exact=True).click();page.get_by_label('پوسته سایت',exact=True).select_option('dark');page.get_by_role('button',name='افزودن پروژه',exact=True).click();modal().screenshot(path=str(art/'project-create-dark.png'));page.keyboard.press('Escape')
 tab(2);page.get_by_role('button',name='تعریف پروژه',exact=True).click();expect(modal()).to_be_visible();page.keyboard.press('Escape');assert len(raw()['records']['projects'])==1
 page.reload();main('Risk Treatment Plan');tab(1);expect(page.get_by_label('عنوان پروژه ردیف 1',exact=True)).to_have_value('آزمون ثبت در پنجره')
 # Start the dialog and edit while disconnected, including on a mobile viewport.
 ctx.set_offline(True);page.set_viewport_size({'width':390,'height':844});page.get_by_role('button',name='افزودن پروژه',exact=True).click();modal().get_by_label('عنوان پروژه',exact=True).fill('آفلاین موبایل');assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');page.screenshot(path=str(art/'project-create-mobile.png'));modal().get_by_role('button',name='ثبت پروژه',exact=True).click();assert len(raw()['records']['projects'])==2
 main('داشبورد مدیریتی');page.emulate_media(reduced_motion='reduce');assert page.locator('.v8-sweep').evaluate("e=>getComputedStyle(e).animationName")=='none';page.locator('.v8-concept').screenshot(path=str(art/'radar-mobile.png'));assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');assert not errors,errors;assert all(url==args.url for url in requests),requests
 (art/'result.json').write_text(json.dumps({'result':'PASS','errors':errors,'requests':requests,'compliance_colors':colors,'radii':known},indent=2));print('PASS v9: ten sectors, 93 compliance dots, correct layers/colors and gray outside, independent implementation, linked hover/click, Light/Dark/System persistence, add-project fields/save/cancel/errors, unchanged dual grids, offline/mobile/reduced-motion; no errors or external requests.');b.close()
