/* Verbatim controls from the user's uploaded Annex A, separate from audit guidance. */
function V17AnnexAuditTitle({id}){
 const item=V17AnnexControls[id];
 if(!item)return null;
 return <h2 id="audit-title" className="v17-annex-audit-title"><span data-v17-title-fa lang="fa" dir="rtl">{item.titleFa}</span><span className="english-title" data-v17-title-en lang="en" dir="ltr">{item.titleEn}</span></h2>;
}

function V17AnnexReference({id}){
 const item=V17AnnexControls[id];
 if(!item)return null;
 const source=item.source;
 return <section className="v17-annex-reference" data-v17-annex-reference={id} aria-label={'متن کنترل استاندارد '+id}>
  <div className="v17-annex-reference-head"><span>متن مرجع کنترل</span><small data-v17-source lang="en" dir="ltr">{source.standard} · Annex {source.annex} · {id}{source.printedPage?' · p. '+source.printedPage:''}</small></div>
  <div className="v17-annex-reference-body">
   <div className="v17-annex-reference-en" lang="en" dir="ltr"><h3>Control</h3><p data-v17-text-en>{item.textEn}</p></div>
   <div className="v17-annex-reference-fa" lang="fa" dir="rtl"><h3>ترجمهٔ فنی کنترل</h3><p data-v17-text-fa>{item.textFa}</p></div>
  </div>
 </section>;
}
