/* Date-based portfolio views; never overwrite a project's execution status. */
var V19Portfolio=(()=>{
 const day=86400000,clamp=value=>Math.max(0,Math.min(100,value));
 const isDate=value=>typeof value==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(value)&&Number.isFinite(Date.parse(value+'T12:00:00Z'))&&new Date(value+'T12:00:00Z').toISOString().slice(0,10)===value;
 const stamp=value=>Date.parse(value+'T12:00:00Z');
 const days=(a,b)=>isDate(a)&&isDate(b)?Math.round((stamp(a)-stamp(b))/day):null;
 const iso=time=>new Date(time).toISOString().slice(0,10);
 const progress=p=>Number.isFinite(Number(p.progress))?clamp(Number(p.progress)):0;
 const labels={completed:'تکمیل شده',ontrack:'در مسیر',atrisk:'در معرض تأخیر',delayed:'تأخیردار',unknown:'زمان‌بندی ناقص'};
 const optionsOf=options=>({completed:options?.completed||((p)=>p.status==='completed'),blocked:options?.blocked||((p)=>p.status==='blocked')});
 function health(project,today,options={}){
  const checks=optionsOf(options),actual=progress(project),valid=isDate(project.start)&&isDate(project.due)&&isDate(today)&&project.start<=project.due;
  const expected=valid?clamp(days(today,project.start)/Math.max(1,days(project.due,project.start))*100):null;
  let key;
  if(checks.completed(project))key='completed';
  else if(isDate(today)&&isDate(project.due)&&project.due<today)key='delayed';
  else if(checks.blocked(project))key='atrisk';
  else if(!valid)key='unknown';
  else key=actual+1e-9<expected?'atrisk':'ontrack';
  return {key,label:labels[key],expected,progress:actual};
 }
 function summary(rows,today,options={}){
  const classified=rows.map(project=>({project,...health(project,today,options)})),counts=Object.fromEntries(Object.keys(labels).map(key=>[key,classified.filter(row=>row.key===key).length]));
  const groupOf=options.group||((project)=>({1:'A',2:'B',3:'C'})[project.months]||'unknown');
  const groups=['A','B','C'].map(key=>{const members=rows.filter(project=>groupOf(project)===key),nested=classified.filter(row=>groupOf(row.project)===key);return {key,count:members.length,progress:members.length?Math.round(members.reduce((sum,p)=>sum+progress(p),0)/members.length):null,counts:Object.fromEntries(Object.keys(labels).map(status=>[status,nested.filter(row=>row.key===status).length]))};});
  return {total:rows.length,progress:rows.length?Math.round(rows.reduce((sum,p)=>sum+progress(p),0)/rows.length):null,counts,groups,classified};
 }
 const monthKeyFormat=new Intl.DateTimeFormat('en-US-u-ca-persian',{year:'numeric',month:'numeric',timeZone:'UTC'}),monthLabelFormat=new Intl.DateTimeFormat('fa-IR-u-ca-persian',{year:'numeric',month:'long',timeZone:'UTC'});
 const monthKey=time=>monthKeyFormat.format(new Date(time));
 function timeline(rows,today){
  const dated=rows.filter(p=>isDate(p.start)&&isDate(p.due)&&p.start<=p.due);
  if(!dated.length)return {empty:true,start:null,end:null,days:0,months:[],todayPercent:null,todayInRange:false};
  const first=Math.min(...dated.map(p=>stamp(p.start))),last=Math.max(...dated.map(p=>stamp(p.due))),end=last+day,span=(end-first)/day,months=[];
  let cursor=first;
  // Binary-search the next Persian month boundary; no Gregorian approximation.
  while(cursor<end&&months.length<120){
   const key=monthKey(cursor);let low=1,high=35;
   while(low<high){const mid=Math.floor((low+high)/2);if(monthKey(cursor+mid*day)===key)low=mid+1;else high=mid;}
   const next=Math.min(end,cursor+low*day);
   months.push({start:iso(cursor),end:iso(next-day),label:monthLabelFormat.format(new Date(cursor)),left:(cursor-first)/(end-first)*100,width:(next-cursor)/(end-first)*100});cursor=next;
  }
  let dense=false;
  if(cursor<end){
   dense=true;months.length=0;
   for(let i=0;i<24;i++){const a=first+Math.floor(span*i/24)*day,b=first+Math.floor(span*(i+1)/24)*day;months.push({start:iso(a),end:iso(b-day),label:monthLabelFormat.format(new Date(a)),left:(a-first)/(end-first)*100,width:(b-a)/(end-first)*100});}
  }
  const raw=isDate(today)?(stamp(today)-first)/(end-first)*100:null;
  return {empty:false,start:iso(first),end:iso(last),days:span,months,dense,todayPercent:raw===null?null:clamp(raw),todayInRange:raw!==null&&raw>=0&&raw<100};
 }
 function bar(project,range){
  if(range?.empty||!isDate(range?.start)||!isDate(project.start)||!isDate(project.due)||project.start>project.due)return {valid:false,left:0,width:0,progressWidth:0};
  const left=clamp(days(project.start,range.start)/range.days*100),end=clamp((days(project.due,range.start)+1)/range.days*100),width=Math.max(0,end-left);
  return {valid:true,left,width,progressWidth:width*progress(project)/100};
 }
 return {isDate,days,health,summary,timeline,bar,labels,progress};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=V19Portfolio;
