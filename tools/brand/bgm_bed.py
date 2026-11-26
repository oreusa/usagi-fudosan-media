#!/usr/bin/env python3
"""リールの曲の下地（11/26〜）。owner「遅くしないで」「繋げるなら違和感なく」「もうちょい上手く」。
元の速さのまま。元の曲は38秒から盛り上がるので使わない。和音と音色が一番そろう所（機械で全部の拍を比べた）＝
31.45秒の拍 → 8小節前の 13.67秒の拍 へ戻ってくり返す。拍の頭は音の立ち上がりの時刻でそろえ、
拍の直前 0.2秒 で重ねて入れ替える（拍の頭の音は入る方だけ）。
使い方: bgm_bed.py <長さ秒> <出力.wav>   （元 = tools/brand/reel_bgm.m4a・オーナーのオリジナル）"""
import sys,subprocess,os,numpy as np,wave
L=float(sys.argv[1]);O=sys.argv[2];R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SR=48000;src=os.path.join(R,'tools/brand/reel_bgm.m4a')
raw=subprocess.run(['ffmpeg','-loglevel','error','-i',src,'-f','f32le','-ac','2','-ar',str(SR),'pipe:1'],capture_output=True,check=True).stdout
x=np.frombuffer(raw,dtype=np.float32).reshape(-1,2).copy();assert len(x)>SR*60,'曲が読めない'
S=lambda t:int(round(t*SR))
A0,A1,B0=0.19,31.4427,13.6461   # どちらも拍の頭の音の立ち上がり（onset）
b0=S(B0);a1=S(A1);XF=S(0.2);pre=S(0.01)
need=S(L+1);y=x[S(A0):a1-pre].copy()
while len(y)<need:
    # 出る方（a1-pre-XF〜a1-pre）を下げ、入る方（b0-pre-XF〜）を上げて重ねる
    t=np.linspace(0,np.pi/2,XF)[:,None]
    y[-XF:]=y[-XF:]*np.cos(t)+x[b0-pre-XF:b0-pre]*np.sin(t)
    y=np.concatenate([y,x[b0-pre:a1-pre]])
y=y[:need]
tmp=O+'.raw.wav'
with wave.open(tmp,'wb') as f:
    f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes((np.clip(y,-1,1)*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-loglevel','error','-y','-i',tmp,'-af','loudnorm=I=-20:TP=-1.5:LRA=9','-ar','48000',O],check=True);os.remove(tmp)
