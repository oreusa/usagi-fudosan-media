#!/bin/bash
# HF の映像（声＋めくりの音）に曲を足す：曲は loudnorm -17、声が出ると下がる（好古園と同じ）
set -e; cd "$(dirname "$0")"; R=/home/user/usagi-fudosan-media
END=$(python3 -c "import json;print(json.load(open('times.json'))['END'])")
git -C $R show bae326f:tools/brand/reel_bgm.m4a > bgm.m4a 2>/dev/null || cp $R/tools/brand/reel_bgm.m4a bgm.m4a
ffmpeg -loglevel error -y -ss 0.2 -i bgm.m4a -t $(python3 -c "print($END+1)") -af loudnorm=I=-17:TP=-1.5:LRA=11 -ar 48000 bgm.wav
ffmpeg -loglevel error -y -i hf.mp4 -i bgm.wav -filter_complex "[0:a]aresample=48000,asplit=2[vo][sc];[1:a]afade=t=in:d=0.4,afade=t=out:st=$(python3 -c "print($END-1.6)"):d=1.6[bg0];[bg0][sc]sidechaincompress=threshold=0.02:ratio=5:attack=40:release=500:makeup=1[bg];[bg][vo]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]" -map 0:v -map "[a]" -t $END -c:v copy -c:a aac -b:a 256k -movflags +faststart ishiyama-n.mp4
ffmpeg -loglevel error -y -i ishiyama-n.mp4 -c:v libx264 -preset slow -crf 24 -c:a aac -b:a 160k -movflags +faststart preview.mp4
ls -la ishiyama-n.mp4 preview.mp4
