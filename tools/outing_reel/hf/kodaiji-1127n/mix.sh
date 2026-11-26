#!/bin/bash
# HF の映像（声＋めくりの音）に曲を足す：曲は loudnorm -21（ゆっくり版B）、声が出ると下がる（好古園と同じ）
set -e; cd "$(dirname "$0")"; R=/home/user/usagi-fudosan-media
END=$(python3 -c "import json;print(json.load(open('times.json'))['END'])")
bash $R/tools/brand/bgm_bed.sh $END bgm.wav   # 11/26〜 ゆっくり版B・最後の22秒は静かな所
ffmpeg -loglevel error -y -i hf.mp4 -i bgm.wav -filter_complex "[0:a]aresample=48000,asplit=2[vo][sc];[1:a]afade=t=in:d=0.4,afade=t=out:st=$(python3 -c "print($END-1.6)"):d=1.6[bg0];[bg0][sc]sidechaincompress=threshold=0.02:ratio=5:attack=40:release=900:makeup=1[bg];[bg][vo]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]" -map 0:v -map "[a]" -t $END -c:v copy -c:a aac -b:a 256k -movflags +faststart kodaiji-n.mp4
ffmpeg -loglevel error -y -i kodaiji-n.mp4 -c:v libx264 -preset slow -crf 24 -c:a aac -b:a 160k -movflags +faststart preview.mp4
ls -la kodaiji-n.mp4 preview.mp4
