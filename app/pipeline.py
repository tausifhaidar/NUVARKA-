from pathlib import Path
import uuid
from .config import OUTPUT_DIR, MAX_CLIPS
from .media import probe_duration, render_clip
from .transcription import transcribe
from .highlights import choose_segments
from .subtitles import write_srt

def process_video(source: Path, requested_clips: int = 5) -> list[str]:
    duration = probe_duration(source)
    transcript = transcribe(source)
    windows = choose_segments(transcript, duration, min(requested_clips, MAX_CLIPS))
    job_dir = OUTPUT_DIR / uuid.uuid4().hex[:12]
    job_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for index, (start, end) in enumerate(windows, 1):
        subtitle = write_srt(transcript, start, end, job_dir / f"clip_{index:02}.srt")
        output = job_dir / f"clip_{index:02}.mp4"
        render_clip(source, output, start, end - start, subtitle)
        results.append(str(output))
    return results
