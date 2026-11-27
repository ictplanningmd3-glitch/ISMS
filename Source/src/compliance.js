/* The Annex A radar uses the audit compliance value, independently of implementation. */
var V9Compliance=(()=>{
 const levels=Object.freeze([
  Object.freeze({value:5,rank:0,label:'نقطه قوت',english:'Good Point',token:'--radar-good-point'}),
  Object.freeze({value:0,rank:1,label:'انطباق',english:'Conformity',token:'--radar-conformity'}),
  Object.freeze({value:4,rank:2,label:'توصیه برای بهبود',english:'Improvement Opportunity',token:'--radar-improvement'}),
  Object.freeze({value:3,rank:3,label:'مشاهده',english:'Observation',token:'--radar-observation'}),
  Object.freeze({value:1,rank:4,label:'عدم انطباق جزیی',english:'Minor Nonconformity',token:'--radar-minor'}),
  Object.freeze({value:2,rank:5,label:'عدم انطباق کلی',english:'Major Nonconformity',token:'--radar-major'})
 ]);
 const unknown=Object.freeze({value:null,rank:null,label:'انتخاب نشده',english:'Not Selected',token:'--radar-unknown'});
 const level=value=>levels.find(x=>x.value===value)||unknown;
 function summary(ids,data){const counts=Object.fromEntries([...levels,unknown].map(x=>[String(x.value),0]));for(const id of ids)counts[String(level(data[id]?.compliance).value)]++;return {total:ids.length,counts,conformity:counts['0'],goodPoints:counts['5'],selected:ids.length-counts.null,unknown:counts.null};}
 function point(index,total,value,segment,count){const status=level(value),angle=(segment+(.08+.84*(status.rank===null?(index+.5)/total:((index%3)+.5)/3)))*2*Math.PI/count,radius=status.rank===null?208+(index%2)*5:25+status.rank*28+Math.min(5,Math.floor(index/3))*4.5;return {status,angle,radius,x:260+Math.sin(angle)*radius,y:260-Math.cos(angle)*radius};}
 function nonconformities(ids,data){const rows=ids.filter(id=>data[id]?.applicable!==false),minor=rows.filter(id=>data[id]?.compliance===1).length,major=rows.filter(id=>data[id]?.compliance===2).length,total=minor+major,minorPercent=total?minor/total*100:0;return {minor,major,total,minorPercent,majorPercent:total?100-minorPercent:0};}
 function results(ids,data,values){
  const statuses=values===undefined?levels:levels.filter(status=>values.includes(status.value)),rows=[...new Set(ids)].filter(id=>data[id]?.applicable!==false),counts=Object.fromEntries(statuses.map(status=>[String(status.value),0]));
  for(const id of rows){const value=data[id]?.compliance;if(Object.hasOwn(counts,String(value))&&statuses.some(status=>status.value===value))counts[String(value)]++;}
  const total=Object.values(counts).reduce((sum,count)=>sum+count,0),lastPositive=statuses.reduce((last,status,index)=>counts[String(status.value)]?index:last,-1);let assigned=0;
  const segments=statuses.map((status,index)=>{const count=counts[String(status.value)],percentage=!total||!count?0:index===lastPositive?100-assigned:count/total*100;assigned+=percentage;return {...status,code:status.value,count,percentage};});
  return {total,counts,segments,eligible:rows.length,unknown:rows.filter(id=>level(data[id]?.compliance).value===null).length};
 }
 return {levels,unknown,level,summary,point,nonconformities,results};
})();
