const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const source=fs.readFileSync('src/improvements-v12.jsx','utf8');
const D=require('../src/improvements-domain-v12.js'),R=require('../src/corrective-reports-v18.js');
const context=vm.createContext({V13StandardGroups:()=>[{id:'clause:context',itemIds:['4.1']}],J:[{id:'4.1'}],so:{high:'زیاد'},io:{active:'در حال اجرا'},Gs:s=>/^\d{4}-\d{2}-\d{2}$/.test(s),fe:()=> '2027-02-01',V12Imp:D});
vm.runInContext(source.slice(0,source.indexOf('const V12Num='))+'\nglobalThis.API={values:V18ProjectIndicatorValues,texts:V19ProjectIndicatorTexts,validate:V12ValidateProject};',context);
const A=context.API,plain=x=>JSON.parse(JSON.stringify(x));
const project={id:'v19',title:'طرح کامل',goal:'هدف',owner:'مسئول',resources:'',notes:'',updated:'2027-01-01T00:00:00Z',start:'2027-01-01',due:'2027-02-01',priority:'high',status:'active',months:1,progress:20,mappedIds:['4.1'],scopeIds:[]};
let checks=0;function test(name,fn){fn();checks++;console.log('✓',name);}
test('a complete 50000-character project plan preserves paragraphs and resources are optional',()=>{
 const goal='بخش اول طرح\n\n'+('متن کامل طرح '.repeat(5000)).slice(0,49987);
 assert.equal(goal.length,50000);
 const saved=plain(A.validate({...project,goal,resources:undefined}));assert.equal(saved.goal,goal);assert.equal(saved.resources,'');
 assert.equal(A.validate({...project,resources:''}).resources,'');
 assert.throws(()=>A.validate({...project,goal:goal+'x'}),/شرح/);
 assert.throws(()=>A.validate({...project,resources:42}));
});
test('legacy strings and structured rows migrate to three-field records without changing their titles',()=>{
 const raw=[' شاخص قدیمی ',{title:' پوشش کنترل ',reviewPeriod:' ماهانه ',owner:' فناوری اطلاعات '},{title:'',reviewPeriod:'',owner:''}];
 assert.deepEqual(plain(A.values(raw)),[{title:'شاخص قدیمی',reviewPeriod:'',owner:''},{title:'پوشش کنترل',reviewPeriod:'ماهانه',owner:'فناوری اطلاعات'}]);
 assert.equal(raw[0],' شاخص قدیمی ');assert.equal(raw[1].reviewPeriod,' ماهانه ');
 const restored=plain(A.validate(JSON.parse(JSON.stringify(A.validate({...project,indicators:raw})))));
 assert.deepEqual(restored.indicators,plain(A.values(raw)));
});
test('partial row metadata needs a title and malformed or oversized structured fields are refused',()=>{
 for(const row of [{title:'',reviewPeriod:'فصلی',owner:''},{title:' ',owner:'متولی'},{title:2},{title:'شاخص',reviewPeriod:3},{title:'شاخص',owner:false},{title:'x'.repeat(1001)},{title:'شاخص',reviewPeriod:'x'.repeat(201)},{title:'شاخص',owner:'x'.repeat(201)}])assert.throws(()=>A.values([row]),/شاخص|عنوان/);
 assert.deepEqual(plain(A.values([{title:'شاخص',reviewPeriod:'',owner:''}])),[{title:'شاخص',reviewPeriod:'',owner:''}]);
});
test('native and standalone Word reports include period and owner as literal text, for old and new data',()=>{
 const rows=[{title:'پوشش <کنترل> & هویت',reviewPeriod:'ماهانه',owner:'متولی & عملیات'},'شاخص قدیمی'];
 const formatted=plain(A.texts(rows));assert.equal(formatted[0],'پوشش <کنترل> & هویت — دوره بازبینی: ماهانه — متولی اجرایی: متولی & عملیات');assert.equal(formatted[1],'شاخص قدیمی');
 const items=[{id:'4.1',title:'شناخت',kind:'clause'}],p={...project,indicators:rows};
 for(const type of ['executive','register','project','followup']){
  const model=R.model({projects:[p],data:{'4.1':{compliance:2,applicable:true}},items,scopes:[],today:'2027-01-15',options:{type,projectId:p.id},correctiveEngine:D.V13Corrective,budgetEngine:D,findingNames:['انطباق','جزئی','کلی'],formatDate:s=>s,now:'2027-01-15T00:00:00Z'});
  assert.deepEqual(model.details[0].indicators,formatted);
  const xml=R.documentXml(model);assert.ok(xml.includes('دوره بازبینی: ماهانه'));assert.ok(xml.includes('متولی اجرایی: متولی &amp; عملیات'));assert.ok(xml.includes('&lt;کنترل&gt;'));assert.ok(!xml.includes('[object Object]'));
 }
});
console.log(checks+' corrective form v19 checks passed');
