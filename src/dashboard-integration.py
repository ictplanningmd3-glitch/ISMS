"""Exact build-time dashboard substitutions, before the legacy Babel pass."""
def integrate(base):
    def replace(old,new):
        nonlocal base
        count=base.count(old)
        if count!=1:raise RuntimeError(f'v10 dashboard integration anchor ({count}): {old[:100]}')
        base=base.replace(old,new,1)
    replace('className:"panel radar",children:', 'className:"panel radar v10-implementation-radar",children:')
    replace(',(0,i.jsx)("span",{className:"tag",children:"نمودار عنکبوتی"})', '')
    replace('(0,i.jsx)(sL,{values:Qs.slice(0,7).map(c=>mo(J.filter(y=>y.domain===c)))})', 'DH(V10ImplementationRadar,{values:Qs.slice(0,7).map(c=>mo(J.filter(y=>y.domain===c)))})')
    start=base.index('(0,i.jsxs)("div",{className:"donutrow",children:')
    end=base.index(',(0,i.jsxs)("div",{className:"panelnote",children:',start)
    base=base[:start]+'DH(V10ImplementationPie,{counts:[0,1,2,3,4].map(co).concat(Se.length-Jl.length)})'+base[end:]
    start=base.index('function dcDashboard({data}){')
    end=base.index('function ddDownload',start)
    base=base[:start]+"function dcDashboard({data}){return DH(V10ComplianceDashboard,{data});}\n\n"+base[end:]
    return base
