# index.html の声（v0..v9）だけを並べた音を作る（めくりの音は入れない・11/27 owner「いらない」）
import re, sys, subprocess
d = sys.argv[1]; END = float(sys.argv[2]); out = sys.argv[3]
h = open(f'{d}/index.html', encoding='utf-8').read()
tags = re.findall(r'<audio id="v\d+" src="([^"]+)" data-start="([\d.]+)" data-duration="[\d.]+" data-volume="([\d.]+)"', h)
args, fl = [], []
for i, (src, st, vol) in enumerate(tags):
    args += ['-i', f'{d}/{src}']
    ms = int(float(st) * 1000)
    fl.append(f'[{i}:a]aresample=48000,volume={float(vol)*1.41:.3f},adelay={ms}|{ms},apad[a{i}]')
fl.append(''.join(f'[a{i}]' for i in range(len(tags))) + f'amix=inputs={len(tags)}:normalize=0,atrim=0:{END}[o]')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', *args, '-filter_complex', ';'.join(fl), '-map', '[o]', '-ac', '2', out], check=True)
