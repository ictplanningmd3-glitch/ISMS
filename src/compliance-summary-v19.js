/* User-defined aggregate compliance; individual audit outcomes remain unchanged. */
var V19Compliance=(()=>{
 const definitions=Object.freeze([
  {key:5,token:'--audit-good-point',english:'Good Point'},
  {key:0,token:'--audit-conformity',english:'Conformity'},
  {key:4,token:'--audit-improvement',english:'Improvement Opportunity'},
  {key:3,token:'--audit-observation',english:'Observation'},
  {key:1,token:'--audit-minor',english:'Minor Nonconformity'},
  {key:2,token:'--audit-major',english:'Major Nonconformity'},
  {key:'unknown',token:'--audit-unknown',english:'Not Selected'}
 ].map(Object.freeze));
 const positiveCodes=Object.freeze([5,0,4,3]);
 const outcome=record=>Number.isInteger(record?.compliance)&&record.compliance>=0&&record.compliance<=5?record.compliance:'unknown';
 function validUpdated(value){
  if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2}))?$/.test(value))return false;
  const day=value.slice(0,10),parsed=Date.parse(day+'T12:00:00Z');
  return Number.isFinite(parsed)&&new Date(parsed).toISOString().slice(0,10)===day&&Number.isFinite(Date.parse(value));
 }
 function summary(items=[],data={}){
  const seen=new Set(),rows=items.filter(item=>{if(!item?.id||seen.has(item.id))return false;seen.add(item.id);return data[item.id]?.applicable!==false;});
  const counts=Object.fromEntries(definitions.map(s=>[String(s.key),0]));
  let lastUpdated=null,lastTime=-Infinity;
  for(const item of rows){
   const record=data[item.id];counts[String(outcome(record))]++;
   if(validUpdated(record?.updated)){const time=Date.parse(record.updated);if(time>lastTime){lastTime=time;lastUpdated=record.updated;}}
  }
  const total=rows.length,positive=positiveCodes.reduce((sum,code)=>sum+counts[String(code)],0),unknown=counts.unknown,negative=counts['1']+counts['2'];
  const lastPositive=definitions.reduce((last,s,index)=>counts[String(s.key)]?index:last,-1);let assigned=0;
  const segments=definitions.map((s,index)=>{const count=counts[String(s.key)],percentage=!total||!count?0:index===lastPositive?100-assigned:count/total*100;assigned+=percentage;return {...s,count,percentage};});
  return {total,positive,negative,unknown,assessed:total-unknown,counts,segments,rate:total?positive/total*100:null,lastUpdated};
 }
 return {definitions,positiveCodes,outcome,validUpdated,summary};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=V19Compliance;
