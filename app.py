"""Gradio 网页应用。"""
from __future__ import annotations

from pathlib import Path

import gradio as gr

from src.file_reader import read_book_file
from src.text_preprocess import preprocess_text
from src.tts_engine import PITCH_OPTIONS, RATE_OPTIONS, VOICE_OPTIONS, synthesize_audiobook

LAST_SENTENCES: list[str] = []


def load_and_preprocess(file, max_len: int):
    global LAST_SENTENCES
    if file is None:
        return "请先上传 TXT、PDF 或 EPUB 文件。", "", "", ""
    try:
        path = Path(file.name)
        raw_text = read_book_file(path)
        result = preprocess_text(raw_text, max_len=max_len)
        LAST_SENTENCES = result.sentences
        preview = result.cleaned_text[:1200]
        sentence_preview = "\n".join(f"{i+1}. {s}" for i, s in enumerate(result.sentences[:30]))
        notes = "\n".join(result.correction_notes) if result.correction_notes else "未命中示例多音字规则，交由 TTS 引擎自动处理读音。"
        info = f"读取成功：{path.name}\n原文预览 {len(preview)} 字；分句 {len(result.sentences)} 段。"
        return info, preview, sentence_preview, notes
    except Exception as exc:
        LAST_SENTENCES = []
        return f"处理失败：{exc}", "", "", ""


def synthesize_from_ui(voice, rate, pitch, export_limit):
    if not LAST_SENTENCES:
        return None, None, "请先上传文件并完成文本预处理。"
    try:
        limit = int(export_limit) if export_limit else None
        if limit <= 0:
            limit = None
        result = synthesize_audiobook(
            LAST_SENTENCES,
            voice_label=voice,
            rate_label=rate,
            pitch_label=pitch,
            output_dir="outputs",
            max_sentences=limit,
        )
        download = result.wav_path or result.mp3_path
        return result.mp3_path, download, result.message
    except Exception as exc:
        return None, None, f"合成失败：{exc}\n请确认已联网，并安装 edge-tts。"


def build_demo():
    with gr.Blocks(title="基于语音合成的有声读物生成系统") as demo:
        gr.Markdown(
            """
            # 基于语音合成的有声读物生成系统
            支持 TXT / PDF / EPUB 导入、文本预处理、基础音色选择、语速和音调调节、MP3/WAV 导出。  
            说明：参考音频入口为后续扩展预留，当前版本不进行真实音色克隆。
            """
        )
        with gr.Row():
            file_input = gr.File(label="上传读物文件", file_types=[".txt", ".pdf", ".epub"])
            reference_audio = gr.Audio(label="参考音频（扩展预留，不参与当前合成）", type="filepath")
        max_len = gr.Slider(40, 200, value=120, step=10, label="单句最大长度")
        preprocess_btn = gr.Button("读取并预处理文本", variant="primary")

        status = gr.Textbox(label="处理状态")
        text_preview = gr.Textbox(label="文本预览", lines=8)
        sentence_preview = gr.Textbox(label="分句结果预览（前30句）", lines=10)
        notes = gr.Textbox(label="多音字处理说明", lines=4)

        with gr.Row():
            voice = gr.Dropdown(list(VOICE_OPTIONS.keys()), value="中文女声-晓晓（自然）", label="基础音色")
            rate = gr.Dropdown(list(RATE_OPTIONS.keys()), value="正常", label="语速")
            pitch = gr.Dropdown(list(PITCH_OPTIONS.keys()), value="中", label="音调")
            export_limit = gr.Number(value=20, precision=0, label="演示合成句数上限，0表示全部")

        synth_btn = gr.Button("开始合成有声读物", variant="primary")
        audio_output = gr.Audio(label="合成音频预览", type="filepath")
        download_file = gr.File(label="下载音频文件")
        synth_status = gr.Textbox(label="合成状态")

        preprocess_btn.click(
            load_and_preprocess,
            inputs=[file_input, max_len],
            outputs=[status, text_preview, sentence_preview, notes],
        )
        synth_btn.click(
            synthesize_from_ui,
            inputs=[voice, rate, pitch, export_limit],
            outputs=[audio_output, download_file, synth_status],
        )
    return demo


if __name__ == "__main__":
    build_demo().launch()
