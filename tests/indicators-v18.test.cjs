const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),{spawnSync}=require('child_process');
const source=fs.readFileSync('src/improvements-v12.jsx','utf8');
const context=vm.createContext({V13StandardGroups:()=>[{id:'clause:context',itemIds:['4.1']}],J:[{id:'4.1'}],so:{high:'زیاد'},io:{active:'در حال اجرا'},Gs:s=>/^\d{4}-\d{2}-\d{2}$/.test(s),fe:()=> '2027-02-01',V12Imp:require('../src/improvements-domain-v12.js')});
vm.runInContext(source.slice(0,source.indexOf('const V12Num='))+'\nglobalThis.API={values:V18ProjectIndicatorValues,validate:V12ValidateProject};',context);
const A=context.API,plain=x=>JSON.parse(JSON.stringify(x)),project={id:'ind18',title:'پروژه شاخص',goal:'هدف',owner:'مسئول',resources:'منابع',notes:'یادداشت',updated:'2027-01-01T00:00:00Z',start:'2027-01-01',due:'2027-02-01',priority:'high',status:'active',months:1,progress:20,mappedIds:['4.1'],scopeIds:[]};
let checks=0;function test(name,fn){fn();checks++;console.log('✓',name);}
test('older projects normalize missing indicators to an empty list without changing other data',()=>{
 const normalized=plain(A.validate(project));assert.deepEqual(normalized.indicators,[]);for(const key of Object.keys(project))assert.deepEqual(normalized[key],project[key]);
});
test('saving retains ordered literal textbox content, trims edges and removes only blank rows',()=>{
 const raw=['  درصد پوشش کنترل  ','   ','میانگین زمان <بازیابی> & پاسخ','درصد پوشش کنترل'];
 assert.deepEqual(plain(A.values(raw)),['درصد پوشش کنترل','میانگین زمان <بازیابی> & پاسخ','درصد پوشش کنترل']);
 assert.deepEqual(raw,['  درصد پوشش کنترل  ','   ','میانگین زمان <بازیابی> & پاسخ','درصد پوشش کنترل']);
});
test('indicators survive validation and a full JSON backup/restore round trip',()=>{
 const normalized=A.validate({...project,indicators:['نرخ تحقق هدف','زمان رفع یافته']});
 const restored=A.validate(JSON.parse(JSON.stringify(normalized)));assert.deepEqual(plain(restored.indicators),['نرخ تحقق هدف','زمان رفع یافته']);
 const copy=plain(restored);copy.indicators[0]='شاخص نسخه کپی';assert.equal(normalized.indicators[0],'نرخ تحقق هدف');
});
test('malformed indicator payloads and oversized rows are rejected instead of silently discarded',()=>{
 for(const bad of [null,'متن',{},[1],['شاخص',null],Array(101).fill('شاخص'),['x'.repeat(1001)]])assert.throws(()=>A.validate({...project,indicators:bad}),/شاخص/);
 assert.equal(A.values(Array(100).fill('x'.repeat(1000))).length,100);assert.deepEqual(plain(A.values([])),[]);
});
test('native Word/Excel project tables export normalized indicator rows with real newlines',()=>{
 const py=String.raw`from pathlib import Path
import importlib.util,json
spec=importlib.util.spec_from_file_location('m','src/improvements-integration-v12.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
print(json.dumps(m.integrate(Path('src/base-v6.html').read_text())))`;
 const result=spawnSync('python3',['-c',py],{encoding:'utf8',maxBuffer:8*1024*1024});assert.equal(result.status,0,result.stderr);
 const html=JSON.parse(result.stdout);assert.ok(html.includes("'شاخص‌های اقدام اصلاحی'"));
 const join=html.match(/\(p\.indicators\|\|\[\]\)\.join\(([^)]+)\)/);assert.ok(join,'Native report mapping includes indicators');
 const joined=vm.runInNewContext("['شاخص اول','شاخص دوم'].join("+join[1]+")");assert.equal(joined,'شاخص اول\nشاخص دوم');
});
console.log(checks+' corrective indicator checks passed');
