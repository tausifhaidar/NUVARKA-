from app.highlights import choose_segments

def test_selects_valid_window():
    transcript = [
        {"start": 0, "end": 8, "text": "Here is the important truth about this topic."},
        {"start": 8, "end": 20, "text": "The best way to understand why this works is to look carefully."},
        {"start": 20, "end": 40, "text": "This is another useful explanation with enough words to form a clip."},
        {"start": 40, "end": 55, "text": "Never make this common mistake because it matters."},
    ]
    result = choose_segments(transcript, 55, 2)
    assert result
    assert all(0 <= start < end <= 55 for start, end in result)
