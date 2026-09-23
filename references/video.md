# 可选：本地配音视频

只在用户要求视频时执行。输出 MP4 保存在本地；默认 edge-tts 会将讲稿发送给在线语音服务，所以“本地视频”不等于离线合成。向用户说明这一点；用户要求离线时，使用已有逐页录音或已配置的本地 TTS，不调用 edge-tts。

## 输入与依赖

输入是最终幻灯片 PDF（Beamer 或 PowerPoint 导出的 PDF 均可），以及 UTF-8 JSON 数组。每一项按物理页顺序填写，条目数量必须与 PDF 页数一致：

```json
[
  {"page": 1, "text": "本次分享介绍论文的研究问题与主要结论。"},
  {"page": 2, "text": "第二页的完整讲稿。"}
]
```

有录音时，各项增加 `"audio": "audio/page-001.wav"`，相对路径按 JSON 所在目录解析。支持 ffmpeg 能解码的音频；每页必须有非空讲稿和有效音频。不要用静音代替缺失的讲稿。

脚本自身只依赖 Python 标准库；外部工具为 `pdfinfo`、`pdftoppm`、`ffmpeg`、`ffprobe`。在线配音另需 `edge-tts` 命令。可以用 `PDFINFO`、`PDFTOPPM`、`FFMPEG`、`FFPROBE`、`EDGE_TTS_BIN` 指定工具路径。也支持用户目录安装的 static_ffmpeg / static_ffprobe，找不到系统命令时自动使用。无管理员权限时可用 `uv tool install static-ffmpeg` 和 `uv tool install edge-tts`，随后运行 `static_ffmpeg_paths` 完成一次性二进制下载；离线合成前需已完成下载。仅在当前任务需要时补齐缺少的依赖。

## 执行

先验证页码与输入（不联网、不生成视频）：

```bash
python3 "<SKILL_DIR>/scripts/local_video.py" "<slides.pdf>" "<narrations.json>" --check
```

在线中文配音：

```bash
python3 "<SKILL_DIR>/scripts/local_video.py" "<slides.pdf>" "<narrations.json>" \
  --engine edge --output "<paper_dir>/video/presentation.mp4"
```

使用已有音频（不调用语音服务）：

```bash
python3 "<SKILL_DIR>/scripts/local_video.py" "<slides.pdf>" "<narrations.json>" \
  --engine audio --output "<paper_dir>/video/presentation.mp4"
```

默认中文音色 `zh-CN-XiaoxiaoNeural`，英文可用 `--voice en-US-AriaNeural`。`--rate` 默认 `+0%`，不自动加速讲稿。视频高度默认 1080，宽度按 PDF 页面比例取偶数；每页持续到本页音频结束。

生成前所有输入先校验；构建使用独立临时目录，成功后才放置最终 MP4。已有输出默认拒绝覆盖，用户确实需要替换时加 `--overwrite`。失败保留原视频。

检查实际播放、逐页音画匹配和公式可读性。脚本验证非零时长及音视频流，不能替代听辨发音。缺少工具或未执行在线 TTS 时，如实报告，不声称已生成或验证配音。
