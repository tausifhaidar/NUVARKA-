from pathlib import Path
import shutil
import uuid
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from yt_dlp import YoutubeDL
from .config import UPLOAD_DIR, OUTPUT_DIR
from .pipeline import process_video
from .schemas import YoutubeClipRequest

app = FastAPI(title="AI Clipping API", version="0.1.0",
              description="Local, open-source transcript-based video clipping starter.")
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

@app.get("/")
def home():
    return {"name": "AI Clipping", "status": "ready", "docs": "/docs"}

@app.post("/api/clip/upload")
async def clip_upload(file: UploadFile = File(...), clips: int = 5):
    if clips < 1 or clips > 10:
        raise HTTPException(400, "clips must be between 1 and 10")
    suffix = Path(file.filename or "video.mp4").suffix or ".mp4"
    if suffix.lower() not in {".mp4", ".mov", ".mkv", ".webm", ".avi"}:
        raise HTTPException(400, "Unsupported video format")
    source = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"
    try:
        with source.open("wb") as target:
            shutil.copyfileobj(file.file, target)
        paths = process_video(source, clips)
        return {"clips": ["/outputs/" + str(Path(p).relative_to(OUTPUT_DIR)) for p in paths]}
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc
    finally:
        source.unlink(missing_ok=True)

@app.post("/api/clip/youtube")
def clip_youtube(request: YoutubeClipRequest):
    source = UPLOAD_DIR / f"{uuid.uuid4().hex}.mp4"
    try:
        options = {"format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                   "merge_output_format": "mp4", "outtmpl": str(source),
                   "quiet": True, "noplaylist": True}
        with YoutubeDL(options) as ydl:
            ydl.download([str(request.url)])
        if not source.exists():
            # yt-dlp may append the final extension when merging.
            matches = list(UPLOAD_DIR.glob(source.stem + ".*"))
            if not matches:
                raise RuntimeError("Download did not produce a video file")
            source = matches[0]
        paths = process_video(source, request.clips)
        return {"clips": ["/outputs/" + str(Path(p).relative_to(OUTPUT_DIR)) for p in paths]}
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc
    finally:
        for candidate in UPLOAD_DIR.glob(source.stem + ".*"):
            candidate.unlink(missing_ok=True)
