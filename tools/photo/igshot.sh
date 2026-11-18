#!/bin/bash
# インスタ投稿の埋め込みを写真に撮る（合っているか人が見る用）。igshot.sh 表.tsv 出す先
set -u; mkdir -p "$2"; i=0
while IFS=$'\t' read -r n c; do
  [ -z "$c" ] && continue; i=$((i+1)); f=$(printf "%03d" $i)
  echo "$f	$n	$c" >> "$2/list.tsv"
  timeout 60 npx -y playwright@1.48.2 screenshot --channel=chrome --wait-for-timeout=5000 --viewport-size=400,700 "https://www.instagram.com/$c/embed/captioned/" "$2/$f.png" >/dev/null 2>&1 || echo "$f fail"
done < "$1"
