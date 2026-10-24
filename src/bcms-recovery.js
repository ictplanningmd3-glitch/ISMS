/* Continuity curves and readiness: durations are minutes; capacities are percentages. */
var V10BCP=(()=>{
 const n=v=>V8D.num(v),has=v=>n(v)!==null,add=(a,b)=>has(a)&&has(b)?n(a)+n(b):null;
 const profileNames={target:'هدف مصوب',current:'قابلیت فعلی',actual:'نتیجهٔ واقعی تمرین'};
 function validate(b){
  if(b.scenario!==undefined&&typeof b.scenario!=='string')throw Error('شرح سناریوی وقفه معتبر نیست.');
  for(const k of ['wrt','currentWrt','actualWrt','rto','currentRto','actualRto','rpo','currentRpo','actualRpo'])if(b[k]!==undefined&&b[k]!==''&&(!has(b[k])||n(b[k])<0))throw Error('زمان‌های بازیابی و WRT باید صفر یا بیشتر باشند.');
  if(b.disruptionCapacity!==undefined&&b.disruptionCapacity!==''&&(!has(b.disruptionCapacity)||n(b.disruptionCapacity)<0||n(b.disruptionCapacity)>100))throw Error('ظرفیت هنگام رخداد باید بین صفر و صد باشد.');
  for(const k of ['normalCapacity','minimumCapacity','emergencyCapacity','actualCapacity'])if(b[k]!==undefined&&b[k]!==''&&(!has(b[k])||n(b[k])<0))throw Error('ظرفیت نمی‌تواند منفی یا نامعتبر باشد.');for(const k of ['emergencyCapacity','actualCapacity'])if(has(b[k])&&n(b[k])>100)throw Error('درصد ظرفیت حداکثر صد است.');
  if(b.recoverySteps===undefined)return b;
  if(!Array.isArray(b.recoverySteps)||b.recoverySteps.length>20)throw Error('حداکثر ۲۰ گام بازیابی مجاز است.');
  let time=-1,capacity=-1;
  const ids=new Set();
  for(const row of b.recoverySteps){if(!row||typeof row.id!=='string'||!row.id||ids.has(row.id)||typeof row.title!=='string')throw Error('شناسه یا عنوان گام بازیابی معتبر نیست.');ids.add(row.id);
   for(const key of ['minutes','capacity'])if(row[key]!==''&&row[key]!==undefined&&(!has(row[key])||n(row[key])<0))throw Error('زمان و ظرفیت گام باید صفر یا بیشتر باشد.');
   if(has(row.capacity)&&n(row.capacity)>100)throw Error('ظرفیت گام حداکثر صد درصد است.');
   if(has(row.minutes)&&has(row.capacity)){if(n(row.minutes)<=time)throw Error('زمان گام‌ها باید به‌ترتیب صعودی و بدون تکرار باشد.');if(n(row.capacity)<capacity)throw Error('ظرفیت گام‌های بازیابی باید ثابت یا افزایشی باشد.');time=n(row.minutes);capacity=n(row.capacity);}
  }return b;
 }
 function evaluate(b,base){
  const mtpd=n(base.mtpd),mbco=n(base.mbco),initial=has(b.disruptionCapacity)?n(b.disruptionCapacity):null,steps=(b.tested?b.recoverySteps||[]:[]).filter(s=>has(s.minutes)&&has(s.capacity)).map(s=>({id:s.id,title:s.title,minutes:n(s.minutes),capacity:n(s.capacity)}));
  const incompleteSteps=!!b.tested&&(b.recoverySteps||[]).some(s=>!has(s.minutes)||!has(s.capacity));
  const definitions={target:{rto:n(b.rto),rpo:b.rpoNA?null:n(b.rpo),capacity:mbco,wrt:n(b.wrt)},current:{rto:n(b.currentRto),rpo:b.rpoNA?null:n(b.currentRpo),capacity:n(b.emergencyCapacity),wrt:n(b.currentWrt)},actual:{rto:b.tested?n(b.actualRto):null,rpo:b.rpoNA||!b.tested?null:n(b.actualRpo),capacity:b.tested?n(b.actualCapacity):null,wrt:b.tested?n(b.actualWrt):null}};
  const profiles={};
  for(const [key,d]of Object.entries(definitions)){const points=[],explicit=key==='actual'&&b.tested?steps:[],fullStep=explicit.find(s=>s.capacity===100),fullFromWrt=add(d.rto,d.wrt),full=fullStep?fullStep.minutes:fullFromWrt;
   if(has(initial)){points.push({minutes:0,capacity:initial,title:'رخداد / افت ظرفیت'});if(explicit.length)points.push(...explicit);else if(d.rto!==null&&d.capacity!==null)points.push({minutes:d.rto,capacity:key==='target'?Math.max(initial,d.capacity):d.capacity,title:key==='target'&&initial>d.capacity?'حفظ ظرفیت سناریو بالاتر از حداقل خدمت':'بازگشت خدمت'});if(!fullStep&&fullFromWrt!==null&&d.rto!==null&&d.capacity!==null&&(!explicit.length||explicit.at(-1).minutes<=fullFromWrt))points.push({minutes:fullFromWrt,capacity:100,title:'بازگشت کامل — WRT ثبت‌شده'});}
   const margin=full!==null&&mtpd!==null?mtpd-full:null,derivedWrt=d.wrt===null&&fullStep&&d.rto!==null&&fullStep.minutes>=d.rto?fullStep.minutes-d.rto:d.wrt;
   profiles[key]={key,name:profileNames[key],...d,wrt:derivedWrt,wrtSource:d.wrt===null&&derivedWrt!==null?'steps':'input',points,full,fullSource:fullStep?'steps':fullFromWrt!==null?'wrt':null,margin,overTolerance:margin!==null&&margin<0};
  }
  const critical=[],missing=[],warnings=[];
  for(const p of Object.values(profiles))if(p.overTolerance)critical.push(p.name+': بازگشت کامل '+V8D.human(-p.margin)+' پس از MTPD است.');
  if(initial===null)missing.push('ظرفیت سناریو در لحظهٔ رخداد ثبت نشده است.');
  if(!has(b.wrt))missing.push('WRT هدف و زمان بازگشت کامل مشخص نیست.');
  if(!has(b.currentWrt))missing.push('WRT قابلیت فعلی ثبت نشده است.');
  if(b.tested&&profiles.actual.full===null)missing.push('بازگشت کامل در تمرین با WRT واقعی یا گام ۱۰۰٪ ثبت نشده است.');
  if(incompleteSteps)missing.push('زمان یا ظرفیت بعضی گام‌های بازیابی ناقص است.');
  if(has(b.wrt)&&has(b.currentWrt)&&n(b.currentWrt)>n(b.wrt))critical.push('قابلیت فعلی WRT از هدف بیشتر است: '+V8D.human(n(b.currentWrt)-n(b.wrt)));
  if(b.tested&&has(b.wrt)&&profiles.actual.wrt!==null&&profiles.actual.wrt>n(b.wrt))critical.push('WRT واقعی تمرین از هدف بیشتر است.');
  for(const key of ['current','actual']){const p=profiles[key];if(initial!==null&&p.capacity!==null&&p.rto!==null&&p.capacity<initial)critical.push(p.name+': ظرفیت در بازیابی از ظرفیت سناریوی هنگام رخداد کمتر است.');}
  if(steps.length&&initial!==null&&steps[0].capacity<initial)critical.push('ظرفیت اولین گام از ظرفیت سناریو هنگام رخداد کمتر است.');
  if(b.tested&&steps.length&&has(b.actualRto)&&mbco!==null){const firstMinimum=steps.find(s=>s.capacity>=mbco);if(firstMinimum&&firstMinimum.minutes!==n(b.actualRto))critical.push('زمان بازیابی واقعی با اولین گام تحقق MBCO یکسان نیست.');if(!firstMinimum)critical.push('گام‌های واقعی ثبت‌شده تحقق MBCO را نشان نمی‌دهند؛ با ادعای بازیابی خدمت سازگار نیستند.');}
  if(b.tested&&steps.length&&has(b.actualRto)&&has(b.actualCapacity)){const atRto=steps.find(s=>s.minutes===n(b.actualRto));if(!atRto)critical.push('گام متناظر با زمان RTO واقعی ثبت نشده است؛ منحنی گام‌ها و مقدار مستقل بازیابی همخوان نیستند.');if(atRto&&atRto.capacity!==n(b.actualCapacity))critical.push('ظرفیت واقعی در زمان RTO با گام متناظر همخوان نیست.');}
  const actualFullStep=steps.find(s=>s.capacity===100);if(b.tested&&actualFullStep&&has(b.actualRto)&&has(b.actualWrt)&&actualFullStep.minutes!==n(b.actualRto)+n(b.actualWrt))critical.push('زمان گام ۱۰۰٪ با مجموع RTO واقعی و WRT واقعی همخوان نیست.');
  if(!b.scenario?.trim())warnings.push('شرح سناریو (KDS) برای تفسیر نمودار ثبت نشده است.');
  return {mtpd,mbco,initial,steps,incompleteSteps,profiles,critical,missing,warnings,wrtGap:has(b.currentWrt)&&has(b.wrt)?n(b.currentWrt)-n(b.wrt):null,actualWrtGap:b.tested&&profiles.actual.wrt!==null&&has(b.wrt)?profiles.actual.wrt-n(b.wrt):null};
 }
 function augmentResult(b,base){try{validate(b);}catch(err){const safe={...b,disruptionCapacity:'',wrt:'',currentWrt:'',actualWrt:'',rto:'',currentRto:'',actualRto:'',rpo:'',currentRpo:'',actualRpo:'',actualCapacity:'',emergencyCapacity:'',recoverySteps:[]},safeBase={...base,mtpd:has(base.mtpd)&&n(base.mtpd)>=0?n(base.mtpd):null,mbco:has(base.mbco)&&n(base.mbco)>=0&&n(base.mbco)<=100?n(base.mbco):null},recovery={...evaluate(safe,safeBase),invalid:true,error:err.message,critical:[err.message]};return {...base,status:'critical',reasons:[err.message,...(base.status==='ready'?[]:base.reasons)],recovery};}const recovery=evaluate(b,base),status=recovery.critical.length?'critical':base.status==='ready'&&recovery.missing.length?'not-tested':base.status,reasons=[...new Set([...recovery.critical,...(base.status==='ready'?[]:base.reasons),...recovery.missing,...recovery.warnings])];return {...base,status,reasons:reasons.length?reasons:base.reasons,recovery};}
 return {validate,evaluate,augmentResult};
})();
