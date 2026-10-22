/* The Annex A radar uses the audit compliance value, independently of implementation. */
var V9Compliance=(()=>{
 const levels=Object.freeze([
  Object.freeze({value:2,rank:0,label:'عدم انطباق کلی',english:'Major Nonconformity',token:'--radar-major'}),
  Object.freeze({value:1,rank:1,label:'عدم انطباق جزیی',english:'Minor Nonconformity',token:'--radar-minor'}),
  Object.freeze({value:4,rank:2,label:'توصیه برای بهبود',english:'Improvement Opportunity',token:'--radar-improvement'}),
  Object.freeze({value:3,rank:3,label:'مشاهده',english:'Observation',token:'--radar-observation'}),
  Object.freeze({value:0,rank:4,label:'انطباق',english:'Conformity',token:'--radar-conformity'})
 ]);
 const unknown=Object.freeze({value:null,rank:null,label:'انتخاب نشده',english:'Not Selected',token:'--radar-unknown'});
 const level=value=>levels.find(x=>x.value===value)||unknown;
 function summary(ids,data){const counts=Object.fromEntries([...levels,unknown].map(x=>[String(x.value),0]));for(const id of ids)counts[String(level(data[id]?.compliance).value)]++;return {total:ids.length,counts,conformity:counts['0'],selected:ids.length-counts.null,unknown:counts.null};}
 function point(index,total,value,segment,count){const status=level(value),angle=(segment+(.08+.84*(status.rank===null?(index+.5)/total:((index%3)+.5)/3)))*2*Math.PI/count,radius=status.rank===null?208+(index%2)*5:31+status.rank*34+Math.floor(index/3)*4.5;return {status,angle,radius,x:260+Math.sin(angle)*radius,y:260-Math.cos(angle)*radius};}
 return {levels,unknown,level,summary,point};
})();
