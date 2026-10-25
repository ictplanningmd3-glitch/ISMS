const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const c=vm.createContext({Object,Math});vm.runInContext(fs.readFileSync('src/compliance.js','utf8')+'\nglobalThis.R=V9Compliance;',c);const R=c.R;
let checks=0;function test(name,fn){fn();checks++;console.log('✓',name);}
test('Good Point appends value 5 while audit codes retain their meanings',()=>{assert.equal(R.levels.length,6);for(const [value,rank] of [[2,0],[1,1],[4,2],[3,3],[0,4],[5,5]])assert.equal(R.level(value).rank,rank);assert.equal(R.level(5).english,'Good Point');assert.equal(R.level(5).token,'--radar-good-point');});
test('Good Point remains separate from conformity and unknown',()=>{const s=R.summary(['a','b','c','d','e'],{a:{status:0,compliance:5},b:{status:4,compliance:5},c:{compliance:0},d:{status:4},e:{compliance:'5'}});assert.equal(s.goodPoints,2);assert.equal(s.conformity,1);assert.equal(s.unknown,2);assert.equal(s.selected,3);assert.equal(s.total,5);});
test('six finding levels remain ordered inside radar across largest group',()=>{for(let i=0;i<20;i++){const radii=[2,1,4,3,0,5].map(value=>R.point(i,20,value,0,10).radius);assert.ok(radii.every((r,k)=>r<190&&(k===0||r>radii[k-1])));assert.ok(R.point(i,20,null,0,10).radius>190);}});
console.log(checks+' Good Point checks passed');
