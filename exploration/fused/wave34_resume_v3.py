#!/usr/bin/env python3
"""Wave-34 V3 resume after 19:47:25Z reboot killed the run at TRY 20/25.

Deterministic RNG (random.Random(0x34 ^ 0xD3), sequential make_stages calls),
so this replays tries 1-20 identically to the killed run (expected 0 hits
again, verifying determinism) and computes the missing tries 21-25.
Log: fused/wave34_v3.log (kept separate from the killed-run wave34.log).
"""
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from wave34_probe import screen_variant

if __name__ == "__main__":
    print("WAVE34 V3 RESUME start (seed 0x34^0xD3, 25 tries)", flush=True)
    hits = screen_variant("V3", 4, 25, 0x34 ^ 0xD3)
    print(f"RESUME V3 complete: {len(hits)}/25 hits", flush=True)
