"""Replace only the existing shield-and-eye marks, preserving surrounding UI."""
def integrate(base):
    start=base.index('function DSLogo(){')
    mark_start=base.index("DH('svg',{viewBox:'0 0 80 80'",start)
    mark_end=base.index(",DH('div',{className:'ds-brand-name'}",mark_start)
    base=base[:mark_start]+"DH(V18BrandMark,{size:74,variant:'sidebar'})"+base[mark_end:]
    start=base.index('function DSBanner(){')
    mark_start=base.index("DH('path',{d:'M300 39 365 65v59",start)
    mark_end=base.index(',...[[60,70,210,100]',mark_start)
    base=base[:mark_start]+"DH(V18BrandMark,{size:190,variant:'banner',x:205,y:25,height:210,decorative:true})"+base[mark_end:]
    return base
