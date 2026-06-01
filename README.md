# 基于语音合成的有声读物生成算法设计与实现

这是一个机器学习课程设计项目，目标是把 TXT / PDF / EPUB 读物文本转换为有声读物音频。

## 已实现功能

- 支持 TXT、PDF、EPUB 文件导入。
- 文本预处理：
  - 清理多余空格、换行和特殊符号。
  - 自动分句。
  - 长句二次切分，避免一次输入过长。
  - 提供简单多音字规则说明，便于课程报告分析。
- 语音合成：
  - 使用 edge-tts 在线合成。
  - 支持多种基础中文音色。
  - 支持语速和音调调节。
  - 支持 MP3 导出。
  - 如果本机有 ffmpeg，可额外导出 WAV。
- 网页界面：
  - 使用 Gradio 搭建。
  - 可上传文件、预览文本、查看分句、播放和下载音频。
- 参考音频入口：
  - 当前版本只作为后续扩展预留，不进行真实音色克隆。

## 目录结构

```text
.
├── app.py
├── requirements.txt
├── README.md
├── src/
│   ├── file_reader.py
│   ├── text_preprocess.py
│   └── tts_engine.py
├── notebooks/
│   └── voice_audiobook_generator.ipynb
├── examples/
│   └── sample_story.txt
└── outputs/
```

## 安装依赖

```bash
pip install -r requirements.txt
```

如果只演示 TXT/PDF，可暂时不安装 EPUB 相关依赖。

## 运行网页系统

```bash
python app.py
```

运行后浏览器会打开 Gradio 页面。（目前还在测试阶段）

## 运行 Notebook

打开：

```text
notebooks/voice_audiobook_generator.ipynb
```

从上到下运行即可。运行完成后可导出 HTML，作为课程要求中的 Notebook HTML 文件。

## 注意事项

- edge-tts 需要联网。
- 影视剧、动漫角色音色可能涉及版权问题，本项目当前版本不复刻具体角色声音。
- 不要上传身份证、手机号、账号密码、真实病历、公司内部资料等敏感数据。
