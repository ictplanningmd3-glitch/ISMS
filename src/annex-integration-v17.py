"""Show the supplied Annex A wording only in individual control audit forms."""
def integrate(base):
    def replace(old,new):
        nonlocal base
        count=base.count(old)
        if count!=1:
            raise RuntimeError(f'v17 Annex A integration anchor changed ({count}): {old[:100]}')
        base=base.replace(old,new,1)

    # The original clause header remains byte-for-byte the fallback expression.
    original='(0,i.jsxs)("h2",{id:"audit-title",children:[J.find(c=>c.id===n.id)?.title," ",(0,i.jsxs)("span",{className:"english-title",lang:"en",dir:"ltr",children:["(",J.find(c=>c.id===n.id)?.english,")"]})]})'
    replace(original,'V17AnnexControls[n.id]?DH(V17AnnexAuditTitle,{id:n.id}):'+original)
    original=',(0,i.jsxs)("form",{onSubmit:pL,children:['
    replace(original,',DH(V17AnnexReference,{id:n.id})'+original)
    return base
