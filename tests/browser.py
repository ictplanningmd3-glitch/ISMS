"""Functional browser QA. Run with Python Playwright and a local Chromium.
The optional URL argument points at a static server serving the repository.
"""
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import json, sys, os

ROOT=Path(__file__).resolve().parents[1]
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765/'
ART=Path(os.environ.get('DIDBAN_TEST_ARTIFACTS','/workspace/work/browser-tests'));ART.mkdir(parents=True,exist_ok=True)
checks=[]
def check(name,condition=True):
    assert condition,name
    checks.append(name)
    print('PASS',name,flush=True)

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('DIDBAN_CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    context=browser.new_context(viewport={'width':1536,'height':1050},accept_downloads=True)
    page=context.new_page();errors=[];external=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:external.append(r.url) if not r.url.startswith((URL,'data:','blob:')) else None)
    page.goto(URL+'Didban_Amniat_Offline.html');expect(page.locator('aside nav>button')).to_have_count(9)
    check('nine main menus in requested order',page.locator('aside nav>button').all_text_contents()[0]=='داشبورد مدیریتی')
    def main(text):page.locator('aside nav>button').filter(has_text=text).click()
    def tab(text):page.locator('aside .v7-subnav button').filter(has_text=text).click()
    def modal():return page.get_by_role('dialog').first
    def new():page.get_by_role('button',name='+ ثبت جدید',exact=True).click()
    def field(label,value):modal().get_by_label(label,exact=True).fill(str(value))
    def select(label,value):modal().get_by_label(label,exact=True).select_option(value=value)
    def ref(label,title):modal().get_by_label(label,exact=True).select_option(label=title)
    def multi(label,title):modal().get_by_role('group',name=label,exact=True).get_by_label(title,exact=True).check()
    def save(reason=None):
        if reason:field('دلیل تغییر',reason)
        modal().get_by_role('button',name='ذخیره اطلاعات',exact=True).click()
        expect(page.get_by_role('dialog')).to_have_count(0)
    def record(title):page.get_by_role('row').filter(has=page.get_by_text(title,exact=True)).get_by_role('button',name='جزئیات / ویرایش',exact=True).click()
    def db(t):return page.evaluate('''t=>{const r=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default'));return JSON.parse(localStorage.getItem('didban-project:default:'+r.activeId+':didban-'+t+'-independent-v1'))}''',t)
    # Seed an existing v6 workspace, with an assessment and an unrelated second project.
    page.evaluate('''()=>{const r=JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default'));const id=r.activeId;r.projects[0].organization='سازمان آزمون نسخه ۶';r.projects[0].title='دوره ممیزی موجود';r.projects.push({id:'second',organization:'سازمان دوم',title:'پروژه دوم',created:new Date().toISOString()});localStorage.setItem('didban-security-workspaces-v1:default',JSON.stringify(r));localStorage.setItem('didban-project:default:'+id+':didban-isms-offline-v1',JSON.stringify({'A.5.1':{id:'A.5.1',status:3,compliance:0,applicable:true,reason:'کاربرد قبلی',documents:'شواهد نسخه شش حفظ شود',observations:'مشاهده قبلی',owner:'مسئول قبلی',action:'اقدام قبلی',due:'2026-12-01',updated:'2026-10-01T10:00:00Z'}}));}''')
    page.reload();expect(page.get_by_text('سازمان آزمون نسخه ۶',exact=True).first).to_be_visible()
    main('کنترل‌های Annex A');page.get_by_placeholder('جستجوی عنوان، شناسه یا مسئول…').fill('A.5.1')
    page.get_by_role('row').filter(has=page.get_by_text('A.5.1',exact=True)).first.click()
    check('v6 audit evidence preserved','شواهد نسخه شش حفظ شود' in page.locator('textarea').evaluate_all('(els)=>els.map(e=>e.value)'))
    page.locator('.overlay .paneltitle button').first.click()
    main('Risk Treatment Plan');check('RTP has 17 independent submenus',page.locator('aside .v7-subnav button').count()==17)
    tab('دفتر ثبت ریسک');new();field('عنوان','ریسک آزمایش');field('مالک / مسئول','مالک ریسک آزمایش');field('احتمال',4);field('شدت اثر',5);field('امتیاز مبنای ریسک',20);field('ریسک هدف',5);field('آستانه پذیرش',5);field('ریسک باقیمانده ارزیابی‌شده',5);field('تاریخ ارزیابی مجدد','2026-10-22');field('شواهد ارزیابی مجدد','گزارش ارزیابی مجدد پس از کنترل');save()
    tab('برنامه‌های مواجهه');new();field('عنوان','RTP آزمایش');field('مالک / مسئول','مالک ریسک آزمایش');multi('ریسک‌های مرتبط','ریسک آزمایش');select('وضعیت','approved');modal().get_by_role('button',name='ذخیره اطلاعات',exact=True).click();expect(modal().get_by_role('alert')).to_contain_text('مجوز تصویب');check('approval blocked until local identity configured');select('وضعیت','draft');save()
    page.get_by_role('button',name='کاربر محلی · مدیر سیستم').click();field('نام کاربری','مدیر آزمایش');field('گذرواژه','offline-test-password-2026');modal().get_by_role('button',name='ایجاد حساب',exact=True).click();expect(page.get_by_role('dialog')).to_have_count(0)
    record('RTP آزمایش');select('وضعیت','approved');save('تصویب برنامه توسط مدیر مجاز');check('RTP approved with timestamp',bool(db('rtp')['records']['plans'][0]['approval']['at']))
    tab('پروژه‌ها و پورتفوی');new();field('عنوان','پروژه آزمایش');field('تاریخ شروع','2026-09-01');field('تاریخ هدف پایان','2026-12-01');field('بودجه مصوب',1000);field('هزینه واقعی (یا جمع دفتر هزینه)',0);multi('RTPهای مرتبط','RTP آزمایش');multi('ریسک‌های مرتبط','ریسک آزمایش');save()
    tab('ساختار شکست کار');new();field('عنوان','فعالیت اول');ref('پروژه','پروژه آزمایش');field('تاریخ شروع','2026-09-01');field('تاریخ هدف پایان','2026-10-01');field('پیشرفت (٪)',100);field('وزن نسبی فعالیت در سطح والد',3);field('شواهد / مرجع مستند','تحویل انجام شد');select('وضعیت','completed');save()
    new();field('عنوان','فعالیت دوم');ref('پروژه','پروژه آزمایش');field('تاریخ شروع','2026-10-01');field('تاریخ هدف پایان','2026-11-01');field('وزن نسبی فعالیت در سطح والد',1);save()
    tab('داشبورد RTP');expect(page.locator('.v7-kpi').filter(has_text='پیشرفت وزنی')).to_contain_text('۷۵');check('weighted project progress displayed as 75 percent')
    tab('کنترل‌ها و اثربخشی');new();field('عنوان','کنترل آزمایش');multi('پروژه‌های اجرایی','پروژه آزمایش');multi('ریسک‌های تحت پوشش','ریسک آزمایش');select('وضعیت','implemented');save();expect(page.locator('table')).to_contain_text('تأیید نشده');check('implementation does not certify effectiveness')
    tab('آزمون اثربخشی');new();field('عنوان','آزمون کنترل');ref('کنترل','کنترل آزمایش');field('تاریخ آزمون','2026-10-22');field('ارزیاب','ارزیاب آزمون');field('شواهد / مرجع مستند','گزارش واقعی آزمون');select('نتیجه آزمون','effective');select('وضعیت','approved');save();tab('کنترل‌ها و اثربخشی');expect(page.locator('.v7-table')).to_contain_text('اثربخش');check('approved effectiveness test changes control result')
    tab('پروژه‌ها و پورتفوی');record('پروژه آزمایش');field('تاریخ هدف پایان','2027-01-01');field('دلیل تغییر','تلاش تغییر مستقیم');modal().get_by_role('button',name='ذخیره اطلاعات',exact=True).click();expect(modal().get_by_role('alert')).to_contain_text('Baseline');modal().get_by_role('button',name='بستن',exact=True).click();check('baseline cannot be silently edited')
    tab('داشبورد راداری');page.get_by_role('button',name='ثبت Snapshot / مبنای تاریخی').click();check('historical radar snapshot persisted',len(db('rtp')['snapshots'])==1)
    for label in ['Project Performance Radar','Risk Treatment Effectiveness Radar']:expect(page.get_by_role('heading',name=label,exact=True)).to_be_visible()
    check('separate performance and risk effectiveness radars present')
    # Exercise all BIA wizard steps and real persistence.
    main('تداوم کسب‌وکار (BCMS)');check('BCMS has independent submenus',page.locator('aside .v7-subnav button').count()==14)
    tab('محصولات و خدمات');new();field('عنوان','خدمت پرداخت');save()
    tab('فعالیت‌ها و فرایندها');new();field('عنوان','پردازش پرداخت');ref('محصول / خدمت','خدمت پرداخت');field('ظرفیت عادی',100000);field('حداقل عملیاتی',40000);field('حداقل قراردادی',50000);field('حداقل قانونی / ایمنی',30000);modal().get_by_label('فعالیت بحرانی',exact=True).check();save()
    tab('ارزیابی‌های BIA');new();field('عنوان','BIA پرداخت');field('مالک / مسئول','مالک فعالیت');field('ارزیاب','ارزیاب تداوم');field('دلیل تغییر BIA','ارزیابی اولیه');
    def step(n):modal().locator('.v7-wizard-steps button').nth(n).click()
    step(1);ref('فعالیت','پردازش پرداخت');step(4);modal().get_by_label('عملیاتی 240 دقیقه',exact=True).select_option('3');modal().get_by_label('عملیاتی 480 دقیقه',exact=True).select_option('4');step(5);expect(modal().locator('.v7-kpi').filter(has_text='MTPD')).to_contain_text('8 ساعت');check('BIA computes first threshold crossing at 8 hours')
    step(6);expect(modal().locator('.v7-kpi').filter(has_text='MBCO')).to_contain_text('۵۰');field('MBCO تأییدشده (٪)',50);check('MBCO selects highest minimum capacity (50 percent)');step(7);field('RTO مصوب (دقیقه)',240);step(8);field('RPO مورد نیاز کسب‌وکار (دقیقه)',5);field('RPO مصوب (دقیقه)',5);field('RPO قابل تحققِ اعتبارسنجی‌شده (دقیقه)',4)
    step(11)
    for label,value in [('زمان تشخیص (دقیقه)',10),('زمان تصمیم (دقیقه)',10),('زمان فعال‌سازی (دقیقه)',10),('زمان بازیابی فنی (دقیقه)',120),('زمان اعتبارسنجی (دقیقه)',10),('زمان تثبیت MBCO (دقیقه)',20)]:field(label,value)
    modal().get_by_role('button',name='ذخیره پیش‌نویس این مرحله').click();expect(modal().get_by_role('status')).to_contain_text('ذخیره شد');check('BIA draft saves from any wizard step')
    step(13);select('وضعیت','approved');field('شواهد / مرجع مستند','مصاحبه مالک و گزارش اثر در زمان');field('بازنگری بعدی','2027-10-22');field('دلیل تغییر BIA','تصویب اهداف و روش');modal().get_by_role('button',name='ثبت نهایی وضعیت BIA').click();expect(page.get_by_role('dialog')).to_have_count(0);check('BIA approved and persisted independently')
    tab('برنامه‌های BCP');new();field('عنوان','BCP پرداخت');multi('فعالیت‌های تحت پوشش','پردازش پرداخت');field('بازنگری بعدی','2027-10-22');select('وضعیت','approved');save()
    tab('تمرین‌ها و آزمون‌ها');new();field('عنوان','آزمون بازیابی پرداخت');ref('فعالیت','پردازش پرداخت');ref('BCP مرتبط','BCP پرداخت');field('تاریخ واقعی','2026-10-22');field('زمان تا تحقق MBCO (دقیقه)',180);field('از دست‌رفتن واقعی داده (دقیقه)',4);field('ظرفیت محقق‌شده (٪)',60);field('شواهد / مرجع مستند','گزارش بازیابی مستند');select('وضعیت','completed');save();check('exercise retains its target snapshot',db('bcms')['records']['exercises'][0]['targetSnapshot']['rto']==240)
    tab('داشبورد BCMS');expect(page.get_by_role('row').filter(has=page.get_by_text('پردازش پرداخت',exact=True)).last).to_contain_text('آماده');check('passing exercise plus approvals yields ready activity')
    tab('وابستگی‌ها');new();field('عنوان','پایگاه داده');ref('فعالیت والد','پردازش پرداخت');field('RTO وابستگی (دقیقه)',240);field('زمان تحویل (دقیقه)',60);save();tab('داشبورد BCMS');expect(page.get_by_role('row').filter(has=page.get_by_text('پردازش پرداخت',exact=True)).last).to_contain_text('شکاف بحرانی');check('dependency handover gap downgrades readiness')
    # Backup, reload, export formats, light/dark, mobile, legacy reports.
    tab('گزارش‌ها');
    with page.expect_download() as download:page.get_by_role('button',name='خروجی Excel',exact=True).click()
    download.value.save_as(ART/'bcms.xlsx');check('BCMS Excel export produced', (ART/'bcms.xlsx').stat().st_size>1000)
    page.get_by_label('پوسته سایت').select_option('dark');page.reload();expect(page.locator('html')).to_have_attribute('data-theme','dark');check('dark theme persists after reload')
    main('پشتیبانی سایت')
    with page.expect_download() as download:page.get_by_role('button').filter(has_text='دریافت JSON پروژه فعال').click()
    download.value.save_as(ART/'project.json');backup=json.loads((ART/'project.json').read_text());check('full project backup includes both new modules and v6 audit data',bool(backup['rtp']['records']['plans'] and backup['bcms']['records']['bias'] and backup['assessments']['A.5.1']['documents']=='شواهد نسخه شش حفظ شود'))
    page.get_by_label('بارگذاری نسخه JSON',exact=True).set_input_files(str(ART/'project.json'))
    expect(page.get_by_role('dialog')).to_be_visible();expect(page.get_by_label('نحوه بارگذاری پروژه')).to_have_value('new')
    page.get_by_label('نام سازمان واردشده').fill('سازمان بازیابی');page.get_by_label('عنوان پروژه واردشده',exact=True).fill('پروژه بازیابی')
    page.get_by_role('button',name='واردکردن پروژه',exact=True).click();expect(page.locator('.workspace')).to_contain_text('سازمان بازیابی')
    check('full backup imports into separate project without overwriting original',len(page.evaluate("JSON.parse(localStorage.getItem('didban-security-workspaces-v1:default')).projects"))==3 and db('rtp')['records']==backup['rtp']['records'] and db('bcms')['records']==backup['bcms']['records'])
    main('پشتیبانی سایت');page.locator('.ds-project-list article').filter(has_text='پروژه دوم').get_by_role('button',name='بازکردن پروژه').click();expect(page.locator('.workspace')).to_contain_text('سازمان دوم')
    main('Risk Treatment Plan');expect(page.locator('.v7-kpi').filter(has_text='ریسک‌های فعال')).to_contain_text('۰');check('new modules are isolated across audit workspaces',db('rtp') is None)
    main('پشتیبانی سایت');page.locator('.ds-project-list article').filter(has_text='پروژه بازیابی').get_by_role('button',name='بازکردن پروژه').click();expect(page.locator('.workspace')).to_contain_text('سازمان بازیابی')
    main('داشبورد مدیریتی');check('main dashboard excludes RTP and BCMS records',page.locator('[data-module]').count()==0 and page.get_by_text('پروژه آزمایش',exact=True).count()==0 and page.get_by_text('پردازش پرداخت',exact=True).count()==0)
    # All existing main screens remain reachable.
    for label in ['الزامات استاندارد','کنترل‌های Annex A','اقدامات اصلاحی','روش ارزیابی','مدیریت ریسک','پشتیبانی سایت']:main(label)
    main('Risk Treatment Plan');tab('داشبورد راداری');page.screenshot(path=str(ART/'rtp-radar-dark.png'),full_page=True)
    page.get_by_label('پوسته سایت').select_option('light');main('داشبورد مدیریتی');page.screenshot(path=str(ART/'dashboard-light.png'),full_page=True)
    main('تداوم کسب‌وکار (BCMS)');page.get_by_role('button',name='مشاهده Demo مستقل',exact=True).click();page.screenshot(path=str(ART/'bcms-demo-light.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844});main('Risk Treatment Plan');page.screenshot(path=str(ART/'rtp-mobile.png'),full_page=True);check('mobile viewport has no document-level horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1'))
    page.set_viewport_size({'width':1536,'height':1050});main('داشبورد مدیریتی');page.locator('.v7-concept-card').first.hover();check('hover highlights corresponding radar domain',page.locator('.v7-scope g.selected').count()==1)
    check('no browser JavaScript errors',not errors);check('no external resource requests',not external)
    context.close();browser.close()
    (ART/'results.json').write_text(json.dumps({'checks':checks,'errors':errors,'externalRequests':external},ensure_ascii=False,indent=2))
    print('TOTAL',len(checks),'passed',flush=True)
