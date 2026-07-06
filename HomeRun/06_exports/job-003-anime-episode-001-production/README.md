# HomeRun Epic 001《意外》成片导出

本目录归档 Job 003 的成片输出、关键帧、音频和预览帧。

## 输出内容

- `keyframes/`：本地保留 v0.1 历史关键帧；远端提交以 v0.2 为当前版本。
- `keyframes/v0.2/`：通过本地 `image-gen-web` 生成并复制归档的 13 张白天真实风格关键帧。
- `audio/`：本地合成的节奏鼓点、球场氛围和击球音效母带，可由脚本再生成；远端提交以 MP4 内嵌音频为准。
- `scenes/`：用于质检的成片预览帧，可由脚本再生成；远端提交以工作目录 contact sheet 为准。
- `videos/`：第一版可播放 MP4。

## 当前交付版

- `videos/homerun-epic-001-accident-v0.2.mp4`
- 1080x1920，竖屏 9:16。
- 时长 98 秒。
- H.264 视频 + AAC 音频。
- 视觉方向：白天训练赛，明亮运动番，真实棒球动作，无火球、能量光轨、魔法/爆炸效果。
- 产品画面：使用工作目录 `source-assets/product-070/` 中归档的真实 HomeRun 产品截图合成。

## v0.2 预览与验证

- `scenes/v0.2/`：正式版预览帧，本地保留，可由脚本再生成。
- 工作目录 `progress/episode-v0.2-preview-contact-sheet.jpg`：正式版预览 contact sheet。
- 工作目录 `progress/episode-001-v0.2-ffprobe.json`：视频流与时长验证。
- 工作目录 `scripts/episode-001-scene-manifest-v0.2.json`：镜头时长与字幕清单。

## 制作边界

- 所有 AI 图片生成均通过本地 `image-gen-web` 完成，生成记录见工作目录 `progress/image-gen-web-keyframes.jsonl`。
- 视频合成、字幕、运动镜头、数据叠层和音频由工作目录中的 `scripts/build-episode.py` 生成。
- 官方命名：`北洲航海家 / Beizhou Voyager` 对阵 `城南流星 / Chengnan Meteors`。
