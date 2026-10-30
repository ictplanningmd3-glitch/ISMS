const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const taxonomy=JSON.parse(fs.readFileSync('src/taxonomy-v13.json','utf8'));
const combined=JSON.parse(fs.readFileSync('src/radar-taxonomy-v16.json','utf8')).groups;
const canonical=taxonomy.clauses.map(g=>({...g,id:'clause:'+g.id,kind:'clause'})).concat(taxonomy.groups.map(g=>({...g,id:'annex:'+g.id,kind:'control',itemIds:g.controls})));
const context=vm.createContext({V16RadarCombined:combined,V13StandardGroups:()=>structuredClone(canonical)});
vm.runInContext(fs.readFileSync('src/compliance.js','utf8')+'\n'+fs.readFileSync('src/radar-v16.js','utf8')+'\nglobalThis.R=V16Radar;',context);
const R=context.R,plain=x=>JSON.parse(JSON.stringify(x));let checks=0;
function test(name,fn){fn();checks++;console.log('✓',name);}
test('separate views keep the user’s exhaustive eight and ten canonical domains',()=>{
 for(const [kind,n,count]of [['clause',8,30],['control',10,93]]){
  const groups=plain(R.groups(kind));assert.equal(groups.length,n);assert.equal(groups.flatMap(g=>g.itemIds).length,count);
  assert.deepEqual(groups.map(g=>[g.id,g.itemIds]),canonical.filter(g=>g.kind===kind).map(g=>[g.id,g.itemIds]));
 }
});
test('whole-standard analytical grouping partitions all 123 items exactly once',()=>{
 const groups=plain(R.groups('all')),ids=groups.flatMap(g=>g.itemIds),expected=canonical.flatMap(g=>g.itemIds);
 assert.equal(groups.length,10);assert.equal(new Set(groups.map(g=>g.id)).size,10);assert.equal(ids.length,123);assert.equal(new Set(ids).size,123);assert.deepEqual(ids.sort(),expected.sort());
 assert.deepEqual(groups.map(g=>g.itemIds.length),[13,10,16,11,14,9,9,19,13,9]);
 for(const g of groups){assert.ok(g.title&&g.short&&g.english);assert.equal(g.clauseCount+g.controlCount,g.itemIds.length);}
});
test('mode groups return independent collections without mutating the canonical map',()=>{
 const first=R.groups('all');first[0].itemIds.pop();assert.equal(R.groups('all')[0].itemIds.length,13);
 const second=R.groups('clause');second[0].itemIds.pop();assert.equal(R.groups('clause')[0].itemIds.length,4);
});
test('implementation scores use native 0–4 weights, exclude N/A and keep unassessed in denominator',()=>{
 const data={'4.1':{status:4,compliance:2},'4.2':{status:2,compliance:5},'4.3':{status:4,applicable:false},'A.5.1':{status:3,compliance:0}};
 const group=R.implementation('clause',data)[0];assert.equal(group.score,50);assert.equal(group.assessed,2);assert.equal(group.eligible,3);assert.equal(group.total,4);
 const full=R.implementation('all',data)[0];assert.equal(full.eligible,12);assert.equal(full.assessed,3);assert.equal(full.score,Math.round(225/12));
});
test('implementation ignores compliance-only records and invalid states while zero is assessed',()=>{
 const data={'4.1':{compliance:5},'4.2':{status:0},'4.3':{status:'4'},'4.4':{status:9}};
 const group=R.implementation('clause',data)[0];assert.equal(group.score,0);assert.equal(group.assessed,1);assert.equal(group.eligible,4);
 assert.deepEqual(plain(R.implementation('all',{})).map(g=>g.assessed),Array(10).fill(0));
});
test('all non-applicable is distinguished from assessed zero',()=>{
 const data=Object.fromEntries(canonical.flatMap(g=>g.itemIds).map(id=>[id,{status:4,applicable:false}]));
 for(const mode of ['clause','control','all'])for(const g of R.implementation(mode,data)){assert.equal(g.eligible,0);assert.equal(g.assessed,0);assert.equal(g.score,0);assert.ok(g.total>0);}
});
test('all valid scores match the original application calculation for each domain',()=>{
 const native=fs.readFileSync('src/base-v6.html','utf8'),start=native.indexOf('function Kp('),end=native.indexOf('function Kl(',start);
 vm.runInContext(native.slice(start,end)+'\nglobalThis.K=Kp;',context);
 const ids=canonical.flatMap(g=>g.itemIds),data=Object.fromEntries(ids.filter((_,i)=>i%7!==0).map((id,i)=>[id,{status:i%5,applicable:i%11!==0}]));
 for(const mode of ['clause','control','all'])for(const g of R.implementation(mode,data))assert.equal(g.score,context.K(data,g.itemIds.map(id=>({id}))));
});
test('six ordered bands fit the largest view, keep unknown outside and do not collapse distinct dots',()=>{
 for(const mode of ['clause','control','all']){
  const groups=R.groups(mode),n=groups.length;
  for(const value of [5,0,4,3,1,2,null]){
   const points=groups.flatMap((g,sector)=>g.itemIds.map((_,index)=>R.point(index,g.itemIds.length,value,sector,n)));
   assert.ok(points.every(p=>Number.isFinite(p.x)&&Number.isFinite(p.y)));
   assert.equal(new Set(points.map(p=>p.x.toFixed(4)+','+p.y.toFixed(4))).size,points.length);
   for(let i=0;i<points.length;i++)for(let j=i+1;j<points.length;j++)assert.ok(Math.hypot(points[i].x-points[j].x,points[i].y-points[j].y)>=4.95,'distinct dot spacing');
   assert.ok(points.every(p=>value===null?p.radius>190:p.radius<=188));
  }
  for(const g of groups){const radii=[5,0,4,3,1,2].map(value=>g.itemIds.map((_,i)=>R.point(i,g.itemIds.length,value,0,n).radius));for(let rank=1;rank<6;rank++)assert.ok(Math.min(...radii[rank])>Math.max(...radii[rank-1]));}
 }
});
console.log(checks+' radar checks passed');
