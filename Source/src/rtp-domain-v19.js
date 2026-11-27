/* Additional RTP fields; legacy v2 records remain readable without mutation. */
var V19RtpDomain=(()=>{
 const has= (object,key)=>Object.prototype.hasOwnProperty.call(object,key);
 const money=value=>{
  if(value===''||value===null||value===undefined)return '';
  const normalized=V8DateD.latin(value).replace(/[,٬]/g,'').replace('٫','.').trim();
  if(!/^\d+(?:\.\d{1,2})?$/.test(normalized)||!Number.isFinite(+normalized)||+normalized>1e15)throw Error('مبلغ باید عددی معتبر و نامنفی با حداکثر دو رقم اعشار باشد.');
  return +normalized;
 };
 const rounded=value=>Math.round(value*100)/100;
 function budgetDraft(project){
  const allocations=has(project,'allocations')?structuredClone(project.allocations):
   V8D.num(project.allocated)!==null||project.allocationDate?[{id:'legacy-'+project.id,amount:project.allocated??'',date:project.allocationDate||''}]:[];
  return {approved:project.budget??'',approvedDate:project.budgetDate||'',allocations};
 }
 function budgetTotals(project){
  const approved=V8D.num(project.budget),allocated=has(project,'allocations')?rounded(project.allocations.reduce((sum,row)=>sum+(V8D.num(row.amount)||0),0)):V8D.num(project.allocated)||0;
  return {approved,allocated,remaining:approved===null?null:rounded(approved-allocated)};
 }
 function validateProject(project){
  if(project.description!==undefined&&(typeof project.description!=='string'||project.description.length>100000))throw Error('شرح پروژه باید متن و حداکثر ۱۰۰ هزار نویسه باشد.');
  if(project.budgetDate!==undefined&&(typeof project.budgetDate!=='string'||(project.budgetDate&&!V8DateD.isoDate(project.budgetDate))))throw Error('تاریخ تصویب بودجه معتبر نیست.');
  if(has(project,'allocations')){
   if(!Array.isArray(project.allocations)||project.allocations.length>500)throw Error('ردیف‌های تخصیص بودجه نامعتبر است.');
   const approved=money(project.budget),date=project.budgetDate||'';
   if((approved!==''&&!date)||(approved===''&&date)||(project.allocations.length&&approved===''))throw Error('بودجهٔ مصوب و تاریخ تصویب را با هم کامل کنید؛ تخصیص بدون بودجهٔ مصوب معتبر نیست.');
   const ids=new Set();
   for(const row of project.allocations){
    if(!row||typeof row.id!=='string'||!row.id||row.id.length>150||ids.has(row.id)||money(row.amount)===''||!V8DateD.isoDate(row.date))throw Error('شناسه، مبلغ و تاریخ هر ردیف تخصیص بودجه را کامل و معتبر وارد کنید.');
    ids.add(row.id);
   }
  }
  return project;
 }
 function applyBudget(project,draft){
  if(!draft||typeof draft!=='object'||!Array.isArray(draft.allocations))throw Error('ساختار بودجه نامعتبر است.');
  const approved=money(draft.approved),approvedDate=draft.approvedDate??'';
  if(typeof approvedDate!=='string'||(approvedDate&&!V8DateD.isoDate(approvedDate))||(approved!==''&&!approvedDate)||(approved===''&&approvedDate))throw Error('بودجهٔ مصوب و تاریخ تصویب را با هم کامل کنید.');
  if(draft.allocations.length&&approved==='')throw Error('پیش از تخصیص، بودجهٔ مصوب و تاریخ آن را ثبت کنید.');
  const allocations=draft.allocations.map(row=>({id:row.id,amount:money(row.amount),date:row.date}));
  const next={...project,budget:approved,budgetDate:approvedDate,allocations};
  validateProject(next);
  next.allocated=budgetTotals(next).allocated;
  next.allocationDate=allocations.map(row=>row.date).sort().at(-1)||'';
  return next;
 }
 return {money,budgetDraft,budgetTotals,validateProject,applyBudget};
})();
