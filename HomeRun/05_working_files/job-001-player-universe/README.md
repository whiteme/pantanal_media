# Job 001 - HomeRun 角色宇宙与人物卡

目标：为 HomeRun 第一支产品广告短片建立可复用的球队和人物资产底座。

## 已建立内容

- `data/character-bible.json`：结构化角色设定，便于后续脚本、卡片、分镜复用。
- `data/character-bible.md`：创意团队可读版人物圣经。
- `prompts/card-generation-tasks.jsonl`：每张人物卡的 image-gen-web 任务清单。
- `progress/job-001-progress.md`：进展、依据、完成情况和后续动作。

## 素材引用

- 默认头像：`HomeRun/02_source_assets/reference/player-avatars/`
- 默认头像总览：`HomeRun/02_source_assets/reference/default-player-avatar-contact-sheet.png`
- Hero 背景参考：`HomeRun/02_source_assets/reference/hero-backgrounds/`

## 角色范围

正式角色使用产品当前有效的默认头像 key：

- `boy_01` - `boy_10`
- `girl_01` - `girl_10`

`boy_11`、`boy_12`、`girl_11`、`girl_12` 文件存在，但当前产品代码未纳入有效 key。本 Job 将其记录为未来占位，不进入正式广告角色。
