"""読み上げの声を作る（VOICEVOX。.github/workflows/voice.yml の中で動く）。11/11 月。
使い方: python3 tools/voice/make.py 台本.json
台本: {"name": "置き場の名前", "speakers": [14, 8], "speed": 1.05, "lines": ["1行目", "2行目"]}
結果: shots/voice/<name>/<話者の番号>-<行の番号>.wav と speakers.json（話者の名前の一覧）"""
import json, os, sys, time, urllib.request, urllib.parse

B = "http://127.0.0.1:50021"


def req(path, data=None, method="GET"):
    r = urllib.request.Request(B + path, data=data, method=method, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=120) as f:
        return f.read()


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    for i in range(90):
        try:
            req("/version"); break
        except Exception:
            time.sleep(2)
    out = os.path.join("shots", "voice", spec["name"]); os.makedirs(out, exist_ok=True)
    sp = json.loads(req("/speakers"))
    json.dump([{"name": s["name"], "styles": [{"name": x["name"], "id": x["id"]} for x in s["styles"]]} for s in sp],
              open(os.path.join(out, "speakers.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    kana = {}
    for s in spec["speakers"]:
        for n, line in enumerate(spec["lines"]):
            q = json.loads(req(f"/audio_query?speaker={s}&text=" + urllib.parse.quote(line), b"", "POST"))
            q["speedScale"] = spec.get("speed", 1.0); q["prePhonemeLength"] = 0.05; q["postPhonemeLength"] = 0.1
            q["intonationScale"] = spec.get("intonation", 1.0); q["pitchScale"] = spec.get("pitch", 0.0)
            if "pause" in spec: q["pauseLengthScale"] = spec["pause"]
            kana[f"{s}-{n:02d}"] = q.get("kana", "")
            wav = req(f"/synthesis?speaker={s}", json.dumps(q).encode(), "POST")
            open(os.path.join(out, f"{s}-{n:02d}.wav"), "wb").write(wav)
    json.dump(kana, open(os.path.join(out, "kana.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("voice", spec["name"], len(spec["speakers"]), "話者", len(spec["lines"]), "行")


if __name__ == "__main__":
    main()
