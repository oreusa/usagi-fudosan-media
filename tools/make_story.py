"""インスタのストーリー用の1枚を作る（10/24 オーナー「やろうこれから」）

リール・おでかけの spec（tools/specs4/*.json）の表紙を、v5（おでかけリストと同じ見た目）で描き、
下に「リンクから」の案内を足した 1080x1920 の画像を1枚だけ作る。NEXT の矢印は付けない。
ストーリーのリンクスタンプは画面のまん中あたりに置かれるので、下の案内は控えめにする。
使い方: python3 make_story.py <spec.json> <out.jpg> [案内の文]
"""
import html, json, os, sys, tempfile

import make_reel4 as m
import make_reel5 as v5


def story_html(spec, note):
    cover = next(s for s in spec["slides"] if s["type"] == "cover")
    page = v5.slide_html(spec, cover, 0, 1, "")  # n=1 なので NEXT は付かない
    extra = (f'<div style="position:absolute;left:0;right:0;bottom:250px;text-align:center;'
             f'font-family:M;font-weight:600;font-size:40px;letter-spacing:.12em;color:{v5.ACC}">{html.escape(note)}</div>')
    return page.replace("</body>", extra + "</body>")


def main(spec_path, out, note):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    spec = json.load(open(spec_path, encoding="utf-8"))
    with sync_playwright() as p:
        exe = os.environ.get("REEL_CHROMIUM", "/opt/pw-browsers/chromium")
        b = p.chromium.launch(**({"executable_path": exe} if os.path.exists(exe) else {}))
        pg = b.new_page(viewport={"width": m.W, "height": m.H}, device_scale_factor=2)
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
            f.write(story_html(spec, note))
        pg.goto("file://" + f.name)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(200)
        big = out + ".png"
        pg.screenshot(path=big)
        Image.open(big).convert("RGB").resize((m.W, m.H), Image.LANCZOS).save(out, quality=95)
        os.remove(big)
        os.unlink(f.name)
        b.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "日付と地図つきの一覧は、リンクから")
