const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict'),{spawnSync}=require('child_process');
const R=require('../src/corrective-reports-v18.js'),D=require('../src/improvements-domain-v12.js');
const goal=('طرح کامل & <کنترل>\n').repeat(2200),project={id:'long-plan',title:'طرح بلند',goal,owner:'مالک',resources:'',notes:'',priority:'high',months:1,start:'2026-11-01',due:'2026-12-01',status:'active',progress:20,mappedIds:['4.1'],scopeIds:[],indicators:[{title:'پوشش کنترل',reviewPeriod:'ماهانه',owner:'مسئول بازبینی'}]};
const model=R.model({projects:[project],items:[{id:'4.1',title:'شناخت سازمان',kind:'clause'}],data:{},scopes:[],options:{type:'project',projectId:project.id},meta:{organization:'آزمون'},today:'2026-11-11',correctiveEngine:D.V13Corrective,budgetEngine:D,formatDate:s=>s,now:'2026-11-11T08:00:00Z'});
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'didban-plan19-'));
try{
 const input=path.join(temp,'input.json');fs.writeFileSync(input,JSON.stringify({goal,xml:R.documentXml(model)}));
 const py=String.raw`import json,sys,xml.etree.ElementTree as E
d=json.load(open(sys.argv[1]));root=E.fromstring(d['xml']);n={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def text(el):
 return ''.join(x.text or '' if x.tag.endswith('}t') else '\n' if x.tag.endswith('}br') else '' for x in el.iter())
found=False
for row in root.findall('.//w:tr',n):
 cells=row.findall('w:tc',n)
 if len(cells)==2 and text(cells[0])=='هدف':
  assert text(cells[1])==d['goal'];found=True
 if row.find('w:trPr/w:tblHeader',n) is None:assert row.find('w:trPr/w:cantSplit',n) is None
assert found
joined=''.join(root.itertext());assert 'ماهانه' in joined and 'مسئول بازبینی' in joined
print('PASS full plan and three-field indicators preserved; body rows can paginate')`;
 const result=spawnSync('python3',['-c',py,input],{encoding:'utf8',timeout:20000});assert.equal(result.status,0,result.stderr||result.error?.message);console.log('✓ complete long plans and structured indicators survive OOXML with splittable body rows');console.log('1 long-plan report check passed');
}finally{fs.rmSync(temp,{recursive:true,force:true});}
