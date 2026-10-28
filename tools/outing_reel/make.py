"""おでかけリール（10/28 型・29秒）を作る。
使い方: python3 tools/outing_reel/make.py spec.json out.mp4
spec の欄は example_blumen.json を見る。lat/lon から地図のピン位置を出す。
"""
import json, os, subprocess, sys, shutil, tempfile
D = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(D, '..', '..'))
spec = json.load(open(sys.argv[1])); out = os.path.abspath(sys.argv[2])
# 地図の座標（mapsvg の関西）: 兵庫・滋賀の端で合わせた一次式
px = 19.72 * spec['lon'] - 2438.3
py = 255.75 + (35.67 - spec['lat']) * 23.36
work = tempfile.mkdtemp()
for f in ('grain.png', 'logo.png'): shutil.copy(os.path.join(D, f), work)
# リストの画面（府県のタブを押した所）
shot = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:390,height:844}},deviceScaleFactor:2}});
await p.route('**/c',r=>r.fulfill({{status:204}}));await p.goto('file://{ROOT}/links/index.html');await p.waitForTimeout(1200);
for(const x of await p.$$('button')){{if((await x.textContent()).trim()=='{spec['tab']}'){{await x.click();break;}}}}
await p.waitForTimeout(600);await p.screenshot({{path:'{work}/list.png',fullPage:true}});await b.close()}})();"""
open(f'{work}/shot.js', 'w').write(shot); subprocess.run(['node', f'{work}/shot.js'], check=True)
h = open(os.path.join(D, 'template.html')).read()
t = spec['text']
# 表紙の上の2行（10/28 オーナー決定）。全部のリールで同じ。
KICKER = ('関西の不動産屋が', '街の調査で見つけた、おでかけリスト')
rep = dict(CORNER=t['corner'], K1=KICKER[0], K2=KICKER[1], A1=t['title'][0], A2=t['title'][1], A3=t['place'],
           MT1=t['map_tag'][0], MT2=t['map_tag'][1], MT3=t['map_tag'][2], MC1=t['map_caption'],
           B1=t['date'][0], B1D=t['date'][1], B2=t['date'][2], B2D=t['date'][3], B3=t['date_title'], B3S=str(t.get('date_title_size', 58)), B4=t['date_note'],
           C0=t['point_kicker'], C1=t['point_title'], C2=t['points'][0], C3=t['points'][1], C4=t['points'][2],
           D1K=t['info'][0][0], D1V=t['info'][0][1], D2K=t['info'][1][0], D2V=t['info'][1][1],
           D3K=t['info'][2][0], D3V=t['info'][2][1], D4K=t['info'][3][0], D4V=t['info'][3][1], D5=t['info_note'],
           E2=t['list_caption'], LISTPNG='list.png', PX=f'{px:.2f}', PY=f'{py:.2f}', PREF=spec['pref'], FONTS=os.path.join(ROOT, 'tools', 'fonts'))
for k, v in rep.items(): h = h.replace(f'__{k}__', v)
assert '__' not in h.replace('__proto__', ''), 'placeholder left'
open(f'{work}/reel.html', 'w').write(h)
rec = f"""const {{chromium}}=require('playwright');const fs=require('fs');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
await p.goto('file://{work}/reel.html');await p.waitForTimeout(900);fs.mkdirSync('{work}/fr',{{recursive:true}});
const only=process.argv[2];if(only){{for(const t of only.split(',')){{await p.evaluate(t=>render(t),+t);await p.screenshot({{path:'{work}/c-'+t+'.jpg',type:'jpeg',quality:85}});}}await b.close();return;}}
for(let i=0;i<30*28.8;i++){{await p.evaluate(t=>render(t),i/30);await p.screenshot({{path:'{work}/fr/'+String(i).padStart(4,'0')+'.jpg',type:'jpeg',quality:92}});}}await b.close()}})();"""
open(f'{work}/rec.js', 'w').write(rec)
if len(sys.argv) > 3:  # 確認用の静止画だけ
    subprocess.run(['node', f'{work}/rec.js', sys.argv[3]], check=True); print(work); sys.exit()
subprocess.run(['node', f'{work}/rec.js'], check=True)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '30', '-i', f'{work}/fr/%04d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-c:a', 'aac', '-shortest', '-movflags', '+faststart', out], check=True)
print(out)
