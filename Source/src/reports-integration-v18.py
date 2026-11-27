"""Keep the audit Word template and add a corrective-report entry before its form."""
def integrate(base):
    old="DH('form',{onSubmit:run},...DSOrgGroups.map("
    new="DH(V18CorrectiveReports,{projects,data:assessments,meta,embedded:true}),"+old
    if base.count(old)!=1:
        raise RuntimeError('The existing Word report form integration anchor changed.')
    return base.replace(old,new,1)
