/* Recovery planning/test data are independent; time values are elapsed minutes from T0. */
var V10BCP=(()=>{
 const n=v=>V8D.num(v),has=v=>n(v)!==null,active=b=>b.bcp==='yes'&&b.tested===true;
 const names={target:'هدف طرح / Plan Target',current:'قابلیت فعلی / Current Capability',actual:'نتیجهٔ واقعی آزمون / Test Result'};
 const stageKeys={target:'targetRecoverySteps',current:'currentRecoverySteps',actual:'recoverySteps'};
 function validate(b){
  if(b.scenario!==undefined&&typeof b.scenario!=='string')throw Error('شرح سناریوی KDS معتبر نیست.');
  const times=['wrt','currentWrt','rto','currentRto','rpo','currentRpo',...(!b.rpoNA?['lastBackupAge']:[]),...(active(b)?['actualWrt','actualRto','actualRpo']:[])];
  for(const k of times){if(b.rpoNA&&/rpo$/i.test(k))continue;if(b[k]!==undefined&&b[k]!==''&&(!has(b[k])||n(b[k])<0))throw Error('زمان بازیابی، RPO و زمان پشتیبان باید صفر یا بیشتر باشد.');}
  for(const k of ['disruptionCapacity','emergencyCapacity',...(active(b)?['actualCapacity']:[])])if(b[k]!==undefined&&b[k]!==''&&(!has(b[k])||n(b[k])<0||n(b[k])>100))throw Error('درصد ظرفیت باید بین صفر و صد باشد.');
  for(const k of ['normalCapacity','minimumCapacity'])if(b[k]!==undefined&&b[k]!==''&&(!has(b[k])||n(b[k])<0))throw Error('ظرفیت نباید منفی یا نامعتبر باشد.');
  if(n(b.normalCapacity)>0&&n(b.minimumCapacity)>n(b.normalCapacity))throw Error('حداقل ظرفیت نباید از ظرفیت عادی بیشتر باشد.');
  for(const key of ['targetRecoverySteps','currentRecoverySteps',...(active(b)?['recoverySteps']:[])]){
   const rows=b[key];if(rows===undefined)continue;if(!Array.isArray(rows)||rows.length>20)throw Error('حداکثر ۲۰ مرحله برای هر منبع بازیابی مجاز است.');
   const ids=new Set();let time=-1,capacity=-1;
   for(const row of rows){if(!row||typeof row.id!=='string'||!row.id||ids.has(row.id)||typeof row.title!=='string')throw Error('شناسه یا عنوان مرحلهٔ بازیابی معتبر نیست.');ids.add(row.id);
    for(const k of ['minutes','capacity'])if(row[k]!==undefined&&row[k]!==''&&(!has(row[k])||n(row[k])<0))throw Error('زمان و ظرفیت مرحله باید صفر یا بیشتر باشد.');
    if(has(row.capacity)&&n(row.capacity)>100)throw Error('ظرفیت مرحله نباید از صد درصد بیشتر باشد.');
    if(has(row.minutes)&&has(row.capacity)){if(n(row.minutes)<=time)throw Error('زمان مراحل باید به‌ترتیب صعودی و بدون تکرار باشد.');if(n(row.capacity)<capacity)throw Error('ظرفیت مراحل باید ثابت یا افزایشی باشد.');time=n(row.minutes);capacity=n(row.capacity);}
   }
  }return b;
 }
 function evaluate(b,base){
  const tested=active(b),mtpd=n(base.mtpd),mbco=n(base.mbco),initial=n(b.disruptionCapacity),backupAge=b.rpoNA?null:n(b.lastBackupAge),critical=[],missing=[],warnings=[];
  const defs={target:{rto:n(b.rto),rpo:b.rpoNA?null:n(b.rpo),capacity:mbco,wrt:n(b.wrt)},current:{rto:n(b.currentRto),rpo:b.rpoNA?null:n(b.currentRpo),capacity:n(b.emergencyCapacity),wrt:n(b.currentWrt)},actual:{rto:tested?n(b.actualRto):null,rpo:tested&&!b.rpoNA?n(b.actualRpo):null,capacity:tested?n(b.actualCapacity):null,wrt:tested?n(b.actualWrt):null}};
  const profiles={};let incompleteSteps=false;
  for(const [key,d]of Object.entries(defs)){
   const raw=key==='actual'&&!tested?[]:b[stageKeys[key]]||[],steps=raw.filter(s=>has(s.minutes)&&has(s.capacity)).map(s=>({id:s.id,title:s.title,minutes:n(s.minutes),capacity:n(s.capacity),kind:'stage'}));
   if(raw.some(s=>!has(s.minutes)||!has(s.capacity))){incompleteSteps=true;missing.push(names[key]+': زمان یا ظرفیت بعضی مراحل ناقص است.');}
   const resumeCapacity=key==='target'&&initial!==null&&d.capacity!==null?Math.max(initial,d.capacity):d.capacity;
   const firstFull=steps.find(s=>s.capacity===100),atResumeFull=d.rto!==null&&resumeCapacity===100?d.rto:null,fullStepTime=firstFull?.minutes??atResumeFull;
   const sum=d.rto!==null&&d.wrt!==null?d.rto+d.wrt:null,full=fullStepTime??sum,derived=d.wrt===null&&fullStepTime!==null&&d.rto!==null&&fullStepTime>=d.rto?fullStepTime-d.rto:d.wrt;
   if(full!==null&&d.rto!==null&&full<d.rto)critical.push(names[key]+': بازگشت کامل پیش از زمان بازگشت حداقل خدمت ثبت شده است.');
   if(fullStepTime!==null&&sum!==null&&fullStepTime!==sum)critical.push(names[key]+': زمان ۱۰۰٪ با RTO + WRT همخوان نیست.');
   if(initial!==null&&resumeCapacity!==null&&d.rto!==null&&resumeCapacity<initial)critical.push(names[key]+': ظرفیت بازیابی از ظرفیت پس از رخداد کمتر است.');
   for(const s of steps){if(initial!==null&&s.capacity<initial)critical.push(names[key]+': ظرفیت مرحله از ظرفیت پس از رخداد کمتر است.');
    if(d.rto!==null&&resumeCapacity!==null){if(s.minutes===d.rto&&s.capacity!==resumeCapacity)critical.push(names[key]+': ظرفیت مرحله در RTO با ظرفیت بازگشت خدمت همخوان نیست.');if(s.minutes>d.rto&&s.capacity<resumeCapacity)critical.push(names[key]+': ظرفیت مرحله پس از RTO کمتر از ظرفیت بازگشت خدمت است.');}
    if(d.rto!==null&&mbco!==null&&initial!==null&&initial<mbco&&s.minutes<d.rto&&s.capacity>=mbco)critical.push(names[key]+': مرحله قبل از RTO به MBCO رسیده است؛ زمان بازگشت خدمت را بازبینی کنید.');
    if(sum!==null&&s.minutes>sum&&s.capacity<100)critical.push(names[key]+': پس از زمان بازگشت کامل هنوز ظرفیت صد درصد محقق نشده است.');
   }
   const points=[];
   if(initial!==null){points.push({minutes:0,capacity:initial,title:'Disaster (T0)',kind:'initial'});
    if(d.rto!==null&&resumeCapacity!==null)points.push({minutes:d.rto,capacity:resumeCapacity,title:'Business Resumption',kind:'resumption'});
    for(const s of steps){const same=points.find(p=>p.minutes===s.minutes);if(!same)points.push(s);else if(same.kind!=='resumption')Object.assign(same,s);}
    if(!firstFull&&full!==null&&d.rto!==null&&resumeCapacity!==null&&!steps.some(s=>s.minutes>full)&&!points.some(p=>p.minutes===full&&p.capacity===100))points.push({minutes:full,capacity:100,title:'100% Resumption / Normal Operations',kind:'full'});
    points.sort((a,z)=>a.minutes-z.minutes);
   }
   const margin=full!==null&&mtpd!==null?mtpd-full:null;
   profiles[key]={key,name:names[key],...d,wrt:derived,wrtSource:d.wrt===null&&derived!==null?'steps':'input',points,steps,full,fullSource:fullStepTime!==null?'steps':sum!==null?'wrt':null,margin,overTolerance:margin!==null&&margin<0};
   if(margin!==null&&margin<0)critical.push(names[key]+': بازگشت کامل '+V8D.human(-margin)+' پس از MTPD است.');
  }
  if(initial===null)missing.push('ظرفیت خدمت بلافاصله پس از Disaster (T0) ثبت نشده است.');
  if(!b.scenario?.trim())missing.push('سناریوی KDS ثبت نشده است.');
  if(!b.rpoNA&&backupAge===null)missing.push('زمان Last Consistent Backup پیش از رخداد ثبت نشده است.');
  if(!b.rpoNA&&backupAge!==null&&defs.target.rpo!==null&&backupAge>defs.target.rpo)critical.push('آخرین پشتیبان از پنجرهٔ مجاز RPO عقب‌تر است.');
  if(profiles.target.wrt===null||profiles.target.full===null)missing.push('بازگشت کامل هدف با WRT یا مرحلهٔ ۱۰۰٪ مشخص نشده است.');
  if(profiles.current.wrt===null||profiles.current.full===null)missing.push('بازگشت کامل قابلیت فعلی ثبت نشده است.');
  if(tested&&profiles.actual.full===null)missing.push('بازگشت کامل آزمون با WRT واقعی یا مرحلهٔ ۱۰۰٪ ثبت نشده است.');
  if(!tested)missing.push('نتیجهٔ واقعی آزمون BCP ثبت نشده است.');
  const targetWrt=profiles.target.wrt,currentWrt=profiles.current.wrt,actualWrt=profiles.actual.wrt,wrtGap=targetWrt!==null&&currentWrt!==null?currentWrt-targetWrt:null,actualWrtGap=tested&&targetWrt!==null&&actualWrt!==null?actualWrt-targetWrt:null;
  if(wrtGap>0)critical.push('WRT قابلیت فعلی بیش از هدف است: '+V8D.human(wrtGap));if(actualWrtGap>0)critical.push('WRT واقعی آزمون بیش از هدف است.');
  return {mtpd,mbco,initial,backupAge,steps:profiles.actual.steps,incompleteSteps,profiles,critical:[...new Set(critical)],missing:[...new Set(missing)],warnings,wrtGap,actualWrtGap};
 }
 function augmentResult(b,base){
  try{validate(b);}catch(err){const safe={...b,scenario:'',disruptionCapacity:'',lastBackupAge:'',wrt:'',currentWrt:'',actualWrt:'',rto:'',currentRto:'',actualRto:'',rpo:'',currentRpo:'',actualRpo:'',actualCapacity:'',emergencyCapacity:'',targetRecoverySteps:[],currentRecoverySteps:[],recoverySteps:[]},safeBase={...base,mtpd:has(base.mtpd)&&n(base.mtpd)>=0?n(base.mtpd):null,mbco:has(base.mbco)&&n(base.mbco)>=0&&n(base.mbco)<=100?n(base.mbco):null},recovery={...evaluate(safe,safeBase),invalid:true,error:err.message,critical:[err.message]};return {...base,status:'critical',reasons:[err.message,...(base.status==='ready'?[]:base.reasons)],recovery};}
  const recovery=evaluate(b,base),status=recovery.critical.length?'critical':base.status==='ready'&&recovery.missing.length?'not-tested':base.status,reasons=[...new Set([...recovery.critical,...(base.status==='ready'?[]:base.reasons),...recovery.missing,...recovery.warnings])];return {...base,status,reasons:reasons.length?reasons:base.reasons,recovery};
 }
 return {validate,evaluate,augmentResult};
})();
