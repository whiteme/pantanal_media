# Job 003 - HomeRun 动漫宣传片 Epic 001 成片生产

目标：基于 Job 002 完整剧本，生成第一集动漫宣传片《意外》的第一版可播放成片。

## 输出策略

- 画幅：竖屏 9:16，1080x1920，面向短视频平台。
- 版本：v0.2 daylight production cut。
- 视觉：关键帧使用本地 `image-gen-web` 生成；产品画面使用真实 HomeRun 截图；字幕、数据层、音效与剪辑节奏由本地脚本合成。
- 音频：第一版使用节奏化电子鼓点、球场氛围与击球音效合成，不依赖外部 TTS 服务。
- 命名：主队 `北洲航海家 / Beizhou Voyager`，对手 `城南流星 / Chengnan Meteors`。

## 已建立内容

- `prompts/keyframe-generation-tasks.jsonl`：5 张核心关键帧的 image-gen-web 任务清单。
- `progress/image-gen-web-keyframes.jsonl`：关键帧提交与输出 manifest。
- `scripts/submit-keyframes.py`：提交关键帧到本地 image-gen-web 的脚本。
- `scripts/build-episode.py`：将关键帧、参考素材、字幕和音效合成为第一版视频。

## v0.2 修订

用户反馈后，v0.1 夜场幻想化方向不再作为当前制作方向。v0.2 改为：

- 白天训练赛，明亮运动番风格。
- 真实棒球动作，不出现火球、能量光轨、魔法或超能力效果。
- 产品画面使用 `/Users/shenn-litscope/shenn-work/HomeRun-运营/070` 的真实 HomeRun 截图，并复制归档到 `source-assets/product-070/`。
- 关键帧增加到 13 张，覆盖高速管制、8:30 集合、缺人、HomeRun 决策、替补上垒、满垒、林澈打席、地滚球、扑垒、迟到队员到场和下半局悬念。

v0.2 相关文件：

- `creative-direction-v0.2.md`
- `prompts/keyframe-generation-tasks-v0.2.jsonl`
- `scripts/submit-keyframes-v0.2.py`
- `progress/image-gen-web-keyframes-v0.2.jsonl`
- `scripts/build-episode.py`
- `scripts/episode-001-scene-manifest-v0.2.json`
- `progress/episode-001-v0.2-ffprobe.json`
- `progress/episode-v0.2-preview-contact-sheet.jpg`

## v0.2 成片输出

- 视频：`HomeRun/06_exports/job-003-anime-episode-001-production/videos/homerun-epic-001-accident-v0.2.mp4`
- 音频母带：`HomeRun/06_exports/job-003-anime-episode-001-production/audio/homerun-epic-001-v0.2-synthetic-mix.wav`，本地保留，可由 `scripts/build-episode.py` 再生成。
- 预览帧：`HomeRun/06_exports/job-003-anime-episode-001-production/scenes/v0.2/`，本地保留，可由 `scripts/build-episode.py` 再生成。

验证结果：

- 画幅：1080x1920，竖屏 9:16。
- 时长：98 秒。
- 流：H.264 视频 + AAC 音频。
- 画面质检：白天训练赛、明亮运动番、真实棒球动作；强袭地滚球镜头无火球、能量光轨、魔法或爆炸效果。
- 产品质检：HomeRun 产品段落使用 `source-assets/product-070/` 归档的真实截图合成，不让图像模型重画产品 UI。

## 关键帧范围

- S04：HomeRun 工作台
- S09：林澈看见弱点
- S10：强袭地滚球
- S12：扑回本垒
- S14：下半局悬念

其余剧情段落在第一版中由动态剪辑、字幕卡、已有 hero 背景和数据 UI 运动层承接。
