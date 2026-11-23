# 11/23 関東 宝徳寺 1分版：表紙から開く絵本の流れはそのまま、中の6ページを3D（three.js）のリアルな映像に。字はガラスのカード（オーナーのお洒落＝グラスモーフィズム＋オーロラの線）
import subprocess, json, os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__)); VD = sys.argv[1]; TARGET = float(sys.argv[2]) if len(sys.argv) > 2 else 63.0
def dur(f): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).decode())
D = [dur(f"{VD}/20-{i:02d}.wav") for i in range(9)]
def plan(extra):
    v = [1.8]; T = []
    for k in range(6):  # 6 scenes, each one voice line
        T.append(round(v[k] + D[k] + .45 + extra, 2)); v.append(round(T[-1] + .6, 2))
    # info page: voice 6 then 7
    v.append(round(v[6] + D[6] + .5, 2)); T.append(round(v[7] + D[7] + .9, 2)); v.append(round(T[-1] + .7, 2))
    END = round(v[8] + D[8] + 2.0, 2); return v, T, END
lo, hi = 0.0, 3.0
for _ in range(30):
    mid = (lo + hi) / 2; _, _, e = plan(mid)
    lo, hi = (mid, hi) if e < TARGET else (lo, mid)
v, T, END = plan(round(lo, 2))
spans = [round((T[k] + .7) - (0.8 if k == 0 else T[k - 1]), 2) for k in range(6)]
print("END", END, "T", T, "v", v, "spans", spans)
json.dump(spans, open(HERE + "/spans.json", "w"))
tpl = open(HERE + "/src/tpl-long.txt").read()
css_end = tpl.index("</style>")
css = tpl[:css_end] + """
.clip{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.cap{left:120px;right:150px;top:120px;padding:34px 40px 32px;border-radius:30px;font-family:G;color:#fff;font-size:46px;line-height:1.5;letter-spacing:.05em;text-shadow:0 1px 12px rgba(0,0,0,.25);
 background:linear-gradient(135deg,rgba(255,255,255,.16),rgba(30,16,12,.38) 55%,rgba(20,10,8,.46));backdrop-filter:blur(26px) saturate(1.4) brightness(.8);-webkit-backdrop-filter:blur(26px) saturate(1.4) brightness(.8);
 border:1px solid rgba(255,255,255,.30);box-shadow:0 24px 60px rgba(0,0,0,.28),inset 0 1px 0 rgba(255,255,255,.45)}
.cap:before{display:none}
.cap .lb{font-family:G;font-size:20px;letter-spacing:.36em;color:rgba(255,255,255,.82);margin-bottom:16px}
.cap .ul{height:3px;width:150px;border-radius:3px;margin:22px 0 16px;background:linear-gradient(90deg,#FFB65C,#F6A6C8,#B7A4F2,#2EC4B6)}
.cap small{font-family:G;font-size:26px;letter-spacing:.08em;color:rgba(255,255,255,.88)}
.cap.lo{top:auto;bottom:150px}
/* 11/23 夜 owner「本もデザインアップデートしてお洒落に」：案内ページを写真の上のガラスに */
#dust{display:none}

/* 11/23 23:30 owner「綺麗に見えない」：ガラスの札をやめ、字は下に大きく。下だけ暗くして読ませる */
#dust,#parts{display:none !important}
.cap{left:130px;right:100px;top:auto !important;bottom:160px;white-space:nowrap;padding:0;border-radius:0;background:none;backdrop-filter:none;-webkit-backdrop-filter:none;border:0;box-shadow:none;isolation:isolate;z-index:4;
 font-family:MB;font-size:62px;line-height:1.38;letter-spacing:.06em;color:#fff;text-shadow:0 2px 22px rgba(0,0,0,.55),0 0 3px rgba(0,0,0,.35)}
.cap:after{content:'';position:absolute;left:-200px;right:-200px;bottom:-160px;height:900px;z-index:-1;background:linear-gradient(0deg,rgba(10,5,2,.78),rgba(10,5,2,.45) 45%,rgba(10,5,2,0))}
.cap .lb{display:block;font-family:G;font-size:22px;letter-spacing:.42em;color:#F6D9A2;margin-bottom:22px;text-shadow:0 1px 10px rgba(0,0,0,.5)}
.cap .ul{display:block;height:3px;width:120px;margin:28px 0 20px}
.cap small{font-family:G;font-size:30px;letter-spacing:.1em;color:rgba(255,255,255,.92)}

/* 11/24 早朝：案内ページの後ろを、ぼかした景色がゆっくり進む映像に */
.info:before{display:none}
.info > video.ibg{position:absolute;left:-40px;top:-40px;width:calc(100% + 80px);height:calc(100% + 80px);object-fit:cover;filter:blur(14px) brightness(.58) saturate(1.15)}
.info{background:#120c09;color:#fff;padding:64px 52px}
.info:before{content:'';position:absolute;inset:-30px;background:url(a/L0.jpg) center/cover;filter:blur(18px) brightness(.62) saturate(1.15)}
.info > *{position:relative}
.info h2{font-family:G;font-weight:700;font-size:54px;letter-spacing:.04em;color:#fff;margin:0 0 26px;padding-bottom:22px;border-bottom:3px solid transparent;border-image:linear-gradient(90deg,#FFB65C,#F6A6C8,#B7A4F2,#2EC4B6) 1}
.info .r{border:1px solid rgba(255,255,255,.28);border-radius:22px;margin:0 0 14px;padding:18px 24px;background:linear-gradient(135deg,rgba(255,255,255,.16),rgba(255,255,255,.06));backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);font-family:G;font-size:38px;color:#fff}
.info .r b{color:rgba(255,255,255,.78);font-family:G;font-size:24px;letter-spacing:.2em;width:130px}
.info small{color:rgba(255,255,255,.82);font-family:G;font-size:25px}
.info p{font-family:G;color:#fff;font-size:32px;letter-spacing:.06em}
.info .ph{position:absolute;left:52px;right:52px;bottom:52px;height:330px;border-radius:26px;border:1px solid rgba(255,255,255,.35);box-shadow:0 20px 50px rgba(0,0,0,.35)}
"""
# 古い場面ごとの位置の上書きは消す
css = re.sub(r"#s[0-9] \.cap\{top:\d+px\}\n", "", css)
css = re.sub(r"#s0 \.cap:before,#s1 \.cap:before\{[^\n]*\n", "", css)
body_start = tpl.index("<body>"); body = tpl[css_end:body_start + len("<body>")]
def cap(lb, a, b, sm, lo=False): return f'<div class="cap{" lo" if lo else ""}"><span class="w lb">{lb}</span><span class="w">{a}</span><br><span class="w">{b}</span><i class="ul"></i><small class="w">{sm}</small></div>'
SC = [("base", cap('KYOTO · TAKAO', 'もみじのトンネルが、', '石段をつつむ', '京都・高雄 神護寺')),
      ("up", cap('MORNING LIGHT', '朝の光をすかして、', 'もみじがかがやく', '11月23日の色づきは「今見頃」')),
      ("leaf", cap('FALLEN LEAVES', '石段には、', '散りもみじ', '一段ずつ、しあわせな色に')),
      ("side", cap('STONE STEPS', 'こけむした石垣に', 'そって上る', '金堂へ続く長い石段')),
      ("top", cap('KONDO', '上りきると、', '金堂', '紅葉は、いま見頃')),
      ("down", cap('LOOK BACK', 'ふりかえると、', 'まっかな道', '拝観 9時〜16時'))]
# 映像は各ページが見える間だけ再生
pages = []
for k, (m, c) in enumerate(SC):
    st = 0.8 if k == 0 else T[k - 1]; du = round(T[k] + .7 - st, 2)
    pages.append(f'<div class="sc" id="s{k}" style="z-index:{8-k}"><div class="face"><div class="edge" id="e{k}"></div><video class="clip" src="a/v{k}.mp4" muted data-start="{st}" data-duration="{du}"></video>{c}<div class="shade"></div>{"<div class=cast></div>" if k else ""}<div class="gut"></div></div><div class="bk"></div></div>')
h = tpl[body_start + len("<body>"):]
hp = h[h.index('<div class="sc" id="s5"'):h.index('<div class="sc" id="s4"')].replace('id="s5" style="z-index:0"', 'id="s7" style="z-index:0"')
info = h[h.index('<div class="sc" id="s4"'):h.index('<div class="sc" id="s3"')].replace('id="s4" style="z-index:1"', 'id="s6" style="z-index:1"')
cover = h[h.index('<div class="sc" id="cv"'):h.index('</div>\n <div id="dust">')]
rest = h[h.index(' <div id="dust">'):h.index('<script>')]
info = info.replace('<div class="info">', f'<div class="info"><video class="ibg" src="a/vvi.mp4" muted data-start="{T[5]}" data-duration="{round(T[6]+1.2-T[5],2)}"></video>', 1)
html_book = ' <div id="stage">\n <div id="halo"></div>\n <div id="book">\n  ' + hp + info + "\n  ".join(reversed(pages)) + "\n  " + cover.replace('z-index:6', 'z-index:9') + '</div>\n'
pre = h[:h.index(' <div id="stage">')]
js = h[h.index('<script>'):]
# ---- JS を6場面＋案内＋リスト用に組み直す
j = js
j = j[:j.index("// 層は寝た形から始める")] + j[j.index("// ===== 1."):]
j = j[:j.index("// ===== 2. 切り紙")] + j[j.index("// ===== 2b."):]
j = j.replace('tl.to("#stage",{scale:1,x:0,y:0,duration:1.1,ease:"power2.inOut"},T[3]);', 'tl.to("#stage",{scale:1,x:0,y:0,duration:1.1,ease:"power2.inOut"},T[5]);')
j = j.replace('const turns=[["#s0","#s1",T[0]],["#s1","#s2",T[1]],["#s2","#s3",T[2]],["#s3","#s4",T[3]],["#s4","#s5",T[4]]];', 'const turns=[0,1,2,3,4,5,6].map(k=>["#s"+k,"#s"+(k+1),T[k]]);')
a = j.index("// めくる紙は、めくる時に層を少し寝かせる"); b = j.index("// ===== 4.")
j = j[:a] + j[b:]
j = j.replace('[["#s0",V[0]],["#s1",V[1]],["#s2",V[2]],["#s3",V[3]]].forEach', '[0,1,2,3,4,5].map(k=>["#s"+k,V[k]]).forEach')
j = j.replace('tl.from("#s4 .info > *",{opacity:0,y:24,duration:.5,ease:"power2.out",stagger:.1},T[3]+.4);', 'tl.from("#s6 .info > *",{opacity:0,y:24,duration:.5,ease:"power2.out",stagger:.1},T[5]+.4);')
a = j.index("// ===== 5. 場面の中の空気"); b = j.index("// 光の粒：ゆっくり上へ漂う")
j = j[:a] + j[b:]
j = j.replace('tl.to("#dust",{opacity:0,duration:.6},T[3]-.2);', 'tl.to("#dust",{opacity:0,duration:.6},T[5]-.2);').replace("duration:T[3],ease:\"none\"},0)", "duration:T[5],ease:\"none\"},0)").replace("repeat:Math.floor(T[3]/(1.3+(i%5)*.3))", "repeat:Math.floor(T[5]/(1.3+(i%5)*.3))")
j = j.replace('T.forEach((t,k)=>{if(k<4){', 'T.forEach((t,k)=>{if(k<6){')
a = j.index("// 場面ごとの光"); b = j.index("// 光もれ（organic light leak")
j = j[:a] + j[b:]
j = j.replace("[0.75,...T.slice(0,4)]", "[0.75,...T.slice(0,6)]")
j = j.replace("},T[4]+.2);tl.to(\"#halo\"", "},T[6]+.2);tl.to(\"#halo\"").replace("repeat:2},T[4]+1);", "repeat:2},T[6]+1);")
j = j.replace("const T5=T[4];", "const T5=T[6];").replace('tl.to("#tab",{height:280,duration:.7,ease:"power3.out"},T[3]+1.6);', 'tl.to("#tab",{height:280,duration:.7,ease:"power3.out"},T[5]+1.6);')
# 字が出る動き：ガラスのカードごとふわっと
j = j.replace('// ===== 4. 字：ぼかしから浮かび、金の線が走る =====', '// ===== 4. 字：ガラスのカードがふわっと出て、字が浮かぶ =====\n[0,1,2,3,4,5].forEach(k=>{tl.from("#s"+k+" .cap",{opacity:0,y:40,duration:.9,ease:"power3.out"},V[k]-.6);tl.to("#s"+k+" .cap",{opacity:0,y:-16,duration:.45,ease:"power2.in"},T[k]-.5)});')
for x in ["T[3]", "T[4]"]:
    pass
out = css + body + "\n" + pre + html_book + rest + j
R = {'@END@': str(END), '@T@': json.dumps(T), '@V@': json.dumps(v)}
aud = '\n'.join(f' <audio id="v{i}" src="a/w{i}.wav" data-start="{v[i]}" data-duration="{round(D[i], 2)}" data-volume="1.7"></audio>' for i in range(9))
aud += '\n' + '\n'.join(f' <audio id="flip{j2}" src="a/flip.wav" data-start="{t}" data-duration="0.6" data-volume="0.7"></audio>' for j2, t in enumerate(T))
R['@AUDIO@'] = aud
import random; rr = random.Random(1124)
R['@DUST@'] = ''.join(f'<i style="left:{rr.uniform(20,900):.0f}px;top:{rr.uniform(300,1500):.0f}px;width:{(s:=rr.uniform(6,16)):.0f}px;height:{s:.0f}px" data-d="{rr.uniform(160,520):.0f}" data-x="{rr.uniform(-80,80):.0f}"></i>' for _ in range(14))
for a2, b2 in R.items():
    assert out.count(a2) >= 1, a2; out = out.replace(a2, b2)
left = re.findall(r"T\[[3-4]\]|#S\d[mnf]|F\(\d\)", j)
print("leftover refs:", left)
open(HERE + "/index.html", "w").write(out)
json.dump(dict(END=END, T=T, v=v), open(HERE + "/times.json", "w"))
