"""11/27 owner の曲（フリー・reel_bgm2.m4a）をリールの下に敷く。
使い方: python3 bgm2.py <始める秒> <長さ> <出力wav>
始める秒は、表紙が開く 1.05秒とページをめくる時刻に曲の拍がそろう所（月が onset で選ぶ）。速さ・音の高さは変えない。"""
import subprocess, sys, os
o, L, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
src = os.path.join(os.path.dirname(__file__), 'reel_bgm2.m4a')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(o), '-t', str(L + 0.5), '-i', src,
  '-af', 'loudnorm=I=-20:TP=-3:LRA=9,aresample=48000', '-ac', '2', out], check=True)
