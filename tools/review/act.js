// 全部の部品を実際に押す点検（iPhone 13）
const {chromium,devices}=require('playwright');const fs=require('fs');
const L=fs.readFileSync(process.argv[2],'utf8').trim().split('\n').map(l=>l.split(/\s+/));
const SHOT=process.argv[3]||'';
(async()=>{const b=await chromium.launch();let bad=0;
for(const [nm,url] of L){const c=await b.newContext({...devices['iPhone 13'],deviceScaleFactor:1});const p=await c.newPage();const errs=[];const out=[];
 p.on('pageerror',e=>{if(!/Transition was aborted/.test(e.message))errs.push('JS:'+e.message.slice(0,90))});p.on('console',m=>{if(m.type()==='error'&&!/favicon|net::|Failed to load resource|google|instagram/.test(m.text()))errs.push('CON:'+m.text().slice(0,90))});
 const st0=async()=>p.evaluate(()=>({lock:document.documentElement.classList.contains('hxlock')||document.body.style.overflow==='hidden',open:[...document.querySelectorAll('.hxmu.on,.hxsv.on,.hxsr.on,.hxsh.on,.hxdc.on,.hxtq.on,.hxos.on')].map(e=>e.className.split(' ')[0]).join(','),url:location.pathname+location.search,ov:document.documentElement.scrollWidth-document.documentElement.clientWidth,dup:['.hxfh','.hxkd','.hxoh','.hxbg','.hxtw','#v2bar','.hxsr'].filter(s=>document.querySelectorAll(s).length>1).join(','),bad:(document.body.innerText.match(/NaN|undefined|\[object|null万|Infinity/g)||[]).slice(0,3).join(',')}));
 const st=async()=>{for(let k=0;k<3;k++){try{return await st0()}catch(e){await p.waitForLoadState('domcontentloaded').catch(()=>{});await new Promise(r=>setTimeout(r,800))}}return st0()};
 const ok=async(step)=>{const s=await st();const pr=[];if(s.lock&&!s.open)pr.push('LOCK');if(s.ov>0)pr.push('OV'+s.ov);if(s.dup)pr.push('DUP:'+s.dup);if(s.bad)pr.push('TXT:'+s.bad);out.push(step+(pr.length?' ✗'+pr.join(' '):' ✓')+(s.open?' ['+s.open+']':''));if(pr.length)bad++;return s};
 const tap=async(sel)=>{const es=await p.$$(sel);let e=null;for(const x of es){if(await x.isVisible()){e=x;break}}if(!e)return false;try{await e.tap({timeout:4000});return true}catch(x){out.push('  tapfail '+sel+' '+String(x).slice(0,80));return false}};
 const wait=t=>p.waitForTimeout(t);
 try{await p.goto(url,{waitUntil:'networkidle',timeout:25000})}catch(e){}await wait(2500);await ok('load');
 // scroll all
 await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=400){scrollTo(0,y);await new Promise(r=>setTimeout(r,60))}scrollTo(0,0)});await wait(800);await ok('scroll');
 const home=(await st()).url;
 // MENU: open, each tab, close by X, reopen, close by back
 if(await tap('#v2bar .mn')){await wait(700);let s=await ok('menu-open');if(!/hxmu/.test(s.open)){out.push('  ✗ MENU開かない');bad++}
   for(let i=0;i<3;i++){await tap(`.hxmu .h-tb button:nth-of-type(${i+1})`);await wait(450);}await ok('menu-tabs');
   await tap('.hxmu .h-x, .hxmu [aria-label="閉じる"]');await wait(600);s=await ok('menu-close');if(/hxmu/.test(s.open)){out.push('  ✗ MENU閉じない');bad++}
   if((await st()).url!==home){out.push('  ✗ 閉じたら別のページ '+(await st()).url);bad++;await p.goto(url);await wait(2000)}
   await tap('#v2bar .mn');await wait(700);await p.goBack();await wait(700);s=await ok('menu-back');if(s.url!==home){out.push('  ✗ 戻るでページを出た '+s.url);bad++;await p.goto(url);await wait(2000)}
   // MENU link then back
   await tap('#v2bar .mn');await wait(700);const href=await p.evaluate(()=>{const a=[...document.querySelectorAll('.hxmu.on .h-tr a[href]')].find(a=>a.offsetParent&&!/^#|tel:|mailto:|http/.test(a.getAttribute('href'))&&a.getBoundingClientRect().top>0&&a.getBoundingClientRect().top<innerHeight-120&&a.getBoundingClientRect().left>=0&&a.getBoundingClientRect().right<=innerWidth);if(!a)return '';a.setAttribute('data-act','1');return a.getAttribute('href')});
   if(href){await Promise.all([p.waitForNavigation({timeout:8000}).catch(()=>{}),tap('a[data-act]')]);await wait(1500);await p.goBack();await wait(1500);s=await ok('menu-link→back('+href+')');if(s.url!==home){out.push('  ✗ 戻る1回で元に戻らない '+s.url);bad++;await p.goto(url);await wait(2000)}if(/hxmu/.test(s.open)){out.push('  ✗ 戻ったらMENUが開いたまま');bad++}}
 }
 // story ring
 if(await tap('.hxst button:not(.h-dk)')){await wait(900);let s=await ok('story');if(/hxsv/.test(s.open)){await p.tap('body',{position:{x:350,y:400}}).catch(()=>{});await wait(500);await p.goBack();await wait(700);s=await ok('story-back');if(s.url!==home){out.push('  ✗ ストーリーの戻るでページを出た');bad++;await p.goto(url);await wait(2000)}}}
 // search box (odekake)
 if(await tap('.hxq, [data-hx-search]')){await wait(700);let s=await ok('search');if(/hxsr/.test(s.open)){await p.keyboard.type('きょうと');await wait(700);const n=await p.evaluate(()=>document.querySelectorAll('.hxsr.on a,.hxsr.on [data-i]').length);out.push('  results '+n);
   const r=await p.$('.hxsr.on .h-rs a.h-it');if(r){await r.tap().catch(()=>{});await wait(800);s=await ok('search→item');if(/hxsh/.test(s.open)){await p.goBack();await wait(700);s=await ok('sheet-back');if(!/hxsr/.test(s.open)){out.push('  ✗ 板を閉じたら さがす も閉じた');bad++}}}
   await p.goBack();await wait(700);s=await ok('search-back');if(s.url!==home){out.push('  ✗ さがすの戻るでページを出た '+s.url);bad++;await p.goto(url);await wait(2000)}}}
 // card → sheet → link → back
 await p.goto(url);await wait(2000);
 if(await tap('.card[data-mo], .pr5 a[data-mo], a.fc[href^="/o/"]')){await wait(900);let s=await ok('card→sheet');if(!/hxsh/.test(s.open)){out.push('  ✗ カードで板が出ない');bad++}else{
   const lk=await p.evaluate(()=>{const a=[...document.querySelectorAll('.hxsh.on a[href^="/o/"], .hxsh.on a[href^="/"]')].find(a=>a.offsetParent&&a.getBoundingClientRect().bottom<innerHeight);if(!a)return '';a.setAttribute('data-act2','1');return a.getAttribute('href')});
   if(lk){await Promise.all([p.waitForNavigation({timeout:8000}).catch(()=>{}),tap('a[data-act2]')]);await wait(1500);await ok('sheet-link('+lk+')');await p.goBack();await wait(1500);s=await ok('sheet-link-back');if(s.url!==home){out.push('  ✗ 板のリンクから戻る1回で戻らない '+s.url);bad++}if(/hxsh/.test(s.open)){out.push('  ✗ 戻ったら板が開いたまま');bad++}}
   else{await p.goBack();await wait(700);s=await ok('sheet-back');if(s.url!==home){out.push('  ✗ 板の戻るでページを出た');bad++}}}}
 await p.goto(url);await wait(2000);
 const card=await p.$('.wrap a.card[data-hx], .ec[data-id], [data-hxo]');
 // town widget
 if(await p.$('.hxtw input')){await p.fill('.hxtw input',/8788|kanto|lifenote/.test(url)?'ちよだ':'みやこじま').catch(()=>{});await wait(800);await tap('.hxtw .h-sg button');await wait(1200);const t=await p.evaluate(()=>{const c=document.querySelector('.hxtw .h-tc.on');return c?c.innerText.replace(/\s+/g,' ').slice(0,90):''});out.push('  town: '+(t||'✗ カードが出ない'));if(!t)bad++;await ok('town')}
 // town full search
 if(await tap('[data-hx-town]:not([style*="none"])')){await wait(800);let s=await ok('tsearch');if(/hxtq/.test(s.open)){await p.keyboard.type('なにわ');await wait(600);await p.goBack();await wait(700);s=await ok('tsearch-back');if(s.url!==home){out.push('  ✗ 街さがしの戻るでページを出た');bad++;await p.goto(url);await wait(2000)}}}
 // okaimono rail
 if(await tap('.hxcr button:nth-of-type(2), .hxcr a:nth-of-type(2)')){await wait(1500);const n=await p.evaluate(()=>document.querySelectorAll('#v4m .it, #v4m li, #v4m article').length);out.push('  category items '+n);await ok('okai-cat')}
 // deck
 if(await tap('.hxst .h-dk')){await wait(900);let s=await ok('deck');if(/hxdc/.test(s.open)){for(let i=0;i<3;i++){await tap('.hxdc .h-yes, .hxdc [data-a="y"], .hxdc button[aria-label*="行きたい"]');await wait(500)}await ok('deck-swipe');await p.goBack();await wait(700);s=await ok('deck-back');if(s.url!==home){out.push('  ✗ 週末の戻るでページを出た');bad++;await p.goto(url);await wait(2000)}}}
 // bottom bar links then back
 const bl=await p.$$eval('#v2bar>a[href]',as=>as.map(a=>a.getAttribute('href')));
 for(const h of bl.slice(0,4)){await p.goto(url);await wait(1500);const e=await p.$(`#v2bar>a[href="${h}"]`);if(!e)continue;await Promise.all([p.waitForNavigation({timeout:8000}).catch(()=>{}),e.tap().catch(()=>{})]);await wait(1800);const s2=await st();if(s2.url===home&&!/^#/.test(h)){/* same page link */}
   const s3=await ok('bar:'+h);if(s3.url.startsWith('/')){} await p.goBack();await wait(1200);const s4=await ok('bar-back');if(s4.url!==home&&!h.startsWith('#')){out.push('  ✗ 下のバーから戻れない '+s4.url);bad++}}
 if(SHOT)await p.screenshot({path:`act/${nm}.png`});
 console.log('■ '+nm+(errs.length?'  ERR '+[...new Set(errs)].slice(0,4).join(' | '):'')+'\n  '+out.join('\n  '));
 if(errs.length)bad++;await c.close()}
console.log('BAD',bad);await b.close()})();
