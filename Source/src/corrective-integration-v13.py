"""Move corrective gaps into the independent corrective-action subnavigation."""
def integrate(base):
    old='DH(V12ImprovementPage,{projects:ro,onNew:()=>Kd(),onEdit:c=>O(c),onControl:c=>Pe(c)})'
    new='DH(V13CorrectiveModule,{projects:ro,data:G,tab:v7tab.improvements,onTab:tab=>setV7tab(prev=>({...prev,improvements:tab})),onNew:id=>Kd(id),onEdit:c=>O(c),onControl:c=>Pe(c)})'
    if base.count(old)!=1:
        raise RuntimeError('v13 corrective-action integration anchor changed')
    return base.replace(old,new,1)
