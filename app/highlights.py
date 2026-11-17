import re
from .config import MIN_CLIP_SECONDS, MAX_CLIP_SECONDS

HOOK_WORDS = {"why", "how", "secret", "mistake", "never", "best", "worst",
              "truth", "important", "amazing", "because", "surprising"}

def choose_segments(transcript: list[dict], duration: float, count: int) -> list[tuple[float, float]]:
    if not transcript:
        return [(0.0, min(duration, MAX_CLIP_SECONDS))]
    candidates = []
    # Build windows anchored at transcript segments; score useful, information-rich speech.
    for item in transcript:
        start = max(0.0, item["start"] - 1.0)
        end = min(duration, start + MAX_CLIP_SECONDS)
        if end - start < MIN_CLIP_SECONDS:
            start = max(0.0, end - MIN_CLIP_SECONDS)
        if end - start < min(MIN_CLIP_SECONDS, duration):
            continue
        text = " ".join(
            x["text"] for x in transcript
            if x["start"] < end and x["end"] > start
        ).lower()
        words = re.findall(r"\b[a-z0-9']+\b", text)
        if len(words) < 12:
            continue
        score = min(len(words), 180) / 30
        score += sum(1.5 for w in words if w in HOOK_WORDS)
        score += min(text.count("?") * 0.7, 3)
        candidates.append((score, start, end))
    candidates.sort(reverse=True)
    chosen = []
    for _, start, end in candidates:
        if all(end <= a or start >= b for a, b in chosen):
            chosen.append((start, end))
        if len(chosen) >= count:
            break
    if not chosen:
        chosen = [(0.0, min(duration, MAX_CLIP_SECONDS))]
    return sorted(chosen)
