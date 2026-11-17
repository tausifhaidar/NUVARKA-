import json
import subprocess
from pathlib import Path


def run(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-4000:] or "Media command failed")


def probe(path: Path) -> dict:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "json", str(path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError("Could not read video dimensions. Is FFmpeg installed?")
    streams = json.loads(result.stdout).get("streams", [])
    if not streams:
        raise RuntimeError("No video stream found")
    return streams[0]


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError("Could not read video duration. Is FFmpeg installed?")
    return float(result.stdout.strip())


def detect_face_center(path: Path) -> float | None:
    """Return median face-center x as a 0..1 frame fraction, or None.

    Samples at most 24 frames with OpenCV's bundled Haar cascade. This is
    deliberately a lightweight framing aid, not identity recognition.
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        return None

    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        return None
    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    duration = frame_count / fps if frame_count else 0
    if duration <= 0:
        capture.release()
        return None

    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(str(cascade_path))
    centers = []
    for second in np.linspace(0, max(0, duration - 0.1), num=min(24, max(1, int(duration) + 1)):
        capture.set(cv2.CAP_PROP_POS_MSEC, float(second) * 1000)
        ok, frame = capture.read()
        if not ok:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(40, 40))
        if len(faces):
            x, y, width, height = max(faces, key=lambda face: face[2] * face[3])
            centers.append((x + width / 2) / frame.shape[1])
    capture.release()
    return float(np.median(centers)) if centers else None


def render_clip(source: Path, output: Path, start: float, duration: float,
                subtitle_file: Path | None = None) -> None:
    """Render a 9:16 clip, using a face-guided crop when a face is detected.

    If no face is detected (or OpenCV is unavailable), preserve the full source
    frame over a blurred background canvas instead of cutting off the sides.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    dimensions = probe(source)
    width, height = int(dimensions["width"]), int(dimensions["height"])
    face_x = detect_face_center(source) if width > height else None

    if face_x is not None and width / height > 9 / 16:
        scaled_width = max(1080, round(width * 1920 / height))
        crop_x = max(0, min(scaled_width - 1080, round(face_x * scaled_width - 540)))
        graph = (
            f"[0:v]scale={scaled_width}:1920,crop=1080:1920:{crop_x}:0,"
            "setsar=1[video]"
        )
    else:
        graph = (
            "[0:v]split=2[bg][fg];"
            "[bg]scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,boxblur=22:10[background];"
            "[fg]scale=1080:1920:force_original_aspect_ratio=decrease,"
            "setsar=1[foreground];"
            "[background][foreground]overlay=(W-w)/2:(H-h)/2"
        )
        graph += ",setsar=1[video]"

    if subtitle_file:
        escaped = str(subtitle_file.resolve()).replace("\\", "/").replace(":", r"\\:")
        graph = graph.replace("[video]", f",subtitles='{escaped}'[video]")

    run([
        "ffmpeg", "-y", "-ss", str(max(0, start)), "-i", str(source),
        "-t", str(duration), "-filter_complex", graph,
        "-map", "[video]", "-map", "0:a?",
        "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(output)
    ])
