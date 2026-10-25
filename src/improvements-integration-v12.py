"""Integrate corrective-project UI while keeping native storage and backup workflows."""
def integrate(base):
    def replace(old,new):
        nonlocal base
        count=base.count(old)
        if count!=1: raise RuntimeError(f'v12 improvements integration ({count}): {old[:100]}')
        base=base.replace(old,new,1)
    start=base.index('function Ps(a){')
    end=base.index('function _s(a){',start)
    base=base[:start]+'function Ps(a){return V12ValidateProject(a)}'+base[end:]
    replace('(0,i.jsx)(eL,{projects:ro,onNew:()=>Kd(),onEdit:c=>O(c),onControl:c=>Pe(c)})','DH(V12ImprovementPage,{projects:ro,onNew:()=>Kd(),onEdit:c=>O(c),onControl:c=>Pe(c)})')
    replace('(0,i.jsx)(tL,{value:k,onClose:()=>O(null),onSave:hL,disabled:u},k.id+k.updated)','DH(V12ImprovementForm,{value:k,onClose:()=>O(null),onSave:hL,disabled:u,key:k.id+k.updated})')
    replace('(0,i.jsx)(dcDashboard,{data:G})','DH(V12ProjectDashboard,{projects:ro,onEdit:c=>O(c),compact:true}),(0,i.jsx)(dcDashboard,{data:G})')
    # Native Excel/Word tables now retain the new selected headings and budget figures.
    replace("['اقدامات بهبود',[['عنوان','هدف','مسئول','وضعیت','اولویت','شروع','مدت (ماه)','موعد','پیشرفت','منابع','بندهای مرتبط','یادداشت','آخرین به‌روزرسانی'],...projects.map(p=>[p.title,p.goal,p.owner,io[p.status]||p.status,so[p.priority]||p.priority,p.start,p.months,p.due,p.progress,p.resources,(p.mappedIds||[]).join('، '),p.notes,p.updated])]]", "['اقدامات بهبود',[['عنوان','هدف','مسئول','وضعیت','اولویت','شروع','مدت (ماه)','موعد','پیشرفت','منابع','بندهای مرتبط','یادداشت','آخرین به‌روزرسانی','گروه زمانی','سرفصل‌های مرتبط','بودجه مصوب (ریال)','تاریخ تصویب بودجه','جمع تخصیص (ریال)','مانده بودجه (ریال)'],...projects.map(p=>{const scopes=V12ProjectScopes(),totals=V12Imp.totals(p.budget);return [p.title,p.goal,p.owner,io[p.status]||p.status,so[p.priority]||p.priority,p.start,p.months,p.due,p.progress,p.resources,(p.mappedIds||[]).join('، '),p.notes,p.updated,V12Imp.group(p),V12Imp.scopeIds(p,scopes).map(id=>scopes.find(s=>s.id===id)?.title).join('، '),totals.approved??'',p.budget?.approvedDate||'',totals.allocated,totals.remaining??''];})]],['تخصیص بودجه اقدامات اصلاحی',[['عنوان پروژه','مبلغ تخصیص (ریال)','تاریخ تخصیص'],...projects.flatMap(p=>(p.budget?.allocations||[]).map(r=>[p.title,r.amount,r.date]))]]")
    return base
