// 11/20 おでかけの新しい地図（?map2=1）を本番で押して確かめる（関西・関東・昼夜）
const {chromium}=require('playwright'),fs=require('fs');
(async()=>{const out=process.argv[2];fs.mkdirSync(out,{recursive:true});const b=await chromium.launch();const log=[];
for(const [n,u,lat,lon] of [['ka','https://kansai.townnote.app/odekake',34.7025,135.4959],['kt','https://kanto.townnote.app/odekake',35.6812,139.7671]]){for(const night of [false,true]){
 const ctx=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true,geolocation:{latitude:lat,longitude:lon},permissions:['geolocation']});
 if(night)await ctx.addInitScript(()=>{localStorage.setItem('usagi_theme','night')});
 const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('response',r=>{if(r.status()>=400&&!/\/c$/.test(r.url()))errs.push(r.status()+' '+r.url())});
 const t=n+(night?'-n':'-d');const S=async k=>{await p.waitForTimeout(1300);await p.screenshot({path:`${out}/${t}-${k}.png`})};
 try{
 await p.goto(u+'?map2=1',{waitUntil:'load',timeout:60000});await p.waitForTimeout(1500);
 await p.evaluate(()=>scrollTo(0,document.querySelector('#sent').getBoundingClientRect().top+scrollY-260));await S('1list');
 await p.click('#tomap');await S('2map');
 const pf=await p.$$('.pin.pref .pc');if(pf[1])await pf[1].click();await S('3pref');
 const g=await p.$('.pin.grp .pc');if(g){await g.click();await S('4grp')}
 const o=await p.$('.pin.one .pc');if(o){await o.click();await S('5one')}
 await p.click('#m2w button[data-w="we"]');await S('6we');
 await p.click('.m2z button[data-z="me"]');await S('7me');
 const c=await p.$('#m2c .mcd');if(c){await c.click();await S('8sheet');await p.goBack()}
 await p.goBack();await S('9back');
 log.push(t+' url='+p.url()+' errs='+JSON.stringify(errs));
 }catch(e){log.push(t+' FAIL '+e.message.split('\n')[0]+' errs='+JSON.stringify(errs))}
 await ctx.close()}}
fs.writeFileSync(out+'/log.txt',log.join('\n'));console.log(log.join('\n'));await b.close()})();
// 11/20 20:00 関東の公開後にもう一度
