"""家を買いたい（/sagasu）：「その予算で、どの街に住める？」を TOWN（links/sagasu.html）と LIFE（akari site/sagasu.html）に作る。
11/10 オーナー「買いたい人向けの動線クソ分かりにくい」「工夫しろ その辺のhpと同じなら負ける」→ 見本3 OK「改善点なければok」。
- 種類 → 予算（大きいボタン4つ）→ 街の行を押す＝その街の売り出し中（Yahoo!不動産・広告）。3タップで物件まで。
- TOWN：近畿レインズ 2025年度の「実際に売れた平均」（10件以上の街）で予算に届く街を出す。LIFE：地価公示の住宅地の平均価格×100㎡（土地の目安）。
- 行の下の「いま開催：」はおでかけの1件ページ（links/o・site/o）の endDate が今日以降の物だけ。ページを開いた日にも終わった物は消す。
使い方: python3 tools/fudosan_list/kau.py [akari-auto のパス]
"""
import csv, glob, html, json, os, re, sys
R = os.path.dirname(os.path.abspath(__file__)) + "/../../"
AK = sys.argv[1] if len(sys.argv) > 1 else R + "../akari-auto/"

# ---- TOWN の数字（towns.py の関数を借りる：ページは書かない）
src = open(R + "tools/fudosan_list/towns.py", encoding="utf-8").read().split("\ndef town_page")[0]
ns = {"__file__": R + "tools/fudosan_list/towns.py"}
_argv = sys.argv; sys.argv = ["towns.py"]; exec(compile(src, "towns.py", "exec"), ns); sys.argv = _argv
T = json.load(open(R + "links/assets/towns.json", encoding="utf-8")); T = T.get("towns", T) if isinstance(T, dict) else T
town = []
for t in T:
    sd = ns["sold_of"](t)
    g = lambda k: int(round(float(sd[k]["価格万円"]))) if sd.get(k) and sd[k]["価格万円"] and int(sd[k]["件数"]) >= 10 else None
    town.append({"id": t["id"], "p": t["p"], "n": t["n"], "c": ns["JIS"].get(t["p"] + "|" + t["n"], ""), "m": g("m"), "h": g("k"), "r": t["r8"]})

# ---- LIFE の数字（土地100㎡の目安）
PK = {"tokyo": "東京", "kanagawa": "神奈川", "saitama": "埼玉", "chiba": "千葉", "ibaraki": "茨城", "tochigi": "栃木", "gunma": "群馬"}
price = {}
for f in glob.glob(AK + "data/kanto_chika/*.csv"):
    k = PK.get(os.path.basename(f)[:-4])
    for r in csv.reader(open(f, encoding="utf-8")):
        if k and len(r) >= 4 and r[3].strip().isdigit():
            price[(k, r[0])] = int(r[3])
JK = json.load(open(AK + "scripts/jis_kanto.json", encoding="utf-8"))
L = json.load(open(AK + "site/assets/towns.json", encoding="utf-8")); L = L.get("towns", L) if isinstance(L, dict) else L
life = [{"id": t["id"], "p": t["p"], "n": t["n"], "c": JK.get(t["p"] + "|" + t["n"], ""), "l": round(price[(t["p"], t["n"])] * 100 / 10000) if (t["p"], t["n"]) in price else None, "r": t["r8"]} for t in L]


# ---- いま開催のおでかけ（終わりの日つき）
def events(d):
    out = []
    for f in glob.glob(d + "/*.html"):
        s = open(f, encoding="utf-8").read()
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                j = json.loads(m.group(1))
            except Exception:
                continue
            for it in (j.get("@graph", [j]) if isinstance(j, dict) else j):
                if isinstance(it, dict) and it.get("@type") == "Event" and it.get("endDate") and it.get("name"):
                    out.append((html.unescape(it["name"]).split("（")[0][:22], it["endDate"][:10], json.dumps(it.get("location", ""), ensure_ascii=False)))
    return out


import datetime
today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d")
for D, d in ((town, R + "links/o"), (life, AK + "site/o")):
    ev = [e for e in events(d) if e[1] >= today]
    for t in sorted(D, key=lambda t: -len(t["n"])):
        t["o"] = sorted([[n, e] for n, e, loc in ev if t["n"] in loc], key=lambda x: x[1])[:3]

SITES = [
 dict(D=town, out=R + "links/sagasu.html", area="関西", n="205", brand="TOWN NOTE", base="https://townnote.pages.dev",
      js='<script src="assets/night.js?v=23"></script><script src="assets/menu.js?v=46" defer></script><script src="assets/v2sub.js?v=12" defer></script>',
      order=["大阪", "京都", "兵庫", "奈良", "滋賀", "和歌山"], col={"大阪": "#B97A62", "京都": "#8A7495", "兵庫": "#4F6681", "奈良": "#6F8C68", "滋賀": "#5F8F98", "和歌山": "#C4925A"},
      sid="3786315", pid="892742459", ar="06", kinds=[("m", "中古マンション", "used/mansion"), ("h", "中古一戸建て", "used/house")], bud=[2000, 3000, 4000, 5000], b0=3000,
      unit="実際に売れた平均", usp="売り出し価格ではなく、<b>実際に売れた値段</b>で選べます。",
      src="近畿レインズ「2025年度 年刊市況レポート」市区町村別の成約の平均（2025年4月〜2026年3月・10件以上の街）"),
 dict(D=life, out=AK + "site/sagasu.html", area="関東", n="329", brand="LIFE NOTE", base="https://usagi-life-notes.pages.dev",
      js='<script src="/assets/night.js?v=18"></script><script src="/assets/menu.js?v=43" defer></script><script src="/assets/v2sub.js?v=16" defer></script>',
      order=["東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬"], col={"東京": "#4F86C6", "神奈川": "#3FA3B5", "埼玉": "#E09A3E", "千葉": "#D9775A", "茨城": "#5FA06A", "栃木": "#D2697E", "群馬": "#9C7BB8"},
      sid="3786665", pid="892742457", ar="03", kinds=[("l", "土地（100㎡・約30坪）", "land")], bud=[1000, 2000, 3000, 5000], b0=3000,
      unit="土地100㎡の目安", usp="<b>国の地価公示</b>の住宅地の平均から、土地100㎡（約30坪）の目安で選べます。",
      src="令和8年地価公示の住宅地の平均価格×100㎡（建物は別）"),
]
E = html.escape
for S in SITES:
    title = f"家を買いたい｜その予算で、どの街に住める？{S['area']}{S['n']}の街【2026年】｜{S['brand']}"
    desc = (f"{S['area']}の街を、予算から探せます。" + ("売り出し価格ではなく、実際に売れた中古マンション・一戸建ての平均（近畿レインズ）で、予算に届く街がすぐわかります。" if S["ar"] == "06" else "国の地価公示から出した土地100㎡の目安で、予算に届く街がすぐわかります。")
            + "街を押すと、その街で売り出し中の物件が見られます。")
    kt = "".join(f'<button type="button" data-k="{k}" data-y="{y}"{" class=\"on\"" if i == 0 else ""}>{lb}</button>' for i, (k, lb, y) in enumerate(S["kinds"]))
    D = [{k: v for k, v in t.items() if v not in (None, [], "") or k in ("id", "p", "n", "r")} for t in S["D"]]
    h = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{S['base']}/sagasu">
<meta property="og:title" content="その予算で、どの街に住める？｜{S['area']}{S['n']}の街"><meta property="og:description" content="{E(desc)}">
<link rel="icon" href="/assets/ogp.png"><link rel="apple-touch-icon" href="/assets/icon-180.png"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#FFFFFF">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Jost:wght@300..600&family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#fff;font-family:"Zen Kaku Gothic New";color:#2B2622;padding-bottom:90px}}
.wrap{{max-width:440px;margin:0 auto;padding:0 16px 40px}}
.hero{{padding:64px 0 0;text-align:center}}.hero .en{{font-family:Jost;font-size:10.5px;letter-spacing:.36em;color:#9C8775}}
.hero h1{{font-family:"Shippori Mincho",serif;font-size:22px;font-weight:600;letter-spacing:.06em;margin:6px 0 4px;line-height:1.5}}
.usp{{font-size:12.5px;line-height:1.7;color:#6B6058;margin:0 0 12px}}.usp b{{color:#2B2622}}
.bud{{background:#F4F4F6;border-radius:18px;padding:14px}}
.kd{{display:flex;background:#fff;border:1.5px solid #D6D6D6;border-radius:12px;overflow:hidden;margin-bottom:12px}}.kd button{{flex:1;font:inherit;font-size:13.5px;font-weight:700;padding:10px 4px;border:0;background:#fff;color:#5E544D;cursor:pointer}}.kd button+button{{border-left:1px solid #E3E3E3}}.kd button.on{{background:#3A2E28;color:#fff}}
.bl{{font-size:13.5px;font-weight:700}}
.bc{{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-top:8px}}.bc button{{font:inherit;font-family:Jost,"Zen Kaku Gothic New";font-size:18px;font-weight:600;padding:11px 4px;border-radius:12px;border:1.5px solid #D6D6D6;background:#fff;color:#2B2622;cursor:pointer}}.bc button small{{font-family:"Zen Kaku Gothic New";font-size:12px;font-weight:500;margin-left:2px}}.bc button.on{{background:#3A2E28;border-color:#3A2E28;color:#fff}}
.res{{text-align:center;margin:14px 0 2px;font-family:"Shippori Mincho",serif;font-size:16px}}.res em{{font-style:normal;font-family:Jost;font-size:28px;font-weight:500;margin:0 4px;color:#B5735A}}
.pf{{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;margin:8px -16px 0;padding:0 16px}}.pf::-webkit-scrollbar{{display:none}}
.pf button{{flex:0 0 auto;font:inherit;font-size:13px;font-weight:700;padding:7px 12px;border-radius:99px;border:1.5px solid #DADADA;background:#fff;color:#5E544D;cursor:pointer}}.pf button i{{font-style:normal;font-family:Jost;font-weight:500;margin-left:5px;color:#9C8775}}.pf button.on{{background:var(--c,#3A2E28);border-color:var(--c,#3A2E28);color:#fff}}.pf button.on i{{color:#fff;opacity:.8}}
.so{{display:flex;justify-content:center;gap:4px;margin:10px 0 8px}}.so button{{font:inherit;font-size:12.5px;padding:6px 10px;border:0;background:none;color:#857A70;border-bottom:2px solid transparent;cursor:pointer}}.so button.on{{color:#2B2622;font-weight:700;border-color:#2B2622}}
.lh{{display:flex;justify-content:space-between;font-size:11px;color:#9C8775;margin:0 2px 6px}}
#tl{{display:block;border-top:1px solid #ECECEC;background:#fff}}
#tl a.rw{{display:flex;align-items:center;gap:10px;text-decoration:none;color:#2B2622;background:#fff;margin:0;padding:11px 4px 11px 12px;border:0;border-bottom:1px solid #ECECEC;border-left:4px solid var(--c);border-radius:0;box-shadow:none}}
.rw .a{{flex:1;min-width:0}}.rw .a b{{font-size:16px}}.rw .a small{{font-size:11px;color:#9C8775;margin-left:6px}}.rw .a span{{display:block;font-size:11.5px;color:#857A70;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.rw .b{{text-align:right}}.rw .b b{{display:block;font-family:Jost,"Zen Kaku Gothic New";font-size:17px;font-weight:600}}.rw .b span{{font-size:11px;color:#B5735A}}
.rw:after{{content:"›";font:300 24px Jost,sans-serif;color:#9C8775;margin-left:2px}}
.kmore{{display:block;width:100%;margin:12px 0 0;font:inherit;font-size:14px;font-weight:700;padding:12px;border-radius:12px;border:1.5px solid #D6D6D6;background:#fff;color:#2B2622;cursor:pointer}}
.em{{font-size:13px;color:#857A70;text-align:center;padding:24px 0;line-height:1.9}}
.nt{{font-size:11px;color:#857A70;line-height:1.8;margin:16px 2px 0}}
</style>{S["js"]}</head><body><div class="wrap">
<div class="hero"><div class="en">FIND A HOME BY BUDGET</div><h1>その予算で、どの街に住める？</h1><p class="usp">{S["usp"]}</p></div>
<div class="bud"><div class="kd" id="kd">{kt}</div><div class="bl">予算は？</div><div class="bc" id="bc"></div></div>
<p class="res" id="res"></p>
<div class="pf" id="pf"></div>
<div class="so" id="so"><button type="button" data-s="up" class="on">値上がり順</button><button type="button" data-s="cheap">安い順</button><button type="button" data-s="od">いま開催が多い順</button></div>
<div class="lh"><span>押すと、その街で売り出し中の家（広告）</span><span>{S["unit"]}</span></div>
<div id="tl"></div>
<p class="nt">値段：{S["src"]}。1軒ずつの値段ではありません。「いま開催」は、このサイトのおでかけリストから（終わった物は出しません）。街を押すと Yahoo!不動産 のその街の一覧が開きます（広告）。</p>
<div class="ft" style="text-align:center;font-size:10px;color:#8C7B6E;margin-top:24px">{S["brand"]}</div></div>
<script>(function(){{
var D={json.dumps(D, ensure_ascii=False, separators=(",", ":"))},ORD={json.dumps(S["order"], ensure_ascii=False)},COL={json.dumps(S["col"], ensure_ascii=False)},BUD={json.dumps(S["bud"])},UNIT="{S["unit"]}";
var TD=new Date(Date.now()+9*3600e3).toISOString().slice(0,10),st={{k:"{S["kinds"][0][0]}",y:"{S["kinds"][0][2]}",b:{S["b0"]},p:"",s:"up",n:30}};
D.forEach(function(t){{t.o=(t.o||[]).filter(function(x){{return x[1]>=TD}})}});
var O=false;try{{O=localStorage.getItem("usagi_owner")==="1"}}catch(e){{}}
function c(k){{if(O)return;try{{var b=JSON.stringify({{k:k}});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{{method:"POST",body:b,keepalive:true}})}}catch(e){{}}}}
c("表示：住む街をさがす"+(document.referrer&&document.referrer.indexOf(location.host)<0?"（外から）":""));
function E(s){{return String(s).replace(/[&<>"]/g,function(c){{return{{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c]}})}}
function man(v){{return v>=10000?Math.floor(v/10000)+"億"+(v%10000?(v%10000).toLocaleString()+"万":"")+"円":v.toLocaleString()+"万円"}}
function yu(t){{var u=t.c?"https://realestate.yahoo.co.jp/"+st.y+"/search/{S["ar"]}/"+t.c.slice(0,2)+"/"+t.c+"/":"https://realestate.yahoo.co.jp/";return "https://ck.jp.ap.valuecommerce.com/servlet/referral?sid={S["sid"]}&pid={S["pid"]}&vc_url="+encodeURIComponent(u)}}
var bc=document.getElementById("bc"),tl=document.getElementById("tl");
function draw(){{
 bc.innerHTML=BUD.map(function(v){{return '<button type="button" data-b="'+v+'"'+(v===st.b?' class="on"':'')+'>'+v.toLocaleString()+'<small>万円まで</small></button>'}}).join("");
 var A=D.filter(function(t){{return t[st.k]!=null&&t[st.k]<=st.b}}),cnt={{}};A.forEach(function(t){{cnt[t.p]=(cnt[t.p]||0)+1}});
 document.getElementById("res").innerHTML="この予算で届く街<em>"+A.length+"</em>";
 document.getElementById("pf").innerHTML='<button type="button" data-p=""'+(st.p?'':' class="on"')+'>ぜんぶ<i>'+A.length+'</i></button>'+ORD.map(function(p){{return '<button type="button" data-p="'+p+'" style="--c:'+COL[p]+'"'+(st.p===p?' class="on"':'')+'>'+p+'<i>'+(cnt[p]||0)+'</i></button>'}}).join("");
 var L=A.filter(function(t){{return !st.p||t.p===st.p}});
 L.sort(st.s=="up"?function(a,b){{return b.r-a.r}}:st.s=="cheap"?function(a,b){{return a[st.k]-b[st.k]}}:function(a,b){{return b.o.length-a.o.length||b.r-a.r}});
 tl.innerHTML=L.length?L.slice(0,st.n).map(function(t){{return '<a class="rw" style="--c:'+COL[t.p]+'" href="'+E(yu(t))+'" rel="nofollow sponsored" target="_blank" data-k="家を探す｜Yahoo!不動産｜'+E(t.n)+'"><div class="a"><b>'+E(t.n)+'</b><small>'+t.p+'</small>'+(t.o.length?'<span>いま開催：'+E(t.o[0][0])+(t.o.length>1?' ほか'+(t.o.length-1):'')+'</span>':'')+'</div><div class="b"><b>'+man(t[st.k])+'</b><span>地価 '+(t.r>0?"+":"")+t.r.toFixed(1)+'%'+(t.r>0?" ↑":"")+'</span></div></a>'}}).join("")+(L.length>st.n?'<button type="button" class="kmore" id="kmore">あと'+(L.length-st.n)+'の街を見る</button>':''):'<p class="em">この予算では、まだ届く街がありません。<br>予算を少し上げてみてください。</p>'}}
bc.addEventListener("click",function(e){{var b=e.target.closest("button");if(!b)return;st.b=+b.dataset.b;st.n=30;c("家を買いたい｜予算｜"+st.b);draw()}});
document.getElementById("kd").addEventListener("click",function(e){{var b=e.target.closest("button");if(!b)return;st.k=b.dataset.k;st.y=b.dataset.y;[].forEach.call(this.children,function(x){{x.classList.toggle("on",x===b)}});draw()}});
document.getElementById("pf").addEventListener("click",function(e){{var b=e.target.closest("button");if(!b)return;st.p=b.dataset.p;st.n=30;draw()}});
document.getElementById("so").addEventListener("click",function(e){{var b=e.target.closest("button");if(!b)return;st.s=b.dataset.s;[].forEach.call(this.children,function(x){{x.classList.toggle("on",x===b)}});draw()}});
tl.addEventListener("click",function(e){{if(e.target.id==="kmore"){{st.n+=60;draw();return}}var a=e.target.closest("a.rw");if(a)c("クリック：住む街をさがす｜"+a.getAttribute("data-k"))}});
draw();}})();</script>
</body></html>
'''
    open(S["out"], "w", encoding="utf-8").write(h)
    print("ok", S["out"], len(D), "街")
