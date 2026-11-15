
from pathlib import Path

from faster_whisper import WhisperModel


# Lightweight CPU model
_model = None


def get_whisper_model():
    global _model

    if _model is None:
        _model = WhisperModel(
            "tiny",
            device="cpu",
            compute_type="int8",
        )

    return _model


def transcribe_video_audio(video_path: str) -> dict:
    path = Path(video_path)

    if not path.exists():
        raise FileNotFoundError("Uploaded video file was not found.")

    model = get_whisper_model()

    segments, info = model.transcribe(
        str(path),
        beam_size=1,
        vad_filter=True,
    )

    transcript_segments = []

    for segment in segments:
        transcript_segments.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip(),
        })

    full_text = " ".join(
        item["text"] for item in transcript_segments
    )

    return {
        "language": info.language,
        "duration_seconds": round(info.duration, 2),
        "transcript": full_text,
        "segments": transcript_segments,
    }
