"""関西不動産リスト（links/fudosan-list.html）を、おでかけリスト（links/index.html）から作る。
11/1 オーナー「今のお出かけの派生だからな。バーとかその他もろもろ崩さないように」
→ index.html の head（CSS）・見出し・府県の絞り込み・タブ・カード・下の欄をそのまま使い、
  中のカードと言葉だけを tools/fudosan_list/facts.json（事実確認ずみの投稿の数字と公式ページ）に入れかえる。
使い方: python3 tools/fudosan_list/make.py [--live]   （--live が無いと noindex の見本）
"""
import html, json, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "links/index.html")
OUT = os.path.join(ROOT, "links/fudosan-list.html")
FACTS = json.load(open(os.path.join(ROOT, "tools/fudosan_list/facts.json"), encoding="utf-8"))
URL = "https://townnote.pages.dev/fudosan-list"
live = "--live" in sys.argv
E = html.escape

h = open(SRC, encoding="utf-8").read()
scripts = re.findall(r"<script>.*?</script>", h, flags=re.S)


def drop(pat):
    global h
    hit = [s for s in scripts if re.search(pat, s, flags=re.S)]
    assert hit, pat
    for s in hit:
        h = h.replace(s, "")


# ---- head
h = h.replace("<title>関西おでかけリスト</title>", "<title>関西不動産リスト｜地価・人口・できる物・制度を公式の数字で</title>")
desc = "大阪・京都・兵庫・奈良・滋賀・和歌山の地価、人口、駅の乗る人、新しくできる物、住まいの制度を、公式の資料つきでまとめました。"
h = re.sub(r'<meta name="description"[^>]*>', f'<meta name="description" content="{desc}">' + ("" if live else '<meta name="robots" content="noindex">'), h, count=1)
h = h.replace('content="https://townnote.pages.dev/odekake"', f'content="{URL}"')
h = h.replace('<link rel="canonical" href="https://townnote.pages.dev/odekake">', f'<link rel="canonical" href="{URL}">')
h = h.replace('<meta property="og:title" content="関西おでかけリスト">', '<meta property="og:title" content="関西不動産リスト">')
h = re.sub(r'<meta property="og:description"[^>]*>', f'<meta property="og:description" content="{desc}">', h, count=1)

# ---- おでかけだけの仕組みを外す（季節・日付・今週末・終わった物・宿・地図）
drop(r'getElementById\("sea"\)')            # 季節の表示
drop(r'終わった日を過ぎたカード')            # 終わった物を隠す
drop(r'var M=\["JAN"')                      # 今週のおすすめ・件数
drop(r'var P=document.querySelector\("\.paper"\),cur=null')  # 見出しから欄を作る（欄は下で直接書く）
drop(r'document.querySelectorAll\("\.it \.d"\)')            # 日付の文字の整え
drop(r"var p=document.querySelector\('\.past'\)")          # 終わったおでかけ
drop(r'開催中 / これから split')             # 開催中・これからの振り分け
drop(r'"開催中":\["NOW ON"')                 # 欄の見出しの英字（下で直接書く）
drop(r'近くの宿：')                          # 近くの宿
h = re.sub(r'<script src="/townnotes/map\.js[^"]*" defer></script>', "", h)
h = re.sub(r'<script src="assets/v2\.js[^"]*"></script>', '<script src="assets/v2sub.js?v=7" defer></script>', h)

# ---- 見出し
h = h.replace('<h1>関西おでかけリスト</h1><p class="sub">関西の街を調査して見つけた魅力を、<br>おでかけ先として紹介しています</p>',
              '<h1>関西不動産リスト</h1><p class="sub">関西の街を調査して見つけた数字を、<br>公式の資料つきで紹介しています</p>')
h = re.sub(r'<div class="sea" id="sea">.*?</div><svg class="yr" id="yr".*?</svg>', "", h, count=1, flags=re.S)
SW = ('<nav class="tnsw" aria-label="TOWN NOTE のリスト"><a href="/odekake" data-k="切り替え｜おでかけ">関西おでかけリスト</a>'
      '<a href="fudosan-list" class="on" aria-current="page">関西不動産リスト</a></nav>')
h = h.replace('<a class="ilk" href="illumination">関西イルミネーション 2026 日程一覧<span>→</span></a>',
              '<a class="ilk" href="chika-kansai">関西 __NT__の街 地価ランキング 2026<span>→</span></a>')
h = h.replace("この府県のおでかけは、これから増やしていきます", "この府県の分は、これから増やしていきます")

# ---- カード
# 11/1 オーナーが「売り買いの相場」を選んだ → 地価の次に新しいタブ（近畿レインズの成約価格）。「相場」はこちらに移したので、1つめは「地価」
TABS = [("chika", "b-now", "LAND PRICE", "地価", "地価の数字"),
        ("souba", "b-old", "MARKET", "売り買い", "売り買いの相場（売れた値段）"),
        ("jinko", "b-up", "PEOPLE", "人口・駅", "人口と駅の数字"),
        ("dekiru", "b-new", "NEW", "できる", "できる・できた"),
        ("seido", "b-done", "MONEY", "制度", "住まいの制度とお金")]
ORDER = ["大阪", "京都", "兵庫", "奈良", "滋賀", "和歌山"]
# 売り買いはオーナーの OK まで見本だけ（--try で links/fudosan-list-try.html に出す）。OK が出たら SOUBA_LIVE = True
SOUBA_LIVE = False
TRY = "--try" in sys.argv
if TRY:
    OUT = os.path.join(ROOT, "links/fudosan-list-try.html")
if not (SOUBA_LIVE or TRY):
    TABS = [("chika", "b-now", "LAND PRICE", "地価・相場", "地価・相場の数字")] + [t for t in TABS if t[0] not in ("souba", "chika")]
    FACTS = [o for o in FACTS if o["tab"] != "souba"]


def card(o):
    return (f'<a class="card" data-pref="{o["pref"]}" data-cat="{o["tab"]}" data-date="{o["date"]}" href="{E(o["url"])}">'
            f'<div class="bd"><div class="d">{E(o["src"])}</div><div class="t">{E(o["t"]).replace("｜", "<br>" if o["tab"] == "souba" else "　")}</div>'
            f'<div class="m">{E(o["m"])}</div></div><div class="go">→</div></a>')


blocks = []
for key, cls, en, jp, head in TABS:
    items = [o for o in FACTS if o["tab"] == key]
    items.sort(key=lambda o: (ORDER.index(o["pref"]), o["date"]), reverse=False)
    # 府県が偏らないように、府県を順番に1枚ずつ並べる
    by = {p: sorted([o for o in items if o["pref"] == p], key=lambda o: (o.get("pin", 0), o["date"]), reverse=True) for p in ORDER}
    seq = []
    while any(by.values()):
        for p in ORDER:
            if by[p]:
                seq.append(by[p].pop(0))
    blocks.append(f'<div class="blk {cls}"><div class="wk hd2"><span class="en2">{en}</span><span class="jp2">{head}</span></div>'
                  + "\n".join(card(o) for o in seq) + "</div>")

paper = ('<div class="paper">' + "\n".join(blocks) +
         '<div class="tip">数字は公式の資料の時点のものです。家ごとの値段は、場所・広さ・築年数などで変わります。</div></div>')
h = re.sub(r'<div class="paper">.*?<div class="tip">.*?</div></div>', lambda m: paper, h, count=1, flags=re.S)
h = h.replace("ぴょんと街しらべ│過去のおでかけも、このページに残していきます", "ぴょんと街しらべ│調べた数字は、このページに残していきます")
# 下の箱の「おでかけ掲載」は、不動産リストでは「売る前に大事なこと」に（完全に分ける）
OLD_LS = '<a class="co" data-en="LISTING" href="https://ig.me/m/fudousan_ai_si">おでかけ掲載<span>新しいお店や、毎年のイベント。<br>うさぎがご紹介します。ご相談はこちら</span></a>'
assert OLD_LS in h
h = h.replace(OLD_LS, '<a class="co" data-en="BEFORE SELLING" href="uru.html">売る前に大事なこと<span>売るか、持ち続けるか。<br>迷ったときに読むページです</span></a>')
# 11/1 12:45 オーナー「不動産リスト（の下）にこの項目そのまま入れたら良い」→ ご相談ページ（fudosan.html）の3つをそのまま
FD = open(os.path.join(ROOT, "links/fudosan.html"), encoding="utf-8").read()
items = re.findall(r'<a class="co" data-en="[^"]*" href="[^"]*">.*?</a>', FD, flags=re.S)
assert len(items) == 3, items
h = re.sub(r'<div class="cos">.*?</div>', lambda m: '<div class="cos">' + "\n".join(items) + '</div>', h, count=1, flags=re.S)
# 11/1 オーナー「上の切り替えはやめて、1番下にもう一方のリスト。完全に分ける」
TNX_OLD = '<a class="tnx" href="fudosan-list" data-k="下の入口｜関西不動産リスト"><small>関連サイト</small><b>関西不動産リスト<span>→</span></b><i>地価・人口・できる物・制度を、公式の数字で</i></a>'
assert TNX_OLD in h
h = h.replace(TNX_OLD, '<a class="tnx" href="/odekake" data-k="下の入口｜関西おでかけリスト"><small>関連サイト</small><b>関西おでかけリスト<span>→</span></b><i>関西のイベント・新しいお店や施設を、公式ページつきで</i></a>')

# ---- 府県の絞り込み・カードの包み・数え（index の仕組みを不動産用に短くしたもの）
main_js = r'''<script>(function(){
var O=(function(){try{return localStorage.getItem("usagi_owner")==="1";}catch(e){return false;}})();function c(k){if(O)return;try{var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true});}catch(e){}}
var PC={"大阪":"#B97A62","京都":"#8A7495","兵庫":"#4F6681","奈良":"#6F8C68","滋賀":"#5F8F98","和歌山":"#C4925A"},CAT={chika:"地価",souba:"売り買い",jinko:"人口・駅",dekiru:"できる",seido:"制度"};
document.querySelectorAll(".paper a.card").forEach(function(a){var w=document.createElement("div");w.className="it";var pf=a.getAttribute("data-pref");w.setAttribute("data-pref",pf);if(PC[pf])w.style.setProperty("--pc",PC[pf]);a.parentNode.insertBefore(w,a);w.appendChild(a);
 var bd=a.querySelector(".bd"),d=a.querySelector(".d"),cx=document.createElement("div");cx.className="v2c";cx.innerHTML='<span class="p" data-p="'+pf+'">'+pf+'</span><span>'+CAT[a.getAttribute("data-cat")]+'</span>';
 var dt=document.createElement("div");dt.className="v2d";dt.textContent=d.textContent;bd.insertBefore(dt,bd.firstChild);bd.insertBefore(cx,dt);});
var P=["大阪","京都","兵庫","奈良","滋賀","和歌山"],F=document.getElementById("flt");
["すべて"].concat(P).forEach(function(p,i){var b=document.createElement("button");b.textContent=p;if(PC[p])b.style.setProperty("--pc",PC[p]);if(!i)b.className="on";b.onclick=function(){F.querySelectorAll("button").forEach(function(x){x.className="";});b.className="on";var v=0;document.querySelectorAll(".paper .it").forEach(function(w){var ok=p=="すべて"||w.getAttribute("data-pref")==p;w.style.display=ok?"":"none";if(ok)v++;});document.getElementById("none").style.display=v?"none":"";c("絞り込み（不動産）："+p);};F.appendChild(b);});
document.addEventListener("click",function(ev){var s=ev.target.closest&&ev.target.closest(".v2c span.p");if(!s)return;ev.preventDefault();ev.stopPropagation();var b=[].find.call(F.querySelectorAll("button"),function(x){return x.textContent===s.dataset.p});if(b){b.click();scrollTo({top:F.getBoundingClientRect().top+scrollY-70,behavior:"smooth"});}},true);
var n=document.querySelectorAll(".paper .it").length,x=document.createElement("div");x.className="cnt";x.innerHTML='<span>関西の街<b>__NT__</b></span><span>調べた数字<b>'+n+'</b>件</span>';var nn=document.getElementById("none");nn.parentNode.insertBefore(x,nn.nextSibling);
c("表示：不動産リスト"+(document.referrer&&!/usagi-odekake|townnote.pages/.test(document.referrer)?"（外から）":""));
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a");if(!a)return;var k=a.getAttribute("data-k");if(!k){var t=a.querySelector(".t");k=t?t.textContent:a.textContent;}c("クリック：不動産リスト｜"+k);},true);
})();</script>'''
old_main = [s for s in scripts if 'getElementById("flt")' in s and "wrap(a)" in s]
assert len(old_main) == 1
h = h.replace(old_main[0], main_js)

# タブの名前
old_tabs = '[["b-now","NOW ON","開催中","#2B2622"],["b-up","COMING UP","これから","#2B2622"],["b-new","SOON","もうすぐ","#2B2622"],["b-done","NEW OPEN","できた","#2B2622"]]'
assert old_tabs in h
h = h.replace(old_tabs, json.dumps([[c, en, jp, "#2B2622"] for _, c, en, jp, _ in TABS], ensure_ascii=False))

# 切り替えの見た目（おでかけのタブと同じ線と文字）
SW_CSS = ('<style>.tnsw{display:flex;justify-content:center;gap:0 22px;margin:4px 0 18px}'
          '.tnsw a{font-family:"Shippori Mincho",serif;font-weight:600;font-size:14px;letter-spacing:.06em;color:#9C9187;text-decoration:none;padding:4px 2px 6px;border-bottom:2px solid transparent}'
          '.tnsw a.on{color:#2B2622;border-bottom-color:#2B2622}</style>')
h = h.replace("</head>", SW_CSS + "</head>", 1)


# タブの上の見出し（数字｜街と暮らし）と、府県ボタンをタブの下へ（おでかけの map.js と同じ形・同じ見た目）
MOUNT = r"""<style>.tabs{grid-template-columns:repeat(__NTABS__,1fr)!important}.tgrp{display:grid;grid-template-columns:__NNUM__fr 2fr;gap:0 14px;margin:2px 0 6px}.tgrp span{display:block;text-align:center;font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:11px;letter-spacing:.14em;color:#8C7B6E;padding:0 0 6px;border-bottom:1px solid #D6CCC1;position:relative}.tgrp span:after{content:"";position:absolute;left:50%;bottom:-4px;width:7px;height:7px;background:#FFFFFF;border-right:1px solid #D6CCC1;border-bottom:1px solid #D6CCC1;transform:translateX(-50%) rotate(45deg)}.tn-top{margin-top:-16px}.tn-top .flt{margin:0 0 10px;border-top:0;padding:8px 0;gap:0 13px;flex-wrap:nowrap}</style>
<script>(function(){function mount(){var bar=document.querySelector(".tabs");if(!bar)return;
var tg=document.querySelector(".tgrp");if(!tg){tg=document.createElement("div");tg.className="tgrp";tg.innerHTML='<span>数字</span><span>街と暮らし</span>'}
if(bar.previousSibling!==tg)bar.parentNode.insertBefore(tg,bar);
var top=document.querySelector(".tn-top");if(!top){top=document.createElement("div");top.className="tn-top"}
["flt","none"].forEach(function(id){var e=document.getElementById(id);if(e&&e.parentNode!==top)top.appendChild(e)});
if(bar.nextSibling!==top)bar.parentNode.insertBefore(top,bar.nextSibling);}
mount();document.addEventListener("click",function(e){if(e.target.closest(".tabs,#flt"))setTimeout(mount,80);});})();</script>"""
MOUNT = MOUNT.replace("__NTABS__", str(len(TABS))).replace("__NNUM__", str(len(TABS) - 2))
h = h.replace("</body>", MOUNT + "</body>", 1)


# ---- 下のバーの「街で探す」「新着」（11/1 オーナー「完全別項目で分けろよ」「作る前に工夫考えろよ」）
# 開く人が知りたいのは「自分の街の数字」→ 市・区・駅の名前で探せるようにする。新着はまた見に来る理由。
from collections import Counter
# 府県が偏らないように、6府県からよく探されそうな街を選ぶ（11/1 全部の街を入れたので、候補は入口だけ）
PLACES = ["北区", "吹田市", "豊中市", "中京区", "宇治市", "神戸市中央区", "西宮市", "姫路市", "奈良市", "生駒市", "大津市", "草津市", "和歌山市", "田辺市"]
FQ = r"""<style>#fq{display:none;margin:6px 0 24px}html.fq-on .paper:not(#fq){display:none}#fq.paper{display:none}html.fq-on #fq.paper{display:block}
#fq .fh{display:flex;align-items:baseline;justify-content:space-between;margin:0 0 12px;padding:0 2px 8px;border-bottom:1px solid #D6CCC1}
#fq .fh b{font-family:"Shippori Mincho",serif;font-size:17px;font-weight:600;color:#2B2622;letter-spacing:.06em}
#fq .fh button{border:0;background:none;font-family:"Zen Kaku Gothic New",sans-serif;font-size:12px;font-weight:700;color:#8C7B6E;cursor:pointer;padding:4px 0}
#fq .fi{display:block;width:100%;box-sizing:border-box;font-size:16px;padding:12px 14px;border:1px solid #D6CCC1;border-radius:12px;background:#fff;color:#2B2622;font-family:"Zen Kaku Gothic New",sans-serif;outline:none}
#fq .fi:focus{border-color:#8C7B6E}
#fq .fc{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 14px}
#fq .fc button{border:1px solid #D6CCC1;background:#fff;border-radius:999px;padding:6px 12px;font-family:"Zen Kaku Gothic New",sans-serif;font-size:12.5px;font-weight:700;color:#5C5048;cursor:pointer}
#fq .fn{font-family:"Zen Kaku Gothic New",sans-serif;font-size:12.5px;color:#8C7B6E;margin:4px 2px 10px}
#fq .fr .it{display:block!important}#fq .frq{display:block;width:100%;margin:4px 0 8px;padding:13px;border:0;border-radius:12px;background:#3A2F28;color:#fff;font-family:"Zen Kaku Gothic New",sans-serif;font-size:13.5px;font-weight:700;cursor:pointer}#fq .frq:disabled{background:#8C7B6E}
#fq .tw{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:10px;background:#fff;text-decoration:none;color:#2B2622;padding:13px 14px;margin:0 0 8px;border-left:3px solid var(--pc);box-shadow:0 1px 2px rgba(43,38,34,.05),0 6px 18px rgba(43,38,34,.05);font-family:"Zen Kaku Gothic New",sans-serif}
#fq .tw i{font-style:normal;font-size:11px;font-weight:700;color:var(--pc);border:1px solid var(--pc);border-radius:999px;padding:1px 8px}
#fq .tw b{font-size:15px}#fq .tw b small{display:block;font-size:11px;font-weight:500;color:#8C7B6E;margin-top:2px}
#fq .tw em{font-style:normal;font-family:Jost,sans-serif;font-weight:500;font-size:17px}
#fq .sec{font-family:Jost,sans-serif;font-size:10px;letter-spacing:.3em;color:#9C8775;margin:16px 2px 8px}
#fq .mpf{display:flex;flex-wrap:nowrap;gap:0 12px;justify-content:center;overflow-x:auto;padding:4px 0 10px}
#fq .mpf button{flex:none;border:0;background:none;font-family:"Zen Kaku Gothic New",sans-serif;font-size:13.5px;font-weight:700;color:var(--pc,#5C5048);padding:4px 0;border-bottom:2px solid transparent;cursor:pointer}
#fq .mpf button.on{border-bottom-color:currentColor}#fq .mpc{padding-top:0}#fq .mpc:empty{display:none}#fq .mpc button{font-size:12.5px;color:#5C5048;border:1px solid #D6CCC1;border-radius:999px;padding:5px 12px}#fq .mpc button.on{background:#3A2F28;color:#fff;border-color:#3A2F28}
#fq .mpw{background:#fff;border:1px solid #ECECEC;padding:8px}#fq .mpw svg{display:block;width:100%;height:auto;max-height:70vh;touch-action:manipulation}
#fq .mpw path{cursor:pointer;stroke:#fff;stroke-width:1.1;vector-effect:non-scaling-stroke}#fq .mpw path.sel{stroke:#2B2622;stroke-width:2}
#fq .lg{display:flex;flex-wrap:wrap;gap:6px 14px;font-family:"Zen Kaku Gothic New",sans-serif;font-size:11px;color:#7A6E66;margin:8px 2px 0}#fq .lg span:before{content:"";display:inline-block;width:12px;height:12px;vertical-align:-2px;margin-right:4px;background:var(--b)}
#fq .mpi{min-height:10px;margin-top:10px}</style>
<script>(function(){var PL=__PLACES__;
var PC={"大阪":"#B97A62","京都":"#8A7495","兵庫":"#4F6681","奈良":"#6F8C68","滋賀":"#5F8F98","和歌山":"#C4925A"},PS=["大阪","京都","兵庫","奈良","滋賀","和歌山"];
var O=(function(){try{return localStorage.getItem("usagi_owner")==="1";}catch(e){return false;}})();function c(k){if(O)return;try{var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true});}catch(e){}}
var paper=document.querySelector(".paper"),box=document.createElement("div");box.id="fq";box.className="paper";paper.parentNode.insertBefore(box,paper);
var all=[].slice.call(paper.querySelectorAll(".it"));
var TW=null,TWP=fetch("/assets/towns.json").then(function(r){return r.json()}).then(function(d){TW=d;return d}).catch(function(){TW=[];return[]});
function pct(v){return (v>0?"+":v<0?"−":"±")+Math.abs(v).toFixed(1)+"%"}
function esc(s){return String(s).replace(/[&<>"]/g,function(x){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[x]})}
function twRow(t){return '<a class="tw" style="--pc:'+PC[t.p]+'" href="/machi/'+t.id+'" data-k="街｜'+esc(t.n)+'"><i>'+t.p+'</i><b>'+esc(t.n)+'<small>住宅地 1年の動き・'+t.p+'で'+t.rk+'位／'+t.of+'</small></b><em style="color:'+(t.r8>0?PC[t.p]:"#7A6E66")+'">'+pct(t.r8)+'</em></a>'}
function find(q){q=q.replace(/\s/g,"");var r=box.querySelector(".fr"),fn=box.querySelector(".fn");r.className="fr blk";r.innerHTML="";
 if(!q){fn.textContent="市・区・町の名前を入れるか、下から選んでください（関西 "+(TW?TW.length:"")+" の街）";return;}
 var qq=q.replace(/(市|区|町|村|駅)$/,"");
 var tw=(TW||[]).filter(function(t){return t.n.indexOf(qq)>=0||t.s.indexOf(qq)>=0||(q.length>=3&&q.indexOf(t.s.replace(/(市|町|村)$/,""))>=0&&t.s.replace(/(市|町|村)$/,"").length>=2)}).slice(0,20);
 var hit=all.filter(function(w){return w.textContent.replace(/\s/g,"").indexOf(qq)>=0});
 fn.textContent=tw.length||hit.length?"「"+q+"」　街 "+tw.length+"・調べた数字 "+hit.length+"件":"「"+q+"」はまだありません。";
 if(tw.length){r.insertAdjacentHTML("beforeend",'<div class="sec">TOWN　街の地価</div>'+tw.map(twRow).join(""));}
 if(hit.length){r.insertAdjacentHTML("beforeend",'<div class="sec">NUMBERS　調べた数字</div>');hit.forEach(function(w){r.appendChild(w.cloneNode(true))});}
 if(q.length>=2){var b=document.createElement("button");b.type="button";b.className="frq";b.textContent=(tw.length||hit.length?"「"+q+"」をもっと細かく調べてほしい":"「"+q+"」を調べてほしい");b.onclick=function(){c("調べてほしい："+q);b.disabled=true;b.textContent="受け付けました。調べて、このリストに足します";};r.appendChild(b);}}
// ---- 地図（上がった街・下がった街を色で）
var GEO=null;function geo(){return GEO?Promise.resolve(GEO):fetch("/townnotes/kansai.json").then(function(r){return r.json()}).then(function(d){GEO=d;return d})}
function full(p){var cc=p.c||"";return (!cc||/郡$/.test(cc))?p.n:cc+p.n}
function rings(g){return g.type==="Polygon"?g.coordinates:[].concat.apply([],g.coordinates)}
var LP={"大阪":[135.43,34.52],"京都":[135.45,35.30],"兵庫":[134.78,35.12],"奈良":[135.88,34.30],"滋賀":[136.20,35.05],"和歌山":[135.50,33.98]},CITY={"大阪":["大阪市","堺市"],"京都":["京都市"],"兵庫":["神戸市"]};KU={"大阪市":24,"堺市":7,"京都市":11,"神戸市":9};
function cityOf(n){var m=n.match(/^(大阪市|堺市|京都市|神戸市)/);return m?m[1]:""}
// 11/1 オーナー「地図はちゃんと地名まで入れる」→ 名前と数字を、重ならないように置く（重なる時は少しずらして線でつなぐ）
function drawMap(pf,city){var w=box.querySelector(".mpw"),info=box.querySelector(".mpi");w.innerHTML='<p class="fn">地図を読みこんでいます…</p>';
 Promise.all([geo(),TWP]).then(function(r){var g=r[0],by={},LB={};TW.forEach(function(t){by[t.p+"|"+t.n]=t});g.lab.features.forEach(function(f){LB[f.properties.p+"|"+full(f.properties)]=f.geometry.coordinates});
  var fs=g.muni.features.filter(function(f){return (!pf||f.properties.p===pf)&&(!city||full(f.properties).indexOf(city)===0)});
  var x0=1e9,y0=1e9,x1=-1e9,y1=-1e9,ar={};fs.forEach(function(f){var a0=1e9,b0=1e9,a1=-1e9,b1=-1e9;rings(f.geometry).forEach(function(rg){rg.forEach(function(p){if(p[0]<a0)a0=p[0];if(p[0]>a1)a1=p[0];if(p[1]<b0)b0=p[1];if(p[1]>b1)b1=p[1]})});ar[f.properties.p+"|"+full(f.properties)]=(ar[f.properties.p+"|"+full(f.properties)]||0)+(a1-a0)*(b1-b0);if(a0<x0)x0=a0;if(a1>x1)x1=a1;if(b0<y0)y0=b0;if(b1>y1)y1=b1});
  var k=Math.cos((y0+y1)/2*Math.PI/180),s=1000/Math.max((x1-x0)*k,y1-y0),W=(x1-x0)*k*s,H=(y1-y0)*s;
  function X(p){return (p[0]-x0)*k*s}function Y(p){return (y1-p[1])*s}function P(p){return X(p).toFixed(1)+","+Y(p).toFixed(1)}
  var h='<svg viewBox="-6 -6 '+(W+12).toFixed(0)+' '+(H+12).toFixed(0)+'" role="img" aria-label="関西の地価の地図">',seen={};
  fs.forEach(function(f){var n=full(f.properties),t=by[f.properties.p+"|"+n],fill,op=1;
   if(!t)fill="#F4F4F4";else if(t.r8>0){fill=PC[t.p];op=(.22+.78*Math.min(t.r8,6)/6).toFixed(2)}else fill=t.r8<0?"#CFCFCF":"#E2E2E2";
   var d="";rings(f.geometry).forEach(function(rg){d+="M"+rg.map(P).join("L")+"Z"});
   h+='<path d="'+d+'" fill="'+fill+'" fill-opacity="'+op+'" data-n="'+esc(n)+'" data-p="'+f.properties.p+'"><title>'+esc(n)+(t?" "+pct(t.r8):"")+'</title></path>'});
  // ---- 地名
  var L=[],all=!pf,big=Math.max(W,H)/1000;
  if(all)PS.forEach(function(p){L.push({x:X(LP[p]),y:Y(LP[p]),a:[p],fs:46,c:PC[p],pri:1e9,pf:1})});
  var grp={};
  fs.forEach(function(f){var key=f.properties.p+"|"+full(f.properties);if(seen[key])return;seen[key]=1;var n=full(f.properties),cty=cityOf(n);
   if(cty&&!city){grp[f.properties.p+"|"+cty]=grp[f.properties.p+"|"+cty]||{p:f.properties.p,n:cty,xs:[],ys:[],ar:0};var gg=grp[f.properties.p+"|"+cty],q=LB[key]||[0,0];gg.xs.push(X(q));gg.ys.push(Y(q));gg.ar+=ar[key];return;}
   var q=LB[key];if(!q)return;var t=by[key],nm=city?n.replace(city,""):n;
   L.push({x:X(q),y:Y(q),a:all||!t?[nm]:[nm,pct(t.r8)],fs:all?26:33,c:t&&t.r8>0?PC[t.p]:"#6B6058",pri:ar[key]*(t?1:.3),n:n})});
  Object.keys(grp).forEach(function(k2){var gg=grp[k2],mx=gg.xs.reduce(function(a,b){return a+b},0)/gg.xs.length,my=gg.ys.reduce(function(a,b){return a+b},0)/gg.ys.length;L.push({x:mx,y:my,a:[gg.n],fs:all?30:37,c:"#2B2622",pri:1e8,bold:1})});
  L.sort(function(a,b){return b.pri-a.pri});
  var boxes=[],out="";function hit(b){if(b[0]<-6||b[1]<-6||b[2]>W+6||b[3]>H+6)return true;for(var i=0;i<boxes.length;i++){var o=boxes[i];if(b[0]<o[2]&&b[2]>o[0]&&b[1]<o[3]&&b[3]>o[1])return true}return false}
  L.forEach(function(l){var tries=[[0,0]],lines=l.a;
   function bx(dx,dy,ln){var ww=Math.max.apply(null,ln.map(function(t,i){return t.length*(i?l.fs*.62:l.fs*1.02)})),hh=l.fs*1.12*ln.length;return [l.x+dx-ww/2,l.y+dy-hh/2,l.x+dx+ww/2,l.y+dy+hh/2]}
   var ok=null,b0=bx(0,0,lines),hh=b0[3]-b0[1],ww=b0[2]-b0[0];
   [[0,0],[0,-hh*.75],[0,hh*.75],[ww*.62,0],[-ww*.62,0],[ww*.55,-hh*.7],[-ww*.55,-hh*.7],[ww*.55,hh*.7],[-ww*.55,hh*.7]].some(function(o){var b=bx(o[0],o[1],lines);if(!hit(b)){ok={o:o,b:b,ln:lines};return true}});
   if(!ok&&lines.length>1&&!l.pf){var one=[lines[0]];[[0,0],[0,-l.fs],[0,l.fs]].some(function(o){var b=bx(o[0],o[1],one);if(!hit(b)){ok={o:o,b:b,ln:one};return true}})}
   if(!ok&&l.pf)ok={o:[0,0],b:b0,ln:lines};
   if(!ok)return;boxes.push(ok.b);var cx=l.x+ok.o[0],cy=(ok.b[1]+ok.b[3])/2,n=ok.ln.length,ht=l.fs*1.12;
   if(ok.o[0]||ok.o[1])out+='<line x1="'+l.x.toFixed(0)+'" y1="'+l.y.toFixed(0)+'" x2="'+cx.toFixed(0)+'" y2="'+cy.toFixed(0)+'" stroke="#8C7B6E" stroke-width="1.4" vector-effect="non-scaling-stroke"/><circle cx="'+l.x.toFixed(0)+'" cy="'+l.y.toFixed(0)+'" r="'+(l.fs*.14).toFixed(1)+'" fill="#8C7B6E"/>';
   ok.ln.forEach(function(t,i){var y=cy-(n-1)*ht/2+i*ht;out+='<text x="'+cx.toFixed(0)+'" y="'+y.toFixed(0)+'" font-size="'+(i?l.fs*.82:l.fs).toFixed(0)+'" fill="'+(i?l.c:l.pf?l.c:"#2B2622")+'" font-weight="'+(l.pf||l.bold||!i?700:500)+'"'+(l.pf?' letter-spacing=".12em"':'')+(i?' font-family="Jost,sans-serif"':'')+'>'+esc(t)+'</text>'});});
  h+='<g class="lbl" style="pointer-events:none;font-family:\'Zen Kaku Gothic New\',sans-serif;paint-order:stroke;stroke:#fff;stroke-width:'+(8.5).toFixed(1)+'px;stroke-linejoin:round;text-anchor:middle;dominant-baseline:central">'+out+'</g>';
  w.innerHTML=h+'</svg>';info.innerHTML='<p class="fn">'+(all?"府県を選ぶと、市・区・町の名前と数字が出ます。":"街を押すと、その街の数字が出ます。")+'</p>';
  var cb=box.querySelector(".mpc");cb.innerHTML="";if(pf&&CITY[pf]){[pf+"ぜんぶ"].concat(CITY[pf]).forEach(function(cn,i){var b=document.createElement("button");b.type="button";b.textContent=i?cn+"の"+KU[cn]+"区":cn;if((i&&cn===city)||(!i&&!city))b.className="on";b.onclick=function(){drawMap(pf,i?cn:"");c("地図：市 "+cn);};cb.appendChild(b);});}
  w.querySelector("svg").addEventListener("click",function(e){var pth=e.target.closest("path");if(!pth)return;w.querySelectorAll("path.sel").forEach(function(x){x.classList.remove("sel")});pth.classList.add("sel");pth.parentNode.insertBefore(pth,w.querySelector("g.lbl"));
   var t=by[pth.dataset.p+"|"+pth.dataset.n];info.innerHTML=t?twRow(t):'<p class="fn">'+esc(pth.dataset.n)+'は、府県の資料に住宅地の平均がありません。</p><button type="button" class="frq">'+esc(pth.dataset.n)+'を調べてほしい</button>';
   var rb=info.querySelector(".frq");if(rb)rb.onclick=function(){c("調べてほしい："+pth.dataset.n);rb.disabled=true;rb.textContent="受け付けました。調べて、このリストに足します";};c("地図｜"+pth.dataset.n);});
 });}
var tq;
function open(m){document.documentElement.classList.add("fq-on");
 if(m==="new"){box.innerHTML='<div class="fh"><b>新着の数字</b><button type="button">リストにもどる ×</button></div><div class="fn"></div><div class="fr"></div>';
  var l=all.slice().sort(function(a,b){return (b.querySelector("a").dataset.date||"").localeCompare(a.querySelector("a").dataset.date||"")}).slice(0,12);var r=box.querySelector(".fr");r.className="fr blk";box.querySelector(".fn").textContent="最近足した数字 "+l.length+"件";l.forEach(function(w){r.appendChild(w.cloneNode(true))});c("不動産リスト｜新着");}
 else if(m==="map"){box.innerHTML='<div class="fh"><b>地図で見る</b><button type="button">リストにもどる ×</button></div><nav class="mpf"></nav><nav class="mpf mpc"></nav><div class="mpw nofilt"></div><div class="lg"><span style="--b:linear-gradient(90deg,#E9D3C9,#B97A62)">色が濃いほど上がった</span><span style="--b:#CFCFCF">下がった</span><span style="--b:#E2E2E2">横ばい</span><span style="--b:#F4F4F4;outline:1px solid #E4E4E4">数字なし</span></div><div class="mpi"></div><p class="fn" style="margin-top:12px">住宅地の1年の動き（令和8年地価公示、2026年1月1日時点）</p>';
  var nv=box.querySelector(".mpf");["すべて"].concat(PS).forEach(function(p,i){var b=document.createElement("button");b.type="button";b.textContent=p;if(PC[p])b.style.setProperty("--pc",PC[p]);if(!i)b.className="on";b.onclick=function(){nv.querySelectorAll("button").forEach(function(x){x.className=""});b.className="on";drawMap(i?p:"");c("地図：府県 "+p);};nv.appendChild(b);});
  drawMap("");c("不動産リスト｜地図");}
 else{box.innerHTML='<div class="fh"><b>街で探す</b><button type="button">リストにもどる ×</button></div><input class="fi" type="search" placeholder="例：吹田、西宮、草津" enterkeyhint="search"><div class="fc"></div><div class="fn"></div><div class="fr"></div>';
  var fc=box.querySelector(".fc"),fi=box.querySelector(".fi");PL.forEach(function(p){var b=document.createElement("button");b.type="button";b.textContent=p;b.onclick=function(){fi.value=p;find(p);c("街で探す："+p);};fc.appendChild(b);});
  fi.oninput=function(){find(fi.value);clearTimeout(tq);tq=setTimeout(function(){if(fi.value.trim())c("街で探す："+fi.value.trim())},1500);};find("");TWP.then(function(){if(!fi.value)find("")});c("不動産リスト｜街で探す");}
 box.querySelector(".fh button").onclick=close;
 if(window.V2BAR)window.V2BAR.querySelectorAll("a[data-m]").forEach(function(a){a.classList.toggle("cur",a.dataset.m===m)});
 scrollTo({top:box.getBoundingClientRect().top+scrollY-14,behavior:"smooth"});}
function close(){document.documentElement.classList.remove("fq-on");box.innerHTML="";if(window.V2BAR)window.V2BAR.querySelectorAll("a[data-m]").forEach(function(a){a.classList.remove("cur")});scrollTo({top:paper.getBoundingClientRect().top+scrollY-120,behavior:"smooth"});}
window.FQ={open:open,close:close};
var q=(location.search.match(/[?&]fq=(q|new|map)/)||[])[1];if(q){history.replaceState(null,"",location.pathname+location.hash);addEventListener("load",function(){setTimeout(function(){open(q)},200)});}
})();</script>""".replace("__PLACES__", json.dumps(PLACES, ensure_ascii=False))
h = h.replace("</body>", FQ + "</body>", 1)

h = h.replace("__NT__", str(len(json.load(open(os.path.join(ROOT, "links/assets/towns.json"), encoding="utf-8")))))
open(OUT, "w", encoding="utf-8").write(h)
print("ok", "live" if live else "preview(noindex)", len(FACTS), "cards", len(h), "bytes")
