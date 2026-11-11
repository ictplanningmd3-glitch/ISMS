const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const context=vm.createContext({Intl,Date,Map,Set,structuredClone});
vm.runInContext(['jalali.js','minimal-domain.js','rtp-domain-v19.js'].map(name=>fs.readFileSync('src/'+name,'utf8')).join('\n')+'\nglobalThis.API={R:V19RtpDomain,D:V8D};',context);
const {R,D}=context.API,plain=x=>JSON.parse(JSON.stringify(x));
const project=extra=>({id:'p1',code:'RTP-001',title:'پروژهٔ آزمون',strategy:'mitigate',status:'none',progress:0,budget:'',allocated:'',allocationDate:'',...extra});
const state=p=>({...plain(D.defaults('rtp')),records:{projects:[p],activities:[{id:'a1',project:'p1',title:'فعالیت',progress:20,status:'active'}],payments:[{id:'pay1',project:'p1',amount:25,status:'پرداخت ثبت‌شده'}]}});
let checks=0;function test(name,fn){fn();checks++;console.log('✓',name);}
test('old v18 projects, incomplete legacy allocation dates, activities and payments load without mutation',()=>{
 const s=state(project({budget:1000,allocated:250,allocationDate:'',notes:'اطلاعات قبلی'})),before=JSON.stringify(s);
 D.validateState(s,'rtp');assert.equal(JSON.stringify(s),before);assert.equal(R.budgetTotals(s.records.projects[0]).allocated,250);
 assert.equal(R.budgetDraft(s.records.projects[0]).allocations[0].date,'');
});
test('long project descriptions accept 100000 characters and reject invalid or oversized values',()=>{
 const p=project({description:'پ'.repeat(100000)});D.validateState(state(p),'rtp');
 for(const description of [3,null,'x'.repeat(100001)])assert.throws(()=>D.validateState(state(project({description})),'rtp'),/شرح پروژه/);
});
test('legacy allocations can be completed explicitly without counting old and new fields twice',()=>{
 const old=project({budget:1000,allocated:250,allocationDate:'',description:'طرح کامل'}),draft=R.budgetDraft(old);
 assert.throws(()=>R.applyBudget(old,draft),/تاریخ/);draft.approvedDate='2026-11-11';draft.allocations[0].date='2026-11-10';
 const next=R.applyBudget(old,draft);assert.equal(next.description,'طرح کامل');assert.equal(next.allocated,250);assert.equal(R.budgetTotals(next).allocated,250);assert.equal(R.budgetTotals(next).remaining,750);
 assert.equal(old.allocationDate,'');assert.equal(old.allocations,undefined);
});
test('repeated allocation totals, latest date and remaining amount derive from actual rows',()=>{
 const next=R.applyBudget(project(),{approved:'۱٬۰۰۰',approvedDate:'2026-11-11',allocations:[{id:'b',amount:150,date:'2026-11-11'},{id:'a',amount:200,date:'2026-11-09'}]});
 assert.deepEqual(plain(R.budgetTotals(next)),{approved:1000,allocated:350,remaining:650});assert.equal(next.allocationDate,'2026-11-11');
 const stale={...next,allocated:999};assert.equal(R.budgetTotals(stale).allocated,350);
 assert.equal(R.budgetTotals({...stale,allocations:[]}).allocated,0);
 assert.equal(R.budgetTotals(R.applyBudget(next,{approved:'',approvedDate:'',allocations:[]})).approved,null);
});
test('new budget saves require paired dates and reject malformed, duplicate or negative allocation rows',()=>{
 const draft={approved:1000,approvedDate:'2026-11-11',allocations:[{id:'a',amount:100,date:'2026-11-11'}]};
 for(const bad of [{...draft,approvedDate:''},{...draft,approved:''},{...draft,allocations:[{id:'a',amount:-1,date:'2026-11-11'}]},{...draft,allocations:[{id:'a',amount:1,date:'2026-02-30'}]},{...draft,allocations:[draft.allocations[0],draft.allocations[0]]}])assert.throws(()=>R.applyBudget(project(),bad));
 assert.throws(()=>D.validateState(state(project({allocations:[{id:'a',amount:3,date:''}]})),'rtp'));
 const saved=R.applyBudget(project(),draft);assert.throws(()=>D.validateState(state({...saved,budget:''}),'rtp'),/بودجه/);assert.throws(()=>D.validateState(state({...saved,budgetDate:''}),'rtp'),/بودجه/);
 assert.throws(()=>R.money('1.234'));assert.throws(()=>R.money(true));
});
test('full JSON backup round trips descriptions and allocations alongside existing activity and payment logs',()=>{
 const p=R.applyBudget(project({description:'شرح\nکامل & <پروژه>'}),{approved:500,approvedDate:'2026-11-11',allocations:[{id:'a',amount:120,date:'2026-11-11'}]});
 const s=state(p),restored=JSON.parse(JSON.stringify(s));D.validateState(restored,'rtp');assert.deepEqual(restored,plain(s));assert.equal(restored.records.payments[0].amount,25);
});
test('new RTP fields never bypass effectiveness, closure or date-order requirements',()=>{
 assert.throws(()=>D.validateState(state(project({description:'طرح',status:'effective',progress:100})),'rtp'),/اثربخشی/);
 assert.throws(()=>D.validateState(state(project({description:'طرح',closed:true,progress:100})),'rtp'),/اختتام/);
 assert.throws(()=>D.validateState(state(project({start:'2026-11-11',due:'2026-11-10'})),'rtp'),/موعد/);
 const p=project({progress:100,effectiveness:'pending',description:'تکمیل اجرایی'});D.validateState(state(p),'rtp');assert.equal(D.closed(p),false);
});
test('Excel project columns retain their old positional order with description appended',()=>{
 const text=fs.readFileSync('src/minimal-rtp.jsx','utf8'),line=text.slice(0,text.indexOf('\n'));
 const keys=[...line.matchAll(/key:'([^']+)'/g)].map(m=>m[1]);
 assert.deepEqual(keys,['code','title','strategy','risk','threat','vulnerability','owner','executor','start','due','progress','status','decision','budget','description']);
});
console.log(checks+' RTP v19 domain checks passed');
