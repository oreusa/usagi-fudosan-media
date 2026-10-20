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
.cv-c {{ margin-top: 26px; font-size: 52px; font-weight: 700; letter-spacing: .08em; }}
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
.sh .shot {{ margin: 44px auto 0; width: 560px; height: 600px; overflow: hidden; border: 2px solid {LINE}; border-radius: 34px;
             box-shadow: 0 10px 30px rgba(60,45,35,.10); background: #FAF8F5; }}
.sh .shot img {{ width: 100%; display: block; }}
/* 飾り（10/21 オーナー「投稿だしデザインもうちょい加えたい」）。枚ごとにうすい色が変わる（--pc 地の丸、--pd 濃いめ） */
.panel {{ overflow: hidden; }}
.panel:before {{ content: ""; position: absolute; right: -150px; top: -150px; width: 380px; height: 380px; border-radius: 50%; background: var(--pc); opacity: .75; }}
.panel:after {{ content: ""; position: absolute; left: -110px; bottom: -110px; width: 260px; height: 260px; border-radius: 50%;
                border: 3px dashed var(--pd); opacity: .5; }}
.panel > * {{ position: relative; z-index: 1; }}
.panel > .cv-logo {{ position: absolute; }}
.cv {{ padding-top: 40px; }}
.inner {{ position: absolute !important; inset: 22px; border: 1.5px solid {LINE}; pointer-events: none; z-index: 0 !important; }}
.cv-b {{ background: var(--pc); border-color: var(--pd); color: {INK}; }}
.cv-t .hl, .ttl .hl {{ background: none; }}
.cv-c b {{ font-family: M; font-weight: 700; color: var(--pd); }}
.spark {{ display: block; margin: 0 auto -6px; }}
.nowrap {{ display: flex; align-items: center; gap: 26px; }}
.no {{ width: 150px; height: 150px; border-radius: 50%; background: var(--pc); display: flex; align-items: center; justify-content: center;
       font-size: 64px !important; font-weight: 400 !important; color: {INK} !important; flex: none; }}
.no.w {{ font-size: 44px !important; letter-spacing: .08em; }}
.ttl {{ margin-top: 0 !important; }}
.ttl span.u {{ background: linear-gradient(transparent 66%, var(--pc) 66%); }}
.ck svg circle {{ fill: var(--pc); stroke: var(--pd); }}
.ck svg path {{ stroke: {INK}; }}
.tip {{ background: var(--pc) !important; border-left: 0 !important; border-radius: 0 0 0 0; position: relative; }}
.tip i {{ color: {INK} !important; }}
.sv .cta {{ background: {ACC}; border-color: {ACC}; }}
.sv .cta .l1 {{ color: #F3E9E0; }} .sv .cta .l2 {{ color: #fff; }}
.sv .cta svg path {{ stroke: #fff; }}
.dots {{ position: absolute; left: 0; right: 0; top: 1540px; display: flex; justify-content: center; gap: 14px; }}
.dots i {{ width: 14px; height: 14px; border-radius: 50%; background: {LINE}; }}
.dots i.on {{ background: {ACC}; width: 40px; border-radius: 7px; }}
"""

ARROW = (f'<svg width="96" height="24" viewBox="0 0 96 24" fill="none" stroke="{ACC}" stroke-width="2.4" stroke-linecap="round" '
         f'stroke-linejoin="round"><path d="M2 12h90M80 3l12 9-12 9"/></svg>')
CHECK = (f'<svg width="40" height="40" viewBox="0 0 40 40" fill="none"><circle cx="20" cy="20" r="18" stroke="{ACC}" stroke-width="2.4"/>'
         f'<path d="M12 20.5l5.5 5.5L28.5 14" stroke="{ACC}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>')


PAL = [("#F8E1CF", "#D9A98A"), ("#DCEAF3", "#8FB0C6"), ("#E2EBD9", "#9DB68C"), ("#F5DFE2", "#D59EA7")]
SPARK = ('<svg class="spark" width="120" height="44" viewBox="0 0 120 44" fill="none" stroke="#A07E66" stroke-width="2.2" stroke-linecap="round">'
         '<path d="M60 4v14M60 26v14M46 22h-14M88 22h-14M52 14l-5-5M68 14l5-5M52 30l-5 5M68 30l5 5"/><path d="M8 22h16M96 22h16" opacity=".5"/></svg>')


def slide_html(spec, s, i, n, credit):
    logo = f"file://{LOGO}"
    pc, pd = PAL[i % len(PAL)]
    t = s["type"]
    label = spec.get("page_label") or spec.get("series")
    if t == "cover":
        body = ('<div class="brand">USAGI-CHAN TOWN NOTES</div><div class="panel cv"><div class="inner"></div>'
                + (f'<div class="cv-b">{tx(s["badge"])}</div>' if s.get("badge") else "")
                + (f'<div class="cv-k">{tx(s["kicker"])}</div>' if s.get("kicker") else "")
                + f'{SPARK}<div class="cv-t">{tx(s["title"])}</div><div class="cv-line"></div>'
                + (f'<div class="cv-c"><b>{html.escape(str(s["count"]))}</b>{tx(s.get("count_text", "つのポイント"))}</div>' if s.get("count") else "")
                + ("" if s.get("badge") else f'<div class="cv-s">{tx(spec.get("series"))}</div>')
                + f'<img class="cv-logo" src="{logo}"></div>')
    else:
        body = f'<div class="brand"><img src="{logo}">USAGI-CHAN TOWN NOTES</div>'
        if label:
            body += f'<div class="strip">{tx(label)}</div>'
        if t == "item":
            checks = "".join(f'<div class="ck">{CHECK}<span>{tx(c)}</span></div>' for c in s.get("checks", []))
            body += (f'<div class="panel it"><div class="nowrap"><div class="no{" w" if len(s["n"]) > 2 else ""}">{html.escape(s["n"])}</div>'
                     f'<div class="ttl"><span class="u">{tx(s["title"])}</span></div></div>'
                     f'<div class="desc">{tx(s["desc"])}</div><div class="checks">{checks}</div>'
                     + (f'<div class="tip"><i>POINT</i>{tx(s["tip"])}</div>' if s.get("tip") else "") + '</div>')
        elif t == "save":
            src = (("出典：" + tx(spec["source"])) if spec.get("source") else "") + (("<br>" if spec.get("source") else "") + html.escape(credit) if credit else "")
            body += (f'<div class="panel sv"><h2>{tx(s["head"])}</h2><div class="body">{tx(s.get("body"))}</div>'
                     f'<div class="cta"><div><div class="l1">{tx(s.get("bridge", "売るか決めていない段階でも大丈夫です"))}</div>'
                     f'<div class="l2">{tx(s.get("cta", "相談はプロフィールから"))}</div></div>{ARROW}</div>'
                     f'<div class="src">{src}</div></div>')
        elif t == "shot":  # ページの画面をのせる枚（お知らせ用）。img は画像ファイルの場所
            body += (f'<div class="panel sh"><h2>{tx(s["head"])}</h2>'
                     + (f'<div class="sub">{tx(s["sub"])}</div>' if s.get("sub") else "")
                     + f'<div class="shot"><img src="file://{os.path.abspath(s["img"])}"></div></div>')
        else:
            raise ValueError(t)
        body += f'<div class="page">{i + 1:02d} / {n:02d}</div>'
    body += '<div class="dots">' + "".join(f'<i class="{"on" if k == i else ""}"></i>' for k in range(n)) + '</div>'
    nxt = f'<div class="next">NEXT{ARROW}</div>' if i < n - 1 else ""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body style="--pc:{pc};--pd:{pd}">{body}{nxt}</body></html>'


m.slide_html = slide_html

if __name__ == "__main__":
    m.main(sys.argv[1], sys.argv[2], "--images-only" in sys.argv[3:])
