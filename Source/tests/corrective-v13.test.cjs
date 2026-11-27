/* Corrective actions are projects linked to audit findings, not implementation gaps. */
const assert=require('node:assert/strict');
const {V13Corrective:D}=require('../src/improvements-domain-v12.js');
const today='2026-10-26';
const items=[...Array.from({length:8},(_,i)=>({id:'A.5.'+(i+1),kind:'control',title:'کنترل '+(i+1)})),{id:'A.6.1',kind:'control',title:'افراد'},{id:'4.1',kind:'clause',title:'شناخت سازمان'},{id:'4.2',kind:'clause',title:'ذی‌نفعان'}];
const scopes=[{id:'annex:governance',kind:'control',itemIds:items.filter(x=>x.id.startsWith('A.5.')).map(x=>x.id)},{id:'annex:people',kind:'control',itemIds:['A.6.1']},{id:'clause:context',kind:'clause',itemIds:['4.1','4.2']}];
const row=(compliance,extra={})=>({compliance,status:4,applicable:true,...extra});
const data={'A.5.1':row(2),'A.5.2':row(1),'A.5.3':row(4),'A.5.4':row(3),'A.5.5':row(0,{status:0}),'A.5.6':row(5,{status:0}),'A.5.7':row(null,{status:0}),'A.5.8':row(2,{applicable:false}),'4.1':row(3),'4.2':row(4)};
const projects=[
 {id:'p1',status:'active',progress:30,due:'2026-10-25',mappedIds:['A.5.1','A.5.1'],scopeIds:['annex:governance','annex:governance']},
 {id:'p2',status:'completed',progress:100,due:'2026-10-20',mappedIds:['A.5.1'],scopeIds:['clause:context']},
 {id:'p3',status:'completed',progress:100,due:'2027-01-01',mappedIds:['A.5.4'],scopeIds:['annex:governance']},
 {id:'p4',status:'active',progress:100,due:today,mappedIds:['4.1'],scopeIds:[]},
 {id:'p5',status:'completed',progress:100,due:'',mappedIds:['not-a-catalog-item'],scopeIds:['not-a-domain']}
];
const metrics=(p=projects,d=data)=>D.metrics(items,d,p,scopes,today);
const byItem=(m,id)=>m.rows.find(r=>r.item.id===id);
let checks=0;function test(name,fn){fn();checks++;console.log('✓',name);}

test('all four actionable audit results qualify regardless of implementation status',()=>{
 const m=metrics();
 assert.deepEqual([...D.findingOrder],[4,3,1,2]);
 assert.deepEqual(m.rows.map(r=>r.row.compliance),[4,4,3,3,1,2]);
 assert.equal(m.attention.length,6);assert.equal(m.assessed.length,8);
 for(const id of ['A.5.5','A.5.6','A.5.7','A.5.8','A.6.1'])assert.equal(byItem(m,id),undefined,id);
 assert.ok(byItem(m,'A.5.1'));assert.equal(byItem(m,'A.5.1').row.status,4);
 const invalid={...data,'A.6.1':row('1')};assert.equal(metrics(projects,invalid).attention.length,6);
});

test('exact and heading links form a union and retain completed projects once',()=>{
 const m=metrics();
 assert.deepEqual(byItem(m,'A.5.1').related.map(p=>p.id),['p1','p2','p3']);
 assert.deepEqual(byItem(m,'A.5.4').related.map(p=>p.id),['p1','p3']);
 assert.deepEqual(byItem(m,'4.2').related.map(p=>p.id),['p2']);
 assert.equal(byItem(m,'A.5.1').related.filter(p=>p.id==='p1').length,1);
 assert.equal(byItem(m,'4.2').related[0].status,'completed');
});

test('zero projects are unplanned and any unfinished linked project keeps an action active',()=>{
 const empty=metrics([]);assert.ok(empty.rows.every(r=>r.actionStatus==='unplanned'));
 assert.equal(empty.actionStates.find(s=>s.key==='unplanned').count,6);
 const m=metrics();assert.equal(byItem(m,'A.5.1').actionStatus,'active');
 assert.equal(byItem(m,'4.1').actionStatus,'active','100 percent progress does not replace completed project status');
 assert.equal(byItem(m,'4.2').actionStatus,'done');
});

test('completing every related project changes action state without changing the audit finding',()=>{
 const before=JSON.stringify(data),copy=projects.map(p=>({...p,status:'completed',progress:100}));
 const m=metrics(copy);
 assert.ok(m.rows.every(r=>r.actionStatus==='done'));
 assert.equal(m.actionStates.find(s=>s.key==='done').count,6);
 assert.equal(byItem(m,'A.5.1').row.compliance,2);
 assert.equal(byItem(m,'4.2').row.compliance,4);
 assert.equal(JSON.stringify(data),before);
 assert.equal(projects[0].status,'active');
});

test('four KPIs count findings and all defined projects with a complete/incomplete partition',()=>{
 const m=metrics();assert.deepEqual(m.counts,{attention:6,projects:5,completed:3,incomplete:2});
 assert.equal(m.counts.completed+m.counts.incomplete,m.counts.projects);
 assert.equal(m.actionStates.reduce((n,s)=>n+s.count,0),m.counts.attention);
});

test('project deadlines separate unfinished past/future and completed projects without double counting',()=>{
 const extra=[{id:'future',status:'planned',due:'2027-01-01',mappedIds:[]},{id:'invalid',status:'active',due:'2026-02-30',mappedIds:[]},{id:'undated',status:'active',due:'',mappedIds:[]}];
 const m=metrics([...projects,...extra]);
 assert.deepEqual(m.dueBuckets.map(s=>[s.key,s.count]),[['overdue',1],['scheduled',2],['completed',3]]);
 assert.deepEqual(m.overdueProjects.map(p=>p.id),['p1']);
 assert.deepEqual(m.scheduledProjects.map(p=>p.id),['p4','future']);
 assert.deepEqual(m.undatedProjects.map(p=>p.id),['invalid','undated']);
 assert.equal(m.dueBuckets.reduce((n,s)=>n+s.count,0)+m.undatedProjects.length,m.counts.projects);
});

test('four-series domain stacks contain only actionable findings in radar order',()=>{
 const m=metrics(),governance=m.groups.find(g=>g.id==='annex:governance'),context=m.groups.find(g=>g.id==='clause:context'),people=m.groups.find(g=>g.id==='annex:people');
 assert.deepEqual(governance.segments.map(s=>s.code),[4,3,1,2]);
 assert.deepEqual(governance.segments.map(s=>s.count),[1,1,1,1]);
 assert.deepEqual(governance.segments.map(s=>s.percentage),[25,25,25,25]);
 assert.equal(governance.total,4);assert.equal(context.total,2);
 assert.deepEqual(context.segments.map(s=>s.count),[1,1,0,0]);
 assert.deepEqual(context.segments.map(s=>s.percentage),[50,50,0,0]);
 assert.equal(people.total,0);assert.ok(people.segments.every(s=>s.count===0&&s.percentage===0));
 for(const group of m.groups)assert.ok(Math.abs(group.segments.reduce((n,s)=>n+s.percentage,0)-(group.total?100:0))<1e-9);
});

test('completed counts are unique per kind and explicitly allow a project linked to both kinds',()=>{
 const m=metrics();assert.deepEqual(m.completedByKind.map(s=>[s.key,s.count]),[['clause',1],['control',2]]);
 assert.deepEqual(m.completedUnlinkedProjects.map(p=>p.id),['p5']);
 // Three links within the same kind still count one project; a cross-kind project appears once in each.
 const one=metrics([{id:'both',status:'completed',mappedIds:['A.5.1','A.5.2','4.1'],scopeIds:['annex:governance','clause:context']}]);
 assert.deepEqual(one.completedByKind.map(s=>s.count),[1,1]);
 assert.equal(one.completedProjects.length,1);
});

test('empty data has zero KPIs and empty stacks rather than a fabricated completed action',()=>{
 const m=metrics([],{});assert.deepEqual(m.counts,{attention:0,projects:0,completed:0,incomplete:0});
 for(const key of ['assessed','attention','rows','completedProjects','incompleteProjects','overdueProjects','scheduledProjects','undatedProjects'])assert.equal(m[key].length,0,key);
 assert.ok(m.groups.every(g=>g.total===0&&g.segments.every(s=>s.percentage===0)));
 assert.ok(m.dueBuckets.every(s=>s.count===0));assert.ok(m.completedByKind.every(s=>s.count===0));
});

test('deadline date validation rejects impossible dates and retains valid leap days',()=>{
 assert.equal(D.isDate('2026-02-30'),false);assert.equal(D.isDate('2025-02-29'),false);
 assert.equal(D.isDate('2024-02-29'),true);assert.equal(D.isDate('2026-10-26'),true);
 for(const value of ['',null,42,'26/10/2026','2026-1-01'])assert.equal(D.isDate(value),false);
});
console.log(checks+' corrective dashboard checks passed');
