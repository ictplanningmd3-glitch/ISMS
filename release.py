#!/usr/bin/env python3
"""Create the offline distribution; no deployment or runtime installation."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse, hashlib, shutil
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args()
out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
guide='''<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>دیدبان امنیت ۱۲ — راهنمای شروع</title><style>body{font-family:Tahoma,sans-serif;line-height:2;background:#F6F8FC;color:#0F172A;max-width:850px;margin:50px auto;padding:25px}main{background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;padding:32px}a{display:inline-block;padding:12px 18px;border-radius:7px;background:#2563EB;color:white;text-decoration:none;margin:8px}p{color:#475569}h1{font-size:25px}small{font-size:13px}</style><main><h1>دیدبان امنیت — نسخهٔ ۱۲ آفلاین</h1><p>پس از استخراج ZIP، برنامه را با مرورگر باز کنید. اینترنت، نصب یا سرور لازم نیست.</p><a href="Didban_Amniat_Offline.html">بازکردن دیدبان امنیت</a><a href="Didban_Amniat_Offline_Fresh.html">بازکردن نسخهٔ شروع مستقل</a><p>داده‌ها در مرورگر ذخیره می‌شوند؛ خود فایل HTML با ثبت اطلاعات تغییر نمی‌کند. برای انتقال و نگهداری اطلاعات از «پشتیبانی سایت» پشتیبان JSON بگیرید. ساختارهای سنگین RTP و BCMS نسخهٔ ۷ جایگزین شده‌اند و داده‌های آنها مهاجرت داده نمی‌شوند.</p><p>نسخهٔ ۱۲: اقدامات اصلاحی دارای گسترهٔ سرفصل‌ها، گروه‌های A/B/C، نمودار وضعیت و پیشرفت و بودجهٔ جمع‌شونده است. گزینهٔ نقطه قوت (Good Point) نیز به ممیزی و گزارش‌ها افزوده شده است.</p><p>هر ماژول RTP و BCMS فقط سه زیرمنو دارد. در داشبورد BCMS روی نام طرح کلیک کنید؛ نمودار اختصاصی در صفحهٔ خود طرح قرار دارد. ثبت روزانهٔ RTP مستقیماً در سلول‌های جدول انجام می‌شود. پیشرفت اجرایی ۱۰۰٪ با اثربخشی و اختتام موفق یکسان نیست.</p><p>راهنمای کامل در «راهنمای اجرا.txt» و مستندات پوشه docs قرار دارد. از پروژه فعال مرتب پشتیبان JSON بگیرید.</p><small>پس از استخراج، فقط فایل HTML را باز کنید؛ نصب، اینترنت و اجرای کدهای پوشهٔ Source لازم نیست.</small></main></html>'''
(ROOT/'START_HERE.html').write_text(guide)
(out/'Didban_Amniat_Offline.html').write_bytes((ROOT/'Didban_Amniat_Offline.html').read_bytes())
(out/'راهنمای اجرا.txt').write_text((ROOT/'docs/USER-GUIDE.md').read_text())
zipname='Didban_Amniat_Offline_v12.zip'
with ZipFile(out/zipname,'w',ZIP_DEFLATED,compresslevel=9) as z:
 for name in ['Didban_Amniat_Offline.html','Didban_Amniat_Offline_Fresh.html','START_HERE.html','README.md']:
  z.write(ROOT/name,name)
 z.writestr('راهنمای اجرا.txt',(ROOT/'docs/USER-GUIDE.md').read_text())
 for folder in ['docs','assets']:
  for f in sorted((ROOT/folder).rglob('*')):
   if f.is_file():z.write(f,str(f.relative_to(ROOT)))
 for name in ['build.py','release.py','package.json','package-lock.json']:
  if (ROOT/name).exists():z.write(ROOT/name,'Source/'+name)
 for folder in ['src','tests','assets']:
  for f in sorted((ROOT/folder).rglob('*')):
   if f.is_file() and '__pycache__' not in f.parts:z.write(f,'Source/'+str(f.relative_to(ROOT)))
 z.writestr('Source/README.md','Development source. Run npm ci, npm run build, npm test. No build is required to use the HTMLs at the root of the ZIP.\n')
for filename in ['Didban_Amniat_Offline.zip','Didban_ISMS_Offline.zip']:shutil.copyfile(out/zipname,ROOT/filename)
checksums=[]
for f in sorted(out.iterdir()):
 if f.is_file() and f.name!='SHA256SUMS.txt':checksums.append(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name)
(out/'SHA256SUMS.txt').write_text('\n'.join(checksums)+'\n')
with ZipFile(out/zipname) as z:
 assert z.testzip() is None
 assert z.read('Didban_Amniat_Offline.html')==(ROOT/'Didban_Amniat_Offline.html').read_bytes()
print('Validated release:',str(out/zipname),(out/zipname).stat().st_size,'bytes')
