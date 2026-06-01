"""文本预处理模块：清洗、分句、多音字提示性纠错。"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class PreprocessResult:
    cleaned_text: str
    corrected_text: str
    sentences: list[str]
    correction_notes: list[str]


POLYPHONE_RULES = [
    (r"银行|行业|行长|排行", "行", "háng", "命中 银行/行业/行长/排行，按 háng 处理"),
    (r"行走|行人|不行|可以行", "行", "xíng", "命中 行走/行人/不行，按 xíng 处理"),
    (r"重量|重要|重心|严重", "重", "zhòng", "命中 重量/重要/重心/严重，按 zhòng 处理"),
    (r"重复|重新|重来|重播", "重", "chóng", "命中 重复/重新/重来/重播，按 chóng 处理"),
    (r"音乐|乐器|声乐|乐谱", "乐", "yuè", "命中 音乐/乐器/声乐/乐谱，按 yuè 处理"),
    (r"快乐|乐观|欢乐|乐意", "乐", "lè", "命中 快乐/乐观/欢乐/乐意，按 lè 处理"),
]


def clean_text(text: str) -> str:
    """清理多余空白、重复换行和影响合成的杂乱字符。"""
    if not text:
        return ""
    text = text.replace("\ufeff", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\t\u3000]+", " ", text)
    text = re.sub(r" *\n+ *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def polyphone_correction_notes(text: str) -> list[str]:
    """生成多音字处理说明。edge-tts 会自动读音，这里保留可解释规则，便于报告展示。"""
    notes: list[str] = []
    for pattern, char, pinyin, note in POLYPHONE_RULES:
        if re.search(pattern, text):
            notes.append(f"{char} → {pinyin}：{note}")
    return notes


def normalize_for_tts(text: str) -> str:
    """对文本做适合 TTS 的轻量规范化。"""
    replacements = {
        "……": "，",
        "——": "，",
        "“": "",
        "”": "",
        "‘": "",
        "’": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def split_long_sentence(sentence: str, max_len: int) -> list[str]:
    """过长句子按逗号、顿号等二次切分。"""
    if len(sentence) <= max_len:
        return [sentence]
    parts = re.split(r"(?<=[，,、：:])", sentence)
    result: list[str] = []
    buffer = ""
    for part in parts:
        if not part:
            continue
        if len(buffer) + len(part) <= max_len:
            buffer += part
        else:
            if buffer.strip():
                result.append(buffer.strip())
            buffer = part
    if buffer.strip():
        result.append(buffer.strip())

    final: list[str] = []
    for item in result:
        if len(item) <= max_len:
            final.append(item)
        else:
            final.extend(item[i:i + max_len] for i in range(0, len(item), max_len))
    return final


def split_sentences(text: str, max_len: int = 120) -> list[str]:
    """按中文标点分句，并控制每段最大长度。"""
    text = text.replace("\n", "。")
    raw_sentences = re.split(r"(?<=[。！？!?；;])", text)
    sentences: list[str] = []
    for raw in raw_sentences:
        raw = raw.strip()
        if not raw:
            continue
        sentences.extend(split_long_sentence(raw, max_len=max_len))
    return [s for s in sentences if s.strip()]


def preprocess_text(text: str, max_len: int = 120) -> PreprocessResult:
    """完整文本预处理流程。"""
    cleaned = clean_text(text)
    corrected = normalize_for_tts(cleaned)
    notes = polyphone_correction_notes(cleaned)
    sentences = split_sentences(corrected, max_len=max_len)
    return PreprocessResult(
        cleaned_text=cleaned,
        corrected_text=corrected,
        sentences=sentences,
        correction_notes=notes,
    )
