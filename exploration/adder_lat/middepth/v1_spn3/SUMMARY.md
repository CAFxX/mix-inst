# V1 3-stage SPN — verdict O146: COST-CLOSED (2026-10-12)

## S0 measurements (run_synth.py, ref mul64 103.5u, XCHECK pass on all)

| DUT | crit | cells | verdict |
|---|---|---|---|
| S-box layer alone (16x Midori Sb0) | 3.0u | 179 | matches O135 |
| 4-term linear alone `x^r7^r13^r29^r41` | 5.5u | 727 | NOT the ~2-3u estimate |
| stage: S-box + 4-term | 8.2u | 995 | >3.5u stage budget -> 4-term KILLED |
| stage: S-box + rotation-XOR `x^r7^r29` | 6.4u | 816 | >3.5u -> rot-XOR KILLED |
| stage: S-box + PRESENT P-box | 3.0u | 179 | wiring-only, 0u added -> proceeds |
| FULL 3-stage PRESENT (x^k in, ^rotl(k,13) out) | 13.0u | 819 | >10u strict -> V1 KILLED |
| core: 3 stages, no whitening | 9.0u | 624 | = 3x3.0u; whitening XORs cost 4.0u |

## Cost-model correction for DESIGN.md
- 5-term XOR = 3 XOR levels (not 2). Per-XOR2-level cost in mini.genlib ≈ 1.8-2.0u
  (4-term 5.5u/3lv = 1.83u; rot-XOR 3.4u/2lv = 1.7u; whitening 4.0u/2lv = 2.0u;
  consistent with O145's independent XOR2=2.0u).
- "4-term ~2-3u (2 XOR levels)" was doubly wrong. Budget ~1.8-2.0u per XOR level.

## Why dead
3x3.0u S-box = 9.0u leaves 1.0u of budget; the two whitening XORs alone cost 4.0u.
Even a zero-cost linear cannot fit <10u. No Fisher triage (cost gate first).

## Artifacts
- `v1_model.py`: Verilog generator + bit-exact numpy model (Midori Sb0)
- `stage_*.v`, `spn3_present_full.v`, `spn3_core_nowhite.v`: measured RTL
- `s0_*/`: synth workdirs
