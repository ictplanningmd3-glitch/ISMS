/* Offline corrective-action DOCX generation. No network or new runtime dependency. */
var V18CorrectiveWord=(()=>{
 const types=Object.freeze([
  {id:'executive',title:'گزارش مدیریتی',english:'Executive',description:'خلاصهٔ وضعیت، پوشش یافته‌ها، بودجه و شاخص‌های پروژه‌ها'},
  {id:'register',title:'فهرست تفصیلی اقدامات اصلاحی',english:'Register',description:'شناسنامه، ارتباط با استاندارد و شاخص‌های تمام پروژه‌های انتخاب‌شده'},
  {id:'project',title:'پروندهٔ یک پروژه',english:'Project',description:'جزئیات یک اقدام اصلاحی، شاخص‌ها، بودجه و یافته‌های مرتبط'},
  {id:'followup',title:'گزارش پیگیری و تأخیر',english:'Followup',description:'اقدامات تکمیل‌نشده، وضعیت سررسید، پیشرفت و شاخص‌های پیگیری'}
 ]);
 const states={planned:'برنامه‌ریزی شده',active:'در حال اجرا',blocked:'متوقف شده',completed:'تکمیل شده'},priorities={high:'زیاد',medium:'متوسط',low:'کم'};
 const validDate=value=>typeof value==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(value)&&Number.isFinite(Date.parse(value+'T12:00:00Z'))&&new Date(value+'T12:00:00Z').toISOString().slice(0,10)===value;
 const clean=value=>String(value??'').replace(/[\x00-\x08\x0b\x0c\x0e-\x1f]/g,'');
 const xml=value=>clean(value).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&apos;');
 const number=value=>Number(value).toLocaleString('fa-IR',{maximumFractionDigits:2});
 const nonempty=value=>value===null||value===undefined||value===''?'ثبت نشده':String(value);
 const indicators=p=>(Array.isArray(p.indicators)?p.indicators:[]).filter(v=>typeof v==='string'&&v.trim()).map(v=>v.trim());
 const group=p=>({1:'A',2:'B',3:'C'})[p.months]||'B';
 const days=(end,start)=>Math.floor((Date.parse(end+'T12:00:00Z')-Date.parse(start+'T12:00:00Z'))/86400000);
 function select(projects,options={},today){
  if(!types.some(t=>t.id===(options.type||'executive')))throw Error('نوع گزارش معتبر نیست.');
  const type=options.type||'executive';
  let rows=projects.filter(p=>(!options.status||options.status==='all'||p.status===options.status)&&(!options.group||options.group==='all'||group(p)===options.group));
  if(type==='followup')rows=rows.filter(p=>p.status!=='completed');
  if(options.overdueOnly)rows=rows.filter(p=>p.status!=='completed'&&validDate(p.due)&&p.due<today);
  if(type==='project'){
   if(!options.projectId)throw Error('پروژهٔ گزارش را انتخاب کنید.');
   rows=rows.filter(p=>p.id===options.projectId);
   if(rows.length!==1)throw Error('پروژهٔ انتخاب‌شده در محدودهٔ گزارش نیست.');
  }
  return [...rows].sort((a,b)=>{const aDate=validDate(a.due)?a.due:'9999-12-31',bDate=validDate(b.due)?b.due:'9999-12-31';return aDate.localeCompare(bDate)||String(a.title).localeCompare(String(b.title),'fa');});
 }
 function model(input){
  const {projects=[],data={},items=[],scopes=[],meta={},today,options={},correctiveEngine,budgetEngine}=input;
  if(!validDate(today))throw Error('تاریخ گزارش معتبر نیست.');
  if(!correctiveEngine?.metrics||!budgetEngine?.totals)throw Error('محاسبات اقدامات اصلاحی در دسترس نیست.');
  const type=options.type||'executive',selected=select(projects,options,today),metrics=correctiveEngine.metrics(items,data,selected,scopes,today);
  const itemById=new Map(items.map(item=>[item.id,item])),scopeById=new Map(scopes.map(scope=>[scope.id,scope]));
  const formatDate=value=>validDate(String(value||'').slice(0,10))?input.formatDate(String(value).slice(0,10)):'ثبت نشده';
  const details=selected.map(project=>{
   const linked=new Set((project.mappedIds||[]).filter(id=>itemById.has(id)));
   for(const scopeId of project.scopeIds||[])for(const id of scopeById.get(scopeId)?.itemIds||[])if(itemById.has(id))linked.add(id);
   const findings=metrics.rows.filter(row=>row.related.some(p=>p.id===project.id)).map(row=>({id:row.item.id,title:row.item.title,code:row.row.compliance,finding:input.findingNames?.[row.row.compliance]||'ثبت نشده',evidence:row.row.documents||'',observations:row.row.observations||''}));
   const dueState=project.status==='completed'?'تکمیل شده':!validDate(project.due)?'سررسید ثبت نشده':project.due<today?'مهلت گذشته — '+number(days(today,project.due))+' روز':project.due===today?'سررسید امروز':'مهلت آینده — '+number(days(project.due,today))+' روز';
   return {project,group:group(project),indicators:indicators(project),budget:budgetEngine.totals(project.budget),linkedItems:[...linked].map(id=>itemById.get(id)),selectedScopes:(project.scopeIds||[]).map(id=>scopeById.get(id)).filter(Boolean),findings,dueState};
  });
  const approved=details.filter(d=>d.budget.approved!==null),allocated=details.reduce((sum,d)=>sum+d.budget.allocated,0),approvedTotal=approved.reduce((sum,d)=>sum+d.budget.approved,0);
  const filterParts=type==='followup'?['فقط پروژه‌های تکمیل‌نشده']:(!options.status||options.status==='all')?['تمام وضعیت‌ها']:[];
  if(options.status&&options.status!=='all')filterParts.push('وضعیت: '+(states[options.status]||options.status));
  if(options.group&&options.group!=='all')filterParts.push('گروه زمانی: '+options.group);
  if(options.overdueOnly)filterParts.push('فقط سررسیدگذشته');
  if(type==='project')filterParts.push('یک پروژهٔ انتخاب‌شده');
  return {type,typeInfo:types.find(t=>t.id===type),today,meta:{organization:meta.organization||'نام سازمان ثبت نشده',reportNumber:meta.reportNumber||'',auditor:meta.auditor||meta.leadAuditor||'',title:meta.title||''},selected,details,metrics,formatDate,filterDescription:filterParts.join(' · '),statusCounts:Object.keys(states).map(status=>({status,title:states[status],count:selected.filter(p=>p.status===status).length})),groupCounts:['A','B','C'].map(id=>({id,count:selected.filter(p=>group(p)===id).length})),progress:selected.length?Math.round(selected.reduce((sum,p)=>sum+(Number(p.progress)||0),0)/selected.length):null,budget:{approvedCount:approved.length,approved:approvedTotal,allocated,remaining:approved.length?approvedTotal-allocated:null},indicatorCount:details.reduce((sum,d)=>sum+d.indicators.length,0),now:input.now||new Date().toISOString()};
 }
 function paragraph(text,style='Normal',opts={}){
  const textRuns=clean(text).split('\n').map((line,index)=>(index?'<w:br/>':'')+'<w:t xml:space="preserve">'+xml(line)+'</w:t>').join('');
  return '<w:p><w:pPr><w:pStyle w:val="'+style+'"/><w:bidi/><w:jc w:val="'+(opts.center?'center':'right')+'"/>'+(opts.keep?'<w:keepNext/>':'')+'</w:pPr><w:r><w:rPr><w:rtl/>'+(opts.bold?'<w:b/>':'')+'</w:rPr>'+textRuns+'</w:r></w:p>';
 }
 function table(rows,widths){
  if(!rows.length)return '';
  const columns=rows[0].length,sizes=widths||Array(columns).fill(Math.floor(9500/columns));
  const border=['top','left','bottom','right','insideH','insideV'].map(name=>'<w:'+name+' w:val="single" w:sz="4" w:color="CBD5E1"/>').join('');
  return '<w:tbl><w:tblPr><w:bidiVisual/><w:tblW w:w="9500" w:type="dxa"/><w:tblLayout w:type="fixed"/><w:tblBorders>'+border+'</w:tblBorders><w:tblCellMar><w:top w:w="90" w:type="dxa"/><w:left w:w="100" w:type="dxa"/><w:bottom w:w="90" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>'+sizes.map(width=>'<w:gridCol w:w="'+width+'"/>').join('')+'</w:tblGrid>'+rows.map((row,index)=>'<w:tr><w:trPr>'+(index===0?'<w:tblHeader/>':'')+'<w:cantSplit/></w:trPr>'+row.map((cell,k)=>'<w:tc><w:tcPr>'+(cell&&typeof cell==='object'&&cell.color?'<w:tcBorders><w:right w:val="single" w:sz="24" w:color="'+cell.color+'"/></w:tcBorders>':'')+'<w:tcW w:w="'+sizes[k]+'" w:type="dxa"/><w:vAlign w:val="center"/>'+(index===0?'<w:shd w:fill="E2E8F0"/>':'')+'</w:tcPr>'+paragraph(cell&&typeof cell==='object'?cell.text:cell,'TableText',{bold:index===0})+'</w:tc>').join('')+'</w:tr>').join('')+'</w:tbl>'+paragraph('');
 }
 const auditColors={5:'168B78',0:'4FAE66',4:'3C91CF',3:'D6A13D',1:'E87945',2:'C83E50'};
 const heading=(text,level=1)=>paragraph(text,'Heading'+level,{keep:true});
 function indicatorBlock(detail){
  return heading('شاخص‌های اقدام اصلاحی',2)+(detail.indicators.length?table([['ردیف','تعریف شاخص'],...detail.indicators.map((text,index)=>[number(index+1),text])],[700,8800]):paragraph('شاخصی برای این پروژه ثبت نشده است.'));
 }
 function detailBlock(detail,m,full){
  const p=detail.project;
  let out=heading(p.title,1)+table([['مشخصه','مقدار'],['شناسه پروژه',p.id],['هدف',nonempty(p.goal)],['مسئول اجرا',nonempty(p.owner)],['آخرین وضعیت',states[p.status]||nonempty(p.status)],['درصد پیشرفت',number(p.progress)+'٪'],['اولویت',priorities[p.priority]||nonempty(p.priority)],['گروه زمانی',detail.group+' — '+number(p.months)+' ماهه'],['تاریخ شروع',m.formatDate(p.start)],['موعد پایان',m.formatDate(p.due)],['وضعیت مهلت',detail.dueState],['منابع مورد نیاز',nonempty(p.resources)],['یادداشت و آخرین توضیحات ثبت‌شده',nonempty(p.notes)]],[2600,6900]);
  out+=indicatorBlock(detail);
  out+=heading('ارتباط با استاندارد',2);
  out+=detail.selectedScopes.length?paragraph('سرفصل‌های انتخاب‌شده: '+detail.selectedScopes.map(scope=>scope.title).join('، ')):paragraph('سرفصل مستقلی انتخاب نشده است.');
  out+=detail.linkedItems.length?table([['الزام / کنترل','عنوان'],...detail.linkedItems.map(item=>[item.id,item.title])],[1700,7800]):paragraph('بند یا کنترل معتبری به این پروژه مرتبط نشده است.');
  out+=heading('بودجهٔ اقدام اصلاحی',2)+table([['مشخصه','مبلغ / تاریخ'],['بودجه مصوب (ریال)',detail.budget.approved===null?'ثبت نشده':number(detail.budget.approved)],['تاریخ تصویب بودجه',m.formatDate(p.budget?.approvedDate)],['جمع تخصیص (ریال)',number(detail.budget.allocated)],['ماندهٔ بودجه (ریال)',detail.budget.remaining===null?'قابل محاسبه نیست':number(detail.budget.remaining)]],[3500,6000]);
  if(full){
   const allocations=p.budget?.allocations||[];
   out+=heading('ردیف‌های تخصیص بودجه',2)+(allocations.length?table([['ردیف','مبلغ تخصیص (ریال)','تاریخ تخصیص'],...allocations.map((row,index)=>[number(index+1),number(row.amount),m.formatDate(row.date)])],[700,4400,4400]):paragraph('تخصیصی ثبت نشده است.'));
   out+=heading('یافته‌های ممیزی نیازمند اقدام مرتبط',2)+(detail.findings.length?detail.findings.map(finding=>heading(finding.id+' — '+finding.title,2)+table([['مشخصه','مقدار'],['نتیجهٔ ممیزی',{text:finding.finding,color:auditColors[finding.code]}],['شواهد ثبت‌شده',nonempty(finding.evidence)],['مشاهدات ثبت‌شده',nonempty(finding.observations)]],[2600,6900])).join(''):paragraph('یافتهٔ ممیزی نیازمند اقدام در ارتباط‌های این پروژه ثبت نشده است.'));
  }
  return out;
 }
 function documentXml(m){
  let body=paragraph(m.typeInfo.title,'Title',{center:true})+paragraph('اقدامات اصلاحی و پروژه‌های بهبود','Subtitle',{center:true})+paragraph(m.meta.organization,'Subtitle',{center:true});
  body+=table([['مشخصهٔ گزارش','مقدار'],['تاریخ تهیه',m.formatDate(m.today)],['شمارهٔ گزارش',nonempty(m.meta.reportNumber)],['تهیه‌کننده / ممیز',nonempty(m.meta.auditor)],['دامنهٔ انتخاب پروژه‌ها',m.filterDescription],['تعداد پروژه‌های گزارش',number(m.selected.length)]],[3000,6500]);
  body+=paragraph('این گزارش از داده‌های ثبت‌شدهٔ پروژهٔ فعال تهیه شده است. نبود اطلاعات با «ثبت نشده» مشخص می‌شود؛ وجود پروژهٔ مرتبط، تأیید رفع یافته یا اثربخشی نیست.');
  if(!m.selected.length)body+=heading('نتیجهٔ انتخاب',1)+paragraph('پروژه‌ای با معیارهای انتخاب‌شده ثبت نشده است.');
  if(m.type==='executive'){
   body+=heading('خلاصهٔ مدیریتی',1)+table([['شاخص','مقدار'],['کل اقدامات اصلاحی گزارش',number(m.selected.length)],...m.statusCounts.map(row=>[row.title,number(row.count)]),['میانگین پیشرفت',m.progress===null?'فاقد داده':number(m.progress)+'٪'],['پروژه‌های مهلت‌گذشته',number(m.metrics.overdueProjects.length)],['شاخص‌های تعریف‌شده',number(m.indicatorCount)],['بودجه مصوب ثبت‌شده (ریال)',m.budget.approvedCount?number(m.budget.approved):'ثبت نشده'],['جمع تخصیص ثبت‌شده (ریال)',number(m.budget.allocated)]],[6200,3300]);
   body+=heading('پوشش یافته‌های نیازمند اقدام',1)+table([['مبنای پوشش','تعداد / درصد'],['تمام بندها و کنترل‌های نیازمند اقدام در دفتر ممیزی فعال',number(m.metrics.coverage.required)],['موارد دارای پروژهٔ مرتبط در محدودهٔ این گزارش',number(m.metrics.coverage.covered)],['موارد بدون پروژهٔ مرتبط در محدودهٔ این گزارش',number(m.metrics.coverage.uncovered)],['درصد پوشش',m.metrics.coverage.percentage===null?'فاقد مبنای محاسبه':number(m.metrics.coverage.percentage)+'٪']],[6200,3300]);
   body+=paragraph('مخرج پوشش، تمام یافته‌های قابل اعمال با نتیجهٔ مشاهده، توصیه برای بهبود یا عدم انطباق جزیی/کلی در دفتر ممیزی فعال است. در صورت فیلتر پروژه‌ها، فقط ارتباط‌های پروژه‌های همین گزارش در صورت کسر شمرده می‌شوند؛ هر بند یا کنترل یک‌بار محاسبه می‌شود.');
   body+=heading('تقسیم‌بندی زمانی پروژه‌ها',1)+table([['گروه','افق زمانی','تعداد'],...m.groupCounts.map((row,index)=>[row.id,number(index+1)+' ماهه',number(row.count)])],[2200,4000,3300]);
   if(m.details.length)body+=heading('مرور وضعیت و شاخص‌های پروژه‌ها',1)+table([['پروژه / مسئول','وضعیت و پیشرفت','شاخص‌های تعریف‌شده'],...m.details.map(d=>[d.project.title+'\n'+nonempty(d.project.owner),(states[d.project.status]||d.project.status)+' — '+number(d.project.progress)+'٪',d.indicators.length?d.indicators.map((text,index)=>number(index+1)+'. '+text).join('\n'):'ثبت نشده'])],[3000,2200,4300]);
  }else if(m.type==='followup'){
   body+=heading('وضعیت پیگیری',1)+paragraph('این گزارش فقط پروژه‌های تکمیل‌نشده را نشان می‌دهد؛ درصد پیشرفت ۱۰۰ به‌تنهایی وضعیت تکمیل‌شده محسوب نمی‌شود.');
   if(m.details.length)body+=table([['پروژه / مسئول','وضعیت / پیشرفت','سررسید / مهلت'],...m.details.map(d=>[d.project.title+'\n'+nonempty(d.project.owner),(states[d.project.status]||d.project.status)+' — '+number(d.project.progress)+'٪',m.formatDate(d.project.due)+'\n'+d.dueState])],[3500,2600,3400]);
   for(const detail of m.details)body+=heading(detail.project.title,1)+paragraph('آخرین توضیحات ثبت‌شده: '+nonempty(detail.project.notes))+indicatorBlock(detail)+paragraph('بندها و کنترل‌های مرتبط: '+(detail.linkedItems.map(item=>item.id).join('، ')||'ثبت نشده'));
  }else for(const detail of m.details)body+=detailBlock(detail,m,m.type==='project');
  body+=paragraph('پایان گزارش — دیدبان امنیت','Caption');
  return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>'+body+'<w:sectPr><w:footerReference w:type="default" r:id="rIdFooter"/><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1050" w:right="1200" w:bottom="1050" w:left="1200" w:header="500" w:footer="500"/><w:bidi/></w:sectPr></w:body></w:document>';
 }
 function files(m){
  const header='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>';
  const style=(id,name,size,color,bold=false)=>'<w:style w:type="paragraph" w:styleId="'+id+'"><w:name w:val="'+name+'"/><w:basedOn w:val="Normal"/><w:qFormat/><w:pPr><w:bidi/><w:spacing w:after="160"/></w:pPr><w:rPr><w:rFonts w:ascii="Tahoma" w:hAnsi="Tahoma" w:cs="Tahoma"/><w:sz w:val="'+size+'"/><w:szCs w:val="'+size+'"/><w:color w:val="'+color+'"/>'+(bold?'<w:b/><w:bCs/>':'')+'</w:rPr></w:style>';
  const created=new Date(m.now);if(Number.isNaN(+created))throw Error('زمان تولید گزارش معتبر نیست.');
  return {
   '[Content_Types].xml':header+'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/><Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>',
   '_rels/.rels':header+'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rIdOffice" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/><Relationship Id="rIdCore" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rIdApp" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>',
   'word/document.xml':documentXml(m),
   'word/_rels/document.xml.rels':header+'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/><Relationship Id="rIdSettings" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/><Relationship Id="rIdFooter" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/></Relationships>',
   'word/styles.xml':header+'<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Tahoma" w:hAnsi="Tahoma" w:cs="Tahoma"/><w:sz w:val="20"/><w:szCs w:val="20"/><w:rtl/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:bidi/><w:jc w:val="right"/><w:spacing w:after="120" w:line="300" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>'+style('Title','Title',36,'0F172A',true)+style('Subtitle','Subtitle',24,'475569')+style('Heading1','Heading 1',27,'1D4ED8',true)+style('Heading2','Heading 2',22,'0F766E',true)+style('TableText','Table Text',19,'0F172A')+style('Caption','Caption',17,'64748B')+'</w:styles>',
   'word/settings.xml':header+'<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:zoom w:percent="100"/><w:defaultTabStop w:val="720"/><w:compat/><w:themeFontLang w:val="fa-IR" w:bidi="fa-IR"/></w:settings>',
   'word/footer1.xml':header+'<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:pPr><w:jc w:val="center"/><w:bidi/></w:pPr><w:r><w:rPr><w:rtl/><w:sz w:val="16"/></w:rPr><w:t>دیدبان امنیت · صفحهٔ </w:t></w:r><w:fldSimple w:instr="PAGE"><w:r><w:t>1</w:t></w:r></w:fldSimple></w:p></w:ftr>',
   'docProps/core.xml':header+'<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>'+xml(m.typeInfo.title+' — '+m.meta.organization)+'</dc:title><dc:creator>'+xml(m.meta.auditor||'دیدبان امنیت')+'</dc:creator><dcterms:created xsi:type="dcterms:W3CDTF">'+created.toISOString()+'</dcterms:created></cp:coreProperties>',
   'docProps/app.xml':header+'<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Didban Amniat Offline</Application><AppVersion>18.0</AppVersion></Properties>'
  };
 }
 async function download(input,dependencies){
  const m=model(input),archive=new dependencies.JSZip();for(const [path,content] of Object.entries(files(m)))archive.file(path,content);
  const bytes=await archive.generateAsync({type:'uint8array',compression:'DEFLATE'}),date=String(input.formatDate(input.today,false)).replace(/[۰-۹]/g,c=>'۰۱۲۳۴۵۶۷۸۹'.indexOf(c)).replace(/[٠-٩]/g,c=>'٠١٢٣٤٥٦٧٨٩'.indexOf(c)).replace(/[^0-9A-Za-z-]/g,'-');
  const filename='Didban_Corrective_'+m.typeInfo.english+'_'+date+'_'+Date.now()+'.docx';
  dependencies.download(filename,bytes,'application/vnd.openxmlformats-officedocument.wordprocessingml.document');return {filename,model:m};
 }
 return {types,states,priorities,select,model,files,documentXml,download,xml};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=V18CorrectiveWord;
