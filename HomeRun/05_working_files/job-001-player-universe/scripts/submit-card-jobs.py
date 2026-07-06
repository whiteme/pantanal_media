#!/usr/bin/env python3
import argparse
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = Path("/Users/shenn-litscope/shenn-work/pantanal_media")
SUBMITTER = Path("/Users/shenn-litscope/.codex/skills/image-gen-web/scripts/submit_job.py")


def main():
    parser = argparse.ArgumentParser(description="Submit Job 001 character cards to local image-gen-web.")
    parser.add_argument("--limit", type=int, help="Submit only the first N jobs.")
    parser.add_argument("--kind", choices=["player_card", "coach_card"], help="Submit only one card kind.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without submitting.")
    args = parser.parse_args()

    tasks_path = ROOT / "prompts" / "card-generation-tasks.jsonl"
    output_dir = WORKSPACE / "HomeRun" / "06_exports" / "job-001-player-universe" / "cards"
    manifest_path = ROOT / "progress" / "image-gen-web-submissions.jsonl"
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    rows = [json.loads(line) for line in tasks_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.kind:
        rows = [row for row in rows if row["kind"] == args.kind]
    if args.limit:
        rows = rows[: args.limit]

    for row in rows:
        ref = WORKSPACE / row["reference_image"]
        if not ref.exists():
            raise SystemExit(f"Missing reference image for {row['asset_id']}: {ref}")
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as handle:
            handle.write(row["prompt"])
            prompt_file = Path(handle.name)
        cmd = [
            "python3",
            str(SUBMITTER),
            "--prompt-file",
            str(prompt_file),
            "--reference-image",
            str(ref),
            "--copy-output-to",
            str(output_dir),
            "--slug",
            row["output_slug"],
        ]
        if args.dry_run:
            print(" ".join(cmd))
            prompt_file.unlink(missing_ok=True)
            continue
        proc = subprocess.run(cmd, text=True, capture_output=True)
        prompt_file.unlink(missing_ok=True)
        if proc.returncode not in (0, 2):
            raise SystemExit(proc.stderr or proc.stdout)
        try:
            result = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Could not parse submitter output for {row['asset_id']}: {exc}\n{proc.stdout}")
        result["asset_id"] = row["asset_id"]
        result["kind"] = row["kind"]
        result["name_zh"] = row["name_zh"]
        result["team"] = row["team"]
        with manifest_path.open("a", encoding="utf-8") as manifest:
            manifest.write(json.dumps(result, ensure_ascii=False) + "\n")
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
