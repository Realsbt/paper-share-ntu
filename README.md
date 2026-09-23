# Paper Share · NTU

将论文 PDF、LaTeX 源码或 arXiv 链接制作成组会幻灯片、逐页中文讲稿，以及可选的配音视频。

本项目是 [paper-share-skills](https://github.com/yhbcode000/paper-share-skills) 与 [SUSTech Slides Template](https://github.com/yhbcode000/sustech-slides-template) 的个人适配版。保留原版 Beamer 主题与制作流程，默认使用 **南洋理工大学 / Nanyang Technological University** 标识，汇报人姓名由使用者填写。不包含 B 站登录、上传或自动发布功能。

这是个人汇报模板，不是 NTU 官方模板。请在生成幻灯片后填写 `slides-beamer/main.tex` 中的汇报人姓名；如需使用其他学校，请同步修改学校信息与校徽。

## 功能

- 原版 16:10 Beamer 版式：封面、双栏目录、章节页、卡片、独立大图、参考文献、Q&A 和附录。
- 优先读取 arXiv 的 LaTeX 源码与矢量图。
- 输出 PDF、可编辑 LaTeX 源码和逐页讲稿；默认不输出 `.pptx`。
- 附带 Noto 中文字体，嵌入字符映射，改善客户端 PDF 预览兼容性。
- 可选 edge-tts 中文配音，在本机合成 MP4；也支持已有录音。

## 安装到本机 Codex

将本仓库完整放入个人 skills 目录的 `paper-share` 文件夹。与本项目验证环境一致的安装示例：

```bash
git clone https://github.com/Realsbt/paper-share-ntu.git ~/.codex/skills/paper-share
```

若该目录已存在，请先保留自己的版本，不要直接覆盖。安装完成后在 Codex 中使用：

> 用 $paper-share 将这篇论文做成组会汇报，生成 PDF、源码和中文讲稿。

需要视频时追加：

> 生成完整中文配音视频。

## 依赖与本地使用

需要 Python 3、XeLaTeX（包含 ctex、Beamer 等常用宏包）和 Poppler（pdfinfo、pdftoppm、pdftotext）。主题与中文字体已随仓库附带，不必安装到系统字体目录。

```bash
python3 scripts/prepare.py doctor
python3 scripts/prepare.py init /path/to/paper
# 编辑 /path/to/paper/slides-beamer/main.tex，替换示例内容
python3 scripts/build.py /path/to/paper/slides-beamer
```

本地编译不需要联网；下载论文、核实作者背景及 edge-tts 配音需要联网。脚本会选择同一套 TeX 工具并配置主题路径。保留文稿旁边的字体、主题、校徽及图像目录。

## 可选视频

需要 FFmpeg、FFprobe；在线配音另需 edge-tts。已有 uv 时，可在用户目录安装：

```bash
uv tool install edge-tts
uv tool install static-ffmpeg
static_ffmpeg_paths
```

脚本支持系统 ffmpeg/ffprobe，也支持 static_ffmpeg/static_ffprobe。首次初始化 static-ffmpeg 需要下载二进制。

```bash
python3 scripts/local_video.py slides.pdf narrations.json --check
python3 scripts/local_video.py slides.pdf narrations.json --engine edge --output presentation.mp4
```

`narrations.json` 必须与 PDF 的每个物理页对应，包括章节过渡页；格式和录音模式见 [视频说明](references/video.md)。默认音色为 `zh-CN-XiaoxiaoNeural`。edge-tts 会将讲稿发送给在线语音服务；需要离线时使用已有逐页录音。

## 验证范围

2026-09-20 在维护者的 Linux 本机完成 38 页论文幻灯片编译、源码包解压重编译、PDF.js 中文显示检查，以及完整 1080p 中文配音视频生成。其他操作系统尚未实测。生成内容仍需核对论文证据及配音发音。

## 来源与许可证

- 原作者：杨昊波（Haobo Yang）；项目保留原主题源码声明。
- 代码与改编说明：[LICENSE](LICENSE)、[NOTICE](NOTICE)。
- 字体许可：[assets/fonts/LICENSE.txt](assets/fonts/LICENSE.txt)。
- NTU 标识来源：[assets/ntu-logo-source.txt](assets/ntu-logo-source.txt)。标识权利归所属机构，不因本仓库代码许可而转授。

仓库只包含可复用 skill 和模板，不包含示例论文、个人汇报讲稿或生成视频。
