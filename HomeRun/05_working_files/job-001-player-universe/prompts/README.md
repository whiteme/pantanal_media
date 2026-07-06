# Job 001 人物卡生成任务

任务数量：26 张人物卡。

提交方式：使用本地 `image-gen-web` skill 的 `submit_job.py`，每行 JSONL 对应一次生成任务。

示例命令：

```bash
python /Users/shenn-litscope/.codex/skills/image-gen-web/scripts/submit_job.py \
  --prompt-file /path/to/prompt.txt \
  --reference-image /path/to/reference.png \
  --copy-output-to /Users/shenn-litscope/shenn-work/pantanal_media/HomeRun/06_exports/job-001-player-universe/cards \
  --slug P001_boy_01_lin-che
```

注意：当前 app 支持一个参考图。球员卡使用对应默认头像作为参考；教练卡使用 HomeRun hero/dugout 参考图。
