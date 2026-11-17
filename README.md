# AI Clipping

Open-source starter for turning a permitted video source into short vertical clips (30–60 seconds) with transcript-based highlight selection and burned-in subtitles.

## What this version does
- Accepts a local video upload through the FastAPI API.
- Accepts a YouTube URL through the API using yt-dlp. Only process videos you own or have permission to download; respect platform terms and copyright.
- Transcribes audio locally with faster-whisper (CPU mode by default).
- Selects candidate 30–60 second segments using transcript sentence scoring.
- Renders 9:16 MP4 clips with subtitles using FFmpeg.

## Important limitations
- This is a starter backend, not a hosted public website or always-on API.
- GitHub is used for source code and GitHub Actions automation. Actions is temporary CI compute, not a permanent video server; long videos may exceed runner time, storage, or memory limits.
- The initial crop is centered. Face-aware tracking, speaker diarization, and advanced semantic highlight ranking are not implemented yet.
- No paid AI API key is required. Whisper model files are downloaded on first use; choose a smaller model for CPU/low-memory runs.

## Run locally
Requires Python 3.10+ and FFmpeg installed and available on PATH.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs for the API.

## API
- `GET /` health/info
- `POST /api/clip/upload` multipart form field `file`
- `POST /api/clip/youtube` JSON: `{"url":"https://www.youtube.com/watch?v=...","clips":5}`

Response includes generated clip paths. For local use, files are stored under `outputs/`.

## GitHub Actions demo
Use Actions → **Manual clip demo** → Run workflow. Provide a direct video URL that the runner can access and that you are authorized to process. The job uploads resulting MP4s as an artifact. This is best for short demo videos, not production workloads.

## Configuration
- `WHISPER_MODEL`: default `base`; use `tiny` for faster CPU processing.
- `MAX_CLIPS`: default `10`.
- `MIN_CLIP_SECONDS` / `MAX_CLIP_SECONDS`: defaults 30 / 60.

## License
MIT for this project code. Third-party models, model weights, FFmpeg, and source videos have their own licenses and terms.