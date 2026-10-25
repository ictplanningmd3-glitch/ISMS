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
/* Operational gaps use recorded, applicable audit assessments. Unknown is never a gap. */
var V13Corrective = (() => {
 const isDate = value => typeof value==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(value)&&Number.isFinite(Date.parse(value+'T12:00:00Z'))&&new Date(value+'T12:00:00Z').toISOString().slice(0,10)===value;
 function metrics(items,data,projects,scopes,today){
  const assessed=items.filter(item=>{const row=data[item.id];return row&&row.applicable!==false&&Number.isInteger(row.status)&&row.status>=0&&row.status<=4;});
  const overdueAudits=assessed.filter(item=>{const row=data[item.id];return row.status<3&&isDate(row.due)&&row.due<today;});
  const critical=assessed.filter(item=>{const row=data[item.id];return row.status<=1||(row.status<3&&isDate(row.due)&&row.due<today);});
  const major=assessed.filter(item=>data[item.id].compliance===2),minor=assessed.filter(item=>data[item.id].compliance===1),criticalSet=new Set(critical.map(item=>item.id)),overdueSet=new Set(overdueAudits.map(item=>item.id));
  const attention=assessed.filter(item=>criticalSet.has(item.id)||data[item.id].compliance===1||data[item.id].compliance===2);
  const openProjects=projects.filter(p=>p.status!=='completed'),scopeLookup=new Map(scopes.map(scope=>[scope.id,scope]));
  const relatedProjects=item=>openProjects.filter(project=>(project.mappedIds||[]).includes(item.id)||(project.scopeIds||[]).some(id=>scopeLookup.get(id)?.itemIds.includes(item.id)));
  const rows=attention.map(item=>{const row=data[item.id];return {item,row,critical:criticalSet.has(item.id),overdue:overdueSet.has(item.id),related:relatedProjects(item)};}).sort((a,b)=>(b.row.compliance===2)-(a.row.compliance===2)||(b.row.compliance===1)-(a.row.compliance===1)||Number(b.overdue)-Number(a.overdue)||a.row.status-b.row.status||a.item.id.localeCompare(b.item.id));
  const uncovered=rows.filter(row=>!row.related.length),overdueProjects=projects.filter(p=>p.status!=='completed'&&p.progress<100&&isDate(p.due)&&p.due<today).sort((a,b)=>a.due.localeCompare(b.due));
  const dueBuckets=[{key:'overdue',label:'مهلت گذشته',count:rows.filter(r=>r.row.status<3&&isDate(r.row.due)&&r.row.due<today).length},{key:'scheduled',label:'مهلت جاری / آینده',count:rows.filter(r=>r.row.status<3&&isDate(r.row.due)&&r.row.due>=today).length},{key:'no-date',label:'بدون مهلت اقدام',count:rows.filter(r=>r.row.status<3&&!isDate(r.row.due)).length},{key:'implemented',label:'پیاده‌سازی تکمیل؛ نیازمند بررسی یافته',count:rows.filter(r=>r.row.status>=3).length}];
  return {assessed,critical,overdueAudits,major,minor,attention,rows,uncovered,overdueProjects,dueBuckets,coverage:[{key:'covered',label:'دارای پروژه مرتبط باز',count:rows.length-uncovered.length},{key:'uncovered',label:'فاقد پروژه مرتبط باز',count:uncovered.length}],projectStatuses:['planned','active','blocked','completed'].map(status=>({key:status,status,count:projects.filter(p=>p.status===status).length})),groups:scopes.map(scope=>({...scope,count:attention.filter(item=>scope.itemIds.includes(item.id)).length}))};
 }
 return {isDate,metrics};
})();
if(typeof module!=='undefined'&&module.exports)module.exports={...V12Imp,V13Corrective};
