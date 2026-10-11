#!/usr/bin/env python3
"""Batch-15 schedule validator for 3-AND stages.

Design principles (from track-3 wave-9 + 3-AND theory):
1. Danger-zone-free: no rotations in [28,36], none >= 54
2. Within-triple spread: min pairwise diff of (a,b,c) >= 7 (avoid locality)
3. Triple diffs incommensurate: avoid simple ratios like (1,2,4)
4. XOR d: large and incommensurate with triple diffs
5. Across-stage: different triple shapes to avoid resonance
"""

DANGER_LO = range(28, 37)  # [28,36]
DANGER_HI = 54

def check_rot(r):
    if r in DANGER_LO:
        return f"DANGER-LO [{r}]"
    if r >= DANGER_HI:
        return f"DANGER-HI [{r}]"
    return None

def check_triple(a, b, c):
    """Check within-triple spread."""
    diffs = sorted([abs(a-b), abs(b-c), abs(a-c)])
    # Also consider wraparound diffs (rotation is mod 64)
    issues = []
    if diffs[0] < 7:
        issues.append(f"min-diff {diffs[0]} < 7 (too local)")
    # Check for simple ratios (1:2, 1:3, 2:3, etc.)
    d1, d2, d3 = diffs
    # d3 should be ~d1+d2 for a "spread" triple; if d3 << d1+d2, it's clustered
    return diffs, issues

def check_schedule(name, sched):
    print(f"\n=== {name} ===")
    all_ok = True
    for i, (a, b, c, d) in enumerate(sched):
        # Check danger zones
        for r, label in [(a,'a'), (b,'b'), (c,'c'), (d,'d')]:
            err = check_rot(r)
            if err:
                print(f"  Stage {i} {label}={r}: {err}")
                all_ok = False
        # Check triple spread
        diffs, issues = check_triple(a, b, c)
        status = "OK" if not issues else "ISSUES: " + "; ".join(issues)
        print(f"  Stage {i}: triple=({a},{b},{c}) diffs={diffs} d={d} [{status}]")
        if issues:
            all_ok = False
    print(f"  Overall: {'PASS' if all_ok else 'FAIL'}")
    return all_ok

# Batch-14 (failed) schedule for reference
B14 = [
    (1, 2, 3, 13),
    (7, 19, 5, 29),
    (3, 11, 17, 7),
    (11, 23, 37, 19),
    (19, 41, 23, 31),
]

# Batch-15 Schedule A: spread triples, progressive
SCHED_A = [
    (5, 19, 41, 13),
    (7, 23, 47, 17),
    (3, 17, 43, 11),
    (13, 27, 51, 7),
]

# Batch-15 Schedule B: different shapes
SCHED_B = [
    (3, 13, 37, 19),
    (9, 21, 45, 5),
    (7, 17, 41, 23),
    (5, 19, 43, 11),
]

# Batch-15 Schedule C: aggressive spread, varied d
SCHED_C = [
    (7, 25, 49, 13),
    (5, 23, 47, 19),
    (11, 27, 51, 17),
    (3, 21, 43, 9),
]

if __name__ == "__main__":
    print("Reference: Batch-14 (failed) schedule")
    check_schedule("B14 (failed)", B14)
    check_schedule("SCHED_A", SCHED_A)
    check_schedule("SCHED_B", SCHED_B)
    check_schedule("SCHED_C", SCHED_C)
