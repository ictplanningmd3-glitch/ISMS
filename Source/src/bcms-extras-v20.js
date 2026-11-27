/* Optional additive plan data. Existing v2 records and time units remain unchanged. */
var V20BcmsExtras=(()=>{
 const contacts=['name','contactMethod','contactNumber','role','authentication','responsibilities'];
 const resources=['name','type','quantity','location','owner','notes'];
 function validate(b){for(const [key,columns] of [['emergencyContacts',contacts],['planResources',resources]]){if(b[key]===undefined)continue;if(!Array.isArray(b[key])||b[key].length>100)throw Error('حداکثر ۱۰۰ ردیف برای اطلاعات تکمیلی طرح مجاز است.');const ids=new Set();for(const row of b[key]){if(!row||typeof row.id!=='string'||!row.id||ids.has(row.id)||columns.some(k=>row[k]!==undefined&&typeof row[k]!=='string'))throw Error('ساختار اطلاعات تکمیلی طرح معتبر نیست.');ids.add(row.id);}}for(const key of ['planDocuments','operatingProcedure'])if(b[key]!==undefined&&typeof b[key]!=='string')throw Error('مستندات و روش کار طرح باید متنی باشند.');return b;}
 return {contacts,resources,validate};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=V20BcmsExtras;
