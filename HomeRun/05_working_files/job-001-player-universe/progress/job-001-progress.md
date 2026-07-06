# Job 001 进展记录

更新时间：2026-07-06

## 当前状态

状态：角色设定与卡片任务归档完成，人物卡图片已通过 image-gen-web 跑通首张样卡。

## 已完成

- 梳理 HomeRun 当前官网 0.7.0 公测版宣传口径。
- 梳理产品文档中的品牌人格：专业、温度、运动科技。
- 归档系统默认球员头像到 `HomeRun/02_source_assets/reference/player-avatars/`。
- 生成默认头像总览图：`HomeRun/02_source_assets/reference/default-player-avatar-contact-sheet.png`。
- 归档 HomeRun hero 风格背景到 `HomeRun/02_source_assets/reference/hero-backgrounds/`。
- 建立两支广告球队：南湾航海家、城北流星。
- 完成 20 名正式球员人物设定。
- 完成 6 名教练员人物设定。
- 完成人物卡 image-gen-web 任务清单。
- 创建可复用本地 skill：`/Users/shenn-litscope/.codex/skills/image-gen-web`。
- 校验 `image-gen-web` skill 通过。
- 使用 image-gen-web 生成首张样卡：林澈 / `P001_boy_01_lin-che.png`。

## 关键判断

HomeRun 默认头像目录里有 24 张性别化头像和 1 张 default 图，但产品代码当前只认可 `boy_01` - `boy_10`、`girl_01` - `girl_10` 和 `default`。因此本次广告正式角色锁定 20 名球员，避免后续产品数据或分享卡片引用无效头像 key。

## 待完成

- 使用 `prompts/card-generation-tasks.jsonl` 继续逐张提交 image-gen-web 生成剩余 25 张正式人物卡。
- 人工筛选第一版人物卡，记录通过/重生成/废弃状态。
- 基于角色圣经继续推进第一支广告短片的脚本、分镜和拍摄/生成素材计划。

## 首张样卡检查

文件：`HomeRun/06_exports/job-001-player-universe/cards/P001_boy_01_lin-che.png`

结果：可用。画面延续默认头像五官气质和官网 hero 的夜场金光风格，竖版 9:16 构图，下半部有充足文字安全区。后续人物卡可沿用当前提示词结构。

## 风格要求

- 头像延续 HomeRun 默认球员头像的日漫运动番风格。
- 背景延续官网 hero 图的夜场、金色灯光、深蓝阴影、热血但克制的运动科技感。
- 人物卡避免过度营销风，重点服务角色身份、球队关系和后续短片叙事。
