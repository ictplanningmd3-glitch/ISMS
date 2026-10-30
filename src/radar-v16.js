/* Whole-standard grouping is analytical; the separate canonical taxonomies stay intact. */
var V16Radar=(()=>{
 const modes=Object.freeze([
  Object.freeze({id:'clause',label:'الزامات استاندارد',english:'Requirements'}),
  Object.freeze({id:'control',label:'کنترل‌های Annex A',english:'Annex A Controls'}),
  Object.freeze({id:'all',label:'کل استاندارد',english:'Whole Standard'})
 ]);
 function groups(mode){
  const source=mode==='all'?V16RadarCombined:V13StandardGroups().filter(g=>g.kind===(mode==='clause'?'clause':'control'));
  return source.map(g=>{const itemIds=[...new Set(g.itemIds)];return {...g,itemIds,clauseCount:itemIds.filter(id=>!id.startsWith('A.')).length,controlCount:itemIds.filter(id=>id.startsWith('A.')).length};});
 }
 const validStatus=row=>Number.isInteger(row?.status)&&row.status>=0&&row.status<=4;
 function implementation(mode,data={}){
  return groups(mode).map(g=>{
   const ids=g.itemIds.filter(id=>data[id]?.applicable!==false),assessed=ids.filter(id=>validStatus(data[id])).length;
   const points=ids.reduce((sum,id)=>sum+(validStatus(data[id])?data[id].status*25:0),0);
   return {...g,total:g.itemIds.length,eligible:ids.length,assessed,score:ids.length?Math.round(points/ids.length):0};
  });
 }
 function point(index,total,value,segment,count){
  const status=V9Compliance.level(value),sector=2*Math.PI/count;
  let radius,fraction;
  if(status.rank===null){radius=208+(index%2)*6;fraction=.08+.84*(index+.5)/Math.max(1,total);}
  else {
   const bounds=[[12,48],[54,76],[82,104],[110,132],[138,160],[166,188]][status.rank];
   const rings=status.rank===0?[12,18,24,30,36,42,48]:Array.from({length:4},(_,i)=>bounds[0]+(bounds[1]-bounds[0])*i/3);
   const slots=[];
   for(const r of rings){const columns=Math.max(1,Math.floor(r*sector*.84/5));for(let c=0;c<columns;c++)slots.push({radius:r,fraction:.08+.84*(c+.5)/columns});}
   const slot=slots[Math.min(slots.length-1,Math.floor((index+.5)/Math.max(1,total)*slots.length))];
   radius=slot.radius;fraction=slot.fraction;
  }
  const angle=(segment+fraction)*sector;
  return {status,radius,angle,x:260+Math.sin(angle)*radius,y:260-Math.cos(angle)*radius};
 }
 return {modes,groups,implementation,point};
})();
