"""Speaker-following vertical crop.

Splits a clip into shots on the source's camera cuts, then for each shot picks
the face to frame (largest / most mouth-active) and returns a step-wise crop
expression so the vertical window jumps between speakers like a hand edit.

Pure-ish helpers (segments, expression building) are unit-tested; the rest
shells out to ffmpeg/opencv.
"""

import os
import re
import shutil
import subprocess
import tempfile
from itertools import pairwise

from .smartcrop import FFMPEG, ensure_model

DEFAULT_SCENE = 0.15
DEFAULT_FPS = 2.0
DEFAULT_DWELL = 1.5
MIN_FACE_W = 0.04


def detect_cuts(source, start, end, thresh=DEFAULT_SCENE):
    """Return absolute timestamps of camera cuts inside [start, end]."""
    dur = max(end - start, 0.1)
    cmd = [
        FFMPEG,
        "-hide_banner",
        "-ss",
        str(start),
        "-t",
        str(dur),
        "-i",
        source,
        "-vf",
        f"select='gt(scene,{thresh})',metadata=print",
        "-an",
        "-f",
        "null",
        "-",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, check=False)
    cuts = []
    for m in re.finditer(r"pts_time:([0-9.]+)", r.stderr):
        t = float(m.group(1))
        if 0.05 < t < dur - 0.05:
            cuts.append(round(start + t, 2))
    return sorted(set(cuts))


def segments(start, end, cuts, min_shot=0.4):
    """Turn cut timestamps into contiguous (start, end) shots."""
    pts = [start] + [c for c in cuts if start < c < end] + [end]
    segs = []
    for a, b in pairwise(pts):
        if b - a < 0.05:
            continue
        if segs and (b - a) < min_shot:
            segs[-1] = (segs[-1][0], b)
        else:
            segs.append((a, b))
    return segs


def extract_frames(source, start, end, fps, out_dir):
    dur = max(end - start, 0.1)
    pattern = os.path.join(out_dir, "f_%05d.jpg")
    cmd = [
        FFMPEG,
        "-hide_banner",
        "-v",
        "error",
        "-ss",
        str(start),
        "-t",
        str(dur),
        "-i",
        source,
        "-vf",
        f"fps={fps},scale=640:-2",
        "-q:v",
        "3",
        pattern,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    files = sorted(f for f in os.listdir(out_dir) if f.endswith(".jpg"))
    return [(start + i / fps, os.path.join(out_dir, f)) for i, f in enumerate(files)]


def _detect_faces(frames):
    """Per frame, faces with normalized centre x and mouth-band motion."""
    import cv2
    import numpy as np

    model = ensure_model()
    det = None
    prev = None
    out = []
    for t, path in frames:
        img = cv2.imread(path)
        if img is None:
            continue
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        diff = None if prev is None else np.abs(gray - prev)
        if det is None:
            det = cv2.FaceDetectorYN_create(model, "", (w, h), 0.5)
        else:
            det.setInputSize((w, h))
        _, faces = det.detect(img)
        found = []
        if faces is not None:
            for f in faces:
                x, bw, bh = float(f[0]), float(f[2]), float(f[3])
                if bw / w < MIN_FACE_W:
                    continue
                act = 0.0
                if diff is not None:
                    mcx = (float(f[10]) + float(f[12])) / 2
                    mcy = (float(f[11]) + float(f[13])) / 2
                    rx, ry = 0.35 * bw, 0.30 * bh
                    x0, x1 = int(max(mcx - rx, 0)), int(min(mcx + rx, w))
                    y0, y1 = int(max(mcy - ry, 0)), int(min(mcy + ry, h))
                    if y1 > y0 and x1 > x0:
                        act = float(diff[y0:y1, x0:x1].mean())
                found.append({"x": (x + bw / 2) / w, "w": bw / w, "act": act})
        out.append((t, found))
        prev = gray
    return out


def track_centers(xs, gap=0.18):
    """One or two stable face columns from normalized x positions (1-D k-means)."""
    xs = sorted(xs)
    if not xs:
        return []
    if xs[-1] - xs[0] < gap:
        return [sum(xs) / len(xs)]
    c = [xs[0], xs[-1]]
    for _ in range(12):
        near = [[], []]
        for x in xs:
            near[0 if abs(x - c[0]) <= abs(x - c[1]) else 1].append(x)
        nxt = [(sum(b) / len(b)) if b else c[i] for i, b in enumerate(near)]
        if nxt == c:
            break
        c = nxt
    return sorted(c)


def plan_switches(times, acts, n_tracks, min_dwell=1.0, ratio=1.25, floor=1.0, window=3):
    """Pick a displayed track per sample, switching with hysteresis.

    Returns [(start, end, track_index)] covering [times[0], times[-1]]. A switch
    needs the challenger to beat the current track by `ratio` (plus `floor`) and
    `min_dwell` to have elapsed, so laughter/mouth motion pulls the camera
    without jitter. Callers should drop the first sample of a shot (its
    frame-diff spans the camera cut).
    """
    if not times or n_tracks == 0:
        return []
    if n_tracks == 1:
        return [(times[0], times[-1], 0)]
    smooth = []
    for i in range(len(times)):
        lo = max(0, i - window + 1)
        mx = i - lo + 1
        smooth.append(
            [sum(acts[j][k] for j in range(lo, i + 1)) / mx for k in range(n_tracks)]
        )
    cur = max(range(n_tracks), key=lambda k: smooth[0][k])
    start_t = last_switch = times[0]
    plan = []
    for i in range(1, len(times)):
        best = max(range(n_tracks), key=lambda k: smooth[i][k])
        if (
            best != cur
            and smooth[i][best] > smooth[i][cur] * ratio + floor
            and times[i] - last_switch >= min_dwell
        ):
            plan.append((start_t, times[i], cur))
            start_t = last_switch = times[i]
            cur = best
    plan.append((start_t, times[-1], cur))
    return plan


def merge_short(shots, min_seg=0.6):
    """Absorb sub-`min_seg` plan pieces into the previous shot (keeps its x)."""
    out = []
    for sh in shots:
        if out and (sh["end"] - sh["start"]) < min_seg:
            out[-1]["end"] = sh["end"]
        else:
            out.append(dict(sh))
    return out


def plan_to_shots(plan, s, e, centers):
    """Emit shot dicts, snapping the first/last to the true shot bounds.

    plan_switches only sees sampled times (e.g. 515.5..523.5), so without this
    the tail of a shot (523.5..524.0) would fall to the next shot's crop.
    """
    out = []
    for idx, (a, b, k) in enumerate(plan):
        a = s if idx == 0 else max(a, s)
        b = e if idx == len(plan) - 1 else min(b, e)
        if b - a < 0.2:
            continue
        x = round(min(max(centers[k], 0.08), 0.92), 4)
        out.append({"start": a, "end": b, "x": x})
    return out


def target_timeline(source, start, end, settings=None):
    """Per-shot active-speaker targets: [{start, end, x}] in absolute seconds."""
    cfg = (settings or {}).get("clips", {})
    thresh = cfg.get("scene_thresh", DEFAULT_SCENE)
    fps = cfg.get("follow_fps", DEFAULT_FPS)
    dwell = cfg.get("follow_min_dwell", DEFAULT_DWELL)
    try:
        cuts = detect_cuts(source, start, end, thresh)
    except Exception as e:  # noqa: BLE001 - fall back to no cuts
        print(f"  scene detect failed ({e})")
        cuts = []
    tmp = tempfile.mkdtemp(prefix="follow_")
    try:
        frames = extract_frames(source, start, end, fps, tmp)
        ff = _detect_faces(frames)
        out = []
        last = 0.5
        for s, e in segments(start, end, cuts):
            shot = [(t, fl) for t, fl in ff if s <= t < e]
            usable = shot[1:] if len(shot) >= 3 else shot
            centers = track_centers([f["x"] for _, fl in usable for f in fl])
            if not centers:
                out.append({"start": s, "end": e, "x": round(last, 4)})
                continue
            if len(centers) == 1 or not usable:
                plan = [(s, e, 0)]
            else:
                acts = []
                for _t, fl in usable:
                    row = [0.0] * len(centers)
                    for f in fl:
                        k = min(
                            range(len(centers)), key=lambda i: abs(f["x"] - centers[i])
                        )
                        row[k] += f["act"]
                    acts.append(row)
                plan = plan_switches(
                    [t for t, _ in usable], acts, len(centers), dwell
                )
            for sh in plan_to_shots(plan, s, e, centers):
                out.append(sh)
                last = sh["x"]
        return merge_short(out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def build_x_expr(shots, start, sw, cw):
    """Step-wise crop-x expression (pixels) for a time-varying crop."""
    span = sw - cw
    if not shots or span <= 0:
        return None

    def px(xf):
        return int(min(max(round(xf * sw - cw / 2), 0), span))

    expr = px(shots[-1]["x"])
    for sh in reversed(shots[:-1]):
        t_rel = round(float(sh["end"]) - start, 3)
        expr = f"if(lt(t,{t_rel}),{px(sh['x'])},{expr})"
    return str(expr)
