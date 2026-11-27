"""Append implementation details after the management compliance table."""
def integrate(base):
    old='(0,i.jsx)(dcDashboard,{data:G})'
    if base.count(old)!=1:
        raise RuntimeError('v15 implementation dashboard integration anchor changed')
    base=base.replace(old,old+',DH(V15ImplementationDashboard,{data:G,onItem:Pe})',1)
    old="['compliance','انطباق با استاندارد','.dc-section']];"
    if base.count(old)!=1:
        raise RuntimeError('v15 implementation quick navigation anchor changed')
    return base.replace(old,"['compliance','انطباق با استاندارد','.dc-section'],['implementation','وضعیت پیاده‌سازی','[data-v15-implementation-dashboard]']];",1)
