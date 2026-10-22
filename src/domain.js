/* Deterministic offline domain services. No UI, network, storage or date side effects. */
var V7D = (() => {
  const num = v => v === '' || v === null || v === undefined || typeof v === 'boolean' || !Number.isFinite(Number(v)) ? null : Number(v);
  const clamp = v => Math.max(0, Math.min(100, v));
  const unique = rows => [...new Map(rows.map(r => [r.id, r])).values()];
  const mean = rows => { const good=rows.filter(([v,w])=>num(v)!==null && num(w)>0); const den=good.reduce((s,[v,w])=>s+Number(w),0); return den ? good.reduce((s,[v,w])=>s+Number(v)*Number(w),0)/den : null; };
  const diff = (a,b) => num(a)===null||num(b)===null ? null : num(a)-num(b);
  const day = v => /^\d{4}-\d{2}-\d{2}$/.test(v||'') ? Date.parse(v+'T00:00:00Z') : NaN;
  const days = (a,b) => (day(a)-day(b))/86400000;
  const due = (r,today) => !!r.due && day(r.due)<day(today) && !['closed','completed','cancelled','archived','retired'].includes(r.status);
  const review = (date,today,soon=30) => !date ? 'unknown' : days(date,today)<0 ? 'overdue' : days(date,today)<=soon ? 'soon' : 'current';
  const human = v => num(v)===null ? 'ثبت نشده' : v===0 ? '۰ دقیقه' : v<0 ? '−'+human(-v) : v>=1440 && v%1440===0 ? (v/1440)+' روز' : v>=60 ? Math.floor(v/60)+' ساعت'+(v%60?' و '+Math.round(v%60)+' دقیقه':'') : v+' دقیقه';
  const categories = () => [
    ['operational','عملیاتی'],['financial','مالی'],['legal','حقوقی'],['regulatory','مقرراتی'],['contractual','قراردادی'],['customer','مشتری'],['reputation','اعتبار'],['hse','سلامت و ایمنی'],['environment','محیط زیست'],['data','اطلاعات و داده']
  ].map(([id,name])=>({id,name,active:true,threshold:4,veto:['legal','regulatory','hse','environment'].includes(id),criteria:['بدون اثر','جزئی','متوسط','جدی','غیرقابل تحمل','بحرانی / فاجعه‌بار']}));
  const defaults = type => ({version:1,revision:0,records:type==='rtp'?{risks:[],plans:[],projects:[],tasks:[],milestones:[],controls:[],tests:[],changes:[],acceptances:[],expenses:[]}:{services:[],activities:[],resources:[],dependencies:[],bias:[],plans:[],exercises:[],actions:[],reviews:[]},settings:type==='rtp'?{weights:[20,15,10,20,15,10,5,5],targets:[85,90,90,90,80,95,90,100],modelVersion:1,riskScale:5,aggregation:'approved-weight',staleDays:30}:{categories:categories(),timeBuckets:[60,240,480,1440,4320,10080],recommendRto:false,safetyBuffer:60,reviewDays:365,soonDays:30,scaleMax:5},audit:[],versions:[],snapshots:[]});
  function mtpd(impacts,cats,times) {
    for(const t of [...times].sort((a,b)=>a-b)) for(const c of cats.filter(c=>c.active)) {
      const value=num(impacts?.[c.id]?.[t]?.score);
      if(value!==null && value>=Number(c.threshold)) return {minutes:Number(t),category:c.id,score:value,threshold:Number(c.threshold),veto:!!c.veto};
    }
    return {minutes:null,category:null,status:'MTPD not reached in assessed horizon'};
  }
  function mbco(a){const mins=[a.operationalMinimum,a.contractualMinimum,a.legalMinimum].map(num); const units=mins.some(v=>v!==null)?Math.max(...mins.filter(v=>v!==null)):null;return {units,percent:num(a.normalCapacity)>0 && units!==null ? units/num(a.normalCapacity)*100:null};}
  function achievable(a){const fields=['detection','decision','activation','recovery','validation','stabilization'];return fields.every(k=>num(a[k])!==null)?fields.reduce((s,k)=>s+num(a[k]),0):null;}
  function recommended(m,settings){return settings.recommendRto&&num(m)!==null && m>Number(settings.safetyBuffer)?m-Number(settings.safetyBuffer):null;}
  function targets(b,a,settings){
    const m=mtpd(b.impacts,b.criteria||settings.categories,b.timeBuckets||settings.timeBuckets),c=mbco(a||{}), rec=recommended(m.minutes,settings);
    const rto=num(b.approvedRto)??rec, rpo=b.rpoNA ? null : num(b.approvedRpo)??num(b.requiredRpo), mb=num(b.approvedMbco)??c.percent;
    return {mtpd:m.minutes,mtpdSource:m,calculatedMbco:c,recommendedRto:rec,rto,rpo,mbco:mb,achievable:achievable(b),rtoGap:diff(achievable(b),rto),rpoGap:b.rpoNA?null:diff(b.achievableRpo,rpo),rpoNA:!!b.rpoNA};
  }
  const depGap=(d,parent)=>num(d.dependencyRto)===null||num(d.handover)===null||num(parent)===null?null:num(d.dependencyRto)+num(d.handover)-num(parent);
  function backlog(q,incoming,capacity){if([q,incoming,capacity].some(v=>num(v)===null))return null;return capacity-incoming>0?q/(capacity-incoming):Infinity;}
  function exercise(e,t){
    const test=(actual,target,minimum=false)=>num(actual)===null||num(target)===null?'not-tested':(minimum?num(actual)>=num(target):num(actual)<=num(target))?'pass':'fail';
    const rto=test(e.actualRecovery,t.rto),rpo=t.rpoNA?'na':test(e.actualDataLoss,t.rpo),mbco=test(e.actualCapacity,t.mbco,true);
    const vals=[rto,rpo,mbco].filter(x=>x!=='na');
    return {rto,rpo,mbco,overall:vals.includes('fail')?'fail':vals.includes('not-tested')||!e.evidence?'not-tested':'pass'};
  }
  function activityState(a,state,today){
    const r=state.records,b= r.bias.filter(b=>b.activity===a.id && b.status!=='archived').sort((x,y)=>(y.updated||'').localeCompare(x.updated||''))[0];
    const t=b?targets(b,a,state.settings):{mtpd:null,rto:null,rpo:null,mbco:null,rtoGap:null,rpoGap:null};
    const plans=r.plans.filter(p=>(p.activities||[]).includes(a.id)&&p.status!=='retired'),approved=plans.find(p=>['approved','active'].includes(p.status));
    const tests=r.exercises.filter(e=>e.activity===a.id && e.actualDate).sort((x,y)=>(y.actualDate+(y.updated||'')).localeCompare(x.actualDate+(x.updated||'')));
    const last=tests[0],result=last?exercise(last,last.targetSnapshot||t):{overall:'not-tested',rto:'not-tested',rpo:'not-tested',mbco:'not-tested'};
    const gaps=r.dependencies.filter(d=>d.activity===a.id).map(d=>({...d,gap:depGap(d,t.rto)}));
    const resources=r.resources.filter(x=>[...(a.resources||[]),...(b?.resources||[])].includes(x.id));
    const reasons=[];
    if(t.rtoGap>0)reasons.push('شکاف RTO: '+human(t.rtoGap));
    if(t.rpoGap>0)reasons.push('شکاف RPO: '+human(t.rpoGap));
    if(t.mtpd!==null && t.rto!==null && t.rto>=t.mtpd)reasons.push('RTO برابر یا بیشتر از MTPD');
    if(gaps.some(d=>d.gap>0))reasons.push('وابستگی با تأخیر تحویل');
    if(resources.some(x=>x.spof&&!x.alternate)||gaps.some(x=>x.spof&&!x.alternate))reasons.push('نقطه تک‌خرابی بدون جایگزین');
    if(a.critical&&!plans.length)reasons.push('فعالیت بحرانی فاقد BCP');
    if(result.overall==='fail')reasons.push('آخرین آزمون ناموفق است');
    if(reasons.length)return {status:'critical',reasons,b,t,approved,last,result,gaps};
    if(!last || result.overall==='not-tested')return {status:'not-tested',reasons:['اهداف تداوم با شواهد معتبر آزمون نشده‌اند'],b,t,approved,last,result,gaps};
    const missing=!b || b.status!=='approved'||b.reviewRequired||!approved||[t.mtpd,t.rto,t.mbco,t.achievable].some(x=>num(x)===null)||(!t.rpoNA&&(t.rpo===null||num(b.achievableRpo)===null))||gaps.some(d=>d.gap===null);
    const reviews=[review(b?.nextReview,today),review(approved?.nextReview,today)];
    if(missing||reviews.some(v=>v!=='current')||r.actions.some(x=>x.activity===a.id&&x.status!=='closed')||r.reviews.some(x=>x.activity===a.id&&x.status!=='closed'))return {status:'improve',reasons:['تصویب، داده‌های ضروری، بازنگری یا اقدامات باز نیازمند تکمیل است'],b,t,approved,last,result,gaps};
    // An old passing test does not validate newly changed targets.
    if(last.targetSnapshot && ['rto','rpo','mbco'].some(k=>last.targetSnapshot[k]!==t[k]))return {status:'not-tested',reasons:['اهداف پس از آزمون تغییر کرده‌اند؛ آزمون مجدد لازم است'],b,t,approved,last,result,gaps};
    return {status:'ready',reasons:['BIA و BCP مصوب؛ اهداف و وابستگی‌ها معتبر و آزمون موفق؛ بازنگری جاری'],b,t,approved,last,result,gaps};
  }
  function progress(p,r,today){
    const all=r.tasks.filter(t=>t.project===p.id&&t.status!=='cancelled'), parents=new Set(all.map(t=>t.parent).filter(Boolean)),leaves=all.filter(t=>!parents.has(t.id));
    function branch(parent){const rows=all.filter(t=>(t.parent||'')===parent);return mean(rows.map(t=>[parents.has(t.id)?branch(t.id):num(t.progress),t.weight]));}
    const actual=branch(''),planned=mean(leaves.map(t=>[Number.isFinite(day(t.start))&&Number.isFinite(day(t.due))?clamp((day(today)-day(t.start))/Math.max(86400000,day(t.due)-day(t.start))*100):null,t.weight]));
    const overdue=leaves.filter(t=>due(t,today)&&num(t.progress)<100).length;
    const milestones=r.milestones.filter(m=>m.project===p.id&&m.status!=='cancelled');
    const actualCost=num(p.actualCost)??(r.expenses?.some(e=>e.project===p.id)?r.expenses.filter(e=>e.project===p.id).reduce((s,e)=>s+(num(e.amount)||0),0):null);
    return {actual,planned,variance:diff(actual,planned),overdue,remaining:p.due?days(p.due,today):null,delayed:overdue>0||(p.due&&day(p.due)<day(today)&&actual!==100),milestones:milestones.length?milestones.filter(m=>m.status==='completed').length/milestones.length*100:null,actualCost};
  }
  function controlResult(c,r){const tests=r.tests.filter(t=>t.control===c.id).sort((a,b)=>(b.testDate+(b.updated||'')).localeCompare(a.testDate+(a.updated||'')));const t=tests[0];return t && t.testDate && t.evidence && t.assessor && t.confirmedBy ? t.result : 'unverified';}
  const riskScore=r=>num(r.likelihood)!==null&&num(r.impact)!==null?num(r.likelihood)*num(r.impact):null;
  const reduction=r=>num(r.baseline)!==null&&num(r.target)!==null&&num(r.residual)!==null&&r.reassessedAt&&r.reassessmentEvidence&&r.baseline>r.target?clamp((r.baseline-r.residual)/(r.baseline-r.target)*100):null;
  function radar(state,filter,today){
    const r=state.records,projects=unique(r.projects.filter(p=>(!filter?.department||p.department===filter.department)&&(!filter?.project||p.id===filter.project)&&(!filter?.plan||(p.plans||[]).includes(filter.plan))&&(!filter?.owner||p.owner===filter.owner)&&(!filter?.status||p.status===filter.status)&&(!filter?.priority||p.priority===filter.priority)&&(!filter?.from||p.due>=filter.from)&&(!filter?.to||p.start<=filter.to)));
    const ids=new Set(projects.map(p=>p.id)),riskIds=new Set(projects.flatMap(p=>p.risks||[])),planIds=new Set(projects.flatMap(p=>p.plans||[]));
    for(const p of r.plans.filter(p=>planIds.has(p.id)))for(const id of p.risks||[])riskIds.add(id);
    const risks=unique(r.risks.filter(x=>riskIds.has(x.id))),controls=unique(r.controls.filter(c=>(c.projects||[]).some(id=>ids.has(id))));
    const prog=projects.map(p=>[p,progress(p,r,today)]),weight=p=>(num(p.weight)||1)*(state.settings.aggregation==='risk-weight'?Math.max(1,...risks.filter(x=>(p.risks||[]).includes(x.id)).map(x=>riskScore(x)||1)):1);
    const execution=mean(prog.map(([p,x])=>[x.actual,weight(p)]));
    const schedule=mean(prog.map(([p,x])=>[x.planned===null||x.actual===null?null:x.planned===0?100:clamp(x.actual/x.planned*100),weight(p)]));
    const budget=mean(prog.map(([p,x])=>[num(p.budget)>0&&x.actualCost!==null?clamp(100-Math.max(0,(x.actualCost-p.budget)/p.budget*100)):null,weight(p)]));
    const effect=controls.length?controls.filter(c=>controlResult(c,r)==='effective').length/controls.length*100:null;
    const risk=mean(risks.map(x=>[reduction(x),num(x.importance)||1]));
    const milestone=mean(prog.map(([p,x])=>[x.milestones,weight(p)]));
    const tasks=r.tasks.filter(t=>ids.has(t.project)&&t.status!=='cancelled'),evidence=tasks.length?tasks.filter(t=>t.evidence).length/tasks.length*100:null;
    const plans=r.plans.filter(p=>planIds.has(p.id)),gov=plans.length?plans.filter(p=>p.approval?.by).length/plans.length*100:null;
    const vulnerabilities=mean(risks.map(x=>[num(x.vulnerabilityBaseline)>0&&num(x.vulnerabilityCurrent)!==null&&x.vulnerabilityEvidence?clamp((x.vulnerabilityBaseline-x.vulnerabilityCurrent)/x.vulnerabilityBaseline*100):null,num(x.importance)||1]));
    const goals=mean(plans.map(p=>[num(p.goalTarget)>0&&num(p.goalActual)!==null&&p.goalEvidence&&p.goalDate?clamp(p.goalActual/p.goalTarget*100):null,1]));
    const values=[execution,schedule,budget,effect,risk,milestone,evidence,gov],weights=state.settings.weights;
    return {values,effectivenessValues:[effect,risk,vulnerabilities,goals],score:mean(values.map((v,i)=>[v,weights[i]])),coverage:values.reduce((s,v,i)=>s+(v===null?0:Number(weights[i])),0),projects,risks,controls,progress:prog,modelVersion:state.settings.modelVersion};
  }
  function validateWeights(w){if(!Array.isArray(w)||w.length!==8||w.some(x=>num(x)===null||num(x)<0)||Math.abs(w.reduce((s,v)=>s+num(v),0)-100)>0.000001)throw Error('جمع هشت وزن باید دقیقاً ۱۰۰٪ باشد.');}
  function validState(value,type){
    const base=defaults(type);
    if(!value||value.version!==1||!value.records||!value.settings||!Number.isInteger(value.revision)||value.revision<0)throw Error('ساختار ماژول '+type+' نامعتبر است.');
    function walk(v,depth=0){if(depth>25)throw Error('عمق داده بیش از حد است.');if(typeof v==='number'&&!Number.isFinite(v))throw Error('عدد نامعتبر');if(typeof v==='string'&&v.length>3000000)throw Error('متن یا پیوست بیش از حد است.');if(v&&typeof v==='object')for(const [k,x]of Object.entries(v)){if(['__proto__','constructor','prototype'].includes(k))throw Error('کلید داده نامعتبر');walk(x,depth+1);}}
    walk(value);
    const multiKeys=['risks','plans','projects','activities','resources','predecessors'];
    const numberKeys=['normalCapacity','operationalMinimum','contractualMinimum','legalMinimum','approvedRto','approvedRpo','approvedMbco','requiredRpo','achievableRpo','dependencyRto','handover','detection','decision','activation','recovery','validation','stabilization','weight','progress','budget','actualCost','amount','likelihood','impact','baseline','target','residual','actualRecovery','actualCapacity','actualDataLoss'];
    for(const table of Object.keys(base.records)){const rows=value.records[table];if(!Array.isArray(rows)||rows.length>10000||rows.some(x=>!x||typeof x.id!=='string'||!x.id||x.id.length>256||typeof x.title!=='string')||new Set(rows.map(x=>x.id)).size!==rows.length)throw Error('دفتر '+table+' نامعتبر است.');
      for(const row of rows){for(const k of multiKeys)if(row[k]!==undefined&&(!Array.isArray(row[k])||row[k].some(x=>typeof x!=='string')))throw Error('پیوندهای رکورد نامعتبر است.');for(const k of numberKeys)if(row[k]!==undefined&&row[k]!==''&&row[k]!==null&&(typeof row[k]!=='number'||!Number.isFinite(row[k])||row[k]<0))throw Error('مقدار عددی نامعتبر است.');for(const k of ['start','due','nextReview','actualDate','updated','owner','department','status'])if(row[k]!==undefined&&typeof row[k]!=='string')throw Error('نوع اطلاعات رکورد نامعتبر است.');}
    }
    for(const key of ['audit','versions','snapshots'])if(!Array.isArray(value[key]))throw Error('تاریخچه ماژول نامعتبر');
    if(value.snapshots.some(s=>!s||typeof s.id!=='string'||typeof s.at!=='string'||!Array.isArray(s.values)||s.values.length!==8||s.values.some(v=>v!==null&&(typeof v!=='number'||v<0||v>100))||!s.filter||typeof s.filter!=='object'||!s.sources||!s.model))throw Error('Snapshot تاریخی نامعتبر است.');
    if(type==='bcms')for(const b of value.records.bias){if(b.criteria!==undefined&&(!Array.isArray(b.criteria)||b.criteria.some(c=>!c||typeof c.id!=='string'||typeof c.name!=='string'||!Array.isArray(c.criteria))))throw Error('روش ذخیره‌شده BIA نامعتبر');if(b.timeBuckets!==undefined&&(!Array.isArray(b.timeBuckets)||b.timeBuckets.some(t=>typeof t!=='number'||t<=0)))throw Error('بازه زمانی BIA نامعتبر');if(b.impacts!==undefined&&(!b.impacts||typeof b.impacts!=='object'||Array.isArray(b.impacts)))throw Error('ماتریس اثر نامعتبر');}
    if(type==='rtp'){validateWeights(value.settings.weights);if(!Array.isArray(value.settings.targets)||value.settings.targets.length!==8||value.settings.targets.some(v=>num(v)===null||v<0||v>100))throw Error('اهداف رادار نامعتبر');if(num(value.settings.riskScale)<2||num(value.settings.riskScale)>10)throw Error('مقیاس ریسک نامعتبر');}
    else {const s=value.settings;if(!Array.isArray(s.categories)||!s.categories.length||s.categories.length>30||s.categories.some(c=>!c.id||!c.name||num(c.threshold)<=0||num(c.threshold)>num(s.scaleMax)||!Array.isArray(c.criteria))||new Set(s.categories.map(c=>c.id)).size!==s.categories.length)throw Error('معیارهای اثر نامعتبر است');if(!Array.isArray(s.timeBuckets)||!s.timeBuckets.length||s.timeBuckets.length>24||s.timeBuckets.some(t=>num(t)<=0)||new Set(s.timeBuckets).size!==s.timeBuckets.length)throw Error('بازه‌های زمانی باید مثبت و یکتا باشند');}
    return value;
  }
  const approvalRoles=['admin','risk-manager','isms-manager','department-manager'];
  const can=(actor,action,record={})=>{
    if(!actor)return action==='view'||action==='export';
    if(action==='view'||action==='export')return true;
    if(action==='accept')return actor.role==='risk-owner'&&record.owner===actor.name;
    if(action==='approve')return !actor.unconfigured&&approvalRoles.includes(actor.role);
    if(action==='users'||action==='settings')return actor.role==='admin';
    return !['viewer','auditor'].includes(actor.role);
  };
  function validateEntity(type,table,row,state,previous,actor){
    if(!can(actor,'edit'))throw Error('برای ثبت یا تغییر اطلاعات وارد حساب مجاز شوید.');
    const r=state.records;
    const required= (key,label)=>{if(!String(row[key]??'').trim())throw Error(label+' الزامی است.');};
    const ref=(key,target,multi=false)=>{const v=multi?row[key]||[]:row[key]?[row[key]]:[];if(v.some(id=>!r[target].some(x=>x.id===id)))throw Error('ارجاع '+key+' یافت نشد.');};
    required('title','عنوان');
    if(row.start&&row.due&&day(row.due)<day(row.start))throw Error('تاریخ پایان قبل از شروع است.');
    if(table==='risks'){for(const k of ['likelihood','impact'])if(num(row[k])===null||row[k]<1||row[k]>state.settings.riskScale)throw Error('احتمال و اثر خارج از مقیاس است.');if(row.residual!==''&&num(row.residual)!==null&&(!row.reassessedAt||!row.reassessmentEvidence))throw Error('برای ریسک باقیمانده، تاریخ و شواهد ارزیابی مجدد لازم است.');}
    if(type==='rtp'){
      if(table==='plans'){if(!row.risks?.length)throw Error('حداقل یک ریسک به RTP متصل کنید.');ref('risks','risks',true);}
      if(table==='projects'){ref('plans','plans',true);ref('risks','risks',true);ref('parent','projects');if(row.parent===row.id)throw Error('پروژه نمی‌تواند والد خودش باشد.');let id=row.parent,seen=new Set([row.id]);while(id){if(seen.has(id))throw Error('چرخه در زیرپروژه‌ها');seen.add(id);id=r.projects.find(x=>x.id===id)?.parent;}}
      if(['tasks','milestones','expenses','changes'].includes(table)){required('project','پروژه');ref('project','projects');}
      if(table==='tasks'){
        if(num(row.weight)<=0||num(row.progress)===null||row.progress<0||row.progress>100)throw Error('وزن باید مثبت و پیشرفت بین صفر و صد باشد.');
        if(row.status==='completed'&&row.progress!==100)throw Error('فعالیت تکمیل‌شده باید پیشرفت ۱۰۰٪ داشته باشد.');
        const all=[...r.tasks.filter(t=>t.id!==row.id),row];let id=row.parent,seen=new Set([row.id]);while(id){if(seen.has(id))throw Error('چرخه در ساختار شکست کار');seen.add(id);const p=all.find(x=>x.id===id);if(!p||p.project!==row.project)throw Error('والد باید از همین پروژه باشد.');id=p.parent;}
        for(const id of row.predecessors||[]){if(!all.some(x=>x.id===id&&x.project===row.project)||id===row.id)throw Error('پیش‌نیاز نامعتبر');}
        function visit(id,path){if(path.has(id))throw Error('چرخه در وابستگی فعالیت‌ها');const next=new Set(path).add(id);for(const k of all.find(x=>x.id===id)?.predecessors||[])visit(k,next);}visit(row.id,new Set());
      }
      if(table==='controls'){ref('projects','projects',true);ref('risks','risks',true);}
      if(table==='tests'){required('control','کنترل');ref('control','controls');if(['effective','partial','ineffective'].includes(row.result)){for(const [k,l]of [['evidence','شواهد آزمون'],['testDate','تاریخ آزمون'],['assessor','ارزیاب']])required(k,l);}}
      if(table==='acceptances'){
        required('risk','ریسک');ref('risk','risks');const risk=r.risks.find(x=>x.id===row.risk);if(!can(actor,'accept',risk))throw Error('فقط حساب مالک همین ریسک می‌تواند پذیرش را ثبت کند.');
        for(const [k,l]of [['reason','دلیل پذیرش'],['due','تاریخ بازنگری']])required(k,l);
        if(reduction(risk)===null)throw Error('ارزیابی مجدد معتبر ریسک لازم است.');
      }
      if(table==='changes'&&row.status==='approved'){if(!can(actor,'approve'))throw Error('مجوز تصویب Baseline لازم است.');required('reason','دلیل تغییر Baseline');}
      if(table==='plans'&&row.status==='closed'){
        const risks=r.risks.filter(x=>(row.risks||[]).includes(x.id)),projects=r.projects.filter(p=>(p.plans||[]).includes(row.id)),controls=r.controls.filter(c=>(c.projects||[]).some(id=>projects.some(p=>p.id===id)));
        if(!risks.length||!projects.length||!controls.length||projects.some(p=>progress(p,r,row.updated.slice(0,10)).actual!==100)||controls.some(c=>controlResult(c,r)!=='effective')||risks.some(x=>!r.acceptances.some(a=>a.risk===x.id&&a.riskRevision===x.updated&&day(a.due)>=day(row.updated.slice(0,10)))))throw Error('اختتام نیازمند پیشرفت کامل، کنترل‌های اثربخش و پذیرش جاری ریسک‌های ارزیابی‌شده است.');
      }
    } else {
      if(table==='activities'){required('service','محصول / خدمت');ref('service','services');ref('resources','resources',true);}
      if(['bias','dependencies','actions','reviews','exercises'].includes(table)){required('activity','فعالیت');ref('activity','activities');}
      if(table==='plans'){if(!row.activities?.length)throw Error('حداقل یک فعالیت به BCP متصل کنید.');ref('activities','activities',true);}
      if(table==='exercises'){ref('plan','plans');if(row.actualDate && !row.evidence)throw Error('برای ثبت نتیجه واقعی آزمون، شواهد لازم است.');}
      if(table==='bias'){
        const t=targets(row,r.activities.find(a=>a.id===row.activity),state.settings);
        if(num(row.approvedMbco)!==null&&row.approvedMbco!==t.calculatedMbco.percent&&!row.overrideReason)throw Error('تغییر دستی MBCO نیازمند دلیل است.');
        for(const [cat,scores] of Object.entries(row.impacts||{}))for(const cell of Object.values(scores)){if(num(cell.score)!==null&&(num(cell.score)<0||num(cell.score)>state.settings.scaleMax))throw Error('امتیاز اثر خارج از مقیاس است.');}
        if(row.status==='approved'&&(!row.owner||[t.mtpd,t.rto,t.mbco].some(x=>num(x)===null)||(!row.rpoNA&&t.rpo===null)||!row.evidence))throw Error('تصویب BIA نیازمند مالک، شواهد، MTPD و اهداف معتبر است.');
      }
      if(table==='actions'&&row.status==='closed'&&(!row.verifiedBy||!row.verificationDate||!row.verificationMethod))throw Error('اختتام اقدام نیازمند روش، نام و تاریخ تأیید اثربخشی است.');
    }
    if(row.status==='approved'&&previous?.status!=='approved'&&!can(actor,'approve'))throw Error('حساب شما مجوز تصویب ندارد.');
  }
  return {num,clamp,unique,mean,diff,day,days,due,review,human,categories,defaults,mtpd,mbco,achievable,recommended,targets,depGap,backlog,exercise,activityState,progress,controlResult,riskScore,reduction,radar,validateWeights,validState,can,validateEntity};
})();
