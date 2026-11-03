#!/usr/bin/env python3
"""Launch a wave of Parallel.ai research threads, save run_ids, wait, save outputs.

Usage:
    PARALLEL_API_KEY=... python launch_wave.py --wave 1
    PARALLEL_API_KEY=... python launch_wave.py --wave 1 --status

Reads ./wave<N>_threads.json, writes outputs to ../research/wave<N>/<thread_id>/.
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

from parallel import Parallel

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent


def load_protocol(wave: int) -> dict:
    p = HERE / f"wave{wave}_threads.json"
    return json.loads(p.read_text())


def state_path(wave: int) -> Path:
    return HERE / f"wave{wave}_state.json"


def save_state(wave: int, state: dict):
    state_path(wave).write_text(json.dumps(state, indent=2))


def load_state(wave: int) -> Optional[dict]:
    p = state_path(wave)
    return json.loads(p.read_text()) if p.exists() else None


def launch_thread(client, thread: dict) -> Tuple[str, Optional[str], str]:
    tid = thread["thread_id"]
    try:
        run = client.task_run.create(
            input=thread["input"],
            processor=thread["processor"],
            source_policy=thread.get("source_policy") or None,
            task_spec={"output_schema": {"type": "text"}},
            metadata={"protocol": "A_STAR", "thread_id": tid},
        )
        print(f"  {tid} queued -> {run.run_id}", flush=True)
        return tid, run.run_id, "queued"
    except Exception as e:
        print(f"  {tid} FAILED to launch: {e}", flush=True)
        return tid, None, f"launch_error: {e}"


def wait_for_result(client, tid: str, run_id: str, out_dir: Path, timeout: int = 2700) -> Tuple[str, str]:
    print(f"  waiting on {tid} ({run_id})", flush=True)
    start = time.time()
    interval = 15
    while time.time() - start < timeout:
        try:
            r = client.task_run.retrieve(run_id)
            status = r.status
            elapsed = int(time.time() - start)
            if status == "completed":
                # Fetch the result
                res = client.task_run.result(run_id)
                content = ""
                if hasattr(res, "output") and res.output:
                    if hasattr(res.output, "content"):
                        content = res.output.content
                    else:
                        content = str(res.output)
                else:
                    content = str(res)
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / f"{tid}.md").write_text(content)
                # Also save raw result envelope
                try:
                    (out_dir / f"{tid}_raw.json").write_text(json.dumps(res.model_dump(), indent=2, default=str))
                except Exception:
                    pass
                print(f"  {tid} COMPLETED in {elapsed}s -> {out_dir}/{tid}.md ({len(content)} chars)", flush=True)
                return tid, "completed"
            elif status in ("failed", "cancelled"):
                print(f"  {tid} {status} after {elapsed}s", flush=True)
                return tid, status
            else:
                print(f"  {tid} status={status} elapsed={elapsed}s", flush=True)
        except Exception as e:
            print(f"  {tid} poll error: {e}", flush=True)
        time.sleep(interval)
        interval = min(60, int(interval * 1.3))
    return tid, "timeout"


def cmd_launch(wave: int):
    proto = load_protocol(wave)
    client = Parallel(api_key=os.environ["PARALLEL_API_KEY"])
    print(f"Launching wave {wave}: {len(proto['threads'])} threads", flush=True)
    state = {"wave": wave, "launched_at": datetime.now(timezone.utc).isoformat(), "threads": {}}
    with ThreadPoolExecutor(max_workers=len(proto["threads"])) as pool:
        futures = [pool.submit(launch_thread, client, t) for t in proto["threads"]]
        for f in as_completed(futures):
            tid, run_id, status = f.result()
            state["threads"][tid] = {"run_id": run_id, "status": status}
    save_state(wave, state)
    print(f"State saved to {state_path(wave)}", flush=True)


def cmd_wait(wave: int):
    state = load_state(wave) or {}
    if not state.get("threads"):
        print("no state, run --launch first", flush=True)
        sys.exit(1)
    client = Parallel(api_key=os.environ["PARALLEL_API_KEY"])
    out_dir = PROJECT_ROOT / "research" / f"wave{wave}"
    pending = [
        (tid, t["run_id"]) for tid, t in state["threads"].items() if t.get("run_id") and t.get("status") != "completed"
    ]
    print(f"waiting on {len(pending)} threads", flush=True)
    with ThreadPoolExecutor(max_workers=max(1, len(pending))) as pool:
        futures = [pool.submit(wait_for_result, client, tid, rid, out_dir) for tid, rid in pending]
        for f in as_completed(futures):
            tid, status = f.result()
            state["threads"][tid]["status"] = status
            state["threads"][tid]["finished_at"] = datetime.now(timezone.utc).isoformat()
            save_state(wave, state)
    print("done", flush=True)


def cmd_status(wave: int):
    state = load_state(wave)
    if not state:
        print("no state", flush=True)
        return
    print(json.dumps(state, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", type=int, required=True)
    ap.add_argument("--launch", action="store_true")
    ap.add_argument("--wait", action="store_true")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()

    if args.status:
        cmd_status(args.wave)
        return
    if args.launch:
        cmd_launch(args.wave)
    if args.wait:
        cmd_wait(args.wave)
    if not (args.launch or args.wait or args.status):
        cmd_launch(args.wave)
        cmd_wait(args.wave)


if __name__ == "__main__":
    main()
