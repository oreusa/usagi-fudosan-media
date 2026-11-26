#!/usr/bin/env python3
"""リールの曲の下地（11/27〜）。owner「遅くしないで」「切るのは好きじゃない」「元の曲も最後の方がうるさい」。
元の速さのまま、切らずに頭から流す。元の曲は38秒あたりから盛り上がるので、30秒目から最後へ向けて
曲だけ少しずつ小さく（最後は -8dB）し、高い音も少しずつやわらかくする（騒がしさを抑える）。
使い方: bgm_bed.py <長さ秒> <出力.wav>   （元 = tools/brand/reel_bgm.m4a・オーナーのオリジナル）"""
import sys,subprocess,os
L=float(sys.argv[1]);O=sys.argv[2];R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src=os.path.join(R,'tools/brand/reel_bgm.m4a');F=max(5.0,L-32)
af=(f"loudnorm=I=-20:TP=-1.5:LRA=11,"
    f"volume='if(lt(t,30),1,pow(10,-8*min(1,(t-30)/{F})/20))':eval=frame,"
    f"treble=g=-4:f=3000:enable='gte(t,34)'")
subprocess.run(['ffmpeg','-loglevel','error','-y','-ss','0.2','-t',str(L+1),'-i',src,'-af',af,'-ar','48000',O],check=True)
