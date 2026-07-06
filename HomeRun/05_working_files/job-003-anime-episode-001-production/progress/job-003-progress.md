# Job 003 进展记录

更新时间：2026-07-06

## 当前状态

状态：v0.2 白天真实运动番方向已完成第一版成片，并已归档可播放 MP4、脚本、真实产品截图、关键帧、预览 contact sheet 和验证记录。音频母带与逐帧预览图本地保留，可由脚本再生成。

## 创意判断

- 第一版先做完整可播放成片，而不是等待全部 14 个镜头逐一生成。
- 静帧/关键帧生成必须通过本地 `image-gen-web`。
- 视频合成使用本地脚本和 `/opt/homebrew/bin/ffmpeg`。
- 画面风格延续 HomeRun 默认头像与 hero 背景：明亮日漫运动番、真实棒球动作、克制数据叠层。
- 正式队名：`北洲航海家 / Beizhou Voyager` 对阵 `城南流星 / Chengnan Meteors`。
- v0.2 修订：比赛发生在白天，画风要明亮；棒球动作要真实，不能出现火球、能量光轨、魔法/超能力效果；产品画面必须使用真实 HomeRun 截图。

## 已完成

- 5 张核心关键帧已提交到本地 `image-gen-web` 并复制到项目归档目录：
  - `S04_homerun_workbench.png`
  - `S09_linche_reads_gap.png`
  - `S10_ground_ball_gold_streak.png`
  - `S12_linche_home_slide.png`
  - `S14_cliffhanger_defense.png`
- 关键帧 manifest 已归档在 `progress/image-gen-web-keyframes.jsonl`。
- 关键帧人工质检通过：S04 可承接 HomeRun 工作台段落，S09/S10/S12 可承接林澈数据打击与场内本垒打高潮，S14 可承接下半局悬念。
- `media-use` 外部音效解析因本机未安装 `heygen` CLI 失败；第一版采用本地脚本生成可复现的节奏鼓点、球场氛围、whoosh 与击球音效。
- 用户反馈后已建立 `creative-direction-v0.2.md`，记录 v0.2 白天真实风格修订要求。
- 已从 `/Users/shenn-litscope/shenn-work/HomeRun-运营/070` 复制真实产品截图到 `source-assets/product-070/`，用于成片真实产品画面合成。
- 已建立 `prompts/keyframe-generation-tasks-v0.2.jsonl` 与 `scripts/submit-keyframes-v0.2.py`，准备提交 13 张白天真实风格关键帧。
- 已通过本地 `image-gen-web` 生成 13 张 v0.2 白天真实风格关键帧，并归档在 `HomeRun/06_exports/job-003-anime-episode-001-production/keyframes/v0.2/`。
- 已生成 `progress/keyframes-v0.2-contact-sheet.jpg`，人工质检通过：白天、明亮、风格统一，地滚球与扑垒镜头无火球、能量光轨、魔法/爆炸效果。
- 已将 `scripts/build-episode.py` 升级为 v0.2 合成器：13 个剧情镜头、真实产品截图手机/平板面板、浅色字幕与数据层、本地合成音效。
- 已生成第一集 v0.2 成片：
  - `HomeRun/06_exports/job-003-anime-episode-001-production/videos/homerun-epic-001-accident-v0.2.mp4`
  - 时长 98 秒，1080x1920，H.264 视频 + AAC 音频。
- 已生成正式版预览帧与 contact sheet：
  - `HomeRun/06_exports/job-003-anime-episode-001-production/scenes/v0.2/`
  - `progress/episode-v0.2-preview-contact-sheet.jpg`
- 为降低 GitHub 媒体包推送体积，逐帧预览 PNG、WAV 音频母带、v0.1 旧导出关键帧和产品视频抽帧不作为远端提交内容；它们仍在本地工作目录保留，且可通过脚本或源素材复现。
- 已生成 v0.2 验证记录：
  - `progress/episode-001-v0.2-ffprobe.json`
  - `scripts/episode-001-scene-manifest-v0.2.json`

## 质检结论

- 白天设定已落实：成片关键镜头均为晴朗/明亮训练赛场景。
- 不真实动漫特效已规避：成片无火球棒球、能量光轨、魔法阵、爆炸或超能力表现。
- 产品画面已替换为真实 HomeRun 截图：专业计分、数据分布、打席记录、分享战报、Live Console 等画面均来自 `source-assets/product-070/`。
- 剧情覆盖完整：高速管制、8:30 集合、阵容缺失、HomeRun 辅助打线、替补上垒、满垒、林澈地滚球、场内本垒打、迟到队员到场、下半局悬念。
