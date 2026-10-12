#!/usr/bin/env python3
"""S2-screen the top-2D-placeability finalists, sequentially with polite backoff.

Usage: screen_finalists.py <N> [w2d_max]
  Reads place2d/ranked.json, takes top N by W2d (excluding baseline and any
  candidate already having an S2 log), generates validation candidates via
  gen_from_P.py, and S2-screens each via validation/run_s2_screen.py
  (which itself backs off on >=2 foreign heavies).
  Results appended to round_wf/ROUND_WF_TABLE.md "2D phase S2 screens".
Logs to place2d/screen_finalists.log. Designed to run detached.
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
WF = os.path.join(HERE, "..")
EXP = "/home/hatch/workspace/mix/exploration"
TABLE = os.path.join(WF, "ROUND_WF_TABLE.md")
LOG = os.path.join(HERE, "screen_finalists.log")

def emit(s):
    line = f"[{time.strftime('%H:%M:%S')}] {s}"
    print(line, flush=True)
    open(LOG, "a").write(line + "\n")

def main():
    N = int(sys.argv[1])
    w2d_max = float(sys.argv[2]) if len(sys.argv) > 2 else 1e9
    ranked = json.load(open(os.path.join(HERE, "ranked.json")))["ranked"]
    # filter: not baseline, W2d < max, no existing S2 log
    cands = []
    for r in ranked:
        if r["src"] == "baseline":
            continue
        if r["W2d"] >= w2d_max:
            continue
        logp = os.path.join(WF, "validation", "logs", f"s2_wf2d_{r['name']}.log")
        if os.path.exists(logp):
            emit(f"skip {r['name']}: S2 log exists")
            continue
        cands.append(r)
        if len(cands) >= N:
            break
    emit(f"screening {len(cands)} finalists")
    for r in cands:
        name = f"wf2d_{r['name']}"
        # P-box JSON: reconstruct from pool (affine params or SA tour)
        emit(f"=== {name} (W2d={r['W2d']} S={r['S']} src={r['src']}) ===")
        # regenerate P from the pool definitions
        sys.path.insert(0, HERE)
        from place2d import baseline_P, affine_pool, sa_highS_pool
        P = None
        if r["src"] == "affine":
            for e in affine_pool():
                if e["name"] == r["name"]:
                    P = e["P"]; break
        elif r["src"] == "sa_highS":
            for e in sa_highS_pool(os.path.join(WF, "pareto", "frontier.json"), 0):
                if e["name"] == r["name"]:
                    P = e["P"]; break
        if P is None:
            emit(f"  P-box not found for {r['name']}, skipping"); continue
        pf = f"/tmp/wf2d_{r['name']}.json"
        json.dump(P, open(pf, "w"))
        gr = subprocess.run([sys.executable, os.path.join(WF, "validation", "gen_from_P.py"),
                             name, pf], capture_output=True, text=True)
        emit("  gen: " + gr.stdout.strip().split("\n")[-1] if gr.stdout else "  gen FAILED")
        if gr.returncode != 0:
            emit("  gen stderr: " + gr.stderr[-500:]); continue
        # rename log to match our naming (run_s2_screen uses s2_<name>.log)
        sr = subprocess.run([sys.executable, os.path.join(WF, "validation", "run_s2_screen.py"),
                             name], capture_output=True, text=True)
        tail = (sr.stdout + sr.stderr)[-800:]
        emit("  S2 tail: " + tail.replace("\n", " | "))
        # verdict to table
        with open(TABLE, "a") as f:
            f.write(f"\n### 2D finalist {name}: W2d={r['W2d']} S={r['S']} "
                    f"src={r['src']} -> {'S2-KILL' if 'KILL' in tail else ('S2-PASS' if 'PASS' in tail else 'UNKNOWN')}\n")
            f.write(f"Evidence: `validation/logs/s2_{name}.log`.\n")
    emit("done")

if __name__ == "__main__":
    main()
