/* Build-time transformations only; never shipped as a browser dependency. */
const parser=require('@babel/parser'),traverse=require('@babel/traverse').default,t=require('@babel/types'),generate=require('@babel/generator').default;
let source='';process.stdin.setEncoding('utf8');process.stdin.on('data',s=>source+=s);process.stdin.on('end',()=>{
 const ast=parser.parse(source,{sourceType:'script'});let inputs=0,children=0;
 function inputTag(n){if(t.isStringLiteral(n,{value:'input'})){inputs++;return t.identifier('V8Input');}if(t.isConditionalExpression(n)){n.consequent=inputTag(n.consequent);n.alternate=inputTag(n.alternate);}return n;}
 traverse(ast,{CallExpression(p){const n=p.node;let name=t.isIdentifier(n.callee)?n.callee.name:t.isMemberExpression(n.callee)&&t.isIdentifier(n.callee.property)?n.callee.property.name:t.isSequenceExpression(n.callee)&&t.isMemberExpression(n.callee.expressions.at(-1))?n.callee.expressions.at(-1).property.name:'';
  if(!['DH','jsx','jsxs','createElement'].includes(name))return;if(n.arguments.length)n.arguments[0]=inputTag(n.arguments[0]);
  if(['DH','createElement'].includes(name))for(let i=2;i<n.arguments.length;i++)if(!t.isSpreadElement(n.arguments[i])){n.arguments[i]=t.callExpression(t.identifier(t.isStringLiteral(n.arguments[0])&&['option','text','tspan'].includes(n.arguments[0].value)?'V8Plain':'V8Display'),[n.arguments[i]]);children++;}
 },ObjectProperty(p){if(!p.parentPath.isObjectExpression())return;if((t.isIdentifier(p.node.key,{name:'children'})||t.isStringLiteral(p.node.key,{value:'children'}))&&!t.isCallExpression(p.node.value,{callee:t.identifier('V8Display')})){const tag=p.parentPath.parentPath.node.arguments?.[0];p.node.value=t.callExpression(t.identifier(t.isStringLiteral(tag)&&['option','text','tspan'].includes(tag.value)?'V8Plain':'V8Display'),[p.node.value]);children++;}}});
 process.stderr.write(JSON.stringify({date_capable_inputs:inputs,display_nodes:children})+'\n');process.stdout.write(generate(ast,{compact:true,comments:true,jsescOption:{minimal:true}}).code);
});
