夜のロゴ（links/assets/logo-s-night.png）の作り方。11/2 オーナーとそろえた形。
1. python3 gap.py links/assets/logo-s.png g.png 3   … 2倍にして、髪の中の白い線（透けている所）を白に。顔・耳はそのまま
2. NORESIZE=1 SC=2 python3 glow.py g.png out.png prev.png … 銀の丸 (186,187,190)、金の枠だけ光らせる
3. cp out.png links/assets/logo-s-night.png
燈は SC=3.3 で site/logo-s.png から（髪の白は入れない）。night.js が夜のとき logo-s.png を logo-s-night.png に替える。
