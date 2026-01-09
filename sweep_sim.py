#!/usr/bin/env python3

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

def now_ts() -> str:
    return time.strftime("%Y%m%d_%H%M%S")

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def write_json(p: Path, obj: Any) -> None:
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")    

def stable_hash(d: Dict[str, Any]) -> str:
    s = json.dumps(d, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]

def build_cmd(run_script: Path, suite: str, outdir: Path, ram_cfg: Path, max_inst: int, extra: List[str]) -> List[str]:
    # e.g., ./run_multi_sim.py --suite polybench --outdir outs --num-cpus 4 --max-inst 1000 --ramulator-config ./ramulator2_config/ddr5_pch_config.yaml
    cmd = [
        sys.executable,
        str(run_script),
        "--suite", suite,
        "--outdir", str(outdir),
        "--ramulator-config", str(ram_cfg),
        "--max-inst", str(max_inst),
        "--num-cpus", str(4),
        "--no-curses"
    ]
    if extra:
        cmd += extra
    return cmd

def shlex_join(cmd: List[str]) -> str:
    return " ".join(shlex.quote(x) for x in cmd)

def main() -> int:
    bench_list = ["spec_cpu", "polybench"]
    run_script = Path("./run_multi_sim.py")
    ram_cfg_list = ["./ramulator2_config/ddr5_pch_config.yaml"]
    max_inst = 50000
    if not run_script.exists():
        print(f"ERROR: run script not found: {run_script}", file=sys.stderr)
        return 2

    out_root = Path("sim_outs")
    ensure_dir(out_root)        
    # Sweep plan 저장
    plan = {
        "run_script": str(run_script),
        "out_root": str(out_root),
        "suite": bench_list,
        "ramulator_config": ram_cfg_list,
        "max_inst": str(max_inst),
        "timeout": 0,
        "extra": "",
        "timestamp": now_ts(),
    }

    write_json(out_root / f"sweep_plan_{now_ts()}.json", plan)

    results: List[Dict[str, Any]] = []

    for suite in bench_list:
        for ram_cfg_path in ram_cfg_list:
            ram_cfg = Path(ram_cfg_path)
            if not ram_cfg.exists():
                print(f"ERROR: ramulator config not found: {ram_cfg}", file=sys.stderr)
                return 2            

            ram_name = ram_cfg.stem
            meta = {
                "suite": suite,
                "ramulator_config": str(ram_cfg),
                "max_inst": int(max_inst),
            }
            run_id = stable_hash(meta)

            combo_dir = out_root / f"suite={suite}__ram={ram_name}__inst={max_inst}__{run_id}"
            ensure_dir(combo_dir)
            done_path = combo_dir / "sweep_done.json"

            cmd = build_cmd(run_script, suite, combo_dir, ram_cfg, max_inst, "")
            meta_full = {
                **meta,
                "run_id": run_id,
                "outdir": str(combo_dir),
                "cmd": cmd,
                "cmd_str": shlex_join(cmd),
                "timestamp": now_ts(),
            }

            write_json(combo_dir / "sweep_meta.json", meta_full)

            # stdout_path = combo_dir / "sweep_stdout.log"
            # stderr_path = combo_dir / "sweep_stderr.log"

            start = time.time()
            
            try:
                # with open(stdout_path, "w", encoding="utf-8") as fo, open(stderr_path, "w", encoding="utf-8") as fe:
                proc = subprocess.run(cmd)
                elapsed = time.time() - start
                status = "OK" if proc.returncode == 0 else "FAIL"
                result = {
                    **meta_full,
                    "status": status,
                    "returncode": proc.returncode,
                    "elapsed_s": round(elapsed, 3),
                }
            except subprocess.TimeoutExpired:
                elapsed = time.time() - start
                result = {**meta_full, "status": "TIMEOUT", "returncode": None, "elapsed_s": round(elapsed, 3)}
            except Exception as e:
                elapsed = time.time() - start
                result = {**meta_full, "status": "ERROR", "error": repr(e), "returncode": None, "elapsed_s": round(elapsed, 3)}

            write_json(combo_dir / "sweep_result.json", result)
            write_json(done_path, {"done": True, "status": result["status"], "timestamp": now_ts()})
            results.append(result)

    # Sweep summary
    summary = {
        "timestamp": now_ts(),
        "total": len(results),
        "ok": sum(1 for r in results if r.get("status") == "OK"),
        "fail": sum(1 for r in results if r.get("status") == "FAIL"),
        "timeout": sum(1 for r in results if r.get("status") == "TIMEOUT"),
        "error": sum(1 for r in results if r.get("status") == "ERROR"),
        "skip_done": sum(1 for r in results if r.get("status") == "SKIP_DONE"),
        "dry_run": sum(1 for r in results if r.get("status") == "DRY_RUN"),
        "results_file": None,
    }
    results_path = out_root / f"sweep_results_{now_ts()}.json"
    write_json(results_path, results)
    summary["results_file"] = str(results_path)

    write_json(out_root / f"sweep_summary_{now_ts()}.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    raise SystemExit(main())    