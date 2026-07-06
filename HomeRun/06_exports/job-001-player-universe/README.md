# Job 001 导出成果

更新时间：2026-07-06

## 当前导出

- `cards/P001_boy_01_lin-che.png`：林澈人物卡首张样卡，由本地 `image-gen-web` 生成。

## 生成记录

首张样卡 image-gen-web job：

- job id: `47a4cda8d6974efe9f9f495aa75185a5`
- model: `gpt-image-2`
- output: `796ba40ee02941ae862551c07451a937.png`
- copied path: `HomeRun/06_exports/job-001-player-universe/cards/P001_boy_01_lin-che.png`

完整提交记录追加在：

- `HomeRun/05_working_files/job-001-player-universe/progress/image-gen-web-submissions.jsonl`

## 后续导出计划

继续使用：

```bash
python3 HomeRun/05_working_files/job-001-player-universe/scripts/submit-card-jobs.py
```

默认会读取 `prompts/card-generation-tasks.jsonl` 并提交所有人物卡。正式批量生成前建议先按 `--limit` 或 `--kind` 分批提交，便于筛选与控制成本。
