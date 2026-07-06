#!/usr/bin/env python3
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = Path("/Users/shenn-litscope/shenn-work/pantanal_media")
SUBMITTER = Path("/Users/shenn-litscope/.codex/skills/image-gen-web/scripts/submit_job.py")


def main():
    tasks_path = ROOT / "prompts" / "keyframe-generation-tasks.jsonl"
    output_dir = WORKSPACE / "HomeRun" / "06_exports" / "job-003-anime-episode-001-production" / "keyframes"
    manifest_path = ROOT / "progress" / "image-gen-web-keyframes.jsonl"
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    rows = [json.loads(line) for line in tasks_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    completed = set()
    if manifest_path.exists():
        for line in manifest_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("status") == "done":
                completed.add(row.get("shot_id"))

    for row in rows:
        if row["shot_id"] in completed:
            print(f"skip {row['shot_id']} already done")
            continue
        ref = WORKSPACE / row["reference_image"]
        if not ref.exists():
            raise SystemExit(f"Missing reference image for {row['shot_id']}: {ref}")
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
        proc = subprocess.run(cmd, text=True, capture_output=True)
        prompt_file.unlink(missing_ok=True)
        if proc.returncode not in (0, 2):
            raise SystemExit(proc.stderr or proc.stdout)
        try:
            result = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Could not parse submitter output for {row['shot_id']}: {exc}\n{proc.stdout}")
        result["shot_id"] = row["shot_id"]
        result["title"] = row["title"]
        result["output_slug"] = row["output_slug"]
        with manifest_path.open("a", encoding="utf-8") as manifest:
            manifest.write(json.dumps(result, ensure_ascii=False) + "\n")
        print(json.dumps(result, ensure_ascii=False))
        if result.get("status") != "done":
            raise SystemExit(2)


if __name__ == "__main__":
    main()
