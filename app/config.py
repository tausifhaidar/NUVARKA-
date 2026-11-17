import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", BASE_DIR / "outputs"))
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
MAX_CLIPS = int(os.getenv("MAX_CLIPS", "10"))
MIN_CLIP_SECONDS = int(os.getenv("MIN_CLIP_SECONDS", "30"))
MAX_CLIP_SECONDS = int(os.getenv("MAX_CLIP_SECONDS", "60"))

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
