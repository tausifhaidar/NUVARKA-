import subprocess
from pathlib import Path

def run(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-4000:] or "Media command failed")

def probe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError("Could not read video duration. Is FFmpeg installed?")
    return float(result.stdout.strip())

def render_clip(source: Path, output: Path, start: float, duration: float,
                subtitle_file: Path | None = None) -> None:
    """Render a 9:16 clip while preserving the full source frame.

    A blurred, cover-scaled copy fills the vertical canvas; the original video
    is fit on top. This avoids the aggressive center crop that can cut off
    faces or important action in landscape footage.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    graph = (
        "[0:v]split=2[bg][fg];"
        "[bg]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=22:10[background];"
        "[fg]scale=1080:1920:force_original_aspect_ratio=decrease,"
        "setsar=1[foreground];"
        "[background][foreground]overlay=(W-w)/2:(H-h)/2"
    )
    if subtitle_file:
        escaped = str(subtitle_file.resolve()).replace("\\", "/").replace(":", r"\\:")
        graph += f",subtitles='{escaped}'"
    graph += ",setsar=1[video]"
    run([
        "ffmpeg", "-y", "-ss", str(max(0, start)), "-i", str(source),
        "-t", str(duration), "-filter_complex", graph,
        "-map", "[video]", "-map", "0:a?",
        "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(output)
    ])
