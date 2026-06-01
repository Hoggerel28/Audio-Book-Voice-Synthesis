"""语音合成模块：使用 edge-tts 生成 MP3，并尽量转换 WAV。"""
from __future__ import annotations

import asyncio
import shutil
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


VOICE_OPTIONS = {
    "中文女声-晓晓（自然）": "zh-CN-XiaoxiaoNeural",
    "中文男声-云希（清朗）": "zh-CN-YunxiNeural",
    "中文男声-云健（稳重）": "zh-CN-YunjianNeural",
    "中文女声-晓伊（活泼）": "zh-CN-XiaoyiNeural",
    "中文女声-辽宁方言": "zh-CN-liaoning-XiaobeiNeural",
    "中文男声-陕西方言": "zh-CN-shaanxi-XiaoniNeural",
}

RATE_OPTIONS = {
    "慢速": "-20%",
    "正常": "+0%",
    "快速": "+20%",
}

PITCH_OPTIONS = {
    "低": "-8Hz",
    "中": "+0Hz",
    "高": "+8Hz",
}


@dataclass
class SynthesisResult:
    mp3_path: str
    wav_path: str | None
    message: str


async def _save_edge_tts(text: str, voice: str, rate: str, pitch: str, output_path: Path) -> None:
    import edge_tts
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
    await communicate.save(str(output_path))


def synthesize_sentence(text: str, voice: str, rate: str, pitch: str, output_path: Path) -> None:
    """合成单段语音。"""
    asyncio.run(_save_edge_tts(text, voice, rate, pitch, output_path))


def merge_mp3_files(mp3_files: list[Path], output_path: Path) -> None:
    """合并多个 MP3。优先使用 pydub，没有则保留第一段或拼接二进制作为降级方案。"""
    if not mp3_files:
        raise ValueError("没有可合并的音频片段")
    try:
        from pydub import AudioSegment
        combined = AudioSegment.empty()
        pause = AudioSegment.silent(duration=350)
        for file in mp3_files:
            combined += AudioSegment.from_file(file, format="mp3") + pause
        combined.export(output_path, format="mp3")
        return
    except Exception:
        pass

    if len(mp3_files) == 1:
        shutil.copyfile(mp3_files[0], output_path)
    else:
        with output_path.open("wb") as out:
            for file in mp3_files:
                out.write(file.read_bytes())


def convert_mp3_to_wav(mp3_path: Path, wav_path: Path) -> bool:
    """尝试把 MP3 转 WAV。需要 pydub 和 ffmpeg 支持。"""
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(mp3_path, format="mp3")
        audio.export(wav_path, format="wav")
        return True
    except Exception:
        return False


def synthesize_audiobook(
    sentences: list[str],
    voice_label: str,
    rate_label: str,
    pitch_label: str,
    output_dir: str | Path = "outputs",
    basename: str | None = None,
    max_sentences: int | None = None,
) -> SynthesisResult:
    """分句合成有声读物。"""
    if not sentences:
        raise ValueError("没有可合成的文本，请先导入并预处理文本")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    basename = basename or f"audiobook_{uuid4().hex[:8]}"

    voice = VOICE_OPTIONS.get(voice_label, voice_label)
    rate = RATE_OPTIONS.get(rate_label, rate_label)
    pitch = PITCH_OPTIONS.get(pitch_label, pitch_label)

    use_sentences = sentences[:max_sentences] if max_sentences else sentences
    temp_dir = output_dir / f"tmp_{basename}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    part_files: list[Path] = []
    try:
        for index, sentence in enumerate(use_sentences, start=1):
            part_path = temp_dir / f"part_{index:04d}.mp3"
            synthesize_sentence(sentence, voice, rate, pitch, part_path)
            part_files.append(part_path)

        mp3_path = output_dir / f"{basename}.mp3"
        wav_path = output_dir / f"{basename}.wav"
        merge_mp3_files(part_files, mp3_path)
        wav_ok = convert_mp3_to_wav(mp3_path, wav_path)
        message = f"合成完成：共处理 {len(use_sentences)} 段文本。"
        if not wav_ok:
            message += " WAV 转换需要 ffmpeg 支持，当前已生成 MP3。"
        return SynthesisResult(str(mp3_path), str(wav_path) if wav_ok else None, message)
    finally:
        for file in part_files:
            try:
                file.unlink()
            except OSError:
                pass
        try:
            temp_dir.rmdir()
        except OSError:
            pass
