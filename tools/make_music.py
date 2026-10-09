"""リール用の静かなピアノ曲を作る（自作の曲。音はピアノの録音素材を使う）
使い方: python3 make_music.py out.wav 秒数 [seed]

・ピアノの音：FluidR3 GM（gleitz/midi-js-soundfonts、CC BY 3.0）。tools/sound/piano/ に1音ずつ置く
  → 使ったリールには「音：FluidR3 GM（CC BY 3.0）」を出典の行に書く（make_reel3.py が自動で入れる）
・曲：ゆっくり（72BPM）、明るく落ち着いた和音進行。seed で進行と旋律が少し変わるので、毎日同じ曲にならない
・最後の1秒で音を消す。音量は控えめ（文字を読む邪魔をしない）
"""
import os, subprocess, sys, urllib.request
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SDIR = os.path.join(HERE, "sound", "piano")
SRC = "https://raw.githubusercontent.com/gleitz/midi-js-soundfonts/gh-pages/FluidR3_GM/acoustic_grand_piano-mp3/"
SR = 44100
NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
CREDIT = "音：FluidR3 GM（CC BY 3.0）"

PROGS = [  # 和音進行（ルートからの半音。キーは C、1小節に1つ）
    [[0, 4, 7, 11], [9, 12, 16, 19], [5, 9, 12, 16], [7, 11, 14, 17]],      # Cmaj7 Am7 Fmaj7 G
    [[5, 9, 12, 16], [7, 11, 14, 17], [4, 7, 11, 14], [9, 12, 16, 19]],      # Fmaj7 G Em7 Am7
    [[0, 4, 7, 11], [4, 7, 11, 14], [5, 9, 12, 16], [2, 5, 9, 12]],          # Cmaj7 Em7 Fmaj7 Dm7
]


def note_name(m):
    return f"{NAMES[m % 12]}{m // 12 - 1}"


_cache = {}


def sample(m):
    if m in _cache:
        return _cache[m]
    os.makedirs(SDIR, exist_ok=True)
    mp3 = os.path.join(SDIR, note_name(m) + ".mp3")
    if not os.path.exists(mp3):
        urllib.request.urlretrieve(SRC + note_name(m) + ".mp3", mp3)
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", mp3, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    _cache[m] = np.frombuffer(raw, dtype=np.float32).copy()
    return _cache[m]


def place(buf, m, t, vel, length=None):
    s = sample(m) * vel
    if length:
        n = int(length * SR)
        s = s[:n].copy()
        rel = min(int(0.4 * SR), len(s))
        s[-rel:] *= np.linspace(1, 0, rel)
    i = int(t * SR)
    if i >= len(buf):
        return
    s = s[:len(buf) - i]
    buf[i:i + len(s)] += s


def reverb(x):
    n = int(1.8 * SR)
    rng = np.random.default_rng(1)
    ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 6, n))
    ir[0] = 0
    wet = np.convolve(x, ir)[:len(x)] if len(x) < 200000 else _fftconv(x, ir)
    wet /= np.max(np.abs(wet)) + 1e-9
    return x + 0.18 * wet * np.max(np.abs(x))


def _fftconv(x, ir):
    n = len(x) + len(ir)
    N = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[:len(x)]


def make(path, seconds, seed=0):
    rng = np.random.default_rng(seed)
    prog = PROGS[seed % len(PROGS)]
    key = int(rng.choice([0, 2, 5, 7]))            # C / D / F / G
    beat = 60 / 72
    bar = beat * 4
    buf = np.zeros(int((seconds + 3) * SR), dtype=np.float32)
    t, k = 0.0, 0
    while t < seconds:
        ch = [48 + key + n for n in prog[k % len(prog)]]
        place(buf, ch[0] - 12, t, 0.35, bar * 1.5)                      # 低い音（根音）
        for j, n in enumerate([ch[1], ch[2], ch[3], ch[2]] * 2):        # 8分音符のやさしい分散和音
            place(buf, n, t + j * beat / 2, 0.16 + 0.04 * (j % 2 == 0), beat * 1.6)
        if k % 2 == 1 or rng.random() < 0.5:                            # ときどき高い旋律
            for j in range(int(rng.integers(1, 3))):
                m = ch[int(rng.integers(1, 4))] + 12
                place(buf, m, t + beat * (j * 2 + rng.choice([0, 0.5])), 0.24, beat * 2)
        t += bar
        k += 1
    out = reverb(buf[:int(seconds * SR)].astype(np.float64))
    fade = int(1.0 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)
    out[:int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR))
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.5                     # 控えめな音量
    st = np.repeat(out[:, None], 2, axis=1)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f64le", "-ac", "2", "-ar", str(SR), "-i", "-",
                    "-c:a", "pcm_s16le", path], input=st.astype(np.float64).tobytes(), check=True)


if __name__ == "__main__":
    make(sys.argv[1], float(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 0)
