"""リールの数字の答え合わせ（11/16 月。オーナー「リールをもっと完璧に。数字間違わないとか気をつけてほしい」）。
声の読み（yomi.py）と同じく、1つでも合わなければ動画を作らずに止まる。

1. 曜日：台本の「11.14」「SAT」や「11/14(土)」「11月14日（土）」の曜日を、暦で計算して合わせる（spec の date の年から決める）。
2. 数字の出どころ：spec に "facts": [{"q": "公式ページの文そのまま", "url": "公式ページ"}, …] を書く。
   声・絵本の字・表紙・案内・キャプションに出る数字（33・40・21:30・12/6 など）は、どれかの q の中に同じ数字が無ければ止まる。
   = 公式の文から写した数字しか使えない（覚えていた数字・計算した数字・別の年の数字を入れない）。
3. q が本当に公式ページにあるか：url を開いて、q の文がページの中にあるかを見る（機械＝GitHub Actions の時。手元では --offline で飛ばす）。
"facts" が無い spec（前の台本・関東の燈の台本）は、1 の曜日だけ見て、2・3 は「facts なし」と書くだけ（止めない）。
使い方：python3 tools/outing_reel/factcheck.py ig/reels/<名前>.json [--offline]
"""
import datetime, html, json, re, sys, unicodedata, urllib.request

DOW_EN = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
DOW_JA = '月火水木金土日'
SKIP_TEXT = {'ehon5', 'list_caption', 'date_title_size', 'map_tag', 'corner'}   # 決まった文・英字の飾り（数字が無い）


def norm(s):
    s = unicodedata.normalize('NFKC', str(s))
    return s.replace('〜', '~').replace('～', '~').replace('－', '-')


def strings(spec):
    """数字を見る文：声・絵本の字（text の文字の欄）・キャプション（ハッシュタグの行は除く）。"""
    out = []
    for i, v in enumerate(spec.get('voice', [])): out.append((f'voice {i+1}行目', v))
    def walk(k, v):
        if isinstance(v, str): out.append((f'text.{k}', v))
        elif isinstance(v, list):
            for x in v: walk(k, x)
    for k, v in (spec.get('text') or {}).items():
        if k not in SKIP_TEXT: walk(k, v)
    for ln in (spec.get('caption') or '').split('\n'):
        if ln.startswith('#') or ln.startswith('声：'): continue
        out.append(('caption', ln))
    return out


def year_for(month, base):
    """台本の日付（11.14 など）の年：spec の日付より4か月以上前の月なら翌年（12月の台本の 3.14 → 翌年）。"""
    y = base.year
    if month < base.month - 4: y += 1
    return y


def check_dow(spec):
    bad = []
    base = datetime.date.fromisoformat(spec.get('date', '')[:10]) if spec.get('date') else datetime.date.today()
    def one(where, m, d, w, y=None):
        try: day = datetime.date(int(y) if y else year_for(int(m), base), int(m), int(d))
        except ValueError: bad.append(f'{where}：{m}月{d}日 は暦に無い日'); return
        ok = DOW_EN[day.weekday()] if w.isascii() else DOW_JA[day.weekday()]
        if w[:3].upper() != ok and w[0] != ok: bad.append(f'{where}：{day.isoformat()} は {ok}（台本は {w}）')
    T = spec.get('text') or {}
    for key in ('date', 'ehon_night'):
        a = T.get(key) or []
        for i in range(len(a) - 1):
            m = re.fullmatch(r'(\d{1,2})\.(\d{1,2})', norm(a[i]))
            if m and re.fullmatch(r'[A-Z]{3}', norm(a[i + 1])): one(f'text.{key}', m[1], m[2], norm(a[i + 1]))
    for where, s in strings(spec):
        s = norm(s)
        for m in re.finditer(r'(?:(\d{4})[/年])?(\d{1,2})[/月](\d{1,2})日?\s*[(（]([月火水木金土日])', s):
            one(where, m[2], m[3], m[4], m[1])
    return bad


def nums(s):
    return {str(int(x)) for x in re.findall(r'\d+', norm(s))}


def check_facts(spec, offline=False):
    facts = spec.get('facts')
    if not facts: return [], ['facts なし（数字の出どころは見ていない）']
    bad, note = [], []
    have = set()
    for f in facts: have |= nums(f.get('q', ''))
    for where, s in strings(spec):
        miss = sorted(nums(s) - have, key=int)
        if miss: bad.append(f'{where}「{s}」の数字 {"・".join(miss)} が facts の公式の文に無い（公式の文を facts に足すか、数字を直す）')
    if offline: return bad, note + ['公式ページは開いていない（--offline）']
    pages = {}
    for f in facts:
        u = f.get('url', '')
        if u not in pages:
            try:
                req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (reel factcheck)'})
                raw = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
                txt = html.unescape(re.sub(r'<[^>]+>', '', re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', '', raw)))
                pages[u] = re.sub(r'\s+', '', norm(txt))
            except Exception as e:
                pages[u] = None; bad.append(f'公式ページが開けない：{u}（{e}）')
        p = pages[u]
        if p is not None and re.sub(r'\s+', '', norm(f.get('q', ''))) not in p:
            bad.append(f'公式ページに q の文が無い（写し間違いか、ページが変わった）：{u}\n   q「{f.get("q")}」')
    return bad, note


def run(spec, offline=False):
    bad = check_dow(spec)
    b2, note = check_facts(spec, offline)
    return bad + b2, note


if __name__ == '__main__':
    spec = json.load(open(sys.argv[1], encoding='utf-8'))
    bad, note = run(spec, '--offline' in sys.argv)
    for n in note: print('数字の答え合わせ：' + n)
    if bad:
        print('数字の答え合わせで止めた（' + str(len(bad)) + '件）：')
        for b in bad: print(' - ' + b)
        sys.exit(1)
    print('数字の答え合わせ：OK')
