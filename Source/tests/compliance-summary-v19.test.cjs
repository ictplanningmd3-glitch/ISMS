const assert=require('node:assert/strict'),D=require('../src/compliance-summary-v19.js');
const items=Array.from({length:9},(_,i)=>({id:'A.'+(i+1),kind:'control'}));
let checks=0;function test(name,fn){fn();checks++;console.log('✓',name);}
test('overall compliance is the union of the four user-selected positive outcomes only',()=>{
 const data=Object.fromEntries([5,0,4,3,1,2].map((compliance,i)=>[items[i].id,{compliance,status:4}]));
 const s=D.summary(items.slice(0,6),data);assert.equal(s.total,6);assert.equal(s.positive,4);assert.equal(s.negative,2);assert.equal(s.unknown,0);assert.equal(s.rate,4/6*100);assert.deepEqual(D.positiveCodes,[5,0,4,3]);
 for(let code=0;code<=5;code++)assert.equal(D.summary([items[0]],{[items[0].id]:{compliance:code,status:0}}).rate,[5,0,4,3].includes(code)?100:0);
});
test('unknown results remain in the applicable denominator and non-applicable items are excluded',()=>{
 const data={'A.1':{compliance:5},'A.2':{compliance:0,applicable:false},'A.3':{compliance:'0'},'A.4':{compliance:null},'A.5':{compliance:8},'A.6':{compliance:4},'A.7':{status:4}};
 const s=D.summary(items,data);assert.equal(s.total,8);assert.equal(s.positive,2);assert.equal(s.unknown,6);assert.equal(s.rate,25);assert.equal(s.counts['0'],0);assert.equal(s.segments.reduce((n,x)=>n+x.count,0),s.total);assert.equal(s.segments.reduce((n,x)=>n+x.percentage,0),100);
});
test('all-unknown and zero-applicable datasets never fabricate an assessed success',()=>{
 const unknown=D.summary(items,{});assert.equal(unknown.rate,0);assert.equal(unknown.unknown,9);assert.equal(unknown.segments.at(-1).percentage,100);
 for(const s of [D.summary([],{}),D.summary(items,Object.fromEntries(items.map(x=>[x.id,{applicable:false,compliance:5}])))] ){
  assert.equal(s.total,0);assert.equal(s.rate,null);assert.equal(s.positive,0);assert.ok(s.segments.every(x=>x.count===0&&x.percentage===0));
 }
});
test('one catalog item is counted once and audit/implementation enums remain independent',()=>{
 const source={'A.1':{compliance:4,status:0},'A.2':{compliance:2,status:4}};const copy=JSON.stringify(source);
 const s=D.summary([items[0],items[0],items[1]],source);assert.equal(s.total,2);assert.equal(s.rate,50);assert.equal(JSON.stringify(source),copy);
 assert.deepEqual(s.segments.map(x=>x.key),[5,0,4,3,1,2,'unknown']);
});
test('last audit update comes only from valid timestamps in the applicable catalog',()=>{
 const data={'A.1':{compliance:0,updated:'2026-01-05T10:00:00Z'},'A.2':{compliance:3,updated:'2026-02-05T12:00:00+03:30'},'A.3':{compliance:1,updated:'2027-01-01T00:00:00Z',applicable:false},'A.4':{updated:'not a date'},'A.5':{updated:'2026-02-30'},other:{updated:'2030-01-01T00:00:00Z'}};
 assert.equal(D.summary(items,data).lastUpdated,'2026-02-05T12:00:00+03:30');
 assert.equal(D.summary(items,{}).lastUpdated,null);assert.equal(D.validUpdated('2026-02-30'),false);assert.equal(D.validUpdated('2026-13-01T00:00:00Z'),false);assert.equal(D.validUpdated('2024-02-29T23:00:00Z'),true);
});
test('a saved audit edit immediately changes the aggregate without rewriting other records',()=>{
 const before={'A.1':{compliance:1},'A.2':{compliance:0}},after=structuredClone(before);after['A.1'].compliance=3;
 assert.equal(D.summary(items.slice(0,2),before).rate,50);assert.equal(D.summary(items.slice(0,2),after).rate,100);assert.equal(before['A.1'].compliance,1);
});
console.log(checks+' aggregate compliance checks passed');
