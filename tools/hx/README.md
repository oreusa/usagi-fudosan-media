# 激変版（?mihon=2）の部品
- links/assets/hitech2.js：本体（関東 akari site/assets/hitech2.js は同じ物を写す）。night.js が tn_mihon=2 の人だけ読む。
- links/assets/hx-lib.js：Embla Carousel・@formkit/auto-animate・thumbhash を1つに（MIT）。作り直し：
  `npm i embla-carousel @formkit/auto-animate thumbhash budoux esbuild && npx esbuild tools/hx/entry.js --bundle --minify --format=iife --target=es2017 --outfile=links/assets/hx-lib.js`
- links/assets/hx-bx.js：BudouX（Apache-2.0・iPhone の日本語の改行）。`npx esbuild tools/hx/bx.js --bundle --minify --format=iife --outfile=links/assets/hx-bx.js`
- links/assets/pswp/：PhotoSwipe 5.4.4（MIT）
- links/assets/phh.json：写真のぼかし色（tools/hx/phh.py・毎朝 link-stats）
- アイコン：lucide（ISC）の線をそのまま hitech2.js に
