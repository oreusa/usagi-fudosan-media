# 管制室に「機械の点検結果」を足す部品（両方の管制室で同じもの）
CSS = """
/* 機械の点検結果（11/9 オーナー「間違いのないように見れる仕組み」）：月が手で書かず、点検の記録をそのまま出す */
.facts{display:grid;gap:8px;border-top:1px solid var(--line);padding-top:10px}
.facts .fmore summary{cursor:pointer;color:var(--brown,var(--accent));font-size:12.5px;font-weight:700;list-style:none;margin-top:4px}
.facts .fmore summary::-webkit-details-marker{display:none}
.facts .fmore summary::before{content:"＋ "}.facts .fmore[open] summary::before{content:"－ "}
.facts .sub{color:var(--sub);font-size:12px}
.facts h3{font-size:14px;display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;align-items:baseline}
.facts h3 small{font-family:var(--f-body,inherit);font-size:11px;color:var(--sub);font-weight:500}
.fk{display:grid;grid-template-columns:7.2em minmax(0,1fr);gap:4px 10px;font-size:13px;align-items:baseline}
.fk .l{color:var(--sub);font-size:12px;font-weight:700}
.fk .ok{color:var(--good)}.fk .ng{color:var(--bad);font-weight:700}
.fng{margin:2px 0 0;padding-left:1.1em;font-size:12px;color:var(--bad);overflow-wrap:anywhere}
.stale{background:var(--bad-soft);color:var(--bad);border-radius:10px;padding:8px 12px;font-size:13px;font-weight:700}
.gk{list-style:none;margin:0;padding:0}
.gk li{padding:7px 0;border-bottom:1px solid var(--line);font-size:12.5px;display:grid;gap:2px;overflow-wrap:anywhere}
.gk li:last-child{border-bottom:0}
.gk .w{font-weight:700}.gk .m{color:var(--sub);font-size:12px}
.gk .c{font-size:11px;font-weight:700;padding:0 8px;border-radius:999px;justify-self:start}
.gk .c.y{background:var(--good-soft);color:var(--good)}.gk .c.n{background:var(--wait-soft);color:var(--wait)}
"""

JS = r"""
/* 機械の点検結果：morning_report.facts をそのまま出す。日付が今日でない・記録が抜けている時は赤で出す */
function factsHTML(rep,todayStr){
  const E=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const out=[];const warn=[];
  if(!rep)warn.push("朝の報告がありません");
  else if(rep.date!==todayStr)warn.push(`朝の報告が古いままです（${E(rep.date)}）。今日の点検がまだ入っていません`);
  const f=rep&&rep.facts;
  if(rep&&!f)warn.push("点検の記録（機械の数字）が入っていません。手で書いた報告だけです");
  if(warn.length)out.push(`<div class="stale">${warn.map(E).join("<br>")}</div>`);
  if(!f)return out.join("");
  const row=(l,v,ng)=>`<div class="fk"><span class="l">${l}</span><span>${v}${ng&&ng.length?(ng.length>3?`<details class="fmore"><summary>中身を見る（${ng.length}件）</summary>`:"")+`<ul class="fng">${ng.map(x=>`<li>${E(String(x).replace(/^✗\s*/,"").replace(/\s*(https?:\/\/\S+)$/,""))}</li>`).join("")}</ul>`+(ng.length>3?"</details>":""):""}</span></div>`;
  const day=s=>String(s||"").slice(0,10)===todayStr;
  const ac=f.allcheck||{};
  for(const [k,nm] of [["day","全ページ（昼）"],["night","全ページ（夜）"]]){
    const a=ac[k];
    if(!a||!a.pages){out.push(row(nm,'<span class="ng">記録なし</span>'));continue}
    const st=a.ng&&a.ng.length?`<span class="ng">問題 ${a.ng.length}件</span>`:'<span class="ok">問題なし</span>';
    out.push(row(nm,`${st}　<span class="num">${a.pages}</span>ページ（関西 ${a.tsuki}・関東 ${a.akari}）${day(ac.at)?"":`　<span class="ng">点検日 ${E(ac.at||"不明")}</span>`}`,a.ng))}
  const fresh=s=>{const d=String(s||"").slice(0,10);if(!d)return false;const t=new Date(todayStr+"T00:00:00Z"),x=new Date(d+"T00:00:00Z");return (t-x)/864e5<=1};
  for(const [k,nm] of [["linkcheck","リンク（関西）"],["linkcheck_life","リンク（関東）"]]){
    const lc=f[k];if(!lc)continue;
    if(!lc.links){out.push(row(nm,'<span class="ng">記録なし</span>'));continue}
    out.push(row(nm,`${lc.ng&&lc.ng.length?`<span class="ng">開けない ${lc.ng.length}件</span>`:'<span class="ok">全部開けた</span>'}　<span class="num">${lc.links}</span>件　${fresh(lc.at)?`<span class="sub">${E(lc.at)}</span>`:`<span class="ng">点検日 ${E(lc.at||"不明")}</span>`}`,lc.ng))}
  const g=f.gakushu||{};const rows=g.rows||[];
  out.push(row("学習",rows.length?`ミス <span class="num">${rows.length}</span>件 → 仕組みにした <span class="num ${g.open?"":"ok"}">${g.made}</span>件・まだ <span class="num ${g.open?"ng":""}">${g.open}</span>件`:'<span class="ng">帳面が空です</span>'));
  if(rows.length)out.push(`<details class="fmore"><summary>ミス → 仕組みの帳面（直近7日）</summary><ul class="gk">${rows.slice().reverse().map(r=>`<li><span class="w">${E(r.date)}　${E(r.site)}　${E(r.what)}</span><span class="m">直したこと：${E(r.fix)}</span><span class="m">次から：${E(r.how||"")}</span><span class="c ${r.check?"y":"n"}">${r.check?"機械で点検："+E(r.check):"まだ仕組みになっていません"}</span></li>`).join("")}</ul></details>`);
  return `<div class="facts"><h3>機械の点検結果<small>点検の記録をそのまま表示（${E(String(f.made_at||"").replace("T"," ").slice(5,16))} 作成）</small></h3>${out.join("")}</div>`;
}
"""
