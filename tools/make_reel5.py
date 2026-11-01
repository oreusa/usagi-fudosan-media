"""うさぎちゃん不動産 リール・画像ジェネレーター v5（10/21 オーナー「画像もこのサイトに合わせて」）

おでかけリストのページ（links/index.html）と同じ見た目にそろえる：
  ・生成り色の地（#FAF8F5）に、うすい丸（桃・水色・若草・桜）
  ・白いパネルに細い線、パネルの上に茶色の線
  ・見出しは Shippori Mincho、本文は Zen Kaku Gothic New の太字、英字と番号は Jost
  ・矢印は細い線の「→」
ロゴの決まりは v4 と同じ（表紙は右下だけ、2枚目からは上に小さく。色は変えない）。
リールの操作ボタンが重なるので、下420px は空ける。
spec の形・使い方は make_reel4.py と同じ（tools/specs4/ をそのまま使える）。
使い方: python3 make_reel5.py <spec.json> <outdir> [--images-only]
"""
import html, os, sys

import make_reel4 as m

FONT, LOGO, tx = m.FONT, m.LOGO, m.tx
BG, INK, SUB, ACC, LINE, PANEL = "#FAF8F5", "#2B2622", "#7A6E64", "#A07E66", "#E3D9CE", "#FFFFFF"

CSS = f"""
@font-face {{ font-family: G; src: url("file://{FONT}/ZenKakuGothicNew-Medium.ttf"); font-weight: 500; }}
@font-face {{ font-family: G; src: url("file://{FONT}/ZenKakuGothicNew-Bold.ttf"); font-weight: 700; }}
@font-face {{ font-family: G; src: url("file://{FONT}/ZenKakuGothicNew-Black.ttf"); font-weight: 900; }}
@font-face {{ font-family: M; src: url("file://{FONT}/ShipporiMincho-SemiBold.ttf"); font-weight: 600; }}
@font-face {{ font-family: M; src: url("file://{FONT}/ShipporiMincho-Bold.ttf"); font-weight: 700; }}
@font-face {{ font-family: J; src: url("file://{FONT}/Jost-VF.ttf"); font-weight: 100 900; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ width: 1080px; height: 1920px; font-family: G; color: {INK}; position: relative; overflow: hidden;
  background: radial-gradient(circle at 8% 9%, #F8E1CF 0 230px, transparent 231px),
              radial-gradient(circle at 96% 4%, #DCEAF3 0 170px, transparent 171px),
              radial-gradient(circle at 100% 70%, #E2EBD9 0 190px, transparent 191px),
              radial-gradient(circle at 0% 62%, #F5DFE2 0 120px, transparent 121px), {BG};
  font-feature-settings: "palt"; line-break: strict; word-break: keep-all; overflow-wrap: anywhere; -webkit-font-smoothing: antialiased; }}
.brand {{ position: absolute; left: 0; right: 0; top: 150px; text-align: center; font-family: J; font-size: 28px; font-weight: 400;
          letter-spacing: .34em; color: {SUB}; }}
.brand img {{ display: block; height: 96px; margin: 0 auto 18px; }}
.strip {{ position: absolute; left: 0; right: 0; top: 330px; display: flex; align-items: center; justify-content: center; gap: 26px;
          font-family: M; font-weight: 600; font-size: 34px; letter-spacing: .18em; color: {ACC}; }}
.strip:before, .strip:after {{ content: ""; width: 90px; height: 2px; background: {ACC}; opacity: .55; }}
.panel {{ position: absolute; left: 90px; right: 90px; background: {PANEL}; border: 2px solid {LINE}; border-top: 7px solid {ACC};
          box-shadow: 0 6px 24px rgba(60,45,35,.05); }}
.hl {{ background: linear-gradient(transparent 64%, #EFE1D2 64%); }}
.pk {{ background: linear-gradient(transparent 64%, #F4DCDD 64%); }}
.next {{ position: absolute; right: 120px; top: 1600px; display: flex; align-items: center; gap: 20px; font-family: J; font-weight: 400;
         font-size: 40px; letter-spacing: .2em; color: {ACC}; }}
.page {{ position: absolute; left: 120px; top: 1606px; font-family: J; font-size: 32px; letter-spacing: .14em; color: {SUB}; }}
/* 表紙 */
.cv {{ top: 430px; height: 1060px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 0 60px 90px; }}
.cv-b {{ border: 2px solid {ACC}; color: {ACC}; font-size: 38px; font-weight: 700; padding: 10px 34px; letter-spacing: .14em; }}
.cv-k {{ margin-top: 44px; font-size: 46px; font-weight: 700; letter-spacing: .1em; color: {SUB}; }}
.cv-t {{ margin-top: 30px; font-family: M; font-weight: 700; font-size: 100px; line-height: 1.34; letter-spacing: .06em; }}
.cv-line {{ width: 120px; height: 3px; background: {ACC}; margin: 44px auto 0; }}
.cv-c {{ margin-top: 70px; font-size: 52px; font-weight: 700; letter-spacing: .08em; }}
.cv-c b {{ font-family: J; font-weight: 400; font-size: 120px; color: {ACC}; margin-right: 10px; vertical-align: -6px; }}
.cv-s {{ margin-top: 36px; font-size: 34px; font-weight: 500; color: {SUB}; letter-spacing: .12em; }}
.cv-logo {{ position: absolute; right: 60px; bottom: 50px; height: 130px; }}
/* ポイントの枚 */
.it {{ top: 430px; height: 1080px; padding: 64px 76px 0; }}
.no {{ font-family: J; font-weight: 300; font-size: 84px; color: {ACC}; letter-spacing: .04em; line-height: 1; }}
.ttl {{ margin-top: 18px; font-family: M; font-weight: 700; font-size: 74px; line-height: 1.35; letter-spacing: .08em; }}
.desc {{ margin-top: 34px; padding-top: 34px; border-top: 2px solid {LINE}; font-size: 44px; font-weight: 700; line-height: 1.75; letter-spacing: .06em; }}
.checks {{ margin-top: 34px; display: flex; flex-direction: column; gap: 22px; }}
.ck {{ display: flex; gap: 22px; align-items: center; font-size: 40px; font-weight: 700; letter-spacing: .05em; }}
.ck svg {{ flex: none; }}
.tip {{ margin-top: 40px; background: #F7F1EA; border-left: 6px solid {ACC};
        padding: 34px 42px; font-size: 38px; font-weight: 700; line-height: 1.75; letter-spacing: .05em; }}
.tip i {{ display: block; font-style: normal; font-family: J; font-size: 26px; font-weight: 500; letter-spacing: .3em; color: {ACC}; margin-bottom: 8px; }}
/* 最後の枚 */
.sv {{ top: 430px; height: 1080px; padding: 80px 76px 0; }}
.sv h2 {{ font-family: M; font-weight: 700; font-size: 80px; line-height: 1.45; letter-spacing: .08em; }}
.sv .body {{ margin-top: 44px; padding-top: 40px; border-top: 2px solid {LINE}; font-size: 44px; font-weight: 700; line-height: 1.85; letter-spacing: .05em; }}
.sv .cta {{ margin-top: 48px; border: 2px solid {ACC}; padding: 38px 44px; display: flex; align-items: center; justify-content: space-between; gap: 24px; }}
.sv .cta .l1 {{ font-size: 36px; font-weight: 500; line-height: 1.6; color: {SUB}; }}
.sv .cta .l2 {{ font-size: 44px; font-weight: 900; color: {INK}; margin-top: 8px; letter-spacing: .04em; }}
.sv .src {{ margin-top: 36px; font-size: 26px; font-weight: 500; color: {SUB}; line-height: 1.6; }}
.sh {{ top: 430px; height: 1080px; padding: 64px 76px 0; text-align: center; }}
.sh h2 {{ font-family: M; font-weight: 700; font-size: 72px; line-height: 1.4; letter-spacing: .08em; }}
.sh .sub {{ margin-top: 18px; font-size: 36px; font-weight: 700; color: {SUB}; letter-spacing: .06em; }}
.sh .shot {{ margin: 44px auto 0; width: 520px; height: 540px; overflow: hidden; border: 2px solid {LINE}; border-radius: 34px;
             box-shadow: 0 10px 30px rgba(60,45,35,.10); background: #FAF8F5; }}
.sh .shot img {{ width: 100%; display: block; }}
/* 作り込み（10/21 オーナー「色使いすぎ。見やすさとこだわりがある感じ」）：色は茶色1色、細い線と字の組みで見せる */
.panel {{ border-top: 2px solid {LINE}; }}
.panel > * {{ position: relative; z-index: 1; }}
.panel > .cv-logo {{ position: absolute; }}
.inner {{ position: absolute !important; inset: 20px; border: 1.5px solid {LINE}; pointer-events: none; z-index: 0 !important; }}
.corner {{ position: absolute !important; font-family: J; font-size: 24px; letter-spacing: .3em; color: {SUB}; z-index: 2 !important; }}
.corner.tl {{ left: 56px; top: 50px; }} .corner.tr {{ right: 56px; top: 50px; }}
/* 表紙 */
.cv {{ padding-top: 40px; }}
.cv-b {{ border: 0; border-top: 2px solid {ACC}; border-bottom: 2px solid {ACC}; padding: 12px 10px; color: {ACC}; font-size: 36px; letter-spacing: .24em; }}
.cv-k {{ color: {INK}; }}
.cv-line {{ width: 2px; height: 70px; background: {ACC}; margin: 40px auto 0; }}
.cv-c b {{ font-family: M; font-weight: 700; color: {ACC}; }}
/* ポイントの枚 */
.it, .sv {{ height: auto !important; min-height: 940px; padding-bottom: 80px !important; }}
.it {{ padding-top: 110px; }}
.desc {{ line-height: 1.85 !important; }}
.ck {{ padding: 24px 0 !important; }}
.tip {{ margin-top: 40px !important; }}
.head {{ display: flex; align-items: flex-end; gap: 30px; padding-bottom: 30px; border-bottom: 2px solid {INK}; }}
.no {{ font-family: M !important; font-weight: 700 !important; font-size: 130px !important; line-height: .9 !important; color: {ACC} !important; letter-spacing: 0 !important; }}
.no.w {{ font-family: J !important; font-weight: 400 !important; font-size: 64px !important; letter-spacing: .12em !important; padding-bottom: 8px; }}
.ttl {{ margin: 0 0 4px !important; font-size: 70px !important; }}
.desc {{ border-top: 0 !important; margin-top: 36px !important; padding-top: 0 !important; font-size: 46px !important; }}
.hl {{ background: linear-gradient(transparent 66%, #EFE3D6 66%); }}
.pk {{ background: linear-gradient(transparent 66%, #EFE3D6 66%); }}
.checks {{ gap: 0 !important; margin-top: 30px !important; border-top: 1.5px solid {LINE}; }}
.ck {{ padding: 20px 0; border-bottom: 1.5px solid {LINE}; font-size: 39px !important; }}
.tip {{ background: none !important; border-left: 0 !important; padding: 26px 0 0 !important; margin-top: 30px !important; display: flex; gap: 26px; align-items: flex-start; }}
.tip i {{ flex: none; font-family: M !important; font-weight: 700; font-size: 30px !important; letter-spacing: .1em !important; color: #fff !important;
          background: {ACC}; padding: 6px 16px; margin: 6px 0 0 !important; }}
.sv {{ padding-top: 110px; }}
.sv h2 {{ padding-bottom: 34px; border-bottom: 2px solid {INK}; }}
.sv .body {{ border-top: 0 !important; padding-top: 0 !important; margin-top: 36px !important; }}
.sh {{ padding-top: 110px; }}
.head .no {{ flex: none; white-space: nowrap; }}
.head .ttl {{ font-size: 62px !important; }}
.desc {{ font-size: 42px !important; line-height: 1.8 !important; }}
.ck {{ padding: 18px 0 !important; font-size: 37px !important; }}
.tip {{ font-size: 36px !important; margin-top: 30px !important; }}
/* 読みやすさ（10/21 オーナー「文字ばかり。もう少し読みやすさを」）：大きな数字・線の絵・矢印の流れ・左右くらべ。色は茶色1色のまま */
.ico {{ flex: none; width: 112px; height: 112px; border: 2px solid {LINE}; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 6px; }}
.ico svg {{ width: 64px; height: 64px; }}
.big {{ margin-top: 46px; text-align: center; }}
.big .lb {{ font-size: 38px; font-weight: 700; color: {SUB}; letter-spacing: .1em; }}
.big .fig {{ margin-top: 6px; font-family: M; font-weight: 700; color: {ACC}; line-height: 1; letter-spacing: .02em; }}
.big .fig b {{ font-size: 230px; font-weight: 700; }}
.big .fig span {{ font-size: 76px; margin-left: 8px; color: {INK}; }}
.big .note {{ margin-top: 22px; font-size: 38px; font-weight: 700; letter-spacing: .06em; line-height: 1.6; }}
.flow {{ margin-top: 44px; display: flex; flex-direction: column; align-items: stretch; }}
.flow .st {{ border: 2px solid {LINE}; padding: 26px 30px; display: flex; align-items: center; gap: 26px; font-size: 40px; font-weight: 700; letter-spacing: .05em; line-height: 1.5; }}
.flow .st em {{ flex: none; font-style: normal; font-family: J; font-size: 30px; letter-spacing: .14em; color: {ACC}; }}
.flow .st.last {{ border-color: {ACC}; background: #F8F2EB; }}
.flow .dn {{ height: 58px; display: flex; justify-content: center; }}
.flow .dn svg {{ height: 58px; }}
.cmp {{ margin-top: 44px; display: grid; grid-template-columns: 1fr 1fr; gap: 0; border: 2px solid {LINE}; }}
.cmp > div {{ padding: 30px 28px; }}
.cmp > div + div {{ border-left: 2px solid {LINE}; }}
.cmp h4 {{ font-family: M; font-weight: 700; font-size: 44px; text-align: center; padding-bottom: 20px; border-bottom: 1.5px solid {LINE}; letter-spacing: .06em; }}
.cmp > div.on h4 {{ color: {ACC}; }}
.cmp p {{ margin-top: 20px; font-size: 36px; font-weight: 700; line-height: 1.6; letter-spacing: .04em; }}
.one {{ margin-top: 30px; font-size: 40px; font-weight: 700; line-height: 1.75; letter-spacing: .05em; text-align: center; }}
"""

ARROW = (f'<svg width="96" height="24" viewBox="0 0 96 24" fill="none" stroke="{ACC}" stroke-width="2.4" stroke-linecap="round" '
         f'stroke-linejoin="round"><path d="M2 12h90M80 3l12 9-12 9"/></svg>')
CHECK = (f'<svg width="40" height="40" viewBox="0 0 40 40" fill="none"><circle cx="20" cy="20" r="18" stroke="{ACC}" stroke-width="2.4"/>'
         f'<path d="M12 20.5l5.5 5.5L28.5 14" stroke="{ACC}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>')


PAL = [("#F8E1CF", "#D9A98A"), ("#DCEAF3", "#8FB0C6"), ("#E2EBD9", "#9DB68C"), ("#F5DFE2", "#D59EA7")]
SPARK = ('<svg class="spark" width="120" height="44" viewBox="0 0 120 44" fill="none" stroke="#A07E66" stroke-width="2.2" stroke-linecap="round">'
         '<path d="M60 4v14M60 26v14M46 22h-14M88 22h-14M52 14l-5-5M68 14l5-5M52 30l-5 5M68 30l5 5"/><path d="M8 22h16M96 22h16" opacity=".5"/></svg>')


# 細い線の絵（茶色1色）。spec の item に "icon": "名前" で使う
_I = {
 "calendar": '<rect x="10" y="14" width="44" height="40" rx="4"/><path d="M10 26h44M22 8v12M42 8v12M20 36h6M30 36h6M40 36h6M20 45h6M30 45h6"/>',
 "doc": '<path d="M16 6h22l12 12v40H16z"/><path d="M38 6v12h12M24 30h18M24 39h18M24 48h12"/>',
 "house": '<path d="M8 30L32 10l24 20"/><path d="M14 26v28h36V26"/><path d="M27 54V40h10v14"/>',
 "yen": '<circle cx="32" cy="32" r="24"/><path d="M22 18l10 14 10-14M32 32v16M24 34h16M24 41h16"/>',
 "court": '<path d="M8 22L32 10l24 12z"/><path d="M14 26v22M26 26v22M38 26v22M50 26v22M8 54h48"/>',
 "clock": '<circle cx="32" cy="32" r="24"/><path d="M32 18v15l10 6"/>',
 "key": '<circle cx="20" cy="32" r="10"/><path d="M30 32h26M48 32v8M56 32v6"/>',
 "map": '<path d="M8 14l16-6 16 6 16-6v42l-16 6-16-6-16 6z"/><path d="M24 8v42M40 14v42"/>',
 "train": '<rect x="14" y="8" width="36" height="38" rx="8"/><path d="M14 30h36M24 46l-8 10M40 46l8 10"/><circle cx="23" cy="38" r="2"/><circle cx="41" cy="38" r="2"/>',
 "tree": '<path d="M32 8l16 24H38l12 16H14l12-16H16z"/><path d="M32 48v10"/>',
 "shield": '<path d="M32 6l22 8v16c0 14-10 24-22 28C20 54 10 44 10 30V14z"/><path d="M22 32l7 7 13-14"/>',
 "chart": '<path d="M8 56h48M14 48V34M26 48V22M38 48V30M50 48V14"/>',
 "people": '<circle cx="22" cy="20" r="8"/><circle cx="44" cy="22" r="7"/><path d="M8 54c0-10 6-18 14-18s14 8 14 18M34 54c0-8 4-14 10-14s10 6 10 14"/>',
 "flower": '<circle cx="32" cy="24" r="6"/><path d="M32 10a8 8 0 0 1 0 0M32 30v26M32 44c-8 0-14-4-16-10 8 0 14 4 16 10zM32 40c8 0 14-4 16-10-8 0-14 4-16 10z"/><path d="M26 18a8 8 0 1 1 12 0M24 28a8 8 0 1 1 0-8M40 28a8 8 0 1 0 0-8"/>',
}
def icon(name):
    d = _I.get(name)
    return (f'<div class="ico"><svg viewBox="0 0 64 64" fill="none" stroke="{ACC}" stroke-width="2.6" stroke-linecap="round" '
            f'stroke-linejoin="round">{d}</svg></div>') if d else ""
DOWN = (f'<svg viewBox="0 0 24 58" fill="none" stroke="{ACC}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M12 4v48M4 42l8 10 8-10"/></svg>')


def extra(s):
    """item の見せ方。big（大きな数字）・flow（矢印の流れ）・compare（左右くらべ）・one（短い1文）"""
    h = ""
    if s.get("big"):
        b = s["big"]
        h += (f'<div class="big">' + (f'<div class="lb">{tx(b.get("label"))}</div>' if b.get("label") else "")
              + f'<div class="fig"><b>{html.escape(str(b["num"]))}</b><span>{tx(b.get("unit"))}</span></div>'
              + (f'<div class="note">{tx(b.get("note"))}</div>' if b.get("note") else "") + '</div>')
    if s.get("flow"):
        st = s["flow"]
        h += '<div class="flow">' + f'<div class="dn">{DOWN}</div>'.join(
            f'<div class="st{" last" if k == len(st) - 1 else ""}"><em>{k + 1:02d}</em><span>{tx(x)}</span></div>' for k, x in enumerate(st)) + '</div>'
    if s.get("compare"):
        c = s["compare"]
        h += '<div class="cmp">' + "".join(
            f'<div class="{"on" if side.get("on") else ""}"><h4>{tx(side["h"])}</h4>' + "".join(f'<p>{tx(x)}</p>' for x in side.get("items", [])) + '</div>'
            for side in c) + '</div>'
    if s.get("one"):
        h += f'<div class="one">{tx(s["one"])}</div>'
    return h


def slide_html(spec, s, i, n, credit):
    logo = f"file://{LOGO}"
    t = s["type"]
    label = spec.get("page_label") or spec.get("series")
    if t == "cover":
        body = ('<div class="brand">TOWN NOTES</div><div class="panel cv"><div class="inner"></div>'
                + (f'<div class="cv-b">{tx(s["badge"])}</div>' if s.get("badge") else "")
                + (f'<div class="cv-k">{tx(s["kicker"])}</div>' if s.get("kicker") else "")
                + f'<div class="cv-t">{tx(s["title"])}</div>'
                + (f'<div class="cv-c"><b>{html.escape(str(s["count"]))}</b>{tx(s.get("count_text", "つのポイント"))}</div>' if s.get("count") else "")
                + ("" if s.get("badge") else f'<div class="cv-s">{tx(spec.get("series"))}</div>')
                + f'<img class="cv-logo" src="{logo}"></div>')
    else:
        body = f'<div class="brand"><img src="{logo}">TOWN NOTES</div>'
        if label:
            body += f'<div class="strip">{tx(label)}</div>'
        if t == "item":
            checks = "".join(f'<div class="ck">{CHECK}<span>{tx(c)}</span></div>' for c in s.get("checks", []))
            body += (f'<div class="panel it"><div class="inner"></div><div class="corner tl">POINT</div><div class="corner tr">{i + 1:02d} / {n:02d}</div>'
                     f'<div class="head"><div class="no{" w" if len(s["n"]) > 2 else ""}">{html.escape(s["n"])}</div>'
                     f'<div class="ttl">{tx(s["title"])}</div>' + (f'<div style="margin-left:auto">{icon(s["icon"])}</div>' if s.get("icon") else "") + '</div>'
                     + (f'<div class="desc">{tx(s["desc"])}</div>' if s.get("desc") else "") + extra(s)
                     + (f'<div class="checks">{checks}</div>' if checks else "")
                     + (f'<div class="tip"><i>メモ</i>{tx(s["tip"])}</div>' if s.get("tip") else "") + '</div>')
        elif t == "save":
            src = (("出典：" + tx(spec["source"])) if spec.get("source") else "") + (("<br>" if spec.get("source") else "") + html.escape(credit) if credit else "")
            body += (f'<div class="panel sv"><div class="inner"></div><div class="corner tl">SAVE</div><h2>{tx(s["head"])}</h2><div class="body">{tx(s.get("body"))}</div>'
                     f'<div class="cta"><div><div class="l1">{tx(s.get("bridge", "売るか決めていない段階でも大丈夫です"))}</div>'
                     f'<div class="l2">{tx(s.get("cta", "相談はプロフィールから"))}</div></div>{ARROW}</div>'
                     f'<div class="src">{src}</div></div>')
        elif t == "shot":  # ページの画面をのせる枚（お知らせ用）。img は画像ファイルの場所
            body += (f'<div class="panel sh"><div class="inner"></div><div class="corner tl">NEWS</div><h2>{tx(s["head"])}</h2>'
                     + (f'<div class="sub">{tx(s["sub"])}</div>' if s.get("sub") else "")
                     + f'<div class="shot"><img src="file://{os.path.abspath(s["img"])}"></div></div>')
        else:
            raise ValueError(t)
    nxt = f'<div class="next">NEXT{ARROW}</div>' if i < n - 1 else ""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}{nxt}</body></html>'


m.slide_html = slide_html

if __name__ == "__main__":
    m.main(sys.argv[1], sys.argv[2], "--images-only" in sys.argv[3:])
