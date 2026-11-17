from pathlib import Path

def write_srt(transcript: list[dict], start: float, end: float, path: Path) -> Path:
    def stamp(seconds: float) -> str:
        ms = int(max(0, seconds) * 1000)
        h, rem = divmod(ms, 3_600_000)
        m, rem = divmod(rem, 60_000)
        s, milli = divmod(rem, 1000)
        return f"{h:02}:{m:02}:{s:02},{milli:03}"
    rows = []
    index = 1
    for segment in transcript:
        a, b = max(start, segment["start"]), min(end, segment["end"])
        if b <= a:
            continue
        text = segment["text"].replace("-->", "→").strip()
        rows.append(f"{index}\n{stamp(a-start)} --> {stamp(b-start)}\n{text}\n")
        index += 1
    path.write_text("\n".join(rows), encoding="utf-8")
    return path
