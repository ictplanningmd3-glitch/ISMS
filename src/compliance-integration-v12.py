"""Append Good Point and apply the v13 presentation order without renumbering enum IDs."""
def integrate(base):
    def replace(old,new,count=1):
        nonlocal base
        found=base.count(old)
        if found!=count:raise RuntimeError(f'v13 compliance anchor ({found}, expected {count}): {old[:100]}')
        base=base.replace(old,new)
    replace("const dcNames=['انطباق','عدم انطباق جزیی','عدم انطباق کلی','مشاهده','توصیه برای بهبود'];", "const dcNames=['انطباق','عدم انطباق جزیی','عدم انطباق کلی','مشاهده','توصیه برای بهبود','نقطه قوت (Good Point)'];const dcOrder=[5,0,4,3,1,2];")
    replace("const dcColors=['var(--success)','var(--minor)','var(--danger)','var(--info)','var(--warning)'];", "const dcColors=['var(--success)','var(--minor)','var(--danger)','var(--info)','var(--warning)','var(--good-point-fg)'];")
    replace('d.compliance>=0&&d.compliance<5','d.compliance>=0&&d.compliance<6')
    start=base.index('function dcField({value,onChange,disabled}){');end=base.index('function dcDashboard(',start)
    base=base[:start]+"""function dcField({value,onChange,disabled}){return DH('label',{},'انطباق با استاندارد',DH('select',{'aria-label':'انطباق با استاندارد',value:value??'',disabled,onChange:e=>onChange(e.target.value===''?null:+e.target.value)},DH('option',{value:''},'انتخاب نشده'),...dcOrder.map(k=>DH('option',{key:k,value:k},dcNames[k]))),DH('small',{},'این نتیجه مستقل از وضعیت پیاده‌سازی است.'))}\n"""+base[end:]
    replace("...dcNames.map((name,i)=>DH('option',{key:i,value:String(i)},name))", "...dcOrder.map(i=>DH('option',{key:i,value:String(i)},dcNames[i]))")
    # Reports use the same conceptual grouping and status order as the screen.
    start=base.index('function DSSummary(data){');end=base.index('function dsReportTables(',start)
    base=base[:start]+"""function DSSummary(data){const values=V13StandardGroups().map(g=>{const items=g.itemIds.map(id=>J.find(x=>x.id===id)).filter(Boolean),eligible=items.filter(x=>data[x.id]?.applicable!==false);return [g.title,...dcOrder.map(s=>eligible.filter(x=>data[x.id]?.compliance===s).length),'ثبت نشده: '+eligible.filter(x=>data[x.id]?.compliance==null).length+'؛ غیرقابل اعمال: '+(items.length-eligible.length)]});return [...values,['مجموع',...dcOrder.map(s=>J.filter(x=>data[x.id]?.applicable!==false&&data[x.id]?.compliance===s).length),'تعداد کل الزامات و کنترل‌ها: '+J.length]]}\n"""+base[end:]
    old="'عدم انطباق جزیی','عدم انطباق کلی','مشاهده','توصیه برای بهبود','انطباق','توضیحات'"
    new="'نقطه قوت (Good Point)','انطباق','توصیه برای بهبود','مشاهده','عدم انطباق جزیی','عدم انطباق کلی','توضیحات'"
    replace(old,new)
    replace("'عدم انطباق جزیی','عدم انطباق کلی','مشاهده','توصیه بهبود','انطباق','توضیح'", "'نقطه قوت (Good Point)','انطباق','توصیه بهبود','مشاهده','عدم انطباق جزیی','عدم انطباق کلی','توضیح'")
    # The original DOCX template contains fixed official-clause summary fields.
    # Fill those by enum key rather than presentation index, then append the full
    # canonical 20-group table below. This retains the supplied report template.
    start=base.index('function DSTemplateValues(data,meta){');end=base.index('function DSFindingsXml(',start)
    base=base[:start]+"""function DSTemplateValues(data,meta){const values={...meta,auditor:meta.auditor||meta.leadAuditor,implementationDates:'شروع: '+dsNonempty(meta.implementationStart)+' — پایان: '+dsNonempty(meta.implementationEnd),placeDate:dsNonempty(meta.site)+' — '+dsNonempty(meta.date)},domains=[...new Set(J.map(x=>x.domain))];for(const domain of [...domains,'total']){const items=domain==='total'?J:J.filter(x=>x.domain===domain),eligible=items.filter(x=>data[x.id]?.applicable!==false),key=domain.replace('.','_');for(const status of dcOrder)values['summary_'+key+'_'+status]=eligible.filter(x=>data[x.id]?.compliance===status).length;values['summary_'+key+'_note']=(domain==='total'?'تعداد کل الزامات و کنترل‌ها: '+J.length:'ثبت نشده: '+eligible.filter(x=>data[x.id]?.compliance==null).length+'؛ غیرقابل اعمال: '+(items.length-eligible.length))+'؛ نقطه قوت (Good Point): '+values['summary_'+key+'_5'];}return values}\n"""+base[end:]
    old="[{value:0,title:'4.1. موارد انطباق',part:'conformTable'},{value:2,title:'4.2. عدم انطباق کلی',part:'majorTable'},{value:1,title:'4.3. عدم انطباق جزیی',part:'minorTable'},{value:3,title:'4.4. مشاهدات',part:'conformTable'},{value:4,title:'4.5. توصیه‌های بهبود',part:'recommendTable'}]"
    new="[{value:5,title:'4.1. نقطه قوت (Good Point)',part:'conformTable'},{value:0,title:'4.2. موارد انطباق',part:'conformTable'},{value:4,title:'4.3. توصیه‌های بهبود',part:'recommendTable'},{value:3,title:'4.4. مشاهدات',part:'conformTable'},{value:1,title:'4.5. عدم انطباق جزیی',part:'minorTable'},{value:2,title:'4.6. عدم انطباق کلی',part:'majorTable'}]"
    replace(old,new)
    replace("[[0,'انطباق'],[2,'عدم انطباق کلی'],[1,'عدم انطباق جزیی'],[3,'مشاهده'],[4,'توصیه برای بهبود']]", "[[5,'نقطه قوت (Good Point)'],[0,'انطباق'],[4,'توصیه برای بهبود'],[3,'مشاهده'],[1,'عدم انطباق جزیی'],[2,'عدم انطباق کلی']]")
    replace("let appendix=dsParagraph('ضمائم — اقدامات بهبود و ماژول مستقل ریسک','Heading1');", "let appendix=dsParagraph('خلاصه کامل وضعیت انطباق با استاندارد','Heading1')+dsDocTable([['حوزه / سرفصل','نقطه قوت (Good Point)','انطباق','توصیه برای بهبود','مشاهده','عدم انطباق جزیی','عدم انطباق کلی','توضیحات'],...DSSummary(data)])+dsParagraph('ضمائم — اقدامات بهبود و ماژول مستقل ریسک','Heading1');")
    return base
