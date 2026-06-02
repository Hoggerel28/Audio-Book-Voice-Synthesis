"""Generate the full sample audiobook audio used for course demonstration."""
from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.file_reader import read_book_file
from src.text_preprocess import preprocess_text
from src.tts_engine import synthesize_audiobook


def main() -> None:
    text = read_book_file(PROJECT_ROOT / "examples" / "sample_story.txt")
    result = preprocess_text(text, max_len=80)

    print("示例文本分句：")
    for index, sentence in enumerate(result.sentences, start=1):
        print(f"{index}. {sentence}")

    audio = synthesize_audiobook(
        result.sentences,
        voice_label="中文女声-晓晓（自然）",
        rate_label="正常",
        pitch_label="中",
        output_dir=PROJECT_ROOT / "outputs",
        basename="sample_story_full",
    )
    print(audio.message)
    print("MP3:", audio.mp3_path)
    if audio.wav_path:
        print("WAV:", audio.wav_path)


if __name__ == "__main__":
    main()
