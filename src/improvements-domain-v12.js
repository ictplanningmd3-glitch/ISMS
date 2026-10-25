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
