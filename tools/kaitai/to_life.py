"""関西の費用ページ links/kaitai.html を、関東 LIFE NOTE 用に写す（11/11。オーナー「直したら関西と関東の両方」）。
値段は全国の目安なので中身は同じ。名前・アドレス・対象の都県・部品の版だけ替える。
使い方：python3 tools/kaitai/build.py の後に  python3 tools/kaitai/to_life.py ../akari-auto  → akari-auto/site/kaitai.html
（関西の費用ページを直したら、必ずこれも回して akari に入れる）"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
dst = os.path.join(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "akari-auto"), "site", "kaitai.html")
s = open(os.path.join(ROOT, "links", "kaitai.html"), encoding="utf-8").read()
PAIRS = (
    # 関東の側の部品の名前と版（akari-auto site/moushikomi.html と同じ）
    ("https://townnote.pages.dev/assets/ogp.png", "https://lifenote-kanto.pages.dev/og-v10.png"),
    ('href="assets/ogp.png"', 'href="/logo-s.png"'),
    ('src="assets/logo-s.png?v=2"', 'src="/logo-s.png"'),
    ('src="assets/night.js?v=25"', 'src="/assets/night.js?v=18"'),
    ('src="assets/menu.js?v=49"', 'src="/assets/menu.js?v=46"'),
    ('src="assets/v2sub.js?v=12"', 'src="/assets/v2sub.js?v=17"'),
    ("townnote\\.pages", "lifenote-kanto\\.pages"),
    ("townnote.pages.dev", "lifenote-kanto.pages.dev"),
    ("TOWN NOTE", "LIFE NOTE"),
    ("関西（大阪・京都・兵庫・奈良・滋賀・和歌山）", "関東（東京・神奈川・埼玉・千葉・茨城・栃木・群馬）"),
    ("関西不動産リスト", "関東不動産リスト"),
    ("関西の無料", "関東の無料"),
    ("（関西）", "（関東）"),
)
# 市の補助の表：関西の市の段を外し、関東の市区（tools/kaitai/kanto_hojo.tsv。公式ページで月が確かめた行だけ）があれば、同じ形で入れる
import html as _h
_kp = os.path.join(HERE, "kanto_hojo.tsv")
_rows = [l.rstrip("\n").split("\t") for l in open(_kp, encoding="utf-8") if l.strip() and not l.startswith("#")] if os.path.exists(_kp) else []
_rows = [r for r in _rows if len(r) == 5]
_E = _h.escape
_kh = ""
if _rows:
    _kh = ('<section id="hojo" class="ps" style="--c:#4F7BA8"><h2>解体の補助がある市区</h2><p class="rk-sub">公式ページで確かめられた市区だけ・順に足します</p>'
           + "".join(f'<div class="kt-hj"><b>{_E(c)}</b>' + (f'<em class="{"x" if st in ("受付停止", "受付終了") else ""}">{_E(st)}</em>' if st else "")
                     + f'<p>{_E(tx)}</p><a href="{_E(u)}" target="_blank" rel="noopener" data-k="費用｜市の補助｜{_E(c)}">{_E(c)}の公式ページ（{_E(d)}に確認） →</a></div>' for c, tx, st, u, d in _rows)
           + '<p class="kt-n">受付・条件・上限は変わります。交付が決まる前に契約や工事を始めると、対象外になる市区が多いので、見積りの前に公式ページで確かめてください。ここに無い市区も、役所の「空き家」の窓口で聞けます。</p></section>')
s, _n = re.subn(r"<!--hojo-->.*?<!--/hojo-->", lambda m: _kh, s, flags=re.S)
if _n != 1:
    sys.exit("市の補助の段が見つかりません（to_life.py を直す）")
for a, b in PAIRS:
    if a not in s:
        sys.exit("元のページに見つかりません（to_life.py を直す）: " + a)
    s = s.replace(a, b)
bad = re.findall(r"[^\n]{0,12}(?:関西|近畿|大阪|神戸|townnote|TOWN|assets/ogp|\"assets/)[^\n]{0,12}", s)
if bad:
    sys.exit("関西の言葉・部品が残っています: " + " / ".join(bad[:5]))
open(dst, "w", encoding="utf-8").write(s)
print("書いた:", dst, len(s))
