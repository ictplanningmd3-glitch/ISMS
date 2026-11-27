"""Report-only integration. No storage keys, record formats or domain calculations change."""
from pathlib import Path

def integrate(base):
 def replace(a,b):
  nonlocal base
  if base.count(a)!=1:raise RuntimeError('v20 report anchor: '+a[:90]+' count='+str(base.count(a)))
  base=base.replace(a,b,1)
 def between(start,end,value):
  nonlocal base
  a=base.index(start);b=base.index(end,a);base=base[:a]+value+'\n'+base[b:]
 between('function DSDescription(', 'function DSFindingRows(', 'function DSDescription(item,a){return V20Description(item,a)}')
 between('function dsReportTables(', 'function DSFill(', 'function dsReportTables(data,projects,risk,meta){return V20AuditTables(data,meta)}')
 between('async function dsWord(', 'function DSSafeName(', 'async function dsWord(data,projects,risk,meta){return V20DownloadAuditWord(data,meta)}')
 between('function dsPrint(', 'function V13StandardGroups(', 'function dsPrint(data,projects,risk,meta){return V20PrintAudit(data,meta)}')
 replace("const risk=drRead();if(risk.loadError)throw Error(risk.loadError);if(type==='word')await dsWord(assessments,projects,risk,valid);else if(type==='excel')await dsExcel(assessments,projects,risk,valid);else dsPrint(assessments,projects,risk,valid)","if(type==='word')await dsWord(assessments,[],null,valid);else if(type==='excel')await dsExcel(assessments,[],null,valid);else if(type==='html')V20DownloadAuditHTML(assessments,valid);else dsPrint(assessments,[],null,valid)")
 replace("DH(V18CorrectiveReports,{projects,data:assessments,meta,embedded:true}),",'')
 replace("DH('button',{type:'submit',value:'excel',disabled:!!busy},'دریافت Excel (.xlsx)'),", "DH('button',{type:'submit',value:'excel',disabled:!!busy},'دریافت Excel (.xlsx)'),DH('button',{type:'submit',value:'html',disabled:!!busy},'دریافت گزارش HTML'),")
 replace('گزارش Word با قالب پیوست شما ساخته می‌شود. ستون «بررسی‌کننده» نام ممیز هر بند یا نام ممیز این فرم و ستون «یافته ممیزی» وضعیت انطباق است. شواهد و مشاهدات در شرح یافته درج می‌شوند. مشخصات برای همین پروژه ذخیره می‌شوند.', 'این گزارش فقط ممیزی الزامات و Annex A است. شرح یافته فقط شامل فیلدهای پرشده است؛ یافته ممیزی با رنگ‌بندی نرم‌افزار نمایش داده می‌شود. خروجی HTML آفلاین، نمودارها، منو و جستجو دارد. گزارش اقدامات اصلاحی در بخش مستقل خودش در دسترس است.')
 return base
