/* Corrective project calculations. Scope counts count each project once per heading. */
var V12Imp = (() => {
 const group = p => ({1:'A',2:'B',3:'C'})[p.months] || 'B';
 const amount = (v,label) => {if(v===''||v==null)return '';if((typeof v!=='number'&&typeof v!=='string')||!/^\d+(?:\.\d{1,2})?$/.test(String(v))||!Number.isFinite(+v)||+v<0||+v>1e15)throw Error(label+' باید مبلغی معتبر و نامنفی باشد.');return +v;};
 function budget(raw={},isDate){
  if(!raw||typeof raw!=='object'||Array.isArray(raw))throw Error('ساختار بودجه اقدام اصلاحی نامعتبر است.');
  const approved=amount(raw.approved,'بودجه مصوب'),approvedDate=raw.approvedDate??'',rows=raw.allocations??[];
  if(typeof approvedDate!=='string'||(approvedDate&&!isDate(approvedDate))||!Array.isArray(rows)||rows.length>500)throw Error('تاریخ یا ردیف‌های بودجه نامعتبر است.');
  if((approved!==''&&!approvedDate)||(approved===''&&approvedDate))throw Error('بودجه مصوب و تاریخ تصویب آن را با هم تکمیل کنید.');
  const allocations=rows.map((r,i)=>{if(!r||typeof r!=='object'||typeof r.id!=='string'||!r.id||r.id.length>150)throw Error('شناسه ردیف تخصیص بودجه نامعتبر است.');const n=amount(r.amount,'مبلغ تخصیص ردیف '+(i+1));if(n===''||typeof r.date!=='string'||!isDate(r.date))throw Error('مبلغ و تاریخ هر ردیف تخصیص بودجه را تکمیل کنید.');return {id:r.id,amount:n,date:r.date};});
  if(new Set(allocations.map(r=>r.id)).size!==allocations.length)throw Error('شناسه تخصیص بودجه تکراری است.');
  if(allocations.length&&approved==='')throw Error('پیش از ثبت تخصیص‌ها، بودجه مصوب و تاریخ آن را وارد کنید.');
  return {approved,approvedDate,allocations};
 }
 const totals=b=>{const approved=b?.approved===''||b?.approved==null?null:Number(b.approved),allocated=(b?.allocations||[]).reduce((s,r)=>s+(Number.isFinite(+r.amount)?+r.amount:0),0);return {approved,allocated,remaining:approved===null?null:Math.round((approved-allocated)*100)/100};};
 function scopeIds(p,scopes){const selected=new Set(p.scopeIds||[]);for(const id of p.mappedIds||[])for(const s of scopes)if(s.itemIds.includes(id))selected.add(s.id);return scopes.filter(s=>selected.has(s.id)).map(s=>s.id);}
 function scopeCounts(projects,scopes){return scopes.map(s=>({...s,count:projects.filter(p=>scopeIds(p,scopes).includes(s.id)).length}));}
 function summary(projects,today){const states=['planned','active','blocked','completed'];return {count:projects.length,progress:projects.length?Math.round(projects.reduce((s,p)=>s+p.progress,0)/projects.length):0,overdue:projects.filter(p=>p.status!=='completed'&&p.due<today).length,statuses:states.map(status=>({status,count:projects.filter(p=>p.status===status).length})),groups:['A','B','C'].map(key=>{const rows=projects.filter(p=>group(p)===key);return {key,count:rows.length,progress:rows.length?Math.round(rows.reduce((s,p)=>s+p.progress,0)/rows.length):0};})};}
 return {group,amount,budget,totals,scopeIds,scopeCounts,summary};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=V12Imp;
/* Corrective actions follow the audit finding, independently of implementation status. */
var V13Corrective = (() => {
 const findingOrder=Object.freeze([4,3,1,2]);
 const isDate = value => typeof value==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(value)&&Number.isFinite(Date.parse(value+'T12:00:00Z'))&&new Date(value+'T12:00:00Z').toISOString().slice(0,10)===value;
 const completed = project => project.status==='completed';
 function metrics(items,data,projects,scopes,today){
  const catalog=new Map(items.map(item=>[item.id,item])),scopeLookup=new Map(scopes.map(scope=>[scope.id,scope]));
  const assessed=[...catalog.values()].filter(item=>{const row=data[item.id];return row&&row.applicable!==false&&Number.isInteger(row.compliance)&&row.compliance>=0&&row.compliance<=5;});
  const attention=assessed.filter(item=>findingOrder.includes(data[item.id].compliance));
  // A project can be linked both by its exact item and by a selected heading.
  // Sets prevent either path from counting the same project twice for one item.
  const projectLinks=projects.map(project=>{const itemIds=new Set((project.mappedIds||[]).filter(id=>catalog.has(id)));for(const id of project.scopeIds||[]){for(const itemId of scopeLookup.get(id)?.itemIds||[])if(catalog.has(itemId))itemIds.add(itemId);}return {project,itemIds};});
  const rows=attention.map(item=>{const related=projectLinks.filter(link=>link.itemIds.has(item.id)).map(link=>link.project),actionStatus=!related.length?'unplanned':related.every(completed)?'done':'active';return {item,row:data[item.id],related,actionStatus};}).sort((a,b)=>findingOrder.indexOf(a.row.compliance)-findingOrder.indexOf(b.row.compliance)||a.item.id.localeCompare(b.item.id));
  const completedProjects=projects.filter(completed),incompleteProjects=projects.filter(project=>!completed(project));
  const overdueProjects=incompleteProjects.filter(project=>isDate(project.due)&&project.due<today).sort((a,b)=>a.due.localeCompare(b.due));
  const scheduledProjects=incompleteProjects.filter(project=>isDate(project.due)&&project.due>=today),undatedProjects=incompleteProjects.filter(project=>!isDate(project.due));
  const dueBuckets=[{key:'overdue',label:'مهلت گذشته',count:overdueProjects.length},{key:'scheduled',label:'مهلت آینده',count:scheduledProjects.length},{key:'completed',label:'تکمیل شده',count:completedProjects.length}];
  const groups=scopes.map(scope=>{const selected=attention.filter(item=>scope.itemIds.includes(item.id)),total=selected.length,segments=findingOrder.map(code=>{const count=selected.filter(item=>data[item.id].compliance===code).length;return {code,value:code,count,percentage:total?count/total*100:0};});return {...scope,count:total,total,segments};});
  const completedLinks=projectLinks.filter(link=>completed(link.project)),kindsForLink=link=>new Set([...link.itemIds].map(id=>catalog.get(id)?.kind).filter(kind=>kind==='clause'||kind==='control'));
  const completedByKind=[{key:'clause',kind:'clause',label:'الزامات استاندارد'},{key:'control',kind:'control',label:'کنترل‌های Annex A'}].map(group=>({...group,count:completedLinks.filter(link=>kindsForLink(link).has(group.kind)).length}));
  const completedUnlinkedProjects=completedLinks.filter(link=>!kindsForLink(link).size).map(link=>link.project);
  const actionStates=[{key:'unplanned',label:'برنامه‌ریزی نشده'},{key:'active',label:'در حال اقدام'},{key:'done',label:'اقدام شده'}].map(state=>({...state,count:rows.filter(row=>row.actionStatus===state.key).length}));
  // Coverage is the union of actionable audit items linked to at least one project.
  // A scope/exact-link overlap, or several projects on one item, never adds another item.
  // Completed projects remain defined coverage; this indicator does not assert closure.
  const attentionIds=new Set(attention.map(item=>item.id)),coveredItems=rows.filter(row=>row.related.length).map(row=>row.item),uncoveredItems=rows.filter(row=>!row.related.length).map(row=>row.item);
  const coverageProjects=projectLinks.map(link=>{const itemIds=[...link.itemIds].filter(id=>attentionIds.has(id));return {project:link.project,itemIds,count:itemIds.length};});
  const coverage={required:attention.length,defined:projects.length,covered:coveredItems.length,uncovered:uncoveredItems.length,percentage:attention.length?coveredItems.length/attention.length*100:null,coveredItems,uncoveredItems,projects:coverageProjects,contributingProjects:coverageProjects.filter(link=>link.count>0)};
  return {assessed,attention,rows,actionStates,coverage,counts:{attention:attention.length,projects:projects.length,completed:completedProjects.length,incomplete:incompleteProjects.length},completedProjects,incompleteProjects,overdueProjects,scheduledProjects,undatedProjects,dueBuckets,groups,completedByKind,completedUnlinkedProjects};
 }
 return {findingOrder,isDate,completed,metrics};
})();
if(typeof module!=='undefined'&&module.exports)module.exports={...V12Imp,V13Corrective};
