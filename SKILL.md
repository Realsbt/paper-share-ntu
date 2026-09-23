---
name: paper-share
description: 将论文 PDF、TeX 或 arXiv 链接按原 SUSTech Beamer 模板制作中文组会幻灯片，使用可配置的汇报人信息与 NTU 标识，交付 PDF、源码和逐页讲稿；按需生成本地配音视频。适用于论文分享、文献精读和 paper-to-slides。
---

# 论文分享：原版流程 · NTU 个人适配

沿用 paper-share-skills 的 paper-to-beamer 制作流程和随包的原版 `sustech` 主题（小写），不是重新设计的简化 Madrid 模板。默认 16:10，保留原配色、封面字段、双栏目录、章节过渡页、纵向卡片、callout、独立大图、参考文献和 Q&A。详细逐页要求见 [references/beamer-workflow.md](references/beamer-workflow.md)，制作前读取。

## 个人信息与边界

- 汇报人姓名由使用者填写；学校：南洋理工大学 / Nanyang Technological University，简称 NTU。用 `setpresenter`，不要把汇报人写成论文作者。
- 论文作者和所属机构保留在 `author` / `institute`；NTU 标识代表汇报人学校。
- 使用附带 NTU logo，保持比例及原色，位于标题、汇报人信息和学校信息下方。不要保留可见的南科大校徽或原作者个人头像。此为个人适配，非 NTU 官方模板。
- 保留源码许可证及原主题作者声明；封面用 `hidecredits` 隐藏原 B 站频道宣传。
- 默认交付 PDF + LaTeX 源码 + `speaker-notes.md`。用户另要 PowerPoint 才生成可编辑 PPTX，不把 PDF 称为 PPTX。
- 不含 B 站登录、上传、标题推荐、自动发布。仅在用户明确需要视频时读取 [references/video.md](references/video.md)。edge-tts 使用在线服务；本地生成视频不等于离线 TTS。

## 输入与本地制作

`<SKILL_DIR>` 是本文件所在目录。用 `python3`，不假设 `python` 存在。

1. 在 `论文分享/<论文简称>/` 工作。用户输入、同步 `sources/` 只读；保留已有用户改动，重做使用新目录。
2. arXiv 优先下载 TeX：`python3 "<SKILL_DIR>/scripts/download_source.py" "<arxiv-id-or-url>" --output "<paper_dir>"`。有源码直接读取并复用矢量图；只有 PDF 时使用文本提取和页面检查，复杂版面按需 OCR，不强依赖作者的 MinerU 环境。
3. `python3 "<SKILL_DIR>/scripts/prepare.py" doctor` 检查依赖。
4. `python3 "<SKILL_DIR>/scripts/prepare.py" init "<paper_dir>"` 复制原版完整模板、主题、校徽和字体；拒绝覆盖已有模板。保持 `assets/` 原样，编辑生成的 `slides-beamer/main.tex`。
5. 按逐页指南填入真实内容，删除示例占位符；保留原主题，不自行降级为简化模板。
6. `python3 "<SKILL_DIR>/scripts/build.py" "<paper_dir>/slides-beamer"` 本地编译。该脚本自动使用同一 TeX 发行版、设置系统对应的主题路径，编译三遍解析目录与页码，并检查溢出及缺字。也可在文稿目录用 `latexmk -xelatex main.tex`，配套 latexmkrc 已适配平台路径。
7. 渲染检查全部页面，核对图表、标题、页脚和章节页。中文字体必须嵌入且带 ToUnicode 映射（`pdffonts` 中中文字体的 `uni` 为 yes）；用附带 Noto CJK 字体，避免客户端预览依赖外部 CMap。
8. 为最终 PDF 的每个物理页写讲稿，包括自动章节页、图页、Q&A、附录。视频输入逐页对齐，不能仅按源文件显式 frame 数量生成。

## 内容真实性与交付

论文结论、作者信息、历史脉络和汇报者推断要区分，图表标注原文位置。联网核实作者介绍；资料不足就标明未核实，不补造履历。历史视角使用可靠文献；新论文不能编造未来传播或采用情况。原作者私人课程/调研文件缺失时，以可核查公开文献替代；无法核实的 Oral 模式分析省略并说明，不能让私人依赖阻塞主流程。

交付 PDF、包含主题/字体/许可证的源码包、讲稿和简短验证结果。说明实际本机测试与尚未验证的可选能力；仅依赖检测不等于已跑通。用户当次明确要求优先。
