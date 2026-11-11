"""この場所（関西）だけの決まり。make.py は関西・関東で同じ物を使い、違いはこのファイルだけに書く。"""
KICKER = ('関西の不動産屋が', '街の調査で見つけた、おでかけリスト')   # 表紙の上の2行（10/28 オーナー決定）
ACC = '#B5532F'                          # さし色
PREFS = ['osaka', 'kyoto', 'hyogo', 'nara', 'shiga', 'wakayama']
BGM = 'tools/brand/reel_bgm.m4a'
VOICE_CREDIT = 'VOICEVOX:もち子(cv 明日葉よもぎ)'


def pref(spec):
    return spec['pref']


def xy(lat, lon):
    """地図の座標（mapsvg の関西）: 兵庫・滋賀の端で合わせた一次式"""
    return 19.72 * lon - 2438.3, 255.75 + (35.67 - lat) * 23.36


def shot_js(root, spec, work):
    """リストの画面（府県のタブを押した所）を list.png に撮る node の文"""
    return f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:390,height:844}},deviceScaleFactor:2}});
await p.route('**/c',r=>r.fulfill({{status:204}}));await p.goto('file://{root}/links/index.html');await p.waitForTimeout(1200);
for(const x of await p.$$('button')){{if((await x.textContent()).trim()=='{spec['tab']}'){{await x.click();break;}}}}
await p.waitForTimeout(600);await p.screenshot({{path:'{work}/list.png',fullPage:true}});await b.close()}})();"""
