const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),{spawnSync}=require('node:child_process'),os=require('node:os'),path=require('node:path');
const R=require('../src/corrective-reports-v18.js'),D=require('../src/improvements-domain-v12.js');
const context=vm.createContext({Intl,Date,Map});vm.runInContext(fs.readFileSync('src/jalali.js','utf8')+';globalThis.D=V8DateD;',context);
const items=[{id:'4.1',title:'شناخت سازمان',kind:'clause'},{id:'4.2',title:'ذی‌نفعان',kind:'clause'},{id:'A.5.1',title:'خط‌مشی',kind:'control'},{id:'A.5.2',title:'نقش‌ها',kind:'control'}];
const scopes=[{id:'clause:context',title:'شناخت و دامنه',itemIds:['4.1','4.2']},{id:'annex:governance',title:'حاکمیت',itemIds:['A.5.1','A.5.2']}];
const data=Object.fromEntries(items.map((item,index)=>[item.id,{compliance:[2,3,1,4][index],applicable:true,documents:'شاهد & <نمونه>',observations:'بررسی «واقعی»'}]));
const make=(id,extra={})=>({id,title:'پروژه '+id,goal:'هدف',owner:'مسئول',resources:'منابع',notes:'یادداشت',priority:'high',months:1,start:'2026-01-01',due:'2026-02-01',status:'active',progress:25,mappedIds:[],scopeIds:[],...extra});
const projects=[make('p1',{title:'هویت & <دسترسی>',mappedIds:['4.1','A.5.1'],indicators:['تحقق & <هدف>','پوشش هویت‌ها'],budget:{approved:1000,approvedDate:'2026-01-01',allocations:[{id:'a',amount:100,date:'2026-01-02'},{id:'b',amount:250,date:'2026-01-03'}]}}),make('p2',{months:2,status:'completed',progress:100,mappedIds:['4.2']}),make('p3',{months:3,status:'planned',progress:0,due:'2027-01-01',mappedIds:['A.5.2']})];
const input=options=>({projects,data,items,scopes,today:'2026-11-07',meta:{organization:'سازمان & <آزمون>',auditor:'ممیز آزمایشی',reportNumber:'REP-18'},options,correctiveEngine:D.V13Corrective,budgetEngine:D,findingNames:['انطباق','عدم انطباق جزیی','عدم انطباق کلی','مشاهده','توصیه برای بهبود','نقطه قوت'],formatDate:context.D.format,now:'2026-11-07T12:00:00Z'});
let checks=0;function test(name,fn){fn();checks++;console.log('✓',name);}
(async()=>{
 test('four report variants select the exact declared status, group, project and overdue scope',()=>{
  assert.deepEqual(R.select(projects,{type:'executive',group:'A'},'2026-11-07').map(p=>p.id),['p1']);
  assert.deepEqual(R.select(projects,{type:'register',status:'completed'},'2026-11-07').map(p=>p.id),['p2']);
  assert.deepEqual(R.select(projects,{type:'project',projectId:'p3'},'2026-11-07').map(p=>p.id),['p3']);
  assert.deepEqual(R.select(projects,{type:'followup'},'2026-11-07').map(p=>p.id),['p1','p3']);
  assert.deepEqual(R.select(projects,{type:'followup',overdueOnly:true},'2026-11-07').map(p=>p.id),['p1']);
  assert.throws(()=>R.select(projects,{type:'project'},'2026-11-07'));assert.throws(()=>R.select(projects,{type:'invalid'},'2026-11-07'));
 });
 test('filtered executive coverage reuses the dashboard union and explicitly retains all needed items as denominator',()=>{
  const model=R.model(input({type:'executive',group:'A',status:'active'}));
  assert.equal(model.selected.length,1);assert.equal(model.progress,25);assert.equal(model.metrics.coverage.required,4);assert.equal(model.metrics.coverage.covered,2);assert.equal(model.metrics.coverage.percentage,50);
  assert.equal(model.indicatorCount,2);assert.equal(model.budget.approved,1000);assert.equal(model.budget.allocated,350);
  assert.ok(!model.filterDescription.includes('تمام وضعیت‌ها'));assert.ok(model.filterDescription.includes('در حال اجرا'));
 });
 test('all registered indicators survive detailed reports while older projects show an explicit absent indicator',()=>{
  const model=R.model(input({type:'register'})),xml=R.documentXml(model);
  assert.equal(model.details.find(d=>d.project.id==='p2').indicators.length,0);
  assert.ok(xml.includes('تحقق &amp; &lt;هدف&gt;'));assert.ok(xml.includes('پوشش هویت‌ها'));assert.ok(xml.includes('شاخصی برای این پروژه ثبت نشده است.'));
  assert.ok(xml.includes('هویت &amp; &lt;دسترسی&gt;'));assert.ok(!xml.includes('<دسترسی>'));
 });
 test('a project dossier includes actual budget allocations, linked findings, requested palette and Jalali dates',()=>{
  const model=R.model(input({type:'project',projectId:'p1'})),xml=R.documentXml(model);
  assert.equal(model.details[0].budget.remaining,650);assert.equal(model.details[0].findings.length,2);
  assert.ok(xml.includes('ردیف‌های تخصیص بودجه'));assert.ok(xml.includes('E87945'));assert.ok(xml.includes('C83E50'));
  assert.ok(xml.includes(context.D.format('2026-01-02')));assert.ok(!xml.includes('2026-01-02'));
  assert.ok(xml.includes('شاهد &amp; &lt;نمونه&gt;'));assert.ok(xml.includes('بندها')===false||xml.includes('ارتباط با استاندارد'));
 });
 test('empty scopes and missing metadata remain explicit without invented completion, coverage or budgets',()=>{
  const empty=R.model({...input({type:'executive'}),projects:[],data:{},meta:{}}),xml=R.documentXml(empty);
  assert.equal(empty.progress,null);assert.equal(empty.metrics.coverage.percentage,null);assert.equal(empty.budget.remaining,null);
  assert.ok(xml.includes('نام سازمان ثبت نشده'));assert.ok(xml.includes('فاقد مبنای محاسبه'));assert.ok(xml.includes('پروژه‌ای با معیارهای انتخاب‌شده ثبت نشده است.'));
  assert.throws(()=>R.model({...input({type:'executive'}),today:'2026-02-30'}));
 });
 test('each report package is parseable OOXML with A4, RTL, repeated table headers and resolvable document relationships',()=>{
  const packages=R.types.map(type=>R.files(R.model(input({type:type.id,...(type.id==='project'?{projectId:'p1'}:{})}))));
  const code=String.raw`import sys,json,xml.etree.ElementTree as E,posixpath,zipfile,io
for files in json.load(open(sys.argv[1],encoding='utf-8')):
 for name,content in files.items(): E.fromstring(content)
 root=E.fromstring(files['word/document.xml']);ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
 assert root.find('.//w:pgSz',ns).attrib['{'+ns['w']+'}w']=='11906'
 assert root.find('.//w:bidi',ns) is not None
 assert root.find('.//w:tblHeader',ns) is not None
 rel=E.fromstring(files['word/_rels/document.xml.rels'])
 for item in rel: assert posixpath.normpath('word/'+item.attrib['Target']) in files
 buf=io.BytesIO()
 with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
  for name,content in files.items():z.writestr(name,content)
 with zipfile.ZipFile(buf) as z: assert z.testzip() is None
print('OOXML packages valid')`;
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'didban-report-check-')),file=path.join(temp,'packages.json');fs.writeFileSync(file,JSON.stringify(packages));let result;try{result=spawnSync('python3',['-c',code,file],{encoding:'utf8',timeout:20000});}finally{fs.rmSync(temp,{recursive:true,force:true});}assert.equal(result.status,0,result.stderr||String(result.error));assert.ok(result.stdout.includes('valid'));
 });
 test('original Word report integration adds a separate live-metadata entry without replacing native Word generation',()=>{
  const python=String.raw`from pathlib import Path
import importlib.util
s=importlib.util.spec_from_file_location('integration','src/reports-integration-v18.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
native=Path('src/base-v6.html').read_text();new=m.integrate(native)
assert 'DH(V18CorrectiveReports,{projects,data:assessments,meta,embedded:true})' in new
for anchor in ['async function dsWord(data,projects,risk,meta)','await dsWord(assessments,projects,risk,valid)','DH(\'form\',{onSubmit:run},...DSOrgGroups.map(']:assert new.count(anchor)==native.count(anchor)
print('Original Word preserved')`;
  const result=spawnSync('python3',['-c',python],{encoding:'utf8'});assert.equal(result.status,0,result.stderr);
 });
 let download;class StubZip{constructor(){this.files={};}file(path,content){this.files[path]=content;}async generateAsync(options){assert.equal(options.type,'uint8array');assert.ok(this.files['word/document.xml']);return new Uint8Array([80,75,3,4]);}}
 const output=await R.download({...input({type:'register'}),formatDate:date=>context.D.format(date,true)},{JSZip:StubZip,download:(...args)=>download=args});
 assert.match(output.filename,/^Didban_Corrective_Register_1405-08-16_\d+\.docx$/);assert.equal(download[2],'application/vnd.openxmlformats-officedocument.wordprocessingml.document');assert.ok(download[1] instanceof Uint8Array);
 checks++;console.log('✓ real download adapter emits a DOCX byte stream, MIME type and unique ASCII Jalali filename');
 console.log(checks+' corrective Word report checks passed');
})().catch(error=>{console.error(error);process.exitCode=1;});
