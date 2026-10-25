"""Append audit Good Point without renumbering the five existing compliance findings.
Call integrate after dashboard-integration.integrate and before the legacy Babel pass.
"""
def integrate(base):
    def replace(old, new, count=1):
        nonlocal base
        found = base.count(old)
        if found != count:
            raise RuntimeError(f'v12 compliance anchor ({found}, expected {count}): {old[:100]}')
        base = base.replace(old, new)

    replace("const dcNames=['انطباق','عدم انطباق جزیی','عدم انطباق کلی','مشاهده','توصیه برای بهبود'];", "const dcNames=['انطباق','عدم انطباق جزیی','عدم انطباق کلی','مشاهده','توصیه برای بهبود','نقطه قوت (Good Point)'];")
    replace("const dcColors=['var(--success)','var(--minor)','var(--danger)','var(--info)','var(--warning)'];", "const dcColors=['var(--success)','var(--minor)','var(--danger)','var(--info)','var(--warning)','var(--good-point-fg)'];")
    replace('d.compliance>=0&&d.compliance<5', 'd.compliance>=0&&d.compliance<6')
    start=base.index('function dcField({value,onChange,disabled}){')
    end=base.index('function dcDashboard(',start)
    base=base[:start]+"""function dcField({value,onChange,disabled}){return DH('label',{},'انطباق با استاندارد',DH('select',{'aria-label':'انطباق با استاندارد',className:value===5?'dc-good-point-select':undefined,value:value??'',disabled,onChange:e=>onChange(e.target.value===''?null:+e.target.value)},DH('option',{value:''},'انتخاب نشده'),...dcNames.map((s,k)=>DH('option',{key:k,value:k,className:k===5?'dc-good-point-option':undefined},s))),DH('small',{},'این نتیجه مستقل از وضعیت پیاده‌سازی است.'))}\n"""+base[end:]
    # The optional previous-audit field shares the same enum and selected color.
    replace("DH('select',{'aria-label':label,value:value[key]??'',onChange:", "DH('select',{'aria-label':label,className:String(value[key])==='5'?'dc-good-point-select':undefined,value:value[key]??'',onChange:")
    replace("DH('option',{key:i,value:String(i)},name)", "DH('option',{key:i,value:String(i),className:i===5?'dc-good-point-option':undefined},name)")

    replace('[1,2,3,4,0].map(s=>', '[1,2,3,4,0,5].map(s=>', 2)
    replace("'توصیه برای بهبود','انطباق','توضیحات'", "'توصیه برای بهبود','انطباق','نقطه قوت (Good Point)','توضیحات'")
    replace("'توصیه بهبود','انطباق','توضیح'", "'توصیه بهبود','انطباق','نقطه قوت (Good Point)','توضیح'")
    replace("[1,2,3,4,0,'note'].forEach", "[1,2,3,4,0,5,'note'].forEach")
    # The supplied DOCX has five fixed finding columns. Keep their placeholders
    # stable, mention Good Point in the note, and append a full six-finding table.
    replace("values['summary_'+domain+'_'+key]=row[index+1]", "values['summary_'+domain+'_'+key]=key==='note'?row[index+1]+'؛ نقطه قوت (Good Point): '+row[6]:row[index+1]")
    replace("{value:4,title:'4.5. توصیه‌های بهبود',part:'recommendTable'}", "{value:4,title:'4.5. توصیه‌های بهبود',part:'recommendTable'},{value:5,title:'4.6. نقطه قوت (Good Point)',part:'conformTable'}")
    replace("[4,'توصیه برای بهبود']])", "[4,'توصیه برای بهبود'],[5,'نقطه قوت (Good Point)']])")
    replace("let appendix=dsParagraph('ضمائم — اقدامات بهبود و ماژول مستقل ریسک','Heading1');", "let appendix=dsParagraph('خلاصه کامل وضعیت انطباق با استاندارد','Heading1')+dsDocTable([['بند استاندارد','عدم انطباق جزیی','عدم انطباق کلی','مشاهده','توصیه برای بهبود','انطباق','نقطه قوت (Good Point)','توضیحات'],...DSSummary(data)])+dsParagraph('ضمائم — اقدامات بهبود و ماژول مستقل ریسک','Heading1');")
    return base
