"""Poll HF for Qwen3.6-27B weights; auto-download when ready; notify on complete."""
from __future__ import annotations
import subprocess
import time
from pathlib import Path
from huggingface_hub import HfApi, snapshot_download

VARIANTS = ["8bit", "mxfp8", "6bit"]
POLL_INTERVAL = 900  # 15 min
LOG = Path.home() / "projects/qwen-mlx-bench/watch_27b_uploads.log"
SENTINEL_DIR = Path.home() / "projects/qwen-mlx-bench/.watch_27b_sentinels"
SENTINEL_DIR.mkdir(exist_ok=True)


def log(msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


def notify(title: str, msg: str) -> None:
    subprocess.run(
        ["osascript", "-e", f'display notification "{msg}" with title "{title}" sound name "Glass"'],
        check=False,
    )


def repo_has_weights(api: HfApi, variant: str) -> bool:
    repo = f"mlx-community/Qwen3.6-27B-{variant}"
    try:
        info = api.repo_info(repo, files_metadata=True)
        st = [f for f in info.siblings if f.rfilename.endswith(".safetensors")]
        if not st:
            return False
        total_gb = sum((f.size or 0) for f in st) / 1e9
        log(f"  {variant}: {len(st)} safetensors, {total_gb:.1f} GB total")
        return total_gb > 1.0
    except Exception as e:
        log(f"  {variant}: HF API error: {e}")
        return False


def download(variant: str) -> bool:
    repo = f"mlx-community/Qwen3.6-27B-{variant}"
    log(f"  → downloading {variant}")
    try:
        path = snapshot_download(repo, max_workers=8)
        log(f"  ✅ {variant} done at {path}")
        (SENTINEL_DIR / f"{variant}.done").touch()
        notify("Qwen3.6-27B", f"{variant} downloaded")
        return True
    except Exception as e:
        log(f"  ❌ {variant} download failed: {e}")
        return False


def main() -> None:
    api = HfApi()
    log(f"watcher started (variants={VARIANTS}, poll={POLL_INTERVAL}s)")
    pending = set(VARIANTS)
    while pending:
        log(f"poll pending={sorted(pending)}")
        ready_now = [v for v in pending if repo_has_weights(api, v)]
        for v in ready_now:
            if download(v):
                pending.discard(v)
        if pending:
            log(f"sleeping {POLL_INTERVAL}s ({len(pending)} left)")
            time.sleep(POLL_INTERVAL)
    notify("Qwen3.6-27B", "All 3 variants ready — bench可以跑了")
    log("ALL DONE — sentinels in " + str(SENTINEL_DIR))


if __name__ == "__main__":
    main()
