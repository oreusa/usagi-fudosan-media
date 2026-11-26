#!/bin/bash
# 11/26 owner「最後になっていくと壮大に・プロフィール紹介くらいには騒がしい」→
# ゆっくり版Bの「静かな落ち着く所」(110〜134秒・低音が抜ける所) を最後の22秒に置く。
# 使い方: bgm_bed.sh <長さ秒> <出力.wav>
set -e; R=$(cd "$(dirname "$0")/../.." && pwd); L=$1; O=$2
SRC=$R/tools/brand/reel_bgm_shizuka.m4a
A=$(python3 -c "print(round($L-22+2,2))"); E=$(python3 -c "print(round($L+1,2))")
ffmpeg -loglevel error -y -ss 0.2 -t $A -i $SRC -ss 110 -t 24 -i $SRC -filter_complex \
 "[0:a][1:a]acrossfade=d=2:c1=tri:c2=tri,acompressor=threshold=0.08:ratio=3:attack=200:release=1500,loudnorm=I=-21:TP=-1.5:LRA=7,atrim=0:$E[a]" \
 -map "[a]" -ar 48000 $O
