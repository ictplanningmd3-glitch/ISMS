"""Remove legacy dashboard panels and wire the focused v13 views after v12 integration."""
def integrate(base):
    def replace(old,new):
        nonlocal base
        n=base.count(old)
        if n!=1:raise RuntimeError(f'v13 dashboard integration ({n}): {old[:100]}')
        base=base.replace(old,new,1)
    replace('DH(V10ImplementationRadar,{values:Qs.slice(0,7).map(c=>mo(J.filter(y=>y.domain===c)))})','DH(V10ImplementationRadar,{data:G})')
    start=base.index(',(0,i.jsxs)("div",{className:"bottomgrid"')
    end=base.index(',(0,i.jsx)(oL,{data:G,projects:ro,onOpen:c=>Pe(c),onProject:Kd})',start)
    base=base[:start]+',DH(V13NonconformityRows,{data:G})'+base[end:]
    replace(',(0,i.jsx)(oL,{data:G,projects:ro,onOpen:c=>Pe(c),onProject:Kd})','')
    replace('DH(V12ProjectDashboard,{projects:ro,onEdit:c=>O(c),compact:true}),','')
    start=base.index('const dsDashboardTargets=')
    end=base.index('function DSQuickAccess()',start)
    base=base[:start]+"const dsDashboardTargets=[['health','وضعیت کلی','.org-health'],['stats','شاخص‌ها','.stats'],['charts','نمودار پیاده‌سازی','.charts'],['concept','رادار انطباق','.v8-concept'],['distribution','توزیع عدم‌انطباق‌ها','[data-v13-nc-dashboard]'],['compliance','انطباق با استاندارد','.dc-section']];\n"+base[end:]
    return base
