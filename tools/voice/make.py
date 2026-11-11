"""読み上げの声を作る（VOICEVOX。.github/workflows/voice.yml の中で動く）。11/11 月。
使い方: python3 tools/voice/make.py 台本.json
台本: {"name": "置き場の名前", "speakers": [14, 8], "speed": 1.05, "lines": ["1行目", "2行目"]}
結果: shots/voice/<name>/<話者の番号>-<行の番号>.wav と speakers.json（話者の名前の一覧）"""
import json, os, sys, time, urllib.request, urllib.parse

B = os.environ.get("VOICE_URL", "http://127.0.0.1:50021")   # AivisSpeech は http://127.0.0.1:10101（voice-aivis.yml）


def req(path, data=None, method="GET"):
    r = urllib.request.Request(B + path, data=data, method=method, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=600) as f:
        return f.read()


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    for i in range(400):   # AivisSpeech は最初にモデルを取りに行くので数分かかる
        try:
            req("/version"); break
        except Exception:
            time.sleep(2)
    out = os.path.join("shots", "voice", spec["name"]); os.makedirs(out, exist_ok=True)
    if spec.get("catalog"):   # AivisHub の声の一覧を取る（どの声を入れるか選ぶ用）
        H = "https://api.aivis-project.com/v1/aivm-models/search?"
        for pg in (1, 2, 3):
            for srt in ("download", "like"):
                try:
                    r = urllib.request.Request(H + f"sort={srt}&page={pg}&limit=30", headers={"User-Agent": "voice-tool"})
                    open(os.path.join(out, f"catalog-{srt}-{pg}.json"), "wb").write(urllib.request.urlopen(r, timeout=60).read())
                except Exception as e:
                    open(os.path.join(out, f"catalog-{srt}-{pg}.err"), "w").write(repr(e) + getattr(e, "read", lambda: b"")().decode("utf-8", "ignore")[:2000])
    for u in spec.get("install", []):   # 声のモデルを足す（AivisHub の uuid）
        try:
            req("/aivm_models/" + u + "/install", b"", "POST")
        except Exception as e:
            open(os.path.join(out, f"install-{u}.err"), "w").write(repr(e) + getattr(e, "read", lambda: b"")().decode("utf-8", "ignore")[:2000])
    sp = json.loads(req("/speakers"))
    json.dump([{"name": s["name"], "styles": [{"name": x["name"], "id": x["id"]} for x in s["styles"]]} for s in sp],
              open(os.path.join(out, "speakers.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    kana = {}
    ids = [x["id"] for s in sp for x in s["styles"]] if spec["speakers"] == "all" else spec["speakers"]
    for s in ids:
        for n, line in enumerate(spec["lines"]):
            q = json.loads(req(f"/audio_query?speaker={s}&text=" + urllib.parse.quote(line), b"", "POST"))
            q["speedScale"] = spec.get("speed", 1.0); q["prePhonemeLength"] = 0.05; q["postPhonemeLength"] = 0.1
            q["intonationScale"] = spec.get("intonation", 1.0); q["pitchScale"] = spec.get("pitch", 0.0)
            if "pause" in spec: q["pauseLengthScale"] = spec["pause"]
            if "tempo" in spec: q["tempoDynamicsScale"] = spec["tempo"]
            kana[f"{s}-{n:02d}"] = q.get("kana", "")
            wav = req(f"/synthesis?speaker={s}", json.dumps(q).encode(), "POST")
            open(os.path.join(out, f"{s}-{n:02d}.wav"), "wb").write(wav)
    json.dump(kana, open(os.path.join(out, "kana.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("voice", spec["name"], len(ids), "話者", len(spec["lines"]), "行")


if __name__ == "__main__":
    main()
