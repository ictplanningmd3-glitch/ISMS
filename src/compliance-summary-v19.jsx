function V19ComplianceIcon({value,size=24}){
 const paths={
  5:['M21 11a9 9 0 1 1-8-8','M17 11a5 5 0 1 1-6-4','m12 12 9-9m-5 0h5v5'],
  0:['M8 4H5v17h14V4h-3M8 2h8v5H8z','m8 13 3 3 5-6'],
  4:['m3 17 6-6 4 4 8-10','M15 5h6v6'],
  3:['M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z','M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0'],
  1:['m12 3 10 18H2Z','M12 9v5m0 3h.01'],
  2:['M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0','m8 8 8 8m0-8-8 8']
 };
 return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{(paths[value]||paths[0]).map((d,i)=><path key={i} d={d}/>)}</svg>;
}

function V19ComplianceSummary({data={}}){
 const summary=V19Compliance.summary(J,data),known=summary.segments.slice(0,6),color=s=>'var('+s.token+')',label=s=>s.key==='unknown'?'ثبت نشده':V9Compliance.level(s.key).label,ring=126,circumference=2*Math.PI*ring;
 let cumulative=0;
 const slices=summary.segments.filter(s=>s.count>0).map(s=>{const offset=cumulative,circle=s.percentage/100*circumference; cumulative+=circle;return {...s,offset,length:circle,mid:(offset+circle/2)/circumference*Math.PI*2-Math.PI/2};});
 const date=summary.lastUpdated?new Intl.DateTimeFormat('fa-IR',{timeZone:'Asia/Tehran',year:'numeric',month:'long',day:'numeric'}).format(new Date(summary.lastUpdated)):null;
 const positivePercent=summary.rate===null?'—':V8N(summary.rate)+'٪';
 return <section className="v19-compliance-summary" data-v19-compliance-summary>
  <div className="v19-compliance-heading"><div className="v19-compliance-heading-title"><span><V19ComplianceIcon value={0} size={30}/></span><div><h2>وضعیت انطباق با استاندارد</h2><small lang="en" dir="ltr">Standard Compliance</small></div></div><div className="v19-compliance-updated" data-v19-compliance-updated><V7Icon name="history" size={17}/><span>{date?'آخرین به‌روزرسانی ممیزی: '+date:summary.assessed?'تاریخ آخرین ممیزی ثبت نشده':'هنوز ممیزی ثبت نشده'}</span></div></div>
  <div className="v19-compliance-layout">
   <div className="v19-compliance-donut-wrap"><svg className="v19-compliance-donut" data-v19-compliance-donut viewBox="0 0 360 360" role="img" aria-label={'توزیع نتایج ممیزی در '+V8N(summary.total)+' مورد قابل اعمال؛ انطباق کلی '+positivePercent}><circle cx="180" cy="180" r={ring} fill="none" stroke="var(--surface-alt)" strokeWidth="48"/>{slices.map(s=><circle key={s.key} data-v19-compliance-segment={s.key} data-count={s.count} data-percentage={s.percentage} cx="180" cy="180" r={ring} fill="none" stroke={color(s)} strokeWidth="48" strokeDasharray={(s.count===summary.total?s.length:Math.max(0,s.length-2))+' '+(circumference-(s.count===summary.total?s.length:Math.max(0,s.length-2)))} strokeDashoffset={-s.offset} transform="rotate(-90 180 180)"><title>{label(s)+': '+V8N(s.count)+' مورد، '+V8N(s.percentage)+'٪'}</title></circle>)}{slices.filter(s=>s.percentage>=8).map(s=><text key={s.key} x={180+Math.cos(s.mid)*ring} y={180+Math.sin(s.mid)*ring+4} textAnchor="middle" fill={s.key===2?'#FFFFFF':'#0B1220'} style={{fill:s.key===2?'#FFFFFF':'#0B1220'}} className="v19-compliance-percent-label" fontSize="13" fontWeight="700">{V8N(s.percentage)}٪</text>)}<text x="180" y="151" textAnchor="middle" fill="var(--text-primary)" style={{fill:'var(--text-primary)'}} fontSize="17" fontWeight="700">انطباق کلی</text><text x="180" y="203" textAnchor="middle" fill="var(--audit-conformity-fg)" style={{fill:'var(--audit-conformity-fg)'}} className="v19-compliance-rate-value" data-v19-compliance-donut-rate fontSize="42" fontWeight="800">{positivePercent}</text><text x="180" y="234" textAnchor="middle" fill="var(--text-secondary)" style={{fill:'var(--text-secondary)'}} fontSize="12">{V8N(summary.positive)} از {V8N(summary.total)} مورد قابل اعمال</text></svg><p>{summary.total?'توزیع همهٔ نتایج ممیزی؛ ثبت‌نشده نیز سهم مستقل دارد.':'مورد قابل اعمالی برای محاسبه وجود ندارد.'}</p></div>
   <div className="v19-compliance-main">
    <div className="v19-compliance-counts">{known.map(s=><article key={s.key} data-v19-compliance-count={s.key} data-count={s.count} style={{'--v19-audit-color':color(s)}}><V19ComplianceIcon value={s.key} size={27}/><strong>{V8N(s.count)}</strong><span>{label(s)}</span><small lang="en" dir="ltr">{s.english}</small></article>)}</div>
    <div className="v19-compliance-lower">
     <div className="v19-compliance-legend" aria-label="تعداد و سهم نتایج ممیزی">{summary.segments.map(s=><div key={s.key} data-v19-compliance-legend={s.key} data-v19-compliance-count={s.key==='unknown'?'unknown':undefined} data-count={s.count}><span><i style={{background:color(s)}}/>{label(s)}</span><small>{summary.total?V8N(s.percentage)+'٪':'—'}</small><b>{V8N(s.count)}</b></div>)}</div>
     <section className="v19-compliance-overall" data-v19-compliance-rate data-positive={summary.positive} data-total={summary.total} data-rate={summary.rate===null?'none':summary.rate}><h3>میزان انطباق کلی</h3><div className="v19-compliance-progress"><div role="progressbar" aria-label="درصد انطباق کلی" aria-valuemin="0" aria-valuemax="100" aria-valuenow={summary.rate===null?undefined:summary.rate}><i style={{width:(summary.rate??0)+'%'}}/></div><strong>{positivePercent}</strong></div><p>{V8N(summary.positive)} مورد از {V8N(summary.total)} مورد قابل اعمال</p><small>نقطه قوت + انطباق + توصیه برای بهبود + مشاهده</small><p className="v19-compliance-basis">مبنای درصد، تمام بندها و کنترل‌های قابل اعمال است؛ موارد ثبت‌نشده در مخرج محاسبه باقی می‌مانند.</p></section>
    </div>
   </div>
  </div>
 </section>;
}
