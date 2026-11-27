/* Calendar conversion uses the browser's Persian calendar, including leap years. */
var V8DateD = (() => {
 const latin=s=>String(s??'').replace(/[۰-۹٠-٩]/g,c=>'۰۱۲۳۴۵۶۷۸۹'.includes(c)?'۰۱۲۳۴۵۶۷۸۹'.indexOf(c):'٠١٢٣٤٥٦٧٨٩'.indexOf(c));
 const fmt=new Intl.DateTimeFormat('en-US-u-ca-persian',{timeZone:'UTC',year:'numeric',month:'2-digit',day:'2-digit'});
 const parts=date=>{const p=Object.fromEntries(fmt.formatToParts(date).map(x=>[x.type,x.value]));return [+p.year,+p.month,+p.day];};
 const isoDate=s=>{if(!/^\d{4}-\d{2}-\d{2}$/.test(s||''))return false;const d=new Date(s+'T12:00:00Z');return !Number.isNaN(+d)&&d.toISOString().slice(0,10)===s;};
 const format=(s,persian=true)=>{if(!s)return '';const raw=String(s).slice(0,10);if(!isoDate(raw))return String(s);const p=parts(new Date(raw+'T12:00:00Z'));const result=p[0]+'/'+String(p[1]).padStart(2,'0')+'/'+String(p[2]).padStart(2,'0');return persian?result.replace(/\d/g,c=>'۰۱۲۳۴۵۶۷۸۹'[c]):result;};
 const cache=new Map();
 function parse(value){const s=latin(value).trim().replace(/[.\-]/g,'/');if(!s)return '';const p=s.match(/^(\d{4})\/(\d{1,2})\/(\d{1,2})$/);if(!p)throw Error('تاریخ را به صورت ۱۴۰۵/۰۸/۰۱ وارد کنید.');const y=+p[1],m=+p[2],d=+p[3];
  if(y>=1800){const out=y+'-'+String(m).padStart(2,'0')+'-'+String(d).padStart(2,'0');if(isoDate(out))return out;throw Error('تاریخ معتبر نیست.');}
  if(y<1000||y>1799||m<1||m>12||d<1||d>31)throw Error('تاریخ شمسی معتبر نیست.');const key=y*10000+m*100+d;if(cache.has(key))return cache.get(key);
  let lo=Math.floor(Date.UTC(y+620,0,1)/86400000),hi=Math.floor(Date.UTC(y+623,0,1)/86400000);
  while(lo<=hi){const mid=Math.floor((lo+hi)/2),q=parts(new Date(mid*86400000+43200000)),n=q[0]*10000+q[1]*100+q[2];if(n===key){const out=new Date(mid*86400000).toISOString().slice(0,10);cache.set(key,out);return out;}if(n<key)lo=mid+1;else hi=mid-1;}throw Error('این روز در تقویم شمسی وجود ندارد.');
 }
 const today=()=>new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Tehran',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
 const days=(a,b)=>(Date.parse(a+'T12:00:00Z')-Date.parse(b+'T12:00:00Z'))/86400000;
 const print=value=>String(value??'').replace(/\b(\d{4}-\d{2}-\d{2})(?:T\d{2}:\d{2}(?::[\d.]+)?Z?)?\b/g,(all,date)=>isoDate(date)?format(date):all);
 return {latin,parts,isoDate,format,parse,today,days,print};
})();
