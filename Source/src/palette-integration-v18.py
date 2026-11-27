"""Apply audit-result palette to native badges without changing alert semantics."""
def integrate(base):
    def replace(old,new):
        nonlocal base
        count=base.count(old)
        if count!=1:
            raise RuntimeError(f'v18 audit palette integration ({count}): {old[:100]}')
        base=base.replace(old,new,1)
    replace("const dcColors=['var(--success)','var(--minor)','var(--danger)','var(--info)','var(--warning)','var(--good-point-fg)'];", "const dcColors=['var(--audit-conformity)','var(--audit-minor)','var(--audit-major)','var(--audit-observation)','var(--audit-improvement)','var(--audit-good-point)'];const dcTextColors=['var(--audit-conformity-fg)','var(--audit-minor-fg)','var(--audit-major-fg)','var(--audit-observation-fg)','var(--audit-improvement-fg)','var(--audit-good-point-fg)'];")
    old="function dcBadge(value){const c=value==null?'var(--muted)':dcColors[value];return DH('span',{className:'dc-badge',style:{background:'color-mix(in srgb,'+c+' 4%,var(--surface))',color:c,border:'1px solid '+c}},value==null?'ثبت نشده':dcNames[value])}"
    new="function dcBadge(value){const known=Number.isInteger(value)&&value>=0&&value<dcColors.length,c=known?dcColors[value]:'var(--audit-unknown)',text=known?dcTextColors[value]:'var(--inactive-fg)';return DH('span',{className:'dc-badge','data-audit-status':known?value:'unknown',style:{'--audit-status-color':c,background:'color-mix(in srgb,'+c+' 11%,var(--surface))',color:text,border:'1px solid color-mix(in srgb,'+c+' 45%,var(--border))'}},known?dcNames[value]:'ثبت نشده')}"
    replace(old,new)
    return base
