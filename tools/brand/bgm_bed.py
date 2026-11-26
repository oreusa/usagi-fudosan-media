#!/usr/bin/env python3
"""11/26 owner「遅くしないで」「繋げるなら違和感なく」→ 元の速さのまま、盛り上がる前（38.1秒の拍）で
曲の頭の落ち着いた所（9.2秒の拍＝低い音が入る所）へ拍をそろえてつなぐ。盛り上がり（38秒〜）は使わない。
使い方: bgm_bed.py <長さ秒> <出力.wav>   （元 = tools/brand/reel_bgm.m4a・オーナーのオリジナル）"""
import sys,subprocess,os,numpy as np,wave
L=float(sys.argv[1]);O=sys.argv[2];R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SR=48000
src=os.path.join(R,'tools/brand/reel_bgm.m4a')
raw=subprocess.run(['ffmpeg','-loglevel','error','-i',src,'-f','f32le','-ac','2','-ar',str(SR),'pipe:1'],capture_output=True,check=True).stdout
x=np.frombuffer(raw,dtype=np.float32).reshape(-1,2).copy()
assert len(x)>SR*60,'曲が読めない'
S=lambda t:int(round(t*SR))
A0,A1=0.19,38.100   # 頭〜盛り上がりの直前の拍
B0=9.190            # 低い音が入る拍（A1 と同じ位置の拍）
need=S(L+1)
out=[x[S(A0):S(A1)]]
got=len(out[0])
while got<need:      # 長い時は 9.19〜38.10 を何回でも（同じつなぎ目）
    seg=x[S(B0):S(A1)];out.append(seg);got+=len(seg)
y=np.concatenate(out)[:need]
# つなぎ目：出る方は 60ms で消え、入る方は 15ms で立ち上がる（拍の頭の音は消さない）
fo,fi=S(0.06),S(0.015);pos=len(out[0])
while pos<len(y):
    tail=x[S(A1):S(A1)+fo]*np.linspace(1,0,fo)[:,None]
    n=min(fo,len(y)-pos);y[pos:pos+n]+=tail[:n]
    m=min(fi,len(y)-pos);y[pos:pos+m]*=np.linspace(0,1,fi)[:m,None]**0.5+0  # 軽い立ち上がり
    pos+=S(A1)-S(B0)
tmp=O+'.raw.wav'
with wave.open(tmp,'wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(y,-1,1)*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-loglevel','error','-y','-i',tmp,'-af','loudnorm=I=-20:TP=-1.5:LRA=9','-ar','48000',O],check=True);os.remove(tmp)
