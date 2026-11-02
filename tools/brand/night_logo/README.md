夜のロゴ（links/assets/logo-s-night.png）の作り方。11/2 オーナー「燈の方が綺麗」「雑い、綺麗にやれ」を受けた形。

python3 tools/brand/night_logo/build.py links/assets/logo.png links/assets/logo-s-night.png

- 600pxの元絵を使う（180pxを2倍にしない＝ぼやけない）。顔の半透明のざらつきは消して、燈と同じく顔は銀
- 髪の中の白い線（透けているすき間）は360pxで場所を決め、1200pxで髪の下に白を敷いてから360pxに縮める（ふちがなめらか）
- 顔に接する広いすき間（おでこ・首）と、小さいかけらは白にしない
- 光は glow.py（銀の丸 (186,187,190)、金の枠だけ光らせる、細め・芯は少し金色）
- 作り直したら night.js の logo の ?v= と、各ページの night.js?v= を1つ上げる
燈は SC=3.3 で site/logo-s.png から glow.py（髪の白は入れない）。night.js が夜のとき logo-s.png を logo-s-night.png に替える。
