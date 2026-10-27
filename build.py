#!/usr/bin/env python3
"""Reproducible v15 integration over the unchanged version-6 application.
Usage: python build.py --esbuild /absolute/path/to/esbuild
"""
from pathlib import Path
import argparse, base64, colorsys, re, subprocess, importlib.util

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--esbuild',default=str(ROOT/'node_modules/.bin/esbuild'));args=p.parse_args()
source=ROOT/'src'; base=(source/'base-v6.html').read_text()
def replace(old,new,count=1):
 global base
 if base.count(old)!=count:raise RuntimeError(f'Integration anchor changed: {old[:95]} (found {base.count(old)}, expected {count})')
 base=base.replace(old,new)

_taxonomy_spec=importlib.util.spec_from_file_location('taxonomy_v13',source/'taxonomy-integration-v13.py')
_taxonomy=importlib.util.module_from_spec(_taxonomy_spec);_taxonomy_spec.loader.exec_module(_taxonomy)
base=_taxonomy.integrate(base)

modules=['jalali.js','minimal-domain.js','bcms-recovery.js','compliance.js','implementation-v15.js','improvements-domain-v12.js','minimal-primitives.jsx','date-ui.jsx','minimal-ui.jsx','dashboard-v10.jsx','bcms-recovery.jsx','minimal-rtp.jsx','minimal-bcms.jsx','minimal-radar.jsx','improvements-v12.jsx','implementation-v15.jsx']
combined='\n'.join((source/f).read_text() for f in modules)
compiled=subprocess.run([args.esbuild,'--loader=jsx','--jsx-factory=DH','--jsx-fragment=Ia.Fragment','--target=es2020','--charset=utf8'],input=combined,text=True,capture_output=True,check=True).stdout
replace('content="6"','content="15"')
replace("'didban-report-meta'];","'didban-report-meta','didban-rtp-independent-v2','didban-bcms-independent-v2'];")
replace('function js(){','/*V8_MODULES*/\nfunction js(){const [v7tab,setV7tab]=Ia.useState({rtp:"dashboard",bcms:"dashboard",improvements:"projects"});')
old='let Jd=[["dashboard","نمای کلی",to],["clauses","الزامات استاندارد",uo],["controls","کنترل‌های Annex A",vt],["improvements","اقدامات بهبود",Qt],["method","روش ارزیابی",fo],["risk","مدیریت ریسک",vt],["support","پشتیبانی سایت",()=>DH(DSIcon,{name:"support",size:19})]];'
nav=[('dashboard','داشبورد مدیریتی','dashboard'),('clauses','الزامات استاندارد','list'),('controls','کنترل‌های Annex A','shield'),('improvements','اقدامات اصلاحی','correct'),('rtp','Risk Treatment Plan','target'),('method','روش ارزیابی','method'),('risk','مدیریت ریسک','risk'),('bcms','تداوم کسب‌وکار (BCMS)','activity'),('support','پشتیبانی سایت','support')]
import json
new='let Jd=['+','.join('['+json.dumps(k)+','+json.dumps(title,ensure_ascii=False)+',()=>DH(V7Icon,{name:'+json.dumps(icon)+',size:19})]' for k,title,icon in nav)+'];'
replace(old,new)
oldnav='children:Jd.map(([c,y,P])=>(0,i.jsxs)("button",{className:a===c?"active":"",onClick:()=>{e(c),m("all"),S("all"),f(""),ja("all")},children:[(0,i.jsx)(P,{size:19}),y,c==="controls"&&(0,i.jsx)("em",{children:"۹۳"})]},c))'
newnav='children:Jd.map(([c,y,P])=>DH(Ia.Fragment,{key:c},DH("button",{className:a===c?"active":"",onClick:()=>{e(c);m("all");S("all");f("");ja("all");},"aria-current":a===c?"page":undefined},DH(P,{}),DH("span",{},y,c==="rtp"?DH("small",{style:{display:"block"}},"برنامه‌های مقابله با ریسک"):null),c==="controls"?DH("em",{},"۹۳"):null),a===c?(c==="improvements"?DH(V13CorrectiveSubnav,{tab:v7tab.improvements,onTab:t=>setV7tab(prev=>({...prev,improvements:t}))}):(c==="rtp"||c==="bcms")?DH(V7Subnav,{type:c,tab:v7tab[c],onTab:t=>setV7tab(prev=>({...prev,[c]:t}))}):null):null))'
replace(oldnav,newnav)
replace('a==="risk"||a==="support"?"none":undefined','["risk","support","rtp","bcms"].includes(a)?"none":undefined')
replace('a==="support"?(0,i.jsx)(DSSupport,','(a==="rtp"||a==="bcms")?DH(V7Module,{key:a,type:a,tab:v7tab[a],onTab:t=>setV7tab(prev=>({...prev,[a]:t}))}):a==="support"?(0,i.jsx)(DSSupport,')
start=base.index('(0,i.jsxs)("section",{className:"panel concept-panel"')
end=base.index(',(0,i.jsxs)("div",{className:"bottomgrid"',start)
base=base[:start]+'DH(V7ConceptRadar,{data:G,onGroup:gL,onItem:Pe})'+base[end:]
replace("const dsNav=[['dashboard','نمای کلی'],['clauses','الزامات استاندارد'],['controls','کنترل‌های Annex A'],['improvements','اقدامات بهبود'],['method','روش ارزیابی'],['risk','مدیریت ریسک'],['support','پشتیبانی سایت']];",'const dsNav='+json.dumps([[k,title] for k,title,icon in nav],ensure_ascii=False)+';')
replace("onClick:()=>{setTab(k);setEdit(null)}},v)","onClick:()=>{setTab(k);setEdit(null)}},DH(V7Icon,{name:({overview:'dashboard',context:'settings',assets:'resource',risks:'risk',method:'method'})[k]}),v)")
# Extend the existing all-project backup and atomic import. Older v6 backups start empty new modules.
replace("reportMeta:DSReadReportMeta(),assessments:t,projects:q,risk}","reportMeta:DSReadReportMeta(),assessments:t,projects:q,risk,rtp:V7Read('rtp'),bcms:V7Read('bcms')}")
replace("format:'didban-security-project-v4'","format:'didban-security-project-v5'")
replace('setDSImport({project,assessments:assess,projects:projects||[],risk,meta})',"setDSImport({project,assessments:assess,projects:projects||[],risk,meta,rtp:parsed.rtp===undefined?V7D.defaults('rtp'):V7D.validState(parsed.rtp,'rtp'),bcms:parsed.bcms===undefined?V7D.defaults('bcms'):V7D.validState(parsed.bcms,'bcms')})")
replace("'didban-report-meta':JSON.stringify({...payload.meta,organization})}","'didban-report-meta':JSON.stringify({...payload.meta,organization}),'didban-rtp-independent-v2':JSON.stringify(payload.rtp||V7D.defaults('rtp')),'didban-bcms-independent-v2':JSON.stringify(payload.bcms||V7D.defaults('bcms'))}")
replace('async function dsExcel(assessments,projects,risk,meta){','async function dsExcel(assessments,projects,risk,meta,customTables){')
replace('tables=dsReportTables(assessments,projects,risk,meta),ns=', 'tables=customTables||dsReportTables(assessments,projects,risk,meta),ns=')
replace("ddDownload('Didban_Amniat_Audit.xlsx'","ddDownload(customTables?'Didban_Module_Report.xlsx':'Didban_Amniat_Audit.xlsx'")
# Native inline theme variables keep existing charts live when the theme changes.
replace('Jt=["#ef7274","#e9b853","#52b5db","#22b6a8","#36876f"]','Jt=["var(--impl-none)","var(--impl-planned)","var(--impl-partial)","var(--impl-implemented)","var(--impl-effective)"],JtText=["var(--impl-none-fg)","var(--impl-planned-fg)","var(--impl-partial-fg)","var(--impl-implemented-fg)","var(--impl-effective-fg)"]')
base=re.sub(r'(Jt\[[^\]]+\])\+"(?:12|15|18|20|22|2a)"',r'"color-mix(in srgb,"+\1+" 9%,var(--surface))"',base)
# Implementation status colors stay separate from compliance and alert semantics.
replace('className:"badge",style:{color:Jt[c.status]', 'className:"badge","data-implementation":c.status,style:{color:JtText[c.status]')
replace('className:"badge",style:{color:Jt[G[c.id].status]', 'className:"badge","data-implementation":G[c.id].status,style:{color:JtText[G[c.id].status]')
replace('color:Jt[y]', 'color:JtText[y]')
replace('className:"badge",children:"ارزیابی نشده"', 'className:"badge","data-implementation":"unknown",style:{background:"var(--impl-unknown)",color:"var(--impl-unknown-fg)"},children:"ارزیابی نشده"')
replace("const dcColors=['#15803d','#dc2626','#991b1b','#059669','#2563eb'];","const dcColors=['var(--success)','var(--minor)','var(--danger)','var(--info)','var(--warning)'];")
replace("function dcBadge(value){return DH('span',{className:'dc-badge',style:{background:value==null?'#64748b':dcColors[value]}},value==null?'ثبت نشده':dcNames[value])}","function dcBadge(value){const c=value==null?'var(--muted)':dcColors[value];return DH('span',{className:'dc-badge',style:{background:'color-mix(in srgb,'+c+' 4%,var(--surface))',color:c,border:'1px solid '+c}},value==null?'ثبت نشده':dcNames[value])}")
replace('stroke:"#e4ecee"','stroke:"var(--border)"',2)
replace('fill:"#71858d"','fill:"var(--text-secondary)"')
replace('fill:"#23b8a72a",stroke:"#24b6a6"','fill:"var(--radar-fill)",stroke:"var(--chart-1)"')
replace('fill:"#fff",stroke:"#24b6a6"','fill:"var(--surface)",stroke:"var(--chart-1)"')
replace('fill:"#9aaeb2"','fill:"var(--text-secondary)"',2)
replace("const drColor=n=>n<=4?'#15803d':n<=9?'#b45309':n<=16?'#dc2626':'#991b1b';","const drColor=n=>n<=4?'var(--success)':n<=9?'var(--warning)':n<=16?'var(--minor)':'var(--danger)';")
replace("style:{background:drColor(n)}","style:{background:'color-mix(in srgb,'+drColor(n)+' 4%,var(--surface))',color:drColor(n),border:'1px solid '+drColor(n)}")
replace("style:{background:drColor(l*p)}","style:{background:'color-mix(in srgb,'+drColor(l*p)+' 4%,var(--surface))',color:drColor(l*p)}")
replace('["#28b4a7","#64baca","#6199d5","#698eab"]','["var(--chart-1)","var(--chart-2)","var(--chart-5)","var(--chart-8)"]')
replace('اقدامات بهبود و داده‌های مستقل ریسک. اطلاعات هیچ پروژه دیگری در این فایل قرار نمی‌گیرد.','اقدامات اصلاحی، داده‌های مستقل ریسک و دو ماژول مستقل RTP و BCMS. اطلاعات هیچ پروژه دیگری در این فایل قرار نمی‌گیرد.')
# Replace the header's two-state switch with explicit Light / Dark / System preference.
start=base.index("[dark,setDark]=Ia.useState",base.index('function DSHeader('));end=base.index(' const normal=',start)
base=base[:start]+"[theme,setTheme]=Ia.useState(()=>window.V7ThemePreference||'light');\n Ia.useEffect(()=>{window.V7ApplyTheme(theme);},[theme]);const dark=document.documentElement.dataset.theme==='dark';\n"+base[end:]
old="action(dark?'sun':'moon',dark?'حالت روشن':'حالت تاریک',()=>setDark(!dark),dark)"
new="DH('select',{'aria-label':'پوسته سایت',className:'v7-theme-select',value:theme,onChange:e=>setTheme(e.target.value)},DH('option',{value:'light'},'☀ روشن'),DH('option',{value:'dark'},'☾ تاریک'),DH('option',{value:'system'},'سیستم'))"
replace(old,new)
# Simplify only the native optional audit fields; retain the audit workflow.
a=base.index('const DSExtraFields=');b=base.index('const DSOrgGroups=',a)
base=base[:a]+"""const DSExtraFields={reviewer:'نام ممیز',correctiveAction:'اقدام اصلاحی در ممیزی قبلی (در صورت وجود)',previousCompliance:'وضعیت انطباق در ممیزی قبلی'};
function DSExtractAuditExtra(a){const out={};for(const key of Object.keys(DSExtraFields)){if(a[key]!==undefined&&typeof a[key]!=='string')throw Error('اطلاعات تکمیلی نامعتبر است.');out[key]=a[key]||'';}return out;}
function DSAuditExtra({value,onChange}){return DH('details',{className:'ds-audit-extra'},DH('summary',{},'اطلاعات ممیزی قبلی (در صورت وجود)'),...Object.entries(DSExtraFields).filter(([key])=>key!=='reviewer').map(([key,label])=>DH('label',{key},label,key==='previousCompliance'?DH('select',{'aria-label':label,value:value[key]??'',onChange:e=>onChange({...value,[key]:e.target.value})},DH('option',{value:''},'ثبت نشده'),...dcNames.map((name,i)=>DH('option',{key:i,value:String(i)},name))):DH('textarea',{'aria-label':label,value:value[key]||'',onChange:e=>onChange({...value,[key]:e.target.value})}))));}
function V10AuditReviewer({value,onChange,disabled}){return DH('label',{className:'v10-current-reviewer'},'نام ممیز',DH('input',{'aria-label':'نام ممیز',value:value.reviewer||'',disabled,onChange:e=>onChange({...value,reviewer:e.target.value}),placeholder:'نام ممیز این بند یا کنترل'}));}
"""+base[b:]
replace('(0,i.jsx)(DSAuditExtra,{value:n,onChange:L}),(0,i.jsx)(dcField,','(0,i.jsx)(DSAuditExtra,{value:n,onChange:L}),DH(V10AuditReviewer,{value:n,onChange:L,disabled:u}),(0,i.jsx)(dcField,')
replace("const dsXml=s=>String(s??'')","const dsXml=s=>V8Print(s)")
# Add the v10 dashboard charts before the legacy-only Babel pass.
import importlib.util
_dashboard_spec=importlib.util.spec_from_file_location('dashboard_integration',source/'dashboard-integration.py')
_dashboard=importlib.util.module_from_spec(_dashboard_spec);_dashboard_spec.loader.exec_module(_dashboard)
base=_dashboard.integrate(base)
for _name in ['compliance-integration-v12','improvements-integration-v12','dashboard-integration-v13','corrective-integration-v13','implementation-integration-v15']:
 _spec=importlib.util.spec_from_file_location(_name,source/(_name+'.py'))
 _integration=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_integration)
 base=_integration.integrate(base)
# Preserve the original banner/logo and use a font-independent pause/play icon.
replace("paused?'▷':'Ⅱ'","DH('svg',{viewBox:'0 0 24 24',width:16,height:16,fill:'none',stroke:'currentColor',strokeWidth:2,'aria-hidden':true},DH('path',{d:paused?'m9 5 10 7-10 7Z':'M8 5v14M16 5v14'}))")
# Transform legacy React date inputs and visible date children at build time only.
def transform_script(match):
 script=match.group(1)
 if '/*V8_MODULES*/' not in script:return match.group(0)
 result=subprocess.run(['node',str(source/'transform-legacy.cjs')],input=script,text=True,capture_output=True,check=True)
 print(result.stderr.strip())
 return '<script>'+result.stdout.replace('/*V8_MODULES*/',compiled.replace('</script','<\\/script'))+'</script>'
base=re.sub(r'<script>([\s\S]*?)</script>',transform_script,base)

# Harmonize legacy CSS by declaration, retaining selectors, responsive and print rules.
def color_token(raw,property):
 h=raw.lstrip('#');h=''.join(c*2 for c in h) if len(h) in (3,4) else h
 if len(h)<6:return raw
 r,g,b=[int(h[i:i+2],16)/255 for i in (0,2,4)];hue,light,sat=colorsys.rgb_to_hls(r,g,b)
 if property in ('background','background-color','backgroundColor'):token='--surface' if light>.96 else '--surface-alt'
 elif 'border' in property or property in ('stroke','box-shadow'):token='--border'
 elif light>.87:token='--text-secondary' # light legacy text is replaced by readable semantic text
 elif sat<.25:token='--text-primary' if light<.27 else '--text-secondary'
 elif light<.25:token='--text-primary'
 elif .04<hue<.18:token='--warning'
 elif hue<.04 or hue>.92:token='--danger'
 elif .18<hue<.45:token='--success'
 elif .45<hue<.57:token='--accent'
 else:token='--primary'
 return 'var('+token+')'
def legacy_css(match):
 text=match.group(1)
 text=re.sub(r'background(?:-image)?:\s*(?:linear|radial)-gradient\([^;{}]*\)', 'background:var(--surface-alt)',text)
 def declaration(m):
  prop,val=m.group(1),m.group(2)
  val=re.sub(r'#[0-9a-fA-F]{3,8}\b',lambda c:color_token(c.group(0),prop),val)
  if prop in ('background','background-color') and val.strip() in ('white','#fff'):val='var(--surface)'
  if prop=='color' and val.strip()=='white':val='var(--primary-contrast)'
  return prop+':'+val
 text=re.sub(r'([\w-]+):([^;{}]+)',declaration,text)
 return '<style>'+text+'</style>'
base=re.sub(r'<style>([\s\S]*?)</style>',legacy_css,base)
fonts=''
for family,file in [('Vazirmatn','vazirmatn-arabic-wght-normal.woff2'),('Inter','inter-latin-wght-normal.woff2')]:
 data=base64.b64encode((ROOT/'assets'/file).read_bytes()).decode()
 fonts+="@font-face{font-family:'"+family+"';font-style:normal;font-weight:100 900;src:url(data:font/woff2;base64,"+data+") format('woff2');font-display:swap}"
bootstrap="""<script>(function(){let pref='light';try{pref=window.localStorage.getItem('didban-theme')||'light'}catch{}window.V7ThemePreference=pref;window.V7ApplyTheme=function(p){window.V7ThemePreference=p;document.documentElement.dataset.theme=p==='system'?(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'):p;try{window.localStorage.setItem('didban-theme',p)}catch{}};window.V7ApplyTheme(pref);matchMedia('(prefers-color-scheme:dark)').addEventListener('change',()=>{if(window.V7ThemePreference==='system')window.V7ApplyTheme('system')});})();</script>"""
base=base.replace('</head>','<style>'+fonts+''.join((source/name).read_text() for name in ['theme.css','dashboard-v10.css','bcms-recovery.css','layout-v11.css','improvements-v12.css','dashboard-v13.css','implementation-v15.css','bcms-form-v15.css'])+'</style>'+bootstrap+'</head>')
# Preserve historical filename aliases; clean HTMLs contain no organization data.
for filename in ['Didban_Amniat_Offline.html','Didban_ISMS_Offline.html']:(ROOT/filename).write_text(base)
fresh=base.replace('<meta name="didban-version" content="15">','<meta name="didban-version" content="15"><meta name="didban-store-id" content="fresh-v8">')
(ROOT/'Didban_Amniat_Offline_Fresh.html').write_text(fresh)
print('Built offline v15:',len(base.encode()),'bytes; legacy content retained; embedded fonts and all code.')
