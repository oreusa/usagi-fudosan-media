#!/bin/bash
# HF の映像（声＋めくりの音）に曲を足す：曲は loudnorm -20（元の速さ・盛り上がりは使わない）、声が出ると下がる（好古園と同じ）
set -e; cd "$(dirname "$0")"; R=/home/user/usagi-fudosan-media
END=$(python3 -c "import json;print(json.load(open('times.json'))['END'])")
python3 $R/tools/brand/bgm_bed.py $END bgm.wav   # いつもの曲（11/27 owner：新しい曲2つは「どっちもなし」）
python3 ../voiceonly.py . $END voice.wav
ffmpeg -loglevel error -y -i hf.mp4 -i bgm.wav -i voice.wav -filter_complex "[2:a]aresample=48000,asplit=2[vo][sc];[1:a]afade=t=in:d=0.4,afade=t=out:st=$(python3 -c "print($END-1.6)"):d=1.6[bg0];[bg0]volume=0.62[bg];[sc]anullsink;[bg][vo]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]" -map 0:v -map "[a]" -t $END -c:v copy -c:a aac -b:a 256k -movflags +faststart ootaguro-n.mp4
ffmpeg -loglevel error -y -i ootaguro-n.mp4 -c:v libx264 -preset slow -crf 24 -c:a aac -b:a 160k -movflags +faststart preview.mp4
ls -la ootaguro-n.mp4 preview.mp4
