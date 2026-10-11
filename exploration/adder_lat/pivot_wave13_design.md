# Track-3 pivot design note — wave-13: cheap bijective replacement form
Date: 2026-10-10 17:50Z. Context: 6-stage x^=AND DIFF wall family-terminal (5/7
and6-sched sub-frontier winners DIFF-killed; as6_200_15/68 under local S1
adjudication — the last live 6-stage hope). No more 5/6-stage x^=AND variants.

## Design rule (from track-8 Axis B diagnosis, ledgered 17:50 CEST)
Replacement form `x := N(x) ^ rk` needs a BIJECTIVE nonlinearity; non-bijective
N (maj, AND, chi-at-64) loses differential mass -> deterministic trails or
DIFFz=256. AND-cascade fails via x^= identity trails; replacement removes them.

## Cost target (from track-8 terminal verdict, 2026-10-09)
Need nonlinear-in-x + balanced + <3.96u/stage (5-stage) or <3.3u/stage (6-stage).
Fastest qualifying bit-level function was MUX at 5.27u/stage (dead). The parked
S-box axis measured sboxL 7.55u in-context (needed <5.55u) — but that was an
unoptimized full-width S-box.

## New probe (UNEXPLORED): bitsliced 4-bit S-box replacement
A parallel 4-bit S-box on all 16 nibbles IS bijective on 64 bits (each nibble
permuted independently). Cost class differs from the parked sboxL: an optimal
4-bit S-box (Boyar/Peralta minimal-multiplicative-complexity, ~4 ANDs + XORs)
bitsliced costs ~2-3 gate levels per nibble — plausibly 2.5-3.5u/stage, inside
the 3.3-3.96u bar. Never measured in this flow.

Plan (cheap kills first):
1. P1: proxy triage — 4/5/6-stage `x := nibSbox(x) ^ rot(rk)` with 2-3 known
   optimal 4-bit S-boxes; filter marg2 + DIFF z<25@16 (v2 proxy methodology).
2. P2: S0 on any proxy-clean candidate (bit-exact RTL via gen script).
3. P3: survivors -> GHA S1/S2, then local S2/S3-16MB/S4 (no frontier claim
   without S3+S4).
Kill triggers: proxy z>=25 (DIFF), S0 >20.1u on all schedules (cost), S1 DIFF
rejections (family kill).

## Deliberately NOT repeated
ARX (82u/stage measured, carry-chain cost intrinsic to this delay model),
MUX 6-stage (31.6u), chi-final (not bijective at 64), non-rotational P-box,
5/6-stage x^=AND in any schedule, maj4 schedule variance (falsified).

## Coordination
Track-5 owns maj+chi hybridization (funded) — no duplication. Track-8's
re-test trigger (c) "word-level non-bit-sliced fused structures" is a second
unexplored axis; parked until nibSbox probe verdicts.

## Methodology lesson (2026-10-10 21:15Z, caught before it killed the axis)
The FIRST wave-13 run used s2proxy_v3's sequential domain (xs=arange(2^16))
and reported z=256.0 (saturated) for BOYAR19 4st/5st — would have killed the
whole axis. Root cause: for per-nibble replacement forms, the sequential
domain freezes nibbles >= logN/4 at constant 0, so output bits outside the
differential cone are trivially constant (|z| = 0.5/sqrt(0.25/N) = 256
exactly at N=65536 pairs). This is a MEASUREMENT artifact, not a cipher
defect — the `x ^=` forms the v3 proxy was validated on mix globally every
stage, so the restricted domain never bit. Rule: **the triage input domain
must cover the construction's locality** — replacement forms need random
full-64-bit pairs (the real hash-finalization input model). Same caveat
applies to S2's diffprof (sequential x=0..2^22): any replacement-form
candidate reaching S2 needs the domain question resolved first, or S2 will
reproduce the artifact. Fixed in triage_wave13.py (maxz_for_delta_rand64,
2^18 pairs, seed 0x13A6E13); KEEP bar z<25 unchanged.

## COST VERDICT (2026-10-10 22:30Z, raw evidence)
Bit-exact single-stage S0 (run_synth.py, Yosys 0.69, analyze==analyze2):
pure stage (BOYAR19 nibble-S-box + transpose) = **4.2u**; pre-whitened = 6.4u.
RTLCHECK 200/200 PASS (iverilog). 6-stage chain ~27.4u >> 20.1u frontier
(need <3.3u/stage). The stage delay is the S-box depth; BOYAR19 is minimal-MC.
S-box cost sweep (all 7 pool boxes) in flight; if ALL >3.3u the 4-bit
replacement axis is TERMINAL.

## Wave-14: odd-width chi + nonlinear cap bit (2026-10-10 22:40Z, NEW AXIS)
Motivation: al_chi6 (even-width chi, 6st, 20.4u) S2-KILLED on deterministic
trails (max|z|~103, ledgered 2026-10-08) -- the even-width chi kernel. But
chi_n is BIJECTIVE iff n is odd (Daemen); the kill mechanism vanishes at odd
width. al_chi6's S1 was nearly clean (FLAG: PB 0, RD 1) -- the defect shows
only at S2. UNEXPLORED in this program (family-level kill was even-width only).
Construction: stage(x): y[62:0] = chi_63(x[62:0]); y[63] = x[63]^(x[A]&x[B]);
out = rotl(y, r_i) (0-delay; moves the cap bit each stage). Full map is
bijective: chi_63 inverts on the low 63 bits, then x[63] = y[63]^F(x[62:0]).
Cost class ~3.3u/stage (al_chi6b 19.8u/6st) -> 5st ~17u plausibly sub-frontier.
Outside the x^= DIFF-wall space; does not duplicate track-5 (maj+chi fused)
or track-8 (word-level fused) or track-6 (batch-33 schedules).
Kill triggers: proxy z>=25 (DIFF), S0 >20.1u (cost), S1/S2 kills (quality).
Cheap-kill order: numpy smoke (random-64 domain) -> S0 -> GHA S1/S2.

## Co-design: nibble-transpose diffusion (2026-10-10 21:20Z)
Under the FIXED (random-domain) gate, single-rotl inter-stage diffusion
measured genuinely weak: ~+4 bits/stage cone growth, thousands of
effectively-constant (delta,bit) cells at 6 stages. Root cause: 4 consecutive
bits rotated by (1 mod 4) land in only 2 nibbles -> cone grows ~+4 bits/stage.
Fix (same 0-delay wiring cost): nibble-transpose bit-permutation
bit(4a+b)->bit(16b+a); each nibble's 4 bits land in 4 DIFFERENT nibbles, cone
doubles per stage, full nibble coverage in 2 S-box layers. Positive control:
6-stage constbits=0. Smoke (2^16 random pairs): BOYAR19 6st z=141.0 (d=0x3),
ULBC_s1 6st z=168.9 (d=0x1) -- real differential signal above the z<25 bar;
4st diffusion-incomplete (constbits=1447). 21-try full triage queued behind
backoff. If 0/21 pass, next co-design levers (not kills): more stages vs cost,
8-bit S-boxes, per-stage round keys.
