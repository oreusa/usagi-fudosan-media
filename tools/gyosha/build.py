# 業者さま・士業の先生方への窓口（関西だけ）。入口 gyosha.html と 困りごと5ページを作る
# 11/9 オーナー決定：関西不動産リストと同じ形・問い合わせはオーナーのメールへ（/moushikomi と同じ送り方）
# 決まり：会社名・免許番号は出さない／「必ず買います」と書かない／士業への紹介料は前提にしない／関東(LIFE)には置かない
import csv, json, os, re
R = os.path.dirname(os.path.abspath(__file__)) + "/../../"
L = R + "links/"
REINS = R + "tools/fudosan_list/reins/"
REINS_NAME = "近畿レインズ「2025年度 年刊市況レポート」市区町村別成約状況"

# ---- 送ったあとに出す「この辺りで売れた値段」（市区町村ごとの平均・件数）
sold = {}
for k, fn in (("k", "kodate_2025"), ("m", "mansion_2025")):
    for r in csv.DictReader(open(REINS + fn + ".csv", encoding="utf-8")):
        nm, mid = r["市区町村"], r["地域見出し"]
        if not r["府県"].endswith(("府", "県")):
            continue
        if nm == "合計":
            if mid in ("大阪市", "京都市", "神戸市"):
                nm = mid
            elif not mid:
                nm = r["府県"]
            else:
                continue
        elif mid in ("大阪市", "京都市", "神戸市"):
            nm = mid + nm
        if not r["価格万円"] or not r["件数"]:
            continue
        sold.setdefault(nm, {})[k] = [int(r["件数"]), int(round(float(r["価格万円"])))]
if "篠山市" in sold:  # 表では旧名
    sold["丹波篠山市"] = sold.pop("篠山市")
json.dump(sold, open(L + "assets/gyosha-sold.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

P = [  # slug, ボタンの名前, ページの題, 1行, よくあるご相談, 概要に書いてほしいこと, 状態の初期チェック
 ("jikka", "相続した実家・残置物がある", "相続した実家・残置物のある家のご相談",
  "家財が残ったまま・遠方で片付けに行けない、というご相談をお受けしています。",
  ["親が住んでいた家を相続したが、家財がそのまま残っている", "相続人が遠方に住んでいて、現地に通えない", "空き家のまま、固定資産税だけがかかっている", "相続登記がまだ済んでいない（2024年4月から、相続を知ってから3年以内の登記が義務になりました）"],
  ["市区町村・町名", "家財がどのくらい残っているか", "相続登記が済んでいるか", "相続人の人数"], "残置物あり"),
 ("saikenchiku", "再建築できない・接道が狭い", "再建築不可・接道が狭い家と土地のご相談",
  "建て替えができないと言われた家・土地のご相談をお受けしています。",
  ["前の道が狭い、または道に2m以上接していない（建築基準法の接道の決まり）", "路地の奥・旗竿地で、建て替えができないと言われた", "不動産会社に出したが、なかなか話が進まない", "隣の方に買ってもらえないか考えている"],
  ["市区町村・町名", "前の道の幅と、接している長さ（分かる範囲で）", "建物の築年数と、いま住めるか"], "再建築不可・接道が狭い"),
 ("kyoyu", "共有持分・相続人が大勢いる", "共有持分・相続人が大勢いる不動産のご相談",
  "兄弟・親族で持っている不動産で、話がまとまらないというご相談をお受けしています。",
  ["相続で兄弟・親族の共有になり、売るか残すか決まらない", "共有者の一部と連絡がとれない", "自分の持分だけを手放したい（自分の持分だけなら、ほかの共有者の同意なしに売れます）", "全体を売るには共有者全員の同意が必要で、進まない"],
  ["市区町村・町名", "共有者の人数と、ご自身の持分（分かる範囲で）", "全体を売りたいか、持分だけか"], "共有持分"),
 ("shakuchi", "借地権・底地", "借地権・底地のご相談",
  "借りている土地の上の家（借地権）、貸している土地（底地）のご相談をお受けしています。",
  ["親から借地の上の家を相続した", "借地権を売りたいが、地主さんの承諾が得られるか分からない", "地代が安いまま、貸している土地を手放したい", "借地人・地主のどちらか一方だけでもご相談いただけます"],
  ["市区町村・町名", "借地権か底地か", "契約書の有無と、地代（分かる範囲で）"], "借地権・底地"),
 ("urenokori", "売りに出しても止まっている", "売りに出しても売れない家と土地のご相談",
  "売りに出して長く経つのに決まらない家・土地のご相談をお受けしています。",
  ["売りに出して半年以上、問い合わせがほとんどない", "値段を下げても決まらない", "古家付き・傾斜地・駅から遠いなど、条件が難しい", "このまま待つか、買取も考えるか迷っている"],
  ["市区町村・町名", "売り出してからの期間と、いまの値段", "物件の種類と、広さ・築年数"], "売りに出しても売れない"),
]
STATES = ["残置物あり", "空き家", "再建築不可・接道が狭い", "共有持分", "借地権・底地", "売りに出しても売れない", "入居者あり", "その他"]

HEAD = open(L + "moushikomi.html", encoding="utf-8").read()
HEAD = HEAD[HEAD.index("<link rel=\"preconnect\""):HEAD.index("</head>")]
HEAD = HEAD.replace('<meta name="robots" content="noindex">\n', "").replace('<meta name="robots" content="noindex">', "")
assert "noindex" not in HEAD
CSS = """<style>
.g1{font-family:"Shippori Mincho",serif;font-size:15.5px;line-height:1.95;color:#2B2622;margin:16px 0 22px}
.g1 small{display:block;font-family:"Zen Kaku Gothic New";font-size:12.5px;color:#857A70;margin-top:6px;line-height:1.8}
.gq{display:grid;gap:8px;margin:0}
.gq a{display:flex;align-items:center;justify-content:space-between;gap:10px;text-decoration:none;color:#2B2622;border:1px solid #E3E3E3;border-radius:14px;padding:14px 16px;background:#fff;font-weight:700;font-size:15px}
.gq a:after{content:"→";font-family:Jost;color:#9C8775;font-weight:400}
.gq a i{font-style:normal;font-family:Jost;font-weight:300;font-size:12px;color:#9C8775;margin-right:10px;letter-spacing:.1em}
.gl{list-style:none;margin:0;padding:0}.gl li{position:relative;padding:9px 0 9px 18px;border-top:1px solid #EFEFEF;font-size:14px;line-height:1.8;color:#3A332E}.gl li:first-child{border-top:0}
.gl li:before{content:"";position:absolute;left:3px;top:1.25em;width:6px;height:6px;border-radius:50%;background:#C9B4A3}
.gf{list-style:none;margin:6px 0 0;padding:0;counter-reset:g}.gf li{counter-increment:g;position:relative;padding:8px 0 8px 34px;font-size:14px;line-height:1.75;color:#3A332E}
.gf li:before{content:counter(g);position:absolute;left:0;top:7px;width:24px;height:24px;border-radius:50%;border:1px solid #A07E66;color:#8C6A55;font-family:Jost;font-size:12px;display:flex;align-items:center;justify-content:center}
.mf .ch label.on{border-color:#3A2E28}
.sd{display:none;margin-top:14px;border:1px solid #E3E3E3;border-radius:16px;padding:16px;text-align:left}
.sd b{display:block;font-family:"Shippori Mincho",serif;font-size:16px;margin:0 0 8px}
.sd .r{display:flex;justify-content:space-between;gap:10px;border-top:1px solid #EFEFEF;padding:10px 0;font-size:14px}.sd .r:first-of-type{border-top:0}
.sd .r em{font-style:normal;font-weight:700;font-size:16px}.sd p{font-size:12.5px!important;line-height:1.8!important;color:#857A70!important;margin:8px 0 0!important}
.mf div.fl em{font-style:normal;font-size:11px;color:#B5735A;margin-left:6px;font-weight:400}
.gt{font-size:13px;color:#857A70;margin:20px 0 0;line-height:1.8}.gt a{color:#2B2622}
</style>"""

def form(pre=""):
    st = "".join(f'<label{" class=on" if s == pre else ""}><input type="checkbox" name="st" value="{s}"{" checked" if s == pre else ""}>{s}</label>' for s in STATES)
    return f"""<section class="s3" id="form"><div class="sn">CONTACT</div><h2>概要を送る</h2>
<p>所有者さまのお名前・住所は、まだ書かなくて大丈夫です。分かる範囲でお送りください。</p>
<form class="mf" id="mf" novalidate>
<label class="fl" for="pl">① 市区町村・町名<em>必須</em></label><input type="text" id="pl" name="place" maxlength="60" placeholder="例：大阪市旭区中宮" required>
<div class="fl" style="font-size:13px;font-weight:700;color:#5E544D;margin:16px 0 6px">② 物件の種類</div>
<div class="ch"><label><input type="radio" name="kind" value="戸建て">戸建て</label><label><input type="radio" name="kind" value="土地">土地</label><label><input type="radio" name="kind" value="マンション">マンション</label><label><input type="radio" name="kind" value="アパート・ビル">アパート・ビル</label><label><input type="radio" name="kind" value="その他">その他</label></div>
<div class="fl" style="font-size:13px;font-weight:700;color:#5E544D;margin:16px 0 6px">③ いまの状態<em>いくつでも</em></div>
<div class="ch">{st}</div>
<textarea id="tx" name="text" maxlength="600" style="margin-top:8px;min-height:84px" placeholder="分かる範囲で（広さ・築年数・前の道の幅・共有者の人数 など）"></textarea>
<div class="fl" style="font-size:13px;font-weight:700;color:#5E544D;margin:16px 0 6px">④ ご希望</div>
<div class="ch"><label><input type="radio" name="want" value="買取">買取</label><label><input type="radio" name="want" value="売却（仲介）">売却</label><label><input type="radio" name="want" value="まだ分からない">まだ分からない</label></div>
<label class="fl" for="nm">⑤ ご連絡先　お名前・会社名・事務所名<em>必須</em></label><input type="text" id="nm" name="name" autocomplete="organization" maxlength="40" placeholder="例：〇〇不動産 山田" required>
<label class="fl" for="em">メールアドレス<em>必須</em></label><input type="email" id="em" name="email" autocomplete="email" maxlength="80" required>
<label class="fl" for="tl">電話番号<em>任意・あるとご連絡が早くなります</em></label><input type="tel" id="tl" name="tel" autocomplete="tel" inputmode="tel" maxlength="20">
<div class="hp" aria-hidden="true"><input type="text" name="hp" id="hp" tabindex="-1" autocomplete="off"></div>
<label class="ag"><input type="checkbox" id="ag"><span><a href="/privacy" target="_blank" rel="noopener">プライバシーポリシー</a>を読んで、同意します</span></label>
<button type="submit" id="sb">送信する</button>
<p class="er" id="er" role="alert"></p>
</form>
<div class="done" id="done"><div class="sn">THANK YOU</div><b>ご相談を受け付けました</b><p>内容を確かめて、ご連絡いたします。<br>しばらくお待ちください。</p>
<div class="sd" id="sd"></div></div>
</section>"""

JS = r"""<script>(function(){
var SITE="TOWN NOTE 業者さま",KV="https://usagi-life-notes.pages.dev/moushikomi-send",MAIL="https://formsubmit.co/ajax/"+["Infinity.daikoku","gmail.com"].join("@");
var f=document.getElementById("mf"),er=document.getElementById("er"),sb=document.getElementById("sb");
f.addEventListener("change",function(e){var l=e.target.closest("label");if(l&&e.target.type==="checkbox"&&l.parentNode.className==="ch")l.className=e.target.checked?"on":""});
function v(n){var e=f.querySelector('[name="'+n+'"]:checked')||f.elements[n];return e&&e.value?String(e.value).trim():""}
function man(x){return x>=10000?Math.floor(x/10000)+"億"+(x%10000).toLocaleString()+"万円":x.toLocaleString()+"万円"}
function sold(pl){return fetch("assets/gyosha-sold.json").then(function(r){return r.json()}).then(function(S){
 var s=pl.replace(/\s/g,"").replace(/^(大阪府|京都府|兵庫県|奈良県|滋賀県|和歌山県)/,""),best="";
 Object.keys(S).forEach(function(k){if(s.indexOf(k)===0&&k.length>best.length)best=k});
 if(!best)Object.keys(S).forEach(function(k){if(k.length>2&&s.indexOf(k)>=0&&k.length>best.length)best=k});
 if(!best)return;var d=S[best],h="<b>"+best+"で売れた家の値段</b>";
 if(d.k)h+='<div class="r"><span>中古戸建て（'+d.k[0].toLocaleString()+'件）</span><em>平均 '+man(d.k[1])+'</em></div>';
 if(d.m)h+='<div class="r"><span>中古マンション（'+d.m[0].toLocaleString()+'件）</span><em>平均 '+man(d.m[1])+'</em></div>';
 h+="<p>2025年度に実際に売れた家の平均です（出典："+"__REINS__"+"）。再建築不可・借地権などの物件は、この平均より低くなることが多いです。正式な値段は、資料と現地を見てからお返しします。</p>";
 var b=document.getElementById("sd");b.innerHTML=h;b.style.display="block"}).catch(function(){})}
f.addEventListener("submit",function(e){e.preventDefault();er.textContent="";
 var st=[].map.call(f.querySelectorAll('[name="st"]:checked'),function(x){return x.value}).join("・");
 var d={site:SITE,name:v("name"),email:v("email"),tel:v("tel"),place:v("place"),kind:v("kind"),want:v("want"),text:(st?"【状態】"+st+"\n":"")+v("text"),hp:v("hp"),page:location.pathname.slice(0,60)};
 if(!d.place){er.textContent="市区町村・町名を書いてください";return}
 if(!d.name){er.textContent="お名前・会社名を書いてください";return}
 if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(d.email)){er.textContent="メールアドレスを正しく書いてください";return}
 if(!document.getElementById("ag").checked){er.textContent="プライバシーポリシーへの同意にチェックしてください";return}
 if(d.hp){f.style.display="none";document.getElementById("done").style.display="block";return}
 sb.disabled=true;sb.textContent="送っています…";
 var p1=fetch(KV,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(d)}).then(function(r){return r.ok}).catch(function(){return false});
 var jt=new Date(Date.now()+9*3600e3).toISOString().slice(0,16).replace("T"," ");
 var m={_subject:"【業者さま】"+d.place+"・"+(d.kind||"種類未選択")+"・"+(d.want||"ご希望未選択")+"（"+d.name+" 様）",_template:"table",_captcha:"false",_replyto:d.email,
 "◆ お知らせ":"TOWN NOTE（関西）の業者さま・士業の方の窓口から ご相談が届きました",
 "受付日時（日本時間）":jt,
 "① 場所":d.place,
 "② 種類":d.kind||"未選択",
 "③ 状態":st||"未選択",
 "④ ご希望":d.want||"未選択",
 "⑤ ご連絡先":d.name+" 様",
 "⑥ 電話":d.tel||"なし（メールで返信してください）",
 "⑦ メール":d.email,
 "⑧ くわしく":v("text")||"なし",
 "⑨ 送られたページ":location.pathname,
 "◆ 次にすること":"このメールに「返信」すると、そのまま "+d.name+" 様に届きます"};
 var p2=fetch(MAIL,{method:"POST",headers:{"content-type":"application/json","accept":"application/json"},body:JSON.stringify(m)}).then(function(r){return r.ok}).catch(function(){return false});
 Promise.all([p1,p2]).then(function(a){
  if(a[0]||a[1]){f.style.display="none";document.getElementById("done").style.display="block";document.getElementById("form").scrollIntoView();sold(d.place);
   try{if(localStorage.getItem("usagi_owner")!=="1"){navigator.sendBeacon&&navigator.sendBeacon("/c",JSON.stringify({k:"業者さま｜送信"}))}}catch(x){}}
  else{sb.disabled=false;sb.textContent="送信する";er.textContent="送れませんでした。時間をおいて、もう一度お試しください"}});
});
try{if(localStorage.getItem("usagi_owner")!=="1")navigator.sendBeacon&&navigator.sendBeacon("/c",JSON.stringify({k:"表示："+document.title.split("｜")[0]}))}catch(x){}
})();</script>""".replace("__REINS__", REINS_NAME)

PROMISE = """<section class="s3"><div class="sn">OUR PROMISE</div><h2>ご紹介くださる方へのお約束</h2><ul class="gl">
<li>ご了解なく、所有者さまに直接ご連絡することはしません。</li><li>進み具合を、段階ごとにご報告します。</li><li>お受けできない場合も、理由と次の道をお返しします。</li></ul></section>"""
FLOW = """<section class="s3"><div class="sn">FLOW</div><h2>ご相談の進め方</h2><ol class="gf">
<li>このページから、物件の概要を送っていただきます。</li><li>買取・売却それぞれの考え方と、おおよその目安をお返しします。</li><li>所有者さまのご了解をいただいてから、資料の確認と現地の確認に進みます。</li><li>正式な条件をお出しします。お受けできない場合も、理由をお伝えします。</li></ol></section>"""

def page(fn, title, desc, h1, en, body, canon):
    h = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{desc}">
<link rel="icon" href="assets/ogp.png"><link rel="apple-touch-icon" href="/assets/icon-180.png"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#FFFFFF">
<title>{title}</title><link rel="canonical" href="https://townnote.pages.dev/{canon}">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:image" content="https://townnote.pages.dev/assets/ogp.png">
{HEAD}{CSS}
</head><body><div class="wrap">
<div class="s3h"><img src="assets/logo-s.png?v=2" width="52" height="52" alt="ロゴ"><div><div class="en">{en}</div><h1>{h1}</h1></div></div>
{body}
<a class="back" href="fudosan-list">関西不動産リストへ戻る</a>
<div class="ft">TOWN NOTE</div></div>
{JS}
</body></html>
"""
    open(L + fn, "w", encoding="utf-8").write(h)

# ---- 入口
btn = "".join(f'<a href="gyosha-{s}"><span><i>0{i+1}</i>{b}</span></a>' for i, (s, b, *_) in enumerate(P))
body = f"""<p class="g1">関西で、動かしにくい不動産のご相談をお受けしています。所有者さまが分からない概要だけでも、ご相談いただけます。<small>大阪・京都・兵庫・奈良・滋賀・和歌山。まずは概要だけでもご相談ください。</small></p>
<section class="s3"><div class="sn">CASE</div><h2>困りごとから選ぶ</h2><div class="gq">{btn}</div></section>
{PROMISE}
<section class="s3"><div class="sn">FOR EXPERTS</div><h2>士業の先生方へ</h2><p>相続・登記・税金のご相談の中で、不動産の売り方に困っているお客さまがいらっしゃいましたら、ご紹介ください。税金や登記のご判断は、先生方にお任せします。</p></section>
{FLOW}
{form()}"""
page("gyosha.html", "業者さま・士業の先生方へ｜関西の動かしにくい不動産のご相談｜TOWN NOTE",
     "関西（大阪・京都・兵庫・奈良・滋賀・和歌山）の再建築不可・共有持分・借地権・残置物のある実家・売れ残りの不動産のご相談窓口です。概要だけでもお送りいただけます。",
     "業者さま・士業の先生方へ", "FOR PROFESSIONALS", body, "gyosha")

# ---- 困りごと5ページ
for s, b, t, one, cases, need, pre in P:
    oth = "".join(f'<a href="gyosha-{s2}"><span>{b2}</span></a>' for s2, b2, *_ in P if s2 != s)
    body = f"""<p class="g1">{one}<small>関西（大阪・京都・兵庫・奈良・滋賀・和歌山）の物件が対象です。業者さま・士業の先生方からのご紹介も、所有者さまご本人からのご相談もお受けしています。</small></p>
<section class="s3"><div class="sn">CASE</div><h2>よくあるご相談</h2><ul class="gl">{"".join(f"<li>{c}</li>" for c in cases)}</ul></section>
<section class="s3"><div class="sn">FIRST STEP</div><h2>最初にお送りいただきたいこと</h2><ul class="gl">{"".join(f"<li>{c}</li>" for c in need)}</ul><p class="gt" style="margin-top:10px">分からないところは空けたままで大丈夫です。</p></section>
{FLOW}
{PROMISE}
{form(pre)}
<section class="s3"><div class="sn">OTHER CASES</div><h2>ほかの困りごと</h2><div class="gq">{oth}<a href="gyosha"><span>業者さま・士業の先生方へ（入口）</span></a></div></section>"""
    page(f"gyosha-{s}.html", f"{t}（関西）｜TOWN NOTE",
         f"関西（大阪・京都・兵庫・奈良・滋賀・和歌山）の{t.replace('のご相談','')}について、概要だけでもご相談いただけます。業者さま・士業の先生方からのご紹介もお受けしています。",
         t.replace("のご相談", ""), "FOR PROFESSIONALS", body, f"gyosha-{s}")

# ---- サイトマップ（毎日の作り直しでも消えないよう、ここで足す）
sm = open(L + "sitemap.xml", encoding="utf-8").read()
for u in ["gyosha"] + [f"gyosha-{p[0]}" for p in P]:
    loc = f"<url><loc>https://townnote.pages.dev/{u}</loc>"
    if loc not in sm:
        sm = sm.replace("</urlset>", f"{loc}<lastmod>2026-11-09</lastmod></url>\n</urlset>")
open(L + "sitemap.xml", "w", encoding="utf-8").write(sm)
print("ok", len(sold), "towns")
