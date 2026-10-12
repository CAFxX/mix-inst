import random
from dag_sim import compute_fanin

# Search for 6 offsets giving fan-in 64 for all outputs
# Gate types: 4 AND + 2 XOR (for 9.4u)
best = None
random.seed(42)
for trial in range(50000):
    offsets = [random.randint(1, 63) for _ in range(6)]
    # Skip if any offset is 0 or 32 (degenerate)
    if any(a % 32 == 0 for a in offsets):
        continue
    fanin = compute_fanin([0,0,0,0,1,1], offsets)  # 4 AND, 2 XOR
    min_fanin = min(fanin)
    if min_fanin == 64:
        print(f"Found! offsets={offsets}")
        best = offsets
        break
    if trial % 10000 == 0:
        print(f"Trial {trial}: best min_fanin so far...")

if not best:
    print("No perfect 64 found, searching for max...")
    max_fanin = 0
    best_off = None
    for trial in range(50000):
        offsets = [random.randint(1, 63) for _ in range(6)]
        if any(a % 32 == 0 for a in offsets):
            continue
        fanin = compute_fanin([0,0,0,0,1,1], offsets)
        mf = min(fanin)
        if mf > max_fanin:
            max_fanin = mf
            best_off = offsets
    print(f"Best: min_fanin={max_fanin}, offsets={best_off}")
