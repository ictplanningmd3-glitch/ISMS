/* Coverage measures distinct actionable audit items, not the number of projects. */
const assert=require('node:assert/strict');
const {V13Corrective:D}=require('../src/improvements-domain-v12.js');
const items=[
 {id:'4.1',kind:'clause',title:'شناخت'},
 {id:'4.2',kind:'clause',title:'ذی‌نفعان'},
 {id:'A.5.1',kind:'control',title:'سیاست'},
 {id:'A.5.2',kind:'control',title:'مسئولیت'},
 {id:'A.5.3',kind:'control',title:'انطباق'},
 {id:'A.5.4',kind:'control',title:'خارج از دامنه'}
];
const scopes=[{id:'clause:context',kind:'clause',itemIds:['4.1','4.2']},{id:'annex:governance',kind:'control',itemIds:['A.5.1','A.5.2','A.5.3','A.5.4']}];
const data={
 '4.1':{compliance:4,applicable:true},'4.2':{compliance:3,applicable:true},
 'A.5.1':{compliance:1,applicable:true},'A.5.2':{compliance:2,applicable:true},
 'A.5.3':{compliance:0,applicable:true},'A.5.4':{compliance:2,applicable:false}
};
const project=(id,extra={})=>({id,title:id,status:'active',mappedIds:[],scopeIds:[],due:'2026-12-01',...extra});
const metrics=(projects=[],audits=data,catalog=items)=>D.metrics(catalog,audits,projects,scopes,'2026-10-30');
const ids=rows=>rows.map(row=>row.id).sort();
let checks=0;function test(name,fn){fn();checks++;console.log('✓',name);}

test('four required items, one project covering two gives 50 percent coverage',()=>{
 const m=metrics([project('p1',{mappedIds:['4.1','A.5.1']})]),c=m.coverage;
 assert.equal(c.required,4);assert.equal(c.defined,1);assert.equal(c.covered,2);assert.equal(c.uncovered,2);assert.equal(c.percentage,50);
 assert.deepEqual(ids(c.coveredItems),['4.1','A.5.1']);assert.deepEqual(ids(c.uncoveredItems),['4.2','A.5.2']);
 assert.equal(c.projects[0].count,2);assert.equal(c.contributingProjects.length,1);
 assert.equal(c.covered+c.uncovered,c.required);
});

test('heading and exact links form one covered-item union, even when ids repeat',()=>{
 const c=metrics([project('p1',{mappedIds:['4.1','4.1','4.2'],scopeIds:['clause:context','clause:context']})]).coverage;
 assert.equal(c.covered,2);assert.equal(c.percentage,50);assert.equal(c.projects[0].count,2);
 assert.deepEqual(c.projects[0].itemIds,['4.1','4.2']);
});

test('overlapping project coverage is not added together',()=>{
 const c=metrics([project('p1',{mappedIds:['4.1','A.5.1']}),project('p2',{mappedIds:['4.1','4.2']})]).coverage;
 assert.equal(c.defined,2);assert.equal(c.covered,3);assert.equal(c.uncovered,1);assert.equal(c.percentage,75);
 assert.deepEqual(c.projects.map(p=>p.count),[2,2]);assert.equal(c.contributingProjects.length,2);
 assert.equal(c.projects.reduce((sum,p)=>sum+p.count,0),4,'per-project coverage can overlap, the global union stays three');
});

test('nonapplicable, conforming, good-point and unassessed links do not add needed coverage',()=>{
 const audits={...data,'A.5.3':{compliance:5},'4.2':{compliance:null}};
 const c=metrics([project('p1',{mappedIds:['A.5.3','A.5.4','4.2','not-a-real-item']})],audits).coverage;
 assert.equal(c.required,3);assert.equal(c.defined,1);assert.equal(c.covered,0);assert.equal(c.percentage,0);
 assert.equal(c.projects[0].count,0);assert.equal(c.contributingProjects.length,0);
 const conforming=metrics([project('p2',{mappedIds:['A.5.3']})]).coverage;assert.equal(conforming.projects[0].count,0);
});

test('completed projects count as defined coverage without changing the audit result',()=>{
 const before=JSON.stringify(data),m=metrics([project('done',{status:'completed',mappedIds:['4.1','A.5.1']})]);
 assert.equal(m.coverage.percentage,50);assert.equal(m.coverage.contributingProjects[0].project.status,'completed');
 assert.ok(m.rows.filter(r=>['4.1','A.5.1'].includes(r.item.id)).every(r=>r.actionStatus==='done'));
 assert.equal(JSON.stringify(data),before);assert.equal(data['A.5.1'].compliance,1);
});

test('zero needs is an absent denominator, never fabricated 100 percent',()=>{
 const empty=metrics([],{}).coverage;
 assert.equal(empty.required,0);assert.equal(empty.defined,0);assert.equal(empty.covered,0);assert.equal(empty.uncovered,0);assert.equal(empty.percentage,null);
 assert.deepEqual(empty.coveredItems,[]);assert.deepEqual(empty.uncoveredItems,[]);
 const defined=metrics([project('future',{scopeIds:['clause:context']})],{}).coverage;
 assert.equal(defined.defined,1);assert.equal(defined.percentage,null);assert.equal(defined.projects[0].count,0);
});

test('duplicate catalog rows cannot double count a required or covered item',()=>{
 const c=metrics([project('p1',{mappedIds:['4.1','A.5.1']})],data,[...items,items[0],items[2]]).coverage;
 assert.equal(c.required,4);assert.equal(c.covered,2);assert.equal(c.percentage,50);
 assert.equal(new Set(c.coveredItems.map(item=>item.id)).size,c.coveredItems.length);
});

test('no projects leaves all required items uncovered; a broad project can cover all needs',()=>{
 const empty=metrics().coverage;assert.equal(empty.covered,0);assert.equal(empty.uncovered,4);assert.equal(empty.percentage,0);
 const full=metrics([project('all',{scopeIds:scopes.map(s=>s.id)})]).coverage;
 assert.equal(full.covered,4);assert.equal(full.uncovered,0);assert.equal(full.percentage,100);assert.equal(full.defined,1);
 assert.equal(full.projects[0].count,4,'conforming and NA items within a linked scope are excluded');
});
console.log(checks+' corrective coverage checks passed');
