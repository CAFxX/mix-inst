"""Verbatim Fisher triage (lin_diff.screen_lin_diff) for Repair A candidates.

Usage: python3 fisher_triage.py Ea Eb Oa Ob [Ea2 Eb2]
Builds S[x] for x in [0, 2^18) and calls screen_lin_diff verbatim.
"""
import sys, time
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
import numpy as np
from lin_diff import screen_lin_diff
from toffoli import BITS, run, assemble, N

def main():
    v = list(map(int, sys.argv[1:]))
    assert len(v) in (4, 6) and all(x % 2 == 1 for x in v)
    E1, O1 = (v[0], v[1]), (v[2], v[3])
    seq = [(E1[0], E1[1], 0), (O1[0], O1[1], 1)]
    tag = f"E{E1}+O{O1}"
    if len(v) == 6:
        E2 = (v[4], v[5])
        seq.append((E2[0], E2[1], 0))
        tag += f"+E{E2}"
    t0 = time.time()
    S = assemble(run(BITS, seq))
    print(f"built S ({tag}), N={N}, {time.time()-t0:.1f}s", flush=True)
    t0 = time.time()
    res = screen_lin_diff({0x0: S}, verbose=True)
    print(f"screen took {time.time()-t0:.1f}s", flush=True)
    print(f"VERDICT LIN={res['lin_verdict']} DIFF={res['diff_verdict']}", flush=True)

if __name__ == "__main__":
    main()
