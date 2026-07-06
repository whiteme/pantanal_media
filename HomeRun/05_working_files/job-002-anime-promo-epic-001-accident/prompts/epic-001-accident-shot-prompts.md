# Epic 001《意外》动漫生成提示清单

用途：将完整剧本拆成可用于分镜图、关键帧、动态镜头或视频生成的提示。所有涉及静帧或图像生成的执行工作，应通过本地 `image-gen-web` 项目提交。

## 全局风格提示

HomeRun anime sports promotional film, cinematic Japanese sports anime, Chinese amateur youth baseball, summer cup training game, deep navy shadows, warm golden stadium lights, painterly brush texture, expressive linework, grounded sports-tech UI overlays, premium but warm tone, no real team logos, no MLB marks, no readable dense text, no real players, visual continuity with HomeRun default player avatars and HomeRun hero art.

## 角色锁定

- 林澈：Chinese teenage baseball captain, jersey number 7, South Bay Voyager, two-way CF/P, calm eyes, dark hair, navy and white uniform with gold accents, bat and glove visual cues.
- 沈嘉宁：female coach, composed and analytical, tablet in hand, sports science vibe, warm but decisive.
- 周远航：head coach, former pitcher, steady but pressured, clipboard or cap, dugout leadership.
- 石屿：North City Meteors pitcher, fast tempo, intense posture, black/red/gold uniform accents.
- 赵燃：North City Meteors shortstop, competitive eyes, emotional core for second episode hook.

## 镜头提示

### S01 高速封闭

Prompt：Morning highway entrance near a baseball field, traffic control sign glowing, cars stopped, teenage baseball players in uniforms looking anxiously at phones, warm summer light, dramatic anime sports opening, subtle tension, no readable text.

剧情作用：建立“意外”。

### S02 8:30 球场集合

Prompt：Youth baseball field at 8:30 in summer morning, South Bay Voyager players in deep navy white gold uniforms and North City Meteors players in black red gold warming up, stadium lights still glowing, cinematic anime composition, team contrast, energetic but tense.

剧情作用：建立对阵和时间压力。

### S03 两队缺人

Prompt：Split-screen anime dugouts, both baseball teams checking phones and incomplete lineup boards, coaches stressed, substitute players unsure, baseball bags and gloves on bench, golden dust in air, sports drama mood.

剧情作用：双方都被突发状况扰乱。

### S04 HomeRun 工作台

Prompt：Female coach Shen Jianing opens a tablet with stylized sports analytics interface, baseball lineup cards, player data modules, glowing UI lines, head coach leaning in, dugout background, no readable small text, HomeRun-like professional scoring and roster management mood.

剧情作用：产品第一次成为解决问题的工具。

### S05 点球成金式数据打线

Prompt：Anime tactical board and tablet analytics layered together, highlighted player cards for substitutes, on-base probability, bunt training, contact direction represented as abstract icons and glowing arcs, coaches making a decisive data-driven lineup choice, no movie references visible.

剧情作用：用数据棒球思路完成新打线。

### S06 替补上垒一

Prompt：Female outfielder batter Su Qing calmly taking a pitch outside the zone, catcher reaching, umpire silhouette, golden UI marker showing first base path, cinematic anime baseball shot, crowd and dugout reacting.

剧情作用：替补第一位上垒。

### S07 推进打

Prompt：Quiet shortstop Gu Ming making a controlled opposite-field contact swing, baseball rolling through right side, runner advancing, HomeRun-style scoring trail highlighting base movement, dynamic low angle anime shot.

剧情作用：体现“推进队友”。

### S08 短打制造满垒

Prompt：Ji Anan bunts down the third-base line, third baseman charging, dust rising, close play at first base, runners filling all bases, intense sports anime timing, golden base icons glowing.

剧情作用：满垒形成。

### S09 林澈看见弱点

Prompt：Lin Che jersey number 7 steps into batter box, calm captain expression, bat raised, glove tucked near dugout, subtle analytics overlay reveals defensive gap between third base and shortstop, South Bay Voyager colors, night-blue and golden light mood.

剧情作用：队长用数据做选择。

### S10 强袭地滚球

Prompt：Explosive ground ball hit by Lin Che, golden streak hugging the dirt through the third-short gap, infielders diving late, dust and motion lines, intense anime impact frame, no readable text.

剧情作用：高潮击球。

### S11 场内本垒打

Prompt：Lin Che sprinting around third base toward home, teammates yelling from dugout, outfield relay throw high and late, three runners scoring ahead, golden motion trails across bases, cinematic sports anime climax.

剧情作用：带回 4 分。

### S12 扑回本垒

Prompt：Lin Che sliding headfirst into home plate, dust cloud and golden stadium light burst, catcher reaching too late, number 7 visible, emotional anime freeze frame, victorious but not overdone.

剧情作用：上半局 4:0。

### S13 迟到队员抵达

Prompt：Late players from both teams running into baseball field with bags over shoulders, out of breath, coaches turning, scoreboard glow in background, tension rising again, anime cliffhanger energy.

剧情作用：新的变量进入。

### S14 下半局悬念

Prompt：Lin Che standing in center field with glove raised, Zhao Ran from North City Meteors staring from dugout with competitive eyes, HomeRun highlight card and live stream phone glow in foreground, dramatic sunset-gold stadium lights, cliffhanger ending.

剧情作用：为第二集留钩子。

## 配音与节奏提示

- 前 25 秒：节奏紧，交通意外和缺人焦虑快速推进。
- 25-48 秒：节奏降下来，让 HomeRun 的“清晰”对比现场的混乱。
- 48-88 秒：运动番高潮，连续上垒、满垒、强袭地滚和本垒冲刺。
- 88-120 秒：紧张收束，迟到队员到场，第二集钩子出现。

## 后续生成边界

- 若生成关键帧，优先先做 S04、S09、S10、S12、S14 五张。
- 若生成动态视频，建议每段 4-8 秒，先做无字幕版本，后期再叠加中文标题和 HomeRun 功能字卡。
- 所有图像生成执行必须通过本地 `image-gen-web`；本文件只归档提示，不直接提交生成。
