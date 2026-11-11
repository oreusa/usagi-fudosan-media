"""解体・片付けの費用ページ（/kaitai）を作る。11/11 オーナー「来るために」：解体・片付けで困っている人が「いくらかかるか」を
30秒で見られて、そのまま無料の見積り相談（/moushikomi）へ進める入口。形は /ranking を借りる。
値段は公開されている相場（出どころを RATES / KATA に書く）。変える時は、出どころのページを開いて確かめてから。
使い方: python3 tools/kaitai/build.py 2026-11-11"""
import datetime, html, json, os, re, sys
TODAY = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
BASE = "https://townnote.pages.dev/"
E = html.escape
# 解体：1坪あたり（万円）。三井のリハウス「解体費用の相場」2025.05.14（11/11 に開いて確認）
SRC_K = ("三井のリハウス「家の解体費用の相場」（2025年5月）", "https://www.rehouse.co.jp/relifemode/column/at/at_0059/")
RATES = [("wood", "木造", 3, 5), ("steel", "鉄骨造", 4, 7), ("rc", "鉄筋コンクリート造", 6, 8)]
# 片付け・遺品整理：間取りごと（万円）。郵便局の終活日和「遺品整理の費用相場」（11/11 に開いて確認）
SRC_T = ("郵便局の終活日和「遺品整理の費用相場」", "https://www.post.japanpost.jp/life/inheriting/column7/index.html")
KATA = [("a", "1R・1K", 10, 15, ""), ("b", "1DK・2K", 15, 30, ""), ("c", "1LDK・2DK・3K", 30, 50, ""), ("d", "2LDK・3DK・3LDK以上（一軒家）", 50, 100, "以上")]
# アスベストの調査：アットホーム「解体費用」2025年5月8日更新（11/11 に開いて確認）
SRC_A = ("アットホーム「家の解体費用」（2025年5月）", "https://www.athome.co.jp/contents/custom/build-cost/removal-cost/")

rk = "".join(f"<tr><th>{n}</th><td>{lo}万〜{hi}万円</td><td>{lo*30}万〜{hi*30}万円</td></tr>" for _, n, lo, hi in RATES)
rt = "".join(f"<tr><th>{n}</th><td>{lo}万〜{hi}万円{x}</td></tr>" for _, n, lo, hi, x in KATA)
src = lambda s: f'<p class="kt-s">出どころ：<a href="{s[1]}" target="_blank" rel="noopener" data-k="出どころ">{E(s[0])}</a></p>'
secs = (
 '<section id="keisan" class="ps" style="--c:#4F7BA8"><h2>30秒で目安を出す</h2>'
 '<div class="kt-c"><div class="kt-tab" role="tablist"><button type="button" class="on" data-t="k" role="tab" aria-selected="true">解体</button><button type="button" data-t="t" role="tab" aria-selected="false">片付け</button></div>'
 '<div id="kt-k"><label for="kt-kind">建物の種類</label><select id="kt-kind">' + "".join(f'<option value="{k}">{n}</option>' for k, n, _, _ in RATES) + '</select>'
 '<label for="kt-tsubo">広さ（坪）<small>1坪＝約3.3㎡。30坪は約99㎡</small></label><div class="kt-q">' + "".join(f'<button type="button" data-v="{v}"{" class=on" if v == 30 else ""}>{v}坪</button>' for v in (20, 25, 30, 35, 40, 50)) + '</div>'
 '<input id="kt-tsubo" type="number" inputmode="numeric" min="5" max="300" value="30" aria-label="広さ（坪）"></div>'
 '<div id="kt-t" hidden><label for="kt-ma">間取り</label><select id="kt-ma">' + "".join(f'<option value="{k}"{" selected" if k == "d" else ""}>{n}</option>' for k, n, _, _, _ in KATA) + '</select></div>'
 '<div class="kt-o" aria-live="polite"><small id="kt-ol">木造30坪の解体の目安</small><b id="kt-ov">90万〜150万円</b><span>建物だけの目安です。塀・庭木・家の中の荷物は別にかかります。</span></div>'
 '<a class="kt-b" id="kt-go" href="/moushikomi?lite=1&amp;want=%E8%A7%A3%E4%BD%93%E3%81%AE%E8%A6%8B%E7%A9%8D%E3%82%8A" data-k="見積りを相談">名前なしで、うちの場合の概算を聞く<small>無料・書くのは3つだけ</small></a>'
 '<ul class="kt-a"><li><b>お返事は、メールかお電話で</b>ご希望の方で、2営業日以内にお返事します。</li>'
 '<li><b>ご紹介は、ご希望があった時だけ</b>会社のご紹介は、お話をうかがって、ご希望があった時だけです。</li>'
 '<li><b>費用はかかりません</b>見積りだけで終わっても、費用はかかりません。</li></ul>'
 '<button type="button" class="kt-k" id="kt-keep" data-k="結果を自分に送る">この結果を自分に送る（LINE・メモ）</button><p class="kt-n" id="kt-kn" role="status" hidden></p>'
 '<p class="kt-n">高いと感じた時は、壊さずに「そのまま売る」道もあります。<a href="/jikka/shindan/" data-k="3問診断へ">3問で、次にやることを見る</a></p>'
 '<p class="kt-n">ご紹介した会社から、紹介料をいただく場合があります。</p></div></section>'
 '<section id="kaitai" class="ps" style="--c:#4F7BA8"><h2>解体の費用の目安</h2><p class="rk-sub">建物を壊して更地にするまで</p>'
 '<div class="kt-w"><table class="kt"><thead><tr><th>建物</th><th>1坪あたり</th><th>30坪なら</th></tr></thead><tbody>' + rk + '</tbody></table></div>' + src(SRC_K) +
 '<h3 class="kt-h">別にかかる事がある物</h3><ul class="kt-l"><li>ブロック塀・庭木・物置・土間コンクリートの撤去</li><li>家の中に残った荷物の処分</li><li>アスベストの調査（約20万〜50万円）と、見つかった時の除去</li><li>道が狭くて重機が入らない時の手作業</li><li>地中から古い基礎や浄化槽が出た時</li></ul>' + src(SRC_A) + '</section>'
 '<section id="katazuke" class="ps" style="--c:#4F7BA8"><h2>片付け・遺品整理の費用の目安</h2><p class="rk-sub">分別・運び出し・処分まで</p>'
 '<div class="kt-w"><table class="kt"><thead><tr><th>間取り</th><th>目安</th></tr></thead><tbody>' + rt + '</tbody></table></div>' + src(SRC_T) +
 '<p class="kt-n">荷物の量、階段の有無、トラックを家の前に止められるかで変わります。</p></section>'
 '<section id="junban" class="ps" style="--c:#4F7BA8"><h2>解体までの順番</h2><ol class="kt-st">'
 '<li><b>見積りを取る</b><span>現地を見てもらうと、別にかかる物まで分かります。2〜3社でくらべるのが安心です。</span></li>'
 '<li><b>家の中を片付ける</b><span>荷物を減らしておくと、解体の見積りが下がります。</span></li>'
 '<li><b>届出とご近所へのあいさつ</b><span>床の広さが80㎡以上の解体は、工事の7日前までに届出が要ります（建設リサイクル法）。ふつうは解体の会社が代わりに出します。</span></li>'
 '<li><b>電気・ガスを止める</b><span>水道は、ほこりを抑える水まきに使うので、止める前に解体の会社に聞いてください。</span></li>'
 '<li><b>解体・整地</b><span>終わったら、1か月以内に建物の滅失登記をします。</span></li></ol>'
 '<p class="kt-n">更地にすると、土地の固定資産税の軽減（住宅用地の特例）が外れます。売る予定がある時は、壊す前に「そのまま売る」とくらべるのがおすすめです。</p></section>')
faq = [("解体の費用は、30坪の木造でいくらくらいですか？", f"目安は{RATES[0][2]*30}万〜{RATES[0][3]*30}万円です（1坪あたり{RATES[0][2]}万〜{RATES[0][3]}万円）。塀・庭木・家の中の荷物の処分は、別にかかる事があります。"),
       ("家を壊してから売るのと、そのまま売るのは、どちらがいいですか？", "建物の古さと場所で変わります。更地にすると買い手は見つけやすくなりますが、解体の費用がかかり、土地の固定資産税の軽減が外れます。壊す前に、そのまま売った時の値段とくらべるのがおすすめです。"),
       ("見積りだけでも頼めますか？", "はい。無料で、見積りだけでも大丈夫です。関西（大阪・京都・兵庫・奈良・滋賀・和歌山）のお家が対象です。")]
secs += '<section class="faq"><h2>よくある質問</h2>' + "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq) + "</section>"

s = open(os.path.join(ROOT, "links", "ranking.html"), encoding="utf-8").read()
title = "解体・片付けの費用の目安｜30秒で計算・関西の無料見積り相談"
desc = f"家の解体は木造で1坪{RATES[0][2]}万〜{RATES[0][3]}万円、30坪なら{RATES[0][2]*30}万〜{RATES[0][3]*30}万円が目安。片付け・遺品整理の間取りごとの目安と、別にかかる物、解体までの順番をまとめました。関西の無料の見積り相談もできます。"
ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
      {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "関西不動産リスト", "item": BASE + "fudosan-list"}, {"@type": "ListItem", "position": 2, "name": "解体・片付けの費用", "item": BASE + "kaitai"}]}]
s = re.sub(r'<script type="application/ld\+json">.*?</script>', "", s, flags=re.S)
CSS = ("<style>.kt-c{background:#fff;border-radius:2px;box-shadow:0 1px 2px rgba(43,38,34,.05),0 6px 18px rgba(43,38,34,.05);padding:16px}"
       ".kt-tab{display:grid;grid-template-columns:1fr 1fr;border:1px solid #2B2622;border-radius:99px;overflow:hidden;margin-bottom:14px}"
       ".kt-tab button{font:inherit;font-size:14px;font-weight:700;padding:10px;border:0;background:#fff;color:#2B2622;cursor:pointer}.kt-tab button.on{background:#2B2622;color:#fff}"
       ".kt-c label{display:block;font-size:12.5px;font-weight:700;margin:12px 0 6px}.kt-c label small{font-weight:500;color:#8A7F76;margin-left:8px}"
       ".kt-c select,.kt-c input{font:inherit;font-size:16px;width:100%;padding:11px 12px;border:1px solid #D9D2CB;border-radius:2px;background:#fff;color:#2B2622;box-sizing:border-box}"
       ".kt-q{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}.kt-q button{font:inherit;font-size:13px;padding:7px 12px;border:1px solid #D9D2CB;border-radius:99px;background:#fff;color:#2B2622;cursor:pointer}.kt-q button.on{background:#2B2622;border-color:#2B2622;color:#fff}"
       ".kt-o{margin:16px 0 14px;padding:14px 16px;background:#F4F1EE;border-left:3px solid var(--c)}.kt-o small{display:block;font-size:12px;color:#6E625A}"
       ".kt-o b{display:block;font-family:Jost,sans-serif;font-weight:500;font-size:30px;line-height:1.3;letter-spacing:.01em;color:#2B2622}.kt-o span{display:block;font-size:12px;color:#6E625A;line-height:1.7;margin-top:4px}"
       ".kt-b{display:block;text-align:center;background:#2B2622;color:#fff;text-decoration:none;font-weight:700;font-size:15px;padding:15px;border-radius:2px}"
       ".kt-a{list-style:none;margin:14px 0 0;padding:0;display:grid;gap:8px}.kt-a li{font-size:12.5px;line-height:1.75;color:#5C5048;padding-left:12px;border-left:2px solid #D9D2CB}.kt-a b{display:block;font-size:13px;color:#2B2622}"
       ".kt-b small{display:block;font-size:11.5px;font-weight:400;opacity:.85;margin-top:2px}.kt-k{display:block;width:100%;margin:12px 0 0;padding:11px;border:1.5px solid #CFC6BD;border-radius:12px;background:#fff;color:#3A2E28;font:inherit;font-size:13.5px;font-weight:700;cursor:pointer}.kt-n a{color:inherit}"
      ".kt-n{font-size:12px;color:#7A6E66;line-height:1.8;margin:10px 0 0}.kt-s{font-size:11.5px;color:#7A6E66;margin:8px 0 0}.kt-s a{color:inherit}"
       ".kt-w{overflow-x:auto;background:#fff;box-shadow:0 1px 2px rgba(43,38,34,.05),0 6px 18px rgba(43,38,34,.05)}table.kt{border-collapse:collapse;width:100%;font-size:13.5px}"
       ".kt th,.kt td{padding:12px;text-align:left;border-bottom:1px solid #EEE9E4;vertical-align:top}.kt thead th{font-size:11.5px;font-weight:500;color:#8A7F76}.kt tbody th{font-weight:700}.kt td{white-space:nowrap}.kt tr:last-child th,.kt tr:last-child td{border-bottom:0}"
       ".kt-h{font-size:14px;margin:20px 0 8px}.kt-l{margin:0;padding-left:1.3em;font-size:13.5px;line-height:1.95}"
       ".kt-st{margin:0;padding:0;list-style:none;counter-reset:k;background:#fff;box-shadow:0 1px 2px rgba(43,38,34,.05),0 6px 18px rgba(43,38,34,.05)}"
       ".kt-st li{counter-increment:k;display:grid;grid-template-columns:30px 1fr;gap:2px 10px;padding:13px 14px;border-bottom:1px solid #EEE9E4}.kt-st li:last-child{border-bottom:0}"
       ".kt-st li::before{content:counter(k);grid-row:1/3;font-family:Jost,sans-serif;font-size:22px;color:var(--c);line-height:1.2}.kt-st b{font-size:14px}.kt-st span{font-size:12.5px;color:#6E625A;line-height:1.8}"
       "</style>")
s = re.sub(r"<style>\.rk\{.*?</style>", "", s, count=1, flags=re.S)
s = s.replace("</head>", CSS + "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in ld) + "</head>", 1)
s = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", s, count=1)
for prop in ('<meta name="description" content="', '<meta property="og:description" content="'):
    s = re.sub("(" + re.escape(prop) + ')[^"]*', lambda m: m.group(1) + E(desc), s, count=1)
s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + "解体・片付けの費用の目安 30秒で計算", s, count=1)
s = s.replace(BASE + 'ranking"', BASE + 'kaitai"')
s = s.replace('<body data-kind="関西まちランキング">', '<body data-kind="解体・片付けの費用">', 1)
s = re.sub(r'<div class="en">[^<]*</div>', '<div class="en">DEMOLITION &amp; CLEAN-UP COST</div>', s, count=1)
s = re.sub(r"<h1>.*?</h1>", "<h1>解体・片付けの費用<span>30秒で目安がわかります</span></h1>", s, count=1, flags=re.S)
s = re.sub(r'<p class="sub">.*?</p>', '<p class="sub">家の解体と、家の中の片付けの費用の目安です。<br>そのまま、無料の見積り相談もできます（関西）。</p>', s, count=1, flags=re.S)
s = re.sub(r'<div class="upd">.*?</div>', f'<div class="upd">{TODAY.year}年{TODAY.month}月{TODAY.day}日 更新</div>', s, count=1, flags=re.S)
a = s.index('<section id="'); b = s.rindex("</section>") + len("</section>")
s = s[:a] + secs + s[b:]
s = re.sub(r'<p class="note">.*?</p>', '<p class="note">値段は、それぞれの表の下に書いた公開の資料にある全国の目安です。実際の費用は、建物・道の幅・荷物の量で変わります。正しい金額は、現地を見た見積りで確かめてください。</p>', s, count=1, flags=re.S)
s = re.sub(r'<nav class="also".*?</nav>', '<nav class="also" aria-label="あわせて見る"><small>あわせて見る</small><a href="/jikka/shindan/" data-k="あわせて：3問診断">実家・空き家の3問診断</a><a href="/jikka/" data-k="あわせて：実家・空き家ノート">実家・空き家ノート</a><a href="/uru" data-k="あわせて：家を売りたい">家を売りたい</a></nav>', s, count=1, flags=re.S)
def _sc(m):
    a = m.group(1)
    if "ld+json" in a or "night.js" in a or "menu.js" in a or "v2sub.js" in a: return m.group(0)
    return ""
s = re.sub(r"<script([^>]*)>(.*?)</script>", _sc, s, flags=re.S)
R = {k: [lo, hi, n] for k, n, lo, hi in RATES}; K = {k: [lo, hi, n, x] for k, n, lo, hi, x in KATA}
JS = ('<script>(function(){var O=false;try{O=localStorage.getItem("usagi_owner")==="1";}catch(e){}'
      'function c(k){if(O)return;try{var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true});}catch(e){}}'
      'c("表示：解体・片付けの費用"+(document.referrer&&!/townnote\\.pages/.test(document.referrer)?"（外から）":""));'
      'document.addEventListener("click",function(e){var a=e.target.closest?e.target.closest("[data-k]"):null;if(a)c("クリック：解体・片付けの費用｜"+a.getAttribute("data-k"));});'
      'var R=' + json.dumps(R, ensure_ascii=False) + ',K=' + json.dumps(K, ensure_ascii=False) + ',$=function(i){return document.getElementById(i)},mode="k",used=false,cur="";'
      'function show(){var l,v,w;if(mode==="k"){var r=R[$("kt-kind").value],t=Math.max(5,Math.min(300,Math.round(+$("kt-tsubo").value||0)));'
      'l=r[2]+t+"坪の解体の目安";v=(r[0]*t)+"万〜"+(r[1]*t)+"万円";w="解体の見積り";}'
      'else{var k=K[$("kt-ma").value];l=k[2]+"の片付けの目安";v=k[0]+"万〜"+k[1]+"万円"+k[3];w="片付け・遺品整理の見積り";}'
      '$("kt-ol").textContent=l;$("kt-ov").textContent=v;$("kt-go").href="/moushikomi?lite=1&want="+encodeURIComponent(w)+"&memo="+encodeURIComponent(l+" "+v);cur=mode==="k"?"k."+$("kt-kind").value+"."+t:"t."+$("kt-ma").value;'
      'document.querySelector(".kt-o span").textContent=mode==="k"?"建物だけの目安です。塀・庭木・家の中の荷物は別にかかります。":"荷物の量や階段の有無で変わります。";}'
      'function use(){setTimeout(function(){try{localStorage.setItem("tn_kt",cur);}catch(e){}},0);if(!used){used=true;c("解体・片付けの費用｜計算した｜"+(mode==="k"?"解体":"片付け"));}show();}'
      '["kt-kind","kt-tsubo","kt-ma"].forEach(function(i){$(i).addEventListener("input",function(){if(i==="kt-tsubo")document.querySelectorAll(".kt-q button").forEach(function(b){b.classList.toggle("on",b.getAttribute("data-v")===$("kt-tsubo").value);});use();});});'
      'document.querySelectorAll(".kt-q button").forEach(function(b){b.addEventListener("click",function(){$("kt-tsubo").value=b.getAttribute("data-v");document.querySelectorAll(".kt-q button").forEach(function(x){x.classList.toggle("on",x===b);});use();});});'
      'document.querySelectorAll(".kt-tab button").forEach(function(b){b.addEventListener("click",function(){mode=b.getAttribute("data-t");document.querySelectorAll(".kt-tab button").forEach(function(x){var on=x===b;x.classList.toggle("on",on);x.setAttribute("aria-selected",on);});$("kt-k").hidden=mode!=="k";$("kt-t").hidden=mode!=="t";used=false;use();});});'
      'try{var S=(new URLSearchParams(location.search).get("s")||localStorage.getItem("tn_kt")||"").split(".");if(S[0]==="k"&&R[S[1]]){$("kt-kind").value=S[1];if(+S[2])$("kt-tsubo").value=+S[2];}if(S[0]==="t"&&K[S[1]]){$("kt-ma").value=S[1];document.querySelector(\'.kt-tab button[data-t="t"]\').click();}}catch(e){}$("kt-keep").addEventListener("click",function(){var u=location.origin+"/kaitai?s="+cur,tx=$("kt-ol").textContent+" "+$("kt-ov").textContent,n=$("kt-kn"),ok=function(m){n.hidden=false;n.textContent=m;};if(navigator.share){navigator.share({title:"解体・片付けの費用の目安",text:tx,url:u}).catch(function(){});return;}try{navigator.clipboard.writeText(tx+"\\n"+u).then(function(){ok("コピーしました。メモやLINEに貼ると、あとで同じ結果を開けます。");},function(){ok("このページをブックマークすると、あとで開けます。");});}catch(e){ok("このページをブックマークすると、あとで開けます。");}});if(location.hash==="#katazuke-keisan"){document.querySelector(\'.kt-tab button[data-t="t"]\').click();}show();})();</script>')
s = s.replace("</body>", JS + "</body>", 1)
assert "html.night" not in CSS, "ページ側に夜の色を書かない"
for w in ("ランキング", "順位"):
    assert w not in re.sub(r"<script.*?</script>|<nav.*?</nav>", "", s, flags=re.S), w + " が残っている"
open(os.path.join(ROOT, "links", "kaitai.html"), "w", encoding="utf-8").write(s)
print("kaitai ok", len(s))
