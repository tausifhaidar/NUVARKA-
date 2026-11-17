from pathlib import Path
from faster_whisper import WhisperModel
from .config import WHISPER_MODEL

_model = None

def transcribe(path: Path) -> list[dict]:
    global _model
    if _model is None:
        _model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    segments, _ = _model.transcribe(str(path), vad_filter=True)
    return [
        {"start": float(s.start), "end": float(s.end), "text": s.text.strip()}
        for s in segments if s.text.strip()
    ]
