/* Keep the shield-and-eye identity in a self-contained, scalable brand mark. */
function V18BrandMark({size=74,variant='sidebar',className='',x,y,width,height,decorative=false}){
 const key='v18-brand-'+Ia.useId().replace(/[^a-zA-Z0-9_-]/g,''),id=name=>key+'-'+name,paint=name=>'url(#'+id(name)+')';
 return <svg className={'v18-brand-mark v18-brand-mark--'+variant+(className?' '+className:'')} data-v18-brand-mark={variant} viewBox="0 0 128 128" width={width??size} height={height??size} x={x} y={y} role={decorative?undefined:'img'} aria-label={decorative?undefined:'نشان دیدبان امنیت؛ سپر حفاظت و چشم پایش'} aria-hidden={decorative?true:undefined}>
  <defs>
   <linearGradient id={id('rim')} x1="22" y1="11" x2="100" y2="117" gradientUnits="userSpaceOnUse"><stop stopColor="#B9F1FF"/><stop offset=".31" stopColor="#4DA5E8"/><stop offset=".64" stopColor="#1D608E"/><stop offset="1" stopColor="#53DCC5"/></linearGradient>
   <linearGradient id={id('shield')} x1="39" y1="17" x2="93" y2="116" gradientUnits="userSpaceOnUse"><stop stopColor="#183F6B"/><stop offset=".55" stopColor="#0C284A"/><stop offset="1" stopColor="#071B33"/></linearGradient>
   <linearGradient id={id('glass')} x1="34" y1="22" x2="82" y2="100" gradientUnits="userSpaceOnUse"><stop stopColor="#C5EEFF" stopOpacity=".21"/><stop offset="1" stopColor="#5ED8DB" stopOpacity="0"/></linearGradient>
   <linearGradient id={id('eye')} x1="34" y1="47" x2="94" y2="70" gradientUnits="userSpaceOnUse"><stop stopColor="#D9F8FF"/><stop offset=".58" stopColor="#FFFFFF"/><stop offset="1" stopColor="#80E9DB"/></linearGradient>
   <radialGradient id={id('iris')}><stop stopColor="#73EBD9"/><stop offset=".62" stopColor="#2B92AC"/><stop offset="1" stopColor="#103B61"/></radialGradient>
   <filter id={id('shadow')} x="-25%" y="-20%" width="150%" height="155%"><feDropShadow dx="0" dy="5" stdDeviation="4" floodColor="#061629" floodOpacity=".26"/></filter>
  </defs>
  <g filter={paint('shadow')}>
   <path d="M64 7 109 25v38c0 26-18 45-45 58-27-13-45-32-45-58V25Z" fill={paint('rim')}/>
   <path d="m64 11 41 17v35c0 23-16 41-41 54-25-13-41-31-41-54V28Z" fill={paint('shield')} stroke="#9DDDE9" strokeOpacity=".32" strokeWidth=".8"/>
   <path d="m64 15 36 15v32c0 20-14 36-36 49-22-13-36-29-36-49V30Z" fill="none" stroke="#82CCEC" strokeOpacity=".32" strokeWidth="1"/>
   <path d="m64 15-36 15v32c0 20 14 36 36 49Z" fill={paint('glass')}/>
   <path d="m34 36 11-5m49 5-11-5M31 75l8 4m58-4-8 4" fill="none" stroke="#7DDDD5" strokeOpacity=".6" strokeWidth="1.4" strokeLinecap="round"/>
   <path d="M34 57c9-12 20-20 30-20s21 8 30 20c-9 12-20 20-30 20S43 69 34 57Z" fill="#071D35" fillOpacity=".36" stroke={paint('eye')} strokeWidth="2.8" strokeLinejoin="round"/>
   <circle cx="64" cy="57" r="12.5" fill={paint('iris')} stroke="#B9F8EF" strokeWidth="1.8"/>
   <circle cx="64" cy="57" r="5.1" fill="#071D35"/>
   <circle cx="68" cy="53" r="2.7" fill="#FFFFFF"/>
   <circle cx="59" cy="61" r="1.2" fill="#9CF7E9" fillOpacity=".75"/>
   <path d="m49 91 10 10 23-25" fill="none" stroke="#62E4C8" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"/>
   <path d="m52 91 7 7 20-22" fill="none" stroke="#E0FFF5" strokeOpacity=".65" strokeWidth="1.1" strokeLinecap="round" strokeLinejoin="round"/>
   <path d="M43 23 64 15l22 9" fill="none" stroke="#DEFAFF" strokeOpacity=".55" strokeWidth="1.2" strokeLinecap="round"/>
  </g>
 </svg>;
}
