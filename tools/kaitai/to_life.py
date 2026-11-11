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
    ('src="assets/night.js?v=23"', 'src="/assets/night.js?v=18"'),
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
# 市の補助の表は関西の市だけ → 関東の写しからは外す（関東の市を公式で確かめたら、関東用の表を別に入れる）
s, _n = re.subn(r"<!--hojo-->.*?<!--/hojo-->", "", s, flags=re.S)
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
