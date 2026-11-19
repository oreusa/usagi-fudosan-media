"""飛び出す絵本リール（11/19 owner「絵本だよな？これ絵本？」「ハイクオリティで見せて」「工夫して」）。
机の上の本を three.js で組み、ページをめくると切り紙の部品が起き上がる。絵は月が canvas で描く（写真・GPT なし）。
見開き6つ＝声6行。声が始まる少し前にめくり終わる。効果音は最初に本を開く1回だけ（owner「効果音うざい」）。
使い方: NM=<three の入った node_modules> VDIR=shots/voice/popup-eikando SP=20 python3 popup.py out.mp4 ["t1,t2" 静止画]"""
import json, os, subprocess, sys, wave

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.abspath(sys.argv[1]); STILL = sys.argv[2] if len(sys.argv) > 2 else ''
W = os.path.abspath(os.environ.get('WORK', '/tmp/popup-work')); os.makedirs(W + '/fr', exist_ok=True)
VDIR = os.environ.get('VDIR', ''); SP = os.environ.get('SP', '20'); NM = os.environ.get('NM', HERE + '/node_modules')
N = 6; TURN = .95


def dur(n):
    p = f'{VDIR}/{SP}-{n:02d}.wav'
    if not os.path.exists(p): return 3.2
    w = wave.open(p); return w.getnframes() / w.getframerate()


VD = [dur(n) for n in range(N)]
T = [0.0]; VDL = [0.55]
for n in range(1, N):
    T.append(round(VDL[-1] + VD[n - 1] + .3 + TURN, 3)); VDL.append(T[-1] + .15)
TOTAL = round(VDL[-1] + VD[-1] + 1.7, 3)
print('見開き', T, '声', [round(x, 2) for x in VDL], '全体', TOTAL)
html = open(HERE + '/page.html').read().replace('%POP%', 'file://' + HERE).replace('%NM%', 'file://' + NM).replace('%F%', ROOT + '/tools/fonts').replace('%T%', json.dumps(T)).replace('%TOTAL%', str(TOTAL))
open(f'{W}/page.html', 'w').write(html)
open(f'{W}/rec.js', 'w').write(f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch({{args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--allow-file-access-from-files']}});const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
p.setDefaultTimeout(600000);p.on('pageerror',e=>console.log('ERR',e.message));await p.goto('file://{W}/page.html');await p.waitForFunction(()=>window.ok,null,{{timeout:300000}});
const only=process.argv[2];if(only){{for(const t of only.split(',')){{await p.evaluate(t=>render(t),+t);await p.screenshot({{path:'{W}/c-'+t+'.jpg',type:'jpeg',quality:90}});}}await b.close();return}}
const fs=require('fs');const A=+(process.env.FR0||0),B=+(process.env.FR1||1e9);for(let i=A;i<30*{TOTAL}&&i<B;i++){{const f='{W}/fr/'+String(i).padStart(4,'0')+'.jpg';if(fs.existsSync(f))continue;await p.evaluate(t=>render(t),i/30);await p.screenshot({{path:f,type:'jpeg',quality:93}});}}await b.close()}})();""")
if STILL:
    subprocess.run(['node', f'{W}/rec.js', STILL], check=True); sys.exit()
NF = int(30 * TOTAL) + 1; K = int(os.environ.get('WORKERS', '3')); ps = []
for i in range(K): ps.append(subprocess.Popen(['node', f'{W}/rec.js'], env=dict(os.environ, FR0=str(NF * i // K), FR1=str(NF * (i + 1) // K))))
if any(p.wait() for p in ps): sys.exit('コマを撮れない')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', '0.2', '-i', f'{ROOT}/tools/brand/reel_bgm.m4a', '-t', f'{TOTAL + 1:.2f}', '-af', 'loudnorm=I=-17:TP=-1.5:LRA=11', '-ar', '48000', f'{W}/bgm.wav'], check=True)
ins = ['-i', f'{W}/bgm.wav']; flt = []; k = 2
for n in range(N):
    ins += ['-i', f'{VDIR}/{SP}-{n:02d}.wav']; flt.append(f'[{k}:a]aresample=48000,adelay={int(VDL[n] * 1000)}:all=1[v{n}]'); k += 1
flt.append(''.join(f'[v{n}]' for n in range(N)) + f'amix=inputs={N}:normalize=0,volume=1.7,apad=whole_dur={TOTAL + 1:.2f},asplit=2[vo][sc]')
ins += ['-i', f'{ROOT}/tools/outing_reel/sfx/bookOpen.ogg']; flt.append(f'[{k}:a]aresample=48000,volume=0.35,apad=whole_dur={TOTAL + 1:.2f}[fx]'); k += 1
flt.append(f'[1:a]afade=t=in:d=0.3,afade=t=out:st={TOTAL - 1.8:.2f}:d=1.8[bg0]')
flt.append('[bg0][sc]sidechaincompress=threshold=0.02:ratio=5:attack=40:release=500:makeup=1[bg]')
flt.append('[bg][vo][fx]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]')
flt.append("[0:v]format=gbrp,noise=alls=2:allf=t,format=yuv420p[vv]")
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '30', '-i', f'{W}/fr/%04d.jpg'] + ins + ['-filter_complex', ';'.join(flt), '-map', '[vv]', '-map', '[a]', '-t', f'{TOTAL:.2f}',
                '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', OUT], check=True)
print(OUT, TOTAL, '秒')
