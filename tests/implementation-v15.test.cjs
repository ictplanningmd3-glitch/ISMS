const assert=require('node:assert/strict');
const D=require('../src/implementation-v15.js');
let checks=0;const test=(name,fn)=>{fn();checks++;console.log('✓',name);};
const items=[
 {id:'4.1',kind:'clause',title:'شناخت سازمان',english:'Organizational context',conceptLabel:'شناخت و دامنه'},
 {id:'4.2',kind:'clause',title:'ذینفعان',english:'Interested parties'},
 {id:'5.1',kind:'clause',title:'رهبری',english:'Leadership'},
 ...Array.from({length:7},(_,i)=>({id:'A.5.'+(i+1),kind:'control',title:'کنترل '+(i+1),english:'Control '+(i+1)}))
];
const data={'4.1':{status:0,compliance:5},'4.2':{status:1,compliance:2},'5.1':{status:2,compliance:0},'A.5.1':{status:3,compliance:2},'A.5.2':{status:4,compliance:1},'A.5.3':{status:0,compliance:0},'A.5.4':{status:'4',compliance:5},'A.5.5':{status:8},'A.5.7':{status:4,applicable:false}};
test('implementation classification uses only integer implementation status, independently of audit finding',()=>{
 assert.deepEqual(D.statuses.map(s=>s.key),[0,1,2,3,4,'unknown']);
 for(let status=0;status<5;status++)for(let compliance=0;compliance<6;compliance++)assert.equal(D.status({status,compliance}),status);
 for(const row of [undefined,null,{}, {status:null},{status:''},{status:'0'},{status:false},{status:-1},{status:5},{status:2.5}])assert.equal(D.status(row),'unknown');
});
test('summary includes unassessed items and excludes only explicitly non-applicable items',()=>{
 const s=D.summary(items,data);assert.equal(s.total,9);assert.equal(s.assessed,6);assert.equal(s.unknown,3);
 assert.deepEqual(s.counts,{'0':2,'1':1,'2':1,'3':1,'4':1,unknown:3});
 assert.equal(s.segments.reduce((n,s)=>n+s.count,0),s.total);
 assert.ok(Math.abs(s.segments.reduce((n,s)=>n+s.percentage,0)-100)<1e-10);
 assert.deepEqual(s.segments.map(s=>[s.clauses,s.controls]),[[1,1],[1,0],[1,0],[0,1],[0,1],[0,3]]);
});
test('canonical group stacks share source counts without double counting repeated identifiers',()=>{
 const scopes=[{id:'clause:context',kind:'clause',itemIds:['4.1','4.2','4.2']},{id:'annex:governance',kind:'control',itemIds:['A.5.1','A.5.2','A.5.3','A.5.4','A.5.5','A.5.6','A.5.7']},{id:'empty',kind:'control',itemIds:['A.5.7']}];
 const groups=D.groups(items,data,scopes);assert.deepEqual(groups.map(g=>g.total),[2,6,0]);
 assert.equal(groups[0].counts['0'],1);assert.equal(groups[1].counts.unknown,3);
 assert.ok(groups[2].segments.every(s=>s.count===0&&s.percentage===0));
});
test('each status card list matches its count, across both requirements and Annex A',()=>{
 const s=D.summary(items,data);for(const segment of s.segments){const rows=D.select(items,data,{status:segment.key});assert.equal(rows.length,segment.count);assert.ok(rows.every(item=>D.status(data[item.id])===segment.key));}
 assert.deepEqual(D.select(items,data,{status:'unknown'}).map(x=>x.id),['A.5.4','A.5.5','A.5.6']);
 assert.deepEqual(D.select(items,data,{status:0}).map(x=>x.id),['4.1','A.5.3']);
});
test('list kind, canonical heading and search filters intersect while keeping all audit rows actionable',()=>{
 assert.deepEqual(D.select(items,data,{status:0,kind:'clause'}).map(x=>x.id),['4.1']);
 assert.deepEqual(D.select(items,data,{status:0,scope:{itemIds:['A.5.3']}}).map(x=>x.id),['A.5.3']);
 assert.deepEqual(D.select(items,data,{status:'all',query:'Organizational'}).map(x=>x.id),['4.1']);
 assert.deepEqual(D.select(items,data,{status:0,query:'شناخت و دامنه'}).map(x=>x.id),['4.1']);
 assert.equal(D.select(items,data,{status:4,kind:'clause'}).length,0);
});
test('empty and fully non-applicable catalogs show no fabricated percentages or assessed cases',()=>{
 for(const [catalog,records]of [[[],{}],[items,Object.fromEntries(items.map(x=>[x.id,{status:4,applicable:false}]))]]){const s=D.summary(catalog,records);assert.equal(s.total,0);assert.equal(s.assessed,0);assert.equal(s.unknown,0);assert.ok(s.segments.every(x=>x.percentage===0&&x.count===0));}
 const only=D.summary([items[0]],{});assert.equal(only.counts.unknown,1);assert.equal(only.segments.at(-1).percentage,100);
});
test('editing a saved audit implementation status updates counts and selected-list membership immediately',()=>{
 const next=structuredClone(data);next['A.5.6']={status:4,compliance:2};const before=D.summary(items,data),after=D.summary(items,next);
 assert.equal(after.counts.unknown,before.counts.unknown-1);assert.equal(after.counts['4'],before.counts['4']+1);
 assert.equal(D.select(items,next,{status:'unknown'}).some(x=>x.id==='A.5.6'),false);
 assert.equal(D.select(items,next,{status:4}).some(x=>x.id==='A.5.6'),true);
 assert.equal(next['A.5.6'].compliance,2);
});
console.log(checks+' implementation dashboard checks passed');
