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
URL = "https://usagi-odekake.usagi-fudosan.workers.dev/fudosan-list"
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
h = h.replace('content="https://usagi-odekake.usagi-fudosan.workers.dev/"', f'content="{URL}"')
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
h = re.sub(r'<script src="assets/v2\.js[^"]*"></script>', '<script src="assets/v2sub.js?v=2" defer></script>', h)

# ---- 見出し
h = h.replace('<h1>関西おでかけリスト</h1><p class="sub">関西の街を調査して見つけた魅力を、<br>おでかけ先として紹介しています</p>',
              '<h1>関西不動産リスト</h1><p class="sub">関西の街を調査して見つけた数字を、<br>公式の資料つきで紹介しています</p>')
h = re.sub(r'<div class="sea" id="sea">.*?</div><svg class="yr" id="yr".*?</svg>', "", h, count=1, flags=re.S)
SW = ('<nav class="tnsw" aria-label="TOWN NOTES のリスト"><a href="./" data-k="切り替え｜おでかけ">おでかけ</a>'
      '<a href="fudosan-list" class="on" aria-current="page">不動産</a></nav>')
h = h.replace('<a class="ilk" href="illumination">関西イルミネーション 2026 日程一覧<span>→</span></a>',
              SW + '<a class="ilk" href="chika-osaka">大阪市24区 地価ランキング 2026<span>→</span></a>')
h = h.replace("この府県のおでかけは、これから増やしていきます", "この府県の分は、これから増やしていきます")

# ---- カード
TABS = [("chika", "b-now", "LAND PRICE", "地価・相場", "地価・相場の数字"),
        ("jinko", "b-up", "PEOPLE", "人口・駅", "人口と駅の数字"),
        ("dekiru", "b-new", "NEW", "できる", "できる・できた"),
        ("seido", "b-done", "MONEY", "制度", "住まいの制度とお金")]
ORDER = ["大阪", "京都", "兵庫", "奈良", "滋賀", "和歌山"]


def card(o):
    return (f'<a class="card" data-pref="{o["pref"]}" data-cat="{o["tab"]}" href="{E(o["url"])}">'
            f'<div class="bd"><div class="d">{E(o["src"])}</div><div class="t">{E(o["t"].replace("｜", "　"))}</div>'
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

# ---- 府県の絞り込み・カードの包み・数え（index の仕組みを不動産用に短くしたもの）
main_js = r'''<script>(function(){
var O=(function(){try{return localStorage.getItem("usagi_owner")==="1";}catch(e){return false;}})();function c(k){if(O)return;try{var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true});}catch(e){}}
var PC={"大阪":"#B97A62","京都":"#8A7495","兵庫":"#4F6681","奈良":"#6F8C68","滋賀":"#5F8F98","和歌山":"#C4925A"},CAT={chika:"地価",jinko:"人口・駅",dekiru:"できる",seido:"制度"};
document.querySelectorAll(".paper a.card").forEach(function(a){var w=document.createElement("div");w.className="it";var pf=a.getAttribute("data-pref");w.setAttribute("data-pref",pf);if(PC[pf])w.style.setProperty("--pc",PC[pf]);a.parentNode.insertBefore(w,a);w.appendChild(a);
 var bd=a.querySelector(".bd"),d=a.querySelector(".d"),cx=document.createElement("div");cx.className="v2c";cx.innerHTML='<span class="p" data-p="'+pf+'">'+pf+'</span><span>'+CAT[a.getAttribute("data-cat")]+'</span>';
 var dt=document.createElement("div");dt.className="v2d";dt.textContent=d.textContent;bd.insertBefore(dt,bd.firstChild);bd.insertBefore(cx,dt);});
var P=["大阪","京都","兵庫","奈良","滋賀","和歌山"],F=document.getElementById("flt");
["すべて"].concat(P).forEach(function(p,i){var b=document.createElement("button");b.textContent=p;if(PC[p])b.style.setProperty("--pc",PC[p]);if(!i)b.className="on";b.onclick=function(){F.querySelectorAll("button").forEach(function(x){x.className="";});b.className="on";var v=0;document.querySelectorAll(".paper .it").forEach(function(w){var ok=p=="すべて"||w.getAttribute("data-pref")==p;w.style.display=ok?"":"none";if(ok)v++;});document.getElementById("none").style.display=v?"none":"";c("絞り込み（不動産）："+p);};F.appendChild(b);});
document.addEventListener("click",function(ev){var s=ev.target.closest&&ev.target.closest(".v2c span.p");if(!s)return;ev.preventDefault();ev.stopPropagation();var b=[].find.call(F.querySelectorAll("button"),function(x){return x.textContent===s.dataset.p});if(b){b.click();scrollTo({top:F.getBoundingClientRect().top+scrollY-70,behavior:"smooth"});}},true);
var n=document.querySelectorAll(".paper .it").length,x=document.createElement("div");x.className="cnt";x.innerHTML='<span>調べた数字<b>'+n+'</b>件</span><span>6府県<b>すべて</b></span>';var nn=document.getElementById("none");nn.parentNode.insertBefore(x,nn.nextSibling);
c("表示：不動産リスト"+(document.referrer&&!/usagi-odekake/.test(document.referrer)?"（外から）":""));
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
SW_CSS = ('<style>.tnsw{display:flex;justify-content:center;gap:0 34px;margin:4px 0 18px}'
          '.tnsw a{font-family:"Shippori Mincho",serif;font-weight:600;font-size:15px;letter-spacing:.14em;color:#9C9187;text-decoration:none;padding:4px 2px 6px;border-bottom:2px solid transparent}'
          '.tnsw a.on{color:#2B2622;border-bottom-color:#2B2622}</style>')
h = h.replace("</head>", SW_CSS + "</head>", 1)


# タブの上の見出し（数字｜街と暮らし）と、府県ボタンをタブの下へ（おでかけの map.js と同じ形・同じ見た目）
MOUNT = r"""<style>.tgrp{display:grid;grid-template-columns:1fr 1fr;gap:0 14px;margin:2px 0 6px}.tgrp span{display:block;text-align:center;font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:11px;letter-spacing:.14em;color:#8C7B6E;padding:0 0 6px;border-bottom:1px solid #D6CCC1;position:relative}.tgrp span:after{content:"";position:absolute;left:50%;bottom:-4px;width:7px;height:7px;background:#FFFFFF;border-right:1px solid #D6CCC1;border-bottom:1px solid #D6CCC1;transform:translateX(-50%) rotate(45deg)}.tn-top{margin-top:-16px}.tn-top .flt{margin:0 0 10px;border-top:0;padding:8px 0;gap:0 13px;flex-wrap:nowrap}</style>
<script>(function(){function mount(){var bar=document.querySelector(".tabs");if(!bar)return;
var tg=document.querySelector(".tgrp");if(!tg){tg=document.createElement("div");tg.className="tgrp";tg.innerHTML='<span>数字</span><span>街と暮らし</span>'}
if(bar.previousSibling!==tg)bar.parentNode.insertBefore(tg,bar);
var top=document.querySelector(".tn-top");if(!top){top=document.createElement("div");top.className="tn-top"}
["flt","none"].forEach(function(id){var e=document.getElementById(id);if(e&&e.parentNode!==top)top.appendChild(e)});
if(bar.nextSibling!==top)bar.parentNode.insertBefore(top,bar.nextSibling);}
mount();document.addEventListener("click",function(e){if(e.target.closest(".tabs,#flt"))setTimeout(mount,80);});})();</script>"""
h = h.replace("</body>", MOUNT + "</body>", 1)

open(OUT, "w", encoding="utf-8").write(h)
print("ok", "live" if live else "preview(noindex)", len(FACTS), "cards", len(h), "bytes")
