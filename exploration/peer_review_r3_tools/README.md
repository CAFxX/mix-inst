# Peer-review remediation tools (round 3, 2026-10-01)

- `diffprof.c` — differential profiler: for each input delta (64× weight-1,
  8× weight-2), measures per-output-bit flip bias (max|z|), low-8-bit truncated
  χ², and full-64-bit output-difference repeats over N sequential input pairs
  (deduplicated). Usage: `./diffprof <key_hex> [log2N]`.
  Output for key 0x123456789ABCDEF0, N=2^22: `../results/r3/diffprof_key1234.txt`.
- `colladv.c` — collision-forcing advantage for a chosen input delta:
  P(low8(dx)==0) vs 1/256 and top-8 low-8-bit differences.
  Usage: `./colladv <key_hex> <delta_hex> [log2N]`.
- `recell24.py` — re-runs `screen_lib` reduction cells (mask8, mask32, lemire
  10/1000/2^32) at N=2^24 on SEQ and PTR-j8 scenarios, chunked for low memory.
- `analyze_fo.py` — `synth/analyze.py` variant with a fanout penalty k added
  per unit fanout: `python3 analyze_fo.py <mapped.v> <genlib> <k>`.
  k=0 reproduces the published numbers bit-exactly.
