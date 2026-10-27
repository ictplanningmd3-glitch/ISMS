/* Implementation is independent of audit compliance. Missing or invalid status is unassessed. */
var V15Implementation=(()=>{
 const statuses=Object.freeze([
  {key:0,label:'اجرا نشده',english:'Not Implemented',token:'--impl-none',ink:'--impl-none-fg'},
  {key:1,label:'در حال برنامه‌ریزی',english:'Planned',token:'--impl-planned',ink:'--impl-planned-fg'},
  {key:2,label:'اجرای جزئی',english:'Partially Implemented',token:'--impl-partial',ink:'--impl-partial-fg'},
  {key:3,label:'اجرا شده',english:'Implemented',token:'--impl-implemented',ink:'--impl-implemented-fg'},
  {key:4,label:'اثربخشی تأیید شده',english:'Effectiveness Confirmed',token:'--impl-effective',ink:'--impl-effective-fg'},
  {key:'unknown',label:'ارزیابی نشده',english:'Unassessed',token:'--impl-unknown',ink:'--impl-unknown-fg'}
 ].map(Object.freeze));
 const status=record=>Number.isInteger(record?.status)&&record.status>=0&&record.status<=4?record.status:'unknown';
 const definition=key=>statuses.find(s=>String(s.key)===String(key));
 function eligible(items,data){const seen=new Set();return items.filter(item=>{if(!item?.id||seen.has(item.id))return false;seen.add(item.id);return data[item.id]?.applicable!==false;});}
 function summary(items,data){
  const rows=eligible(items,data),counts=Object.fromEntries(statuses.map(s=>[String(s.key),0]));
  for(const item of rows)counts[String(status(data[item.id]))]++;
  const total=rows.length,lastPositive=statuses.reduce((last,s,index)=>counts[String(s.key)]?index:last,-1);let assigned=0;
  const segments=statuses.map((s,index)=>{const matching=rows.filter(item=>status(data[item.id])===s.key),count=matching.length,percentage=!total||!count?0:index===lastPositive?100-assigned:count/total*100;assigned+=percentage;return {...s,count,percentage,clauses:matching.filter(item=>item.kind==='clause').length,controls:matching.filter(item=>item.kind==='control').length};});
  return {total,counts,segments,assessed:total-counts.unknown,unknown:counts.unknown};
 }
 function groups(items,data,scopes){const catalog=new Map(items.map(item=>[item.id,item]));return scopes.map(scope=>({...scope,...summary(scope.itemIds.map(id=>catalog.get(id)).filter(Boolean),data)}));}
 function select(items,data,options={}){
  const key=options.status==null||options.status==='all'?'all':definition(options.status)?.key,query=String(options.query||'').trim().toLocaleLowerCase(),scope=options.scope||null,ids=scope?new Set(scope.itemIds):null;
  return eligible(items,data).filter(item=>(key==='all'||status(data[item.id])===key)&&(!options.kind||options.kind==='all'||item.kind===options.kind)&&(!ids||ids.has(item.id))&&(!query||[item.id,item.title,item.english,item.conceptLabel,item.conceptEnglish,data[item.id]?.owner,data[item.id]?.reviewer].join(' ').toLocaleLowerCase().includes(query)));
 }
 return {statuses,status,definition,eligible,summary,groups,select};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=V15Implementation;
