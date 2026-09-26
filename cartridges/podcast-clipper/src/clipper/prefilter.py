import json
import re

HOOK_WORDS_EN = re.compile(
    r"\b(mistake|secret|never|always|million|billion|free|hack|truth|lie|"
    r"shocking|insane|crazy|best|worst|first|last|stop|start|quit|rich|"
    r"broke|fail|win|lose|love|hate|fear|war|money|kill|die|dead|nobody|"
    r"everybody|everyone|why|how|what if)\b",
    re.IGNORECASE,
)
HOOK_WORDS_ID = re.compile(
    r"\b(ternyata|rahasia|selalu|jangan|gratis|bohong|benar|salah|"
    r"terbaik|terburuk|pertama|terakhir|berhenti|mulai|kaya|miskin|"
    r"cinta|benci|takut|perang|mati|uang|gagal|menang|nobody|"
    r"semua orang|kenapa|bagaimana|apa jika|banget|parah|gilain|"
    r"reaksi|gemes|sedih|ngakak|viral|trending|kontroversi|"
    r"habis|korban|jahat|balas dendam)\b",
    re.IGNORECASE,
)
QUESTION = re.compile(r"\?")
EXCLAIM = re.compile(r"!")
NUMBER = re.compile(r"\b\d+(\.\d+)?\s*(%|percent|million|billion|thousand|k\b)?")


def score_window(text, words, dur, pos, total_dur, skip_edge):
    score = 0.0
    reasons = []
    if QUESTION.search(text):
        score += 2.0
        reasons.append("question")
    if EXCLAIM.search(text):
        score += 1.5
        reasons.append("exclaim")
    hook_set = set()
    for pat in (HOOK_WORDS_EN, HOOK_WORDS_ID):
        hook_set |= {h.lower() for h in pat.findall(text)}
    if hook_set:
        pts = min(len(hook_set) * 1.0, 4.0)
        score += pts
        reasons.append(f"hooks:{','.join(sorted(hook_set)[:3])}")
    nums = NUMBER.findall(text)
    if nums:
        score += min(len(nums) * 0.5, 2.0)
        reasons.append("numbers")
    wpm = len(words) / max(dur / 60.0, 0.01)
    if 120 <= wpm <= 200:
        score += 1.0
        reasons.append("good-pace")
    if pos < skip_edge or pos + dur > total_dur - skip_edge:
        score -= 3.0
        reasons.append("edge-penalty")
    if dur < 20 or dur > 70:
        score -= 2.0
    return score, reasons


def prefilter(transcript, settings=None, out_path=None):
    cfg = (settings or {}).get("prefilter", {})
    min_s = cfg.get("min_clip_s", 20)
    max_s = cfg.get("max_clip_s", 70)
    top_n = cfg.get("max_candidates", 20)
    skip_edge = cfg.get("skip_intro_outro_s", 30)
    segs = transcript["segments"]
    total_dur = segs[-1]["end"] if segs else 0
    windows = []
    target = (min_s + max_s) / 2
    i = 0
    while i < len(segs):
        start = segs[i]["start"]
        cut = start + target
        j = i
        while j + 1 < len(segs) and segs[j]["end"] < cut:
            j += 1
        while j + 1 < len(segs) and segs[j + 1]["end"] - start <= max_s:
            if abs(segs[j + 1]["end"] - cut) < abs(segs[j]["end"] - cut):
                j += 1
            else:
                break
        texts = [segs[k]["text"] for k in range(i, j + 1)]
        words = [w["w"] for k in range(i, j + 1) for w in segs[k].get("words", [])]
        all_words = [w for k in range(i, j + 1) for w in segs[k].get("words", [])]
        end = segs[j]["end"]
        dur = end - start
        if dur >= min_s:
            text = " ".join(texts)
            s, reasons = score_window(text, words, dur, start, total_dur, skip_edge)
            windows.append(
                {
                    "id": len(windows),
                    "start": round(start, 2),
                    "end": round(end, 2),
                    "dur": round(dur, 1),
                    "text": text,
                    "words": all_words,
                    "prefilter_score": round(s, 2),
                    "signals": reasons,
                }
            )
        step = max(1, (j - i + 1) // 2)
        i += step
    windows.sort(key=lambda w: -w["prefilter_score"])
    top = windows[:top_n]
    if out_path:
        with open(out_path, "w") as f:
            json.dump(top, f, indent=1)
    return top
