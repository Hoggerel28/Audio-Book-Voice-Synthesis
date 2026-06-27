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
  - 支持 10 种基础中文音色。
  - 支持默认、开心、温柔、严肃、激动、悲伤 6 种情绪模式。
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

运行后终端会显示类似下面的地址：

```text
Running on local URL: http://127.0.0.1:7860
```

然后在浏览器打开：

```text
http://127.0.0.1:7860
```

注意：`127.0.0.1:7860` 是本地临时网页，不是一直在线的网站。必须先运行 `python app.py`，服务启动后才能访问；如果关闭 PowerShell、电脑重启、进程退出，网页就会显示无法访问。

如果运行 `python app.py` 后提示 `No module named 'gradio'`，说明当前 Python 没装依赖，请先运行：

```bash
python -m pip install -r requirements.txt
```

如果你在 Codex 工作目录中测试，也可以使用已经安装依赖的 Python：

```powershell
& "C:\Users\杨瑞\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" app.py
```

## GitHub Pages 静态展示页

仓库根目录下的 `index.html`、`styles.css`、`script.js` 是给 GitHub Pages 用的静态展示页。

- 可以在浏览器里直接导入 TXT 并预览文本。
- 不负责真正的语音合成。
- 真正的 MP3 导出仍然使用本地 `python app.py`。

如果你要发布到 GitHub Pages，通常直接把仓库根目录作为发布源即可。

## 网页使用方法

1. 上传 `examples/sample_story.txt`。
2. 点击“读取并预处理文本”。
3. 选择基础音色、情绪、语速和音调。
4. “合成句数上限”填 `0` 表示全文合成。
5. 点击“开始合成有声读物”。
6. 在页面下方播放或下载生成的 MP3。

## 音色与情绪

当前基础音色共 10 种：

```text
中文女声-晓晓（自然）
中文男声-云希（清朗）
中文男声-云健（稳重）
中文女声-晓伊（活泼）
中文女声-辽宁方言
中文男声-陕西方言
中文女声-小双（童声）
中文女声-小梦（温柔）
粤语女声-晓敏
台湾男声-云哲
```

当前情绪模式共 6 种：

```text
默认：保持基础音色
开心：语速略快，音调略高
温柔：语速略慢，音调柔和
严肃：语速偏慢，音调偏低
激动：语速更快，音调更高
悲伤：语速更慢，音调更低
```

情绪模式通过调整语速和音调实现，优点是稳定、容易演示，也方便写进课程设计报告。

## 输出示例

示例输入文件：

```text
examples/sample_story.txt
```

对应的完整合成音频：

```text
outputs/sample_story_full.mp3
```

生成完整样本音频的命令：

```bash
python scripts/generate_sample_audio.py
```

仓库里也保留了旧的快速测试音频：

```text
outputs/test_demo.mp3
```

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
