/* The actual integrated native catalog must use one exhaustive, disjoint taxonomy. */
const fs=require('fs'),assert=require('assert/strict'),vm=require('vm'),{spawnSync}=require('child_process');
(async()=>{
 const taxonomy=JSON.parse(fs.readFileSync('src/taxonomy-v13.json','utf8'));
 const expectedNames=["Governance & Information Security Management","Asset & Information Protection","Identity & Access Management","Human Resources & Security Awareness","Physical & Environmental Security","Infrastructure & Network Security","Security Operations & Monitoring","Data Protection & Resilience","Secure Development & Change Management","Third Party, Incident & Continuity"];
 const expectedCounts=[15,6,9,8,14,5,8,6,10,12];
 const expectedControls=[["A.5.1","A.5.2","A.5.3","A.5.4","A.5.5","A.5.6","A.5.7","A.5.8","A.5.31","A.5.32","A.5.33","A.5.34","A.5.35","A.5.36","A.5.37"],["A.5.9","A.5.10","A.5.11","A.5.12","A.5.13","A.5.14"],["A.5.15","A.5.16","A.5.17","A.5.18","A.8.2","A.8.3","A.8.4","A.8.5","A.8.18"],["A.6.1","A.6.2","A.6.3","A.6.4","A.6.5","A.6.6","A.6.7","A.6.8"],["A.7.1","A.7.2","A.7.3","A.7.4","A.7.5","A.7.6","A.7.7","A.7.8","A.7.9","A.7.10","A.7.11","A.7.12","A.7.13","A.7.14"],["A.8.1","A.8.20","A.8.21","A.8.22","A.8.23"],["A.8.6","A.8.7","A.8.8","A.8.9","A.8.15","A.8.16","A.8.17","A.8.19"],["A.8.10","A.8.11","A.8.12","A.8.13","A.8.14","A.8.24"],["A.8.25","A.8.26","A.8.27","A.8.28","A.8.29","A.8.30","A.8.31","A.8.32","A.8.33","A.8.34"],["A.5.19","A.5.20","A.5.21","A.5.22","A.5.23","A.5.24","A.5.25","A.5.26","A.5.27","A.5.28","A.5.29","A.5.30"]];
 const expectedClauseNames=["Organizational Context, Scope & Interested Parties","Leadership & Governance","Risk Management","Objectives & Change Planning","Resources, Competence & Awareness","Communication & Documented Information","Operational Control","Performance Evaluation & Improvement"];
 const expectedClauseIds=[["4.1","4.2","4.3","4.4"],["5.1","5.2","5.3"],["6.1.1","6.1.2","6.1.3"],["6.2","6.3"],["7.1","7.2","7.3"],["7.4","7.5.1","7.5.2","7.5.3"],["8.1","8.2","8.3"],["9.1","9.2.1","9.2.2","9.3.1","9.3.2","9.3.3","10.1","10.2"]];
 let checks=0;const test=(name,fn)=>{fn();checks++;console.log('✓',name);};
 test('the authoritative user mapping covers each of the 93 official controls exactly once',()=>{
  assert.deepEqual(taxonomy.groups.map(g=>g.english),expectedNames);
  assert.deepEqual(taxonomy.groups.map(g=>g.controls.length),expectedCounts);
  assert.deepEqual(taxonomy.groups.map(g=>g.controls),expectedControls);
  assert.deepEqual(taxonomy.clauses.map(g=>g.english),expectedClauseNames);
  assert.deepEqual(taxonomy.clauses.map(g=>g.itemIds),expectedClauseIds);
  assert.equal(taxonomy.clauses[0].title,'شناخت سازمان، دامنه و ذینفعان');assert.equal(taxonomy.clauses[2].title,'مدیریت ریسک');assert.deepEqual(taxonomy.clauses.map(g=>g.itemIds.length),[4,3,3,2,3,4,3,8]);
  const clauses=taxonomy.clauses.flatMap(g=>g.itemIds);assert.equal(clauses.length,30);assert.equal(new Set(clauses).size,30);
  const actual=taxonomy.groups.flatMap(g=>g.controls),expected=[[5,37],[6,8],[7,14],[8,34]].flatMap(([domain,n])=>Array.from({length:n},(_,i)=>`A.${domain}.${i+1}`));
  assert.equal(actual.length,93);assert.equal(new Set(actual).size,93);assert.deepEqual([...actual].sort(),expected.sort());
 });
 const python=String.raw`from pathlib import Path
import importlib.util,json
spec=importlib.util.spec_from_file_location('taxonomy','src/taxonomy-integration-v13.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
print(json.dumps(m.integrate(Path('src/base-v6.html').read_text())))`;
 const built=spawnSync('python3',['-c',python],{encoding:'utf8',maxBuffer:10*1024*1024});assert.equal(built.status,0,built.stderr);
 const html=JSON.parse(built.stdout),script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).find(s=>s.includes('J=Yp.map'));
 const {parse}=await import('@babel/parser'),{default:generate}=await import('@babel/generator'),ast=parse(script),parts=[],declarations=new Set(['Yp','GS','Yl','V13ClauseGroups','J']),functions=new Set(['V13StandardGroups','DSFindingRows']);
 function visit(node){if(!node||typeof node!=='object')return;if(node.type==='VariableDeclarator'&&declarations.has(node.id?.name)){parts.push('const '+generate(node).code+';');return;}if(node.type==='FunctionDeclaration'&&functions.has(node.id?.name)){parts.push(generate(node).code);return;}for(const [key,value]of Object.entries(node)){if(['loc','extra','comments'].includes(key))continue;if(Array.isArray(value))value.forEach(visit);else if(value&&typeof value==='object')visit(value);}}
 visit(ast);assert.equal(parts.length,7);const context=vm.createContext({Object,Array,Map,Set,DSReviewer:()=>'',DSDescription:()=>'',dcNames:['Conformity','Minor','Major','Observation','Improvement','Good Point']});
 vm.runInContext(parts.join('\n')+'\nglobalThis.API={J,Yl,V13StandardGroups,DSFindingRows};',context);const A=context.API;
 test('native catalog metadata and audit finding groups resolve to the canonical domain',()=>{
  const controls=A.J.filter(x=>x.kind==='control');assert.equal(controls.length,93);
  for(const item of controls){const group=taxonomy.groups.find(g=>g.controls.includes(item.id));assert.ok(group);assert.equal(item.concept,group.id);assert.equal(item.conceptLabel,group.title);assert.equal(item.conceptEnglish,group.english);}
  const clauses=A.J.filter(x=>x.kind==='clause');assert.equal(clauses.length,30);for(const item of clauses){const group=taxonomy.clauses.find(g=>g.itemIds.includes(item.id));assert.ok(group);assert.equal(item.clauseConcept,group.id);assert.equal(item.conceptLabel,group.title);assert.equal(item.conceptEnglish,group.english);}
  const findings=A.DSFindingRows({},{});for(const row of findings){const group=row[2].startsWith('A.')?taxonomy.groups.find(g=>g.controls.includes(row[2])):taxonomy.clauses.find(g=>g.itemIds.includes(row[2]));assert.equal(row[1],group.title);}
 });
 test('shared project/chart scopes contain all requirements and controls without duplicates',()=>{
  const scopes=A.V13StandardGroups();assert.equal(scopes.length,18);assert.equal(scopes.filter(s=>s.kind==='clause').length,8);assert.equal(scopes.filter(s=>s.kind==='control').length,10);
  for(const [index,group]of taxonomy.clauses.entries()){const scope=scopes[index];assert.equal(scope.id,'clause:'+group.id);assert.equal(scope.english,group.english);assert.deepEqual([...scope.itemIds],group.itemIds);}
  const ids=scopes.flatMap(s=>s.itemIds);assert.equal(ids.length,A.J.length);assert.equal(new Set(ids).size,A.J.length);
  for(const [index,group]of taxonomy.groups.entries()){const scope=scopes[index+8];assert.equal(scope.id,'annex:'+group.id);assert.equal(scope.english,group.english);assert.deepEqual([...scope.itemIds],group.controls);}
 });
 console.log(checks+' taxonomy integration checks passed');
})().catch(error=>{console.error(error);process.exitCode=1;});
