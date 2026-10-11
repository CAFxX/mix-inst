# Round 9 — Pareto-frontier search (2026-10-02)

Target: beat `r8_feist6_s1_1sbox_nw` — 42.9u (0.414×), 4,133 cells, area 11,670.
Multiplier reference re-measured fresh in this round's pinned flow: **103.5u**
(cells 12,645, area 35,323). S0 bar: ≤ 0.9 × 103.5 = 93.15u.

S0 numbers below are from `run_synth.py` (authorized path, Yosys 0.69 pinned,
dual-analyzer agreement). Battery S0 (`s0_delay.py`) is the stage gate only.

## S0 pre-screen (all 14 pass the 0.9× bar)

| Candidate | Structure | S0 delay | Ratio | Cells | Area |
|---|---|---:|---:|---:|---:|
| r9_feist5_s1_1sbox_nw | 5r, F=S1x1+lin713, no white | 35.1u | 0.339× | 3,633 | 10,325 |
| r9_feist5_s1_1sbox | 5r, F=S1x1+lin713, white | 36.6u | 0.354× | 3,742 | 10,611 |
| r9_feist6_rot0824_nw | 6r, F=S1+lin(8,24), no white | 40.4u | 0.390× | 4,320 | 12,152 |
| r9_feist6_rot311_nw | 6r, F=S1+lin(3,11), no white | 41.0u | 0.396× | 4,265 | 11,996 |
| r9_feist6_ksalt_nw | 6r, F=S1x1+lin713, alt key halves, no white | 41.8u | 0.404× | 4,628 | 12,946 |
| r9_feist6_rot0719_nw | 6r, F=S1+lin(7,19), no white | 41.8u | 0.404× | 4,602 | 12,963 |
| r9_feist6_rot1119_nw | 6r, F=S1+lin(11,19), no white | 42.2u | 0.408× | 4,502 | 12,707 |
| r9_feist6_ksrot_nw | 6r, F=S1x1+lin713, rk=rotl64(k,8i), no white | 42.5u | 0.411× | 4,777 | 13,351 |
| r9_feist6_rot0925_nw | 6r, F=S1+lin(9,25), no white | 42.7u | 0.413× | 4,138 | 11,546 |
| r9_feist6_nork | 6r, F=S1x1+lin713 no rk, white only | 43.0u | 0.415× | 3,976 | 10,950 |
| r9_feist6_altrot_nw | 6r, F=S1+lin alt (7,13)/(5,17), no white | 43.2u | 0.417× | 4,338 | 12,239 |
| r9_feist6_rot517_nw | 6r, F=S1+lin(5,17), no white | 43.2u | 0.417× | 4,225 | 11,937 |
| r9_feist7_rot517_nw | 7r, F=S1+lin(5,17), no white | 49.3u | 0.476× | 5,454 | 15,308 |
| r9_feist7_s1_lin2_nw | 7r, F=S1+lin713+lin713, no white | 66.6u | 0.643× | 7,532 | 20,968 |

Notes:
- Rotation pair (a,b) ≡ (b,a): lin is XOR-commutative. (13,7)/(17,5) were
  caught as duplicates of (7,13)/(5,17) by output comparison and replaced
  with (9,25)/(7,19) before synthesis.
- Bit-exactness: C↔Python 10,000/10,000 PASS (14/14); RTL↔Python 300/300 PASS (14/14).

## Battery results

| Candidate | S0 delay | Stage reached | Kill reason / notes |
|---|---|---|---|
| r9_feist5_s1_1sbox_nw | 35.1u | S4 PASS* | *S2: 34/115 deltas show repeats (max 7), max\|z\|=35.1; Q1: sac_z5=61. Passes formal gates; differential quality regresses vs 6r. NOT claimed as leader (see notes). |
| r9_feist5_s1_1sbox | 36.6u | S4 PASS* | *Same 5r differential caveat as nw twin. |
| r9_feist6_rot0824_nw | 40.4u | S1 kill | LIN FLAG (rej=10) + DIFF FLAG (rej=10). Byte-aligned rots (8,24) preserve byte structure. |
| r9_feist6_rot311_nw | 41.0u | **S4 PASS** | **New Pareto point** (frontier extension). S2: 0 repeats, max\|z\|=16.5 on two 2-bit deltas (diagnostic, see notes). Q1: clean (sac_z5=0, noise floor). |
| r9_feist6_ksalt_nw | 41.8u | S4 PASS | S2: 0 repeats, max\|z\|=4.3 (clean). Q1 clean. Dominated by rot311 (slower + bigger). |
| r9_feist6_rot0719_nw | 41.8u | S4 PASS | S2: 0 repeats, max\|z\|=7.0. Q1 clean. Dominated by rot311 (slower + bigger). |
| r9_feist6_rot1119_nw | 42.2u | S1 kill | LIN/DIFF pass; marginal FLAG. |
| r9_feist6_ksrot_nw | 42.5u | S4 PASS | S2: 0 repeats, max\|z\|=3.8 (clean). Q1 clean. Dominated by rot311 (slower + bigger). |
| r9_feist6_rot0925_nw | 42.7u | S1 kill | DIFF FLAG (rej=10). |
| r9_feist6_nork | 43.0u | S1 kill | LIN/DIFF pass; marginal FLAG. Round key in F is load-bearing. |
| r9_feist6_altrot_nw | 43.2u | S4 PASS | Heterogeneous alternating (7,13)/(5,17) — fully clean (S2 \|z\|=4.0, Q1 clean). Dominated by rot311 + leader. |
| r9_feist6_rot517_nw | 43.2u | S4 PASS | Slower than leader — not Pareto. |
| r9_feist7_rot517_nw | 49.3u | S4 PASS | **7r-nw repair: YES** — (5,17) rescues 7r-nw where (7,13) died in S1. S2 clean (\|z\|=3.7), Q1 clean. Dominated (slower + bigger than leader). |
| r9_feist7_s1_lin2_nw | 66.6u | S4 PASS | Doubled linear rescues 7r-nw too (S2 \|z\|=3.7, Q1 clean) but costs 66.6u — dominated. |

## Pareto frontier

Standing (pre-round-9): { r8_feist6_s1_1sbox_nw: 42.9u, 4133 cells, 11670 }.

**Round-9 result: THE PARETO FRONTIER EXTENDED.** New fastest qualified point:
**r9_feist6_rot311_nw — 41.0u (0.396× multiplier), 4,265 cells, area 11,996**
(6r Feistel, F = S1 S-box layer → x^rotl32(x,3)^rotl32(x,11) → ^rk32, no input
whitening, affine key schedule).

Evidence for the new Pareto point:
- S0: 41.0u ≤ 93.15u bar (0.396× of 103.5u ref, pinned Yosys-0.69 flow,
  dual-analyzer agreement); cells 4265, area 11996; mapped-netlist
  equivalence 1000/1000 vectors (battery S0).
- S1: CAL_PASS (LIN PASS, DIFF PASS, marginal PB rej=0 RD rej=0).
- S2: PASS, 0 full repeats (115 deltas); max|z|=16.5 on two 2-bit deltas
  (0x0000000900000000, 0x9000000000000000) — diagnostic note, see below.
- S3: PractRand PASS to 1 GB (key=0x123456789ABCDEF0 stride=1, and
  key=0x0 stride=0x9E3779B97F4A7C15).
- S4: TestU01 SmallCrush 15/15 PASS.
- Q1 spot check (SAC/BIC, N=2^18): sac_z5=0, sac_maxdev=0.00353,
  sac_meandev=0.00078, bic_maxcorr=0.00884, avalanche_mean=32.0016 — at noise
  floor, indistinguishable from the old leader.
- Bit-exactness: C↔Python 10,000/10,000; RTL↔Python 300/300.

Frontier (delay, cells, area — lower is better), qualified candidates only:
{ r9_feist6_rot311_nw: 41.0u/4265/11996, r8_feist6_s1_1sbox_nw: 42.9u/4133/11670 }.
rot311 is 4.4% faster but 3.2% larger / 2.8% more area — a genuine tradeoff
point, not a domination.

Quality note on the new point: S2 max|z|=16.5 on two 2-bit input deltas vs
4.0 for the old leader (both 0 repeats; Q1 clean for both). The (3,11)
rotation pair shows more second-order differential structure than (7,13).
Not exploitable under the secret-key threat model (S1 DIFF passes, PractRand
clean), but a real certificational difference: pick (7,13) for max quality,
(3,11) for max speed.

**Deliberately NOT on the frontier:** r9_feist5_s1_1sbox_nw (35.1u) and
r9_feist5_s1_1sbox (36.6u) pass S0–S4 formally but fail the Q1 spot check
required for a Pareto claim (sac_z5=61/55 vs 0 for every qualified leader;
S2: 34/115 deltas with full repeats, max|z|=35.1). Five rounds do not fully
diffuse — there is a differential phase transition between 5 and 6 rounds.
Retained as fast-but-weaker alternatives, not leaders.

## Family summaries

1. **5-round probe:** both pass S0–S4 (35.1u/36.6u) but show the 5r
   differential phase transition. Not claimed.
2. **Rotation sweep (6r-nw):** (3,11) PASS → new Pareto point; (5,17) PASS,
   clean (43.2u, dominated); (7,19) PASS (41.8u, dominated by rot311);
   (8,24) S1 hard kill (LIN+DIFF FLAG) — byte-aligned rotations preserve
   byte structure; (11,19) S1 marginal kill; (9,25) S1 DIFF kill.
   Rotation pair matters statistically, not just for delay.
3. **Key-schedule ablation (6r):** alternating halves (41.8u, S4 PASS, S2
   |z|=4.3 clean, dominated); rotl64(k,8i) (42.5u, S4 PASS, clean,
   dominated); no-round-key (43.0u, S1 marginal kill — round key in F is
   load-bearing). Key schedule barely moves delay (±1u); affine schedule
   retained.
4. **7r-nw repair:** YES — (5,17) rescues 7r-nw (49.3u, S4 PASS, S2/Q1
   clean) where (7,13) died in S1; doubled linear also works (66.6u).
   Both dominated on delay/area.
5. **Heterogeneous:** alternating (7,13)/(5,17) per round — S4 PASS, fully
   clean (S2 |z|=4.0, Q1 clean), 43.2u. Works, but dominated.

## Process notes (escape protocol)

- **S2 threshold mismatch (found 2026-10-02):** the hardened kill threshold
  (10) was changed in `s2_diffprof.c`'s default but `run_fast_battery.sh`
  passes `ref/s2_kill_repeats.txt` (=1000) explicitly, so every battery
  (rounds 7–9) actually ran at 1000. Fixed: ref file → 10; re-ran S2 for
  the only candidates with repeats>0 (the 5-rounders, 7 < 10) — no verdict
  changes. Lesson: a hardened parameter must be verified at the call site,
  not just the default.
- **Rotation commutativity:** lin(a,b) ≡ lin(b,a) (XOR). (13,7)/(17,5) were
  caught as exact duplicates of (7,13)/(5,17) by model-output comparison
  before synthesis and replaced with (9,25)/(7,19). Lesson: dedupe the
  spec space by model equivalence before generating RTL.
- **Queue resilience:** the first R9 queue died when its exec session was
  reaped (2 batteries orphaned mid-S2, 5 never started). Re-ran the 7
  remaining fully detached (setsid/nohup). Lesson: long queues must be
  detached from the spawning session.
