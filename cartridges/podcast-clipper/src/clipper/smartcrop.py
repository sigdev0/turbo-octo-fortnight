import os
import subprocess
import tempfile
import urllib.request

import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

MODEL_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/"
    "models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
)
MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "work", ".yunet.onnx"
)
MODEL_PATH = os.path.normpath(MODEL_PATH)


def ensure_model(path=MODEL_PATH, url=MODEL_URL):
    if os.path.exists(path) and os.path.getsize(path) > 100_000:
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    urllib.request.urlretrieve(url, tmp)
    os.replace(tmp, path)
    return path


def sample_frames(source, start, end, n=8, width=320):
    dur = max(end - start, 0.1)
    paths = []
    tmpdir = tempfile.mkdtemp(prefix="smartcrop_")
    for i in range(n):
        t = start + dur * (i + 0.5) / n
        out = os.path.join(tmpdir, f"f{i}.jpg")
        r = subprocess.run(
            [FFMPEG, "-y", "-v", "error", "-ss", str(t), "-i", source,
             "-frames:v", "1", "-vf", f"scale={width}:-1", out],
            capture_output=True,
            check=False,
        )
        if r.returncode == 0 and os.path.exists(out):
            paths.append(out)
    return paths


def detect_centers(frames, score_thresh=0.5):
    import cv2

    model = ensure_model()
    weighted = []
    det = None
    for fp in frames:
        img = cv2.imread(fp)
        if img is None:
            continue
        h, w = img.shape[:2]
        if det is None:
            det = cv2.FaceDetectorYN_create(model, "", (w, h), score_thresh)
        else:
            det.setInputSize((w, h))
        _, faces = det.detect(img)
        if faces is None or len(faces) == 0:
            continue
        for f in faces:
            x, bw, bh = float(f[0]), float(f[2]), float(f[3])
            area = (bw / w) * (bh / h)
            weighted.append(((x + bw / 2) / w, area))
    return weighted


def smooth_x(centers, fallback=0.5, agree_thresh=0.7, margin=0.12):
    if not centers:
        return fallback
    if centers and isinstance(centers[0], (list, tuple)):
        tot = sum(a for _, a in centers)
        if tot <= 0:
            return fallback
        med = sum(x * a for x, a in centers) / tot
    else:
        xs = sorted(centers)
        med = xs[len(xs) // 2]
    if abs(med - 0.5) < margin:
        return fallback
    if isinstance(centers[0], (list, tuple)):
        side_w = sum(a for x, a in centers if (x < 0.5) == (med < 0.5))
        if side_w / tot < agree_thresh:
            return fallback
    else:
        side = [x for x in centers if (x < 0.5) == (med < 0.5)]
        if len(side) / len(centers) < agree_thresh:
            return fallback
    return min(max(med, 0.15), 0.85)


def smart_cx(source, start, end, settings=None, n=8):
    cfg = (settings or {}).get("clips", {})
    if not cfg.get("smart_crop", False):
        return None
    frames = []
    try:
        frames = sample_frames(
            source, start, end, n=cfg.get("smart_crop_samples", n)
        )
        if not frames:
            return None
        centers = detect_centers(
            frames, cfg.get("smart_crop_thresh", 0.5)
        )
        return smooth_x(centers)
    except Exception as e:  # noqa: BLE001 - any failure falls back to center
        print(f"  smart_crop failed ({e}), using center")
        return None
    finally:
        import shutil

        for fp in frames:
            d = os.path.dirname(fp)
            if os.path.isdir(d):
                shutil.rmtree(d, ignore_errors=True)
                break
