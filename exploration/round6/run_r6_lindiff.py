"""Round 6 LIN/DIFF screen runner."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'models'))
from r6 import CANDIDATES_R6
from screen_cal import screen_calibrated

results = []
for name, fn, desc in CANDIDATES_R6:
    t0 = time.time()
    try:
        r = screen_calibrated(fn, name, verbose=False)
        dt = time.time() - t0
        s1kill = r.get("s1_kill", False)
        verdict = r["cal_verdict"]
        # LIN/DIFF details
        lin_D = max(r.get("lin_D", [0])) if r.get("lin_D") else 0
        diff_w = r.get("diff_worst", 0)
        results.append((name, desc, verdict, s1kill, dt, lin_D, diff_w))
        print(f"{name}: {verdict} s1kill={s1kill} {dt:.1f}s linD<={lin_D} diffW={diff_w:.0f} | {desc}", flush=True)
    except Exception as e:
        print(f"{name}: ERROR {e}", flush=True)
        results.append((name, desc, "ERROR", False, 0, 0, 0))

print("\n=== SUMMARY ===")
for name, desc, verdict, s1kill, dt, lin_D, diff_w in results:
    flag = "PASS*" if verdict == "CAL_PASS" else ("KILL" if s1kill else verdict)
    print(f"{flag:6s} {name:22s} linD<={lin_D:4d} diffW={diff_w:8.0f} {dt:5.1f}s")
