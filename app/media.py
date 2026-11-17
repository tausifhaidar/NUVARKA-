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
    output.parent.mkdir(parents=True, exist_ok=True)
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    if subtitle_file:
        escaped = str(subtitle_file.resolve()).replace("\\", "/").replace(":", r"\\:")
        vf += f",subtitles='{escaped}'"
    run([
        "ffmpeg", "-y", "-ss", str(max(0, start)), "-i", str(source),
        "-t", str(duration), "-vf", vf, "-r", "30",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(output)
    ])
