"""新しいHP：読む・入れるページ（links/shin/doc.js が出す）。11/19 23時 owner「文字列おかしい」「その他も本気でやり直せ」。
前のページ（links/uru.html・ikura.html …）に頭をかぶせるのをやめ、中身をこの土台の部品で書き直す。
前のページは消さない（元のファイルは毎朝ほかの機械が作る。いくら？の数字と計算はそこから読む）。"""
import html, json, os, re

E = html.escape
NAV = [{'t': '街をさがす', 'ic': 'find', 'href': '/fudosan-list'}, {'t': 'ランキング', 'ic': 'rank', 'href': '/ranking'},
       {'t': '売りたい', 'ic': 'sell', 'href': '/uru'}, {'t': 'いくら？', 'ic': 'yen', 'href': '/ikura'}]
MENU = [['家と土地の相場', '/fudosan-list'], ['まちランキング', '/ranking'], ['家を売る前に', '/uru'], ['いくらで売れる？', '/ikura'], ['実家・空き家', '/jikka/'], ['地価ランキング', '/chika-kansai']]
FOOT = '数字はどれも国・府県・不動産流通機構などの公式の発表です。街の平均で、1軒ずつの値段ではありません。<br>「値段を聞く」から先は、提携する不動産会社の査定のご案内です。'
MOU = '/moushikomi?lite=1&want=%E6%9F%BB%E5%AE%9A%E3%81%97%E3%81%A6%E3%81%BB%E3%81%97%E3%81%84'


def cfg(cur, desc):
    return {'nav': [dict(n, cur=1) if n['href'] == cur else n for n in NAV],
            'menu': {'k': 'Home & Land', 'items': [[t, u] + ([1] if u == cur else []) for t, u in MENU]}, 'foot': FOOT, 'desc': desc}


def acc(rows):
    return ''.join(f'<details><summary>{E(q)}</summary><div class="ddd">{a}</div></details>' for q, a in rows)


def uru(L):
    t = open(os.path.join(L, 'uru.html'), encoding='utf-8').read()
    det = re.findall(r'<details>\s*<summary>(.*?)</summary>(.*?)</details>', t, re.S)
    det = [(html.unescape(re.sub('<[^>]+>', '', q)).strip(), a.strip()) for q, a in det if 'class="fq"' not in a]
    know = [d for d in det if not d[0].endswith('？')]
    faq = [d for d in det if d[0].endswith('？')]
    know = [(q, a.replace('class="cmp"', '')) for q, a in know]
    body = (
        '<section class="dsec"><span class="dno">1</span><h2>街の相場を見る</h2><p>あなたの街で、実際に売れた家の値段（国の資料）を見ます。</p>'
        '<input class="din" id="tq" type="search" placeholder="街の名前（例：寝屋川市）" autocomplete="off" aria-label="街の名前で探す"><div id="tqo"></div>'
        '<a class="dbtn2" href="/ikura" data-k="売る前に｜いくらで売れる">種類と広さから、売れそうな値段の目安を出す（30秒）</a></section>'
        '<section class="dsec"><span class="dno">2</span><h2>値段を聞く（無料）</h2><p>「いくらで売れそうか」を、このサイトから聞けます。売るか決めていなくても大丈夫です。</p>'
        f'<a class="dbtn" href="{MOU}" data-k="売る前に｜申し込む">いくらで売れそうか聞く<small>無料・名字だけでOK・約1分</small></a></section>'
        '<section class="dsec"><span class="dno">3</span><h2>大事なことを知っておく</h2>' + acc(know) + '</section>'
        + ('<section class="dsec"><h2>よくある質問</h2>' + acc(faq) + '</section>' if faq else '')
        + '<section class="dsec"><h2>あわせて見る</h2><div class="drel"><a href="/fudosan-list">家と土地の相場<small>関西の街ごとの値段</small></a><a href="/jikka/">実家・空き家<small>売る・片付ける・解体する前に</small></a>'
        '<a href="/kaitai-ranking">解体の補助金<small>市ごとの上限と受付</small></a><a href="/chika-kansai">地価ランキング<small>住宅地の1年の動き</small></a></div></section>')
    return {'h1': '家を売る前に', 'sub': 'この3つの順で進めると、迷いません。', 'html': body}


def ikura(L):
    t = open(os.path.join(L, 'ikura.html'), encoding='utf-8').read()
    js = [m.group(1) for m in re.finditer(r'<script>(.*?)</script>', t, re.S) if 'var D=' in m.group(1)][0]
    sub = re.search(r'<p class="sub">(.*?)</p>', t, re.S).group(1).replace('<br>', '')
    note = re.search(r'<p class="note">(.*?)</p>', t, re.S).group(1)
    js = js.replace('r.style.display="none"', 'r.style.display="none"').replace('var D=', 'var D=', 1)
    body = (
        '<section class="dsec"><div class="dstep"><p class="dq"><i>1</i>お家の種類</p><div class="dchs" id="ty"><button type="button" data-v="m" aria-pressed="true">マンション</button>'
        '<button type="button" data-v="k" aria-pressed="false">一戸建て</button><button type="button" data-v="t" aria-pressed="false">土地</button></div></div>'
        '<div class="dstep"><p class="dq"><i>2</i>お家のある市区</p><select class="din" id="ci" aria-label="市区"></select><p class="dhint" id="cn"></p></div>'
        '<div class="dstep"><p class="dq"><i>3</i><b id="al" style="font-weight:600">専有面積</b></p><div class="drow"><input class="din" id="ar" type="number" inputmode="decimal" min="10" max="2000" placeholder="例 70"><span>㎡</span></div>'
        '<p class="dhint" id="ah">分からなければ空のままで大丈夫です（この街の平均で出します）。</p></div>'
        '<div class="dres" id="res" aria-live="polite"><p class="dlb" id="rl"></p><div class="dbig" id="rb"></div><p class="dlb">目安の幅（実際の値段は、お家の状態・駅からの近さ・築年で上下します）</p><ul id="ru"></ul>'
        '<a class="dbtn" id="go" href="/moushikomi?lite=1" data-k="いくら｜正確な値段を聞く">このお家の正確な値段を聞く（無料）<small>売るか決めていなくても大丈夫です。メールだけなら、お電話はしません</small></a></div></section>'
        f'<p class="dnote">{note}</p>'
        '<section class="dsec"><h2>あわせて見る</h2><div class="drel"><a href="/uru">家を売る前に<small>3つの順で迷わない</small></a><a href="/fudosan-list">家と土地の相場<small>関西の街ごとの値段</small></a></div></section>')
    return {'h1': 'お家はいくらで売れる？', 'sub': sub, 'html': body, 'js': js}


def build(write, L, R, URL):
    for name, url, title, fn, desc in [
        ('uru', '/uru', '家を売る前に｜相場を見る・値段を聞く・大事なこと（関西）｜TOWN NOTE', uru,
         '関西で家を売る前に、街の相場を見る・無料で値段を聞く・知っておく大事なことを、3つの順でまとめました。'),
        ('ikura', '/ikura', 'お家はいくらで売れる？｜関西183の市区の実際に売れた値段から30秒で目安｜TOWN NOTE', ikura,
         '関西183の市区で、去年実際に売れた値段から、マンション・一戸建て・土地の売れそうな値段の目安を30秒で出します。無料・名前も要りません。')]:
        try:
            d = fn(L)
        except Exception as e:
            print('docs: 作れなかった', name, repr(e)); continue
        URL[name] = url
        write(name, title, cfg(url, desc), d, js='doc')
