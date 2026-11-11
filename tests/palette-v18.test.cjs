const fs=require('fs'),assert=require('assert/strict'),vm=require('vm'),{spawnSync}=require('child_process'),esbuild=require('esbuild');
const css=fs.readFileSync('src/theme.css','utf8'),root=css.match(/:root\s*\{([\s\S]*?)\n\}/)[1],dark=css.match(/html\[data-theme=dark\]\s*\{([\s\S]*?)\n\}/)[1];
const vars=s=>Object.fromEntries([...s.matchAll(/(--[\w-]+):\s*([^;]+);/g)].map(m=>[m[1],m[2].trim()])),light=vars(root),night={...light,...vars(dark)},resolve=(key,map)=>{let value=map[key];for(let i=0;i<5&&/^var\(--/.test(value);i++)value=map[value.slice(4,-1)];return value;};
const expected={'--audit-good-point':'#168B78','--audit-conformity':'#4FAE66','--audit-improvement':'#3C91CF','--audit-observation':'#D6A13D','--audit-minor':'#E87945','--audit-major':'#C83E50'};
let count=0;function test(name,fn){fn();count++;console.log('✓',name);}
test('all six audit result fills match the supplied palette in both themes and radar aliases',()=>{
 for(const map of [light,night])for(const [key,value]of Object.entries(expected)){assert.equal(resolve(key,map),value);assert.equal(resolve(key.replace('--audit-','--radar-'),map),value);}
 assert.equal(resolve('--good-point',light),'#168B78');assert.equal(resolve('--good-point',night),'#168B78');
});
test('audit recoloring preserves alert colors and implementation colors independently',()=>{
 for(const [key,value]of Object.entries({'--success':'#15803D','--critical':'#DC2626','--minor':'#C2410C','--impl-partial':'#14B8A6','--impl-effective':'#C4B5FD'}))assert.equal(resolve(key,light),value);
 for(const [key,value]of Object.entries({'--success':'#4ADE80','--critical':'#F87171','--minor':'#FB923C','--impl-partial':'#2DD4BF','--impl-effective':'#C4B5FD'}))assert.equal(resolve(key,night),value);
});
const python=String.raw`import importlib.util,json
spec=importlib.util.spec_from_file_location('palette','src/palette-integration-v18.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old="const dcColors=['var(--success)','var(--minor)','var(--danger)','var(--info)','var(--warning)','var(--good-point-fg)'];"+"function dcBadge(value){const c=value==null?'var(--muted)':dcColors[value];return DH('span',{className:'dc-badge',style:{background:'color-mix(in srgb,'+c+' 4%,var(--surface))',color:c,border:'1px solid '+c}},value==null?'ثبت نشده':dcNames[value])}"
print(json.dumps(m.integrate(old)))`;
const output=spawnSync('python3',['-c',python],{encoding:'utf8'});assert.equal(output.status,0,output.stderr);const native=JSON.parse(output.stdout),context=vm.createContext({DH:(type,props,...children)=>({type,props,children}),dcNames:['Conformity','Minor','Major','Observation','Improvement','Good Point']});
vm.runInContext(native+'\nglobalThis.Badge=dcBadge;',context);
test('native badges use the audit palette while preserving enum meanings and neutral unknown',()=>{
 for(const [code,token]of [[5,'good-point'],[0,'conformity'],[4,'improvement'],[3,'observation'],[1,'minor'],[2,'major']]){const b=context.Badge(code);assert.equal(b.props['data-audit-status'],code);assert.equal(b.props.style['--audit-status-color'],'var(--audit-'+token+')');assert.equal(b.props.style.color,'var(--audit-'+token+'-fg)');}
 for(const value of [null,undefined,'5',9])assert.equal(context.Badge(value).props['data-audit-status'],'unknown');
 assert.ok(!fs.readFileSync('src/palette-integration-v18.py','utf8').includes('dcField('),'Current and prior selectors must stay plain');
});
const taxonomy=JSON.parse(fs.readFileSync('src/taxonomy-v13.json','utf8'));
const groups=taxonomy.clauses.map(g=>({...g,id:'clause:'+g.id,kind:'clause'})).concat(taxonomy.groups.map(g=>({...g,id:'annex:'+g.id,kind:'control',itemIds:g.controls})));
const ids=groups.flatMap(g=>g.itemIds),catalog=groups.flatMap(g=>g.itemIds.map(id=>({id,kind:g.kind}))),data=Object.fromEntries([5,0,4,3,1,2].map((compliance,i)=>[ids[i],{compliance}]));data[ids[7]]={compliance:2,applicable:false};
const ui=vm.createContext({DH:(type,props,...children)=>({type,props:props||{},children}),Ia:{Fragment:'fragment'},V19ComplianceSummary:()=>null,V13StandardGroups:()=>groups,J:catalog,V8N:v=>String(v),dcBadge:code=>({type:'badge',props:{code},children:[]}),dcNames:['Conformity','Minor','Major','Observation','Improvement','Good Point']});
vm.runInContext(fs.readFileSync('src/compliance.js','utf8'),ui);
const compiled=esbuild.transformSync(fs.readFileSync('src/dashboard-v10.jsx','utf8'),{loader:'jsx',jsxFactory:'DH',jsxFragment:'Ia.Fragment',target:'es2020'}).code;
vm.runInContext(compiled+'\nglobalThis.View=V10ComplianceDashboard;',ui);
function nodes(node,fn,result=[]){if(Array.isArray(node)){node.forEach(n=>nodes(n,fn,result));return result;}if(!node||typeof node!=='object')return result;if(fn(node))result.push(node);nodes(node.children,fn,result);return result;}
test('the redesigned table retains all domains, ordered equal status columns and N/A-safe totals',()=>{
 const tree=ui.View({data}),table=nodes(tree,n=>n.props?.['data-v18-compliance-table']!==undefined)[0];assert.ok(table);
 assert.equal(nodes(table,n=>n.props?.['data-v13-compliance-group']).length,18);
 assert.equal(nodes(table,n=>n.type==='col').length,8);
 const headers=nodes(table,n=>n.type==='th'&&n.props['data-compliance-column']!==undefined).map(n=>n.props['data-compliance-column']);assert.deepEqual(headers,[5,0,4,3,1,2,6]);
 const totals=nodes(table,n=>n.props?.['data-v18-compliance-total']!==undefined).map(n=>n.props['data-count']);assert.deepEqual(totals,[1,1,1,1,1,1,116]);assert.equal(totals.reduce((a,b)=>a+b,0),122);
 const tableCss=fs.readFileSync('src/audit-palette-v18.css','utf8');assert.ok(tableCss.includes('.v18-status-column{width:10.285714%}'));assert.ok(tableCss.includes('table-layout:fixed'));
});
console.log(count+' audit palette/table checks passed');
