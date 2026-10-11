# Independent audit of round-7 leader r7_feist8_s1_1sbox (2026-10-02)

Composition: 8-round Feistel, val^key whitening, F = S1 nibble S-box layer
-> x^rotl32(x,7)^rotl32(x,13) -> ^rk32 (ONE S-box layer, vs r6's two).
No final swap; output {R,L}.

## S0 (delay) — CONFIRMED, with toolchain-bug fix
- Pinned run_synth.py (Yosys 0.69): 56.5u = 0.546x (ref mul64 103.5u),
  6063 cells, area 17098. analyze.py == analyze2.py.
- FOUND BUG (fixed): bare "yosys" in subprocess resolved to /usr/bin/yosys
  0.33 when conda env not on PATH, giving 78.3u for identical RTL (38% silent
  error). Same failure class as the 2026-10-01 flow-order bug.
  Fix: YOSYS pinned to ~/tools/micromamba-root/envs/sky130/bin/yosys with
  `yosys -V` asserting "0.69" in run_synth.py AND s0_delay.py.
  Guard red-green tested: rejects 0.33, accepts 0.69.
  Lesson added to ~/AGENTS.md.
- Round-6 numbers used 0.69 (ref 103.5u matches), so cross-round comparison
  r6 86.5u=0.836x vs r7 56.5u=0.546x is valid.
- Other survivors spot-checked: r7_feist8_spn_nw 84.7u=0.818x matches team.

## S1 — CONFIRMED from raw JSON
- s1_result.json: verdict CAL_PASS, 0/0/0/0 rejections (PB/RD/LIN/DIFF).

## S2 — CONFIRMED by independent re-run (2 keys)
- Team reported PASS on 1 key but persisted no log; re-ran both keys
  (N=2^22, 74 deltas, kill>1000), logs at round7/audit/s2_k0.log, s2_k1.log:
  - key=0: PASS, max_repeats=0, max|z|=3.6
  - key=0x123456789ABCDEF0: PASS, max_repeats=0, max|z|=3.8
- Zero full-64-bit repeats on either key (vs 41,889 for h_xorspn3).

## S3 — CONFIRMED from raw logs
- PractRand 1GB "no anomalies in 227 test result(s)" on 3 configs
  (k0 stride1, k1 stride1, k1 stride3). Logs genuine (small, anomaly-only).

## S4 — CONFIRMED from raw log
- SmallCrush: "All tests were passed" (all 15).

## Equivalence — CONFIRMED (stronger than team's)
- ABC cec: RTL vs team's dretime-mapped netlist -> "Networks are equivalent
  after structural hashing" (0.01s). The 56.5u mapping is functionally correct.
- C vs Python model: 10,000/10,000 random vectors.
- RTL vs Python model (iverilog): 300/300 random vectors.

## Bijectivity — CONFIRMED
- Structural: Feistel round (L,R)->(R,L^F(R)) is a permutation for any F;
  whitening val^key is a permutation for fixed key; no-swap output fine.
- Constructive inverse: 20,000/20,000 random (v,k) recovered.

## Kill reasons — spot-verified against raw evidence
- r7_feist6_spn: s1_result.json verdict FLAG, 3 RD rejections (PTR-j8 x2, SEQ).
  6-round borderline kill stands.
- r7_ufeist16_48: smallcrush log shows CollisionOver p=1.6e-4
  (obs 3106 vs exp 2909.25). Kill stands.

## Verdict
r7_feist8_s1_1sbox is a VALIDATED new leader: 56.5u=0.546x, 35% faster and
30% smaller than r6_feist8_spn, full S0-S4 + equivalence + bijectivity.
Pending: S2 second-key confirmation (running), then S5 P&R + peer reviews.
