const assert=require('node:assert/strict'),P=require('../src/portfolio-domain-v19.js');
let checks=0;function test(name,fn){fn();checks++;console.log('✓',name);}
const project=(id,extra={})=>({id,title:id,months:1,start:'2026-11-01',due:'2026-12-01',progress:50,status:'active',...extra});
test('date validation rejects impossible dates and elapsed days remain exact across leap boundaries',()=>{
 assert.equal(P.isDate('2026-02-30'),false);assert.equal(P.isDate('2024-02-29'),true);assert.equal(P.days('2024-03-01','2024-02-28'),2);assert.equal(P.days('bad','2026-01-01'),null);
});
test('health distinguishes completion, overdue execution, elapsed-time lag and unknown dates',()=>{
 const today='2026-11-16';
 assert.equal(P.health(project('complete',{status:'completed',progress:100}),today).key,'completed');
 assert.equal(P.health(project('late',{due:'2026-11-15',progress:100}),today).key,'delayed');
 assert.equal(P.health(project('behind',{progress:49}),today).key,'atrisk');
 assert.equal(P.health(project('track',{progress:50}),today).key,'ontrack');
 assert.equal(P.health(project('nodates',{start:'',due:''}),today).key,'unknown');
 assert.equal(P.health(project('blocked',{status:'blocked',start:'',due:''}),today).key,'atrisk');
});
test('future starts expect zero and caller completion callbacks can preserve independent RTP semantics',()=>{
 const p=project('future',{start:'2026-12-01',due:'2027-01-01',progress:0});assert.equal(P.health(p,'2026-11-16').expected,0);assert.equal(P.health(p,'2026-11-16').key,'ontrack');
 const rtp=project('rtp',{status:'effective',progress:100});assert.equal(P.health(rtp,'2027-01-01',{completed:x=>x.status==='effective'}).key,'completed');
 const paused=project('pause',{status:'paused',progress:80});assert.equal(P.health(paused,'2026-11-16',{blocked:x=>x.status==='paused'}).key,'atrisk');
});
test('the four cards use actual A/B/C membership and averages, with no six-month example data',()=>{
 const rows=[project('a',{months:1,progress:10}),project('b',{months:2,progress:30}),project('c',{months:3,progress:80,status:'completed'})],s=P.summary(rows,'2026-11-16');
 assert.equal(s.total,3);assert.equal(s.progress,40);assert.deepEqual(s.groups.map(g=>g.key),['A','B','C']);assert.deepEqual(s.groups.map(g=>g.count),[1,1,1]);assert.equal(Object.values(s.counts).reduce((a,b)=>a+b,0),3);assert.equal(s.groups[2].counts.completed,1);assert.equal(P.summary([],'2026-11-16').progress,null);
});
test('timeline intervals align to Persian month boundaries and cover the exact inclusive project range',()=>{
 const r=P.timeline([project('p',{start:'2026-03-15',due:'2026-04-04'})],'2026-03-25');
 assert.equal(r.start,'2026-03-15');assert.equal(r.end,'2026-04-04');assert.equal(r.days,21);assert.equal(r.months[0].end,'2026-03-20');assert.equal(r.months[1].start,'2026-03-21');assert.ok(Math.abs(r.months.reduce((sum,m)=>sum+m.width,0)-100)<1e-10);assert.equal(r.todayInRange,true);
});
test('bars preserve relative duration and progress without placing missing or reversed dates on a false timeline',()=>{
 const rows=[project('a',{start:'2026-11-01',due:'2026-11-10',progress:40}),project('b',{start:'2026-11-11',due:'2026-11-20',progress:100})],range=P.timeline(rows,'2026-11-10'),a=P.bar(rows[0],range),b=P.bar(rows[1],range);
 assert.equal(a.left,0);assert.equal(a.width,50);assert.equal(a.progressWidth,20);assert.equal(b.left,50);assert.equal(b.width,50);assert.equal(b.progressWidth,50);assert.equal(P.bar(project('bad',{start:'2026-11-10',due:'2026-11-01'}),range).valid,false);assert.equal(P.bar(project('missing',{start:''}),range).valid,false);
});
test('single-day projects remain visible and outside-range today is explicitly distinguishable',()=>{
 const p=project('same',{start:'2026-11-01',due:'2026-11-01'}),r=P.timeline([p],'2026-11-11');assert.equal(r.days,1);assert.equal(P.bar(p,r).width,100);assert.equal(r.todayInRange,false);assert.equal(r.todayPercent,100);assert.equal(P.timeline([project('missing',{start:'',due:''})],'2026-11-11').empty,true);
});
test('very long real schedules use a bounded compressed display rather than unbounded month rendering',()=>{
 const r=P.timeline([project('long',{start:'1900-01-01',due:'2100-01-01'})],'2026-11-11');assert.equal(r.dense,true);assert.equal(r.months.length,24);assert.ok(Math.abs(r.months.reduce((sum,m)=>sum+m.width,0)-100)<1e-10);
});
console.log(checks+' portfolio dashboard checks passed');
