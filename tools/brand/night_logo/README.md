夜のロゴ（links/assets/logo-s-night.png）の作り方。11/2 オーナー「燈の方が綺麗」→ くっきり版にした。
1. python3 prep.py links/assets/logo.png p.png … 600pxの元絵から360pxに縮める（180pxを2倍にしない＝ぼやけない）。顔の半透明のざらつきを消す（燈と同じく顔は銀）
2. NORESIZE=1 GB=0.9 python3 gap.py p.png g.png 3 … 髪の中の白い線（透けている所）を白に。線のふちをなめらかに。顔に接する広いすき間（おでこ・首）は白にしない（11/2 オーナー「消して」。TH=3 が既定）
3. NORESIZE=1 SC=1.4 GK=1.1 CORE=255,224,165 python3 glow.py g.png out.png prev.png … 銀の丸 (186,187,190)、金の枠だけ光らせる。光は細め、芯は少し金色（燈に近づけた）
4. cp out.png links/assets/logo-s-night.png（night.js の logo の ?v= と、各ページの night.js?v= を1つ上げる）
燈は SC=3.3 で site/logo-s.png から（髪の白は入れない）。night.js が夜のとき logo-s.png を logo-s-night.png に替える。
