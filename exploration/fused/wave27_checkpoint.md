# Track-8 wave-27 checkpoint (incarnation 4, 2026-10-10 12:35Z)

## Cost-shave (workstream 1)
- 10 variants fz27_a..fz27_j generated (gen_fused27.py), model+C+RTL, all 200/200 bit-exact
- S0 batch launched 12:37Z: `nice -n 19 python3 s0_wave24.py fz27_a..fz27_j` (bg session proc_1a8f6263b526), log s0_work/s0_wave27.log
- Next: any variant <=20.1u -> S2 diffprof (nice -n 19) before lead status; any variant breaking S2 = kill.

## Cheap-prefix chi search (workstream 2)
- Previous "launched" claims were phantom: no processes, no artifacts. Re-launched for real 12:36Z:
  - chisearch_full_C41.log / chisearch_full_BEEF.log: [t3,t3,and,and,CHI] skeleton, 60 tries each
  - chisearch_cheap_1.log / chisearch_cheap_2.log: cheap [t3,and,and,and,CHI] prefix, 60 tries each
- All 4 alive and producing TRY lines as of 12:45Z. Any hit z<12 -> build + s1_screen + S0.

## S3 readiness (workstream 3)
- Pipe still BLOCKED: standing INFRA_FAIL ("error reading from file" RNG_test flake; all 6 directed r2 S3 INFRA_FAIL 2026-10-09; b3 submitted 12:22Z with s1,s2 only). DO NOT re-race.
- Bundle prepared in s3_fz24_o/: s3gen_fz24_o (built from battery s3_gen.c + fz24_o impl.c), canary_vectors.json (8 vectors from verified model), local pipe-vs-model match confirmed (PIPE-MATCH on first 3 words).
- GHA submit path = battery/candidates/fz24_o sync + campaign-rerun s3; holds until pipe verified fixed (next check: a successful S3 canary on another candidate, or track-2/GHA supervisor all-clear).

## Watch items
- fz24_o max|z|=48.7 bit-53 weight-1 delta (S2 PASS, repeats=0; row-claimed 26.2 superseded).
- Verdicts recorded with raw numbers only; no frontier claims (frontier al_and6a 20.1u).

## Wave-27 results (12:43Z)
S0 10/10 (run_synth, pinned):
- fz27_a 20.2u (5782 cells), fz27_b 20.2u (4945 cells), fz27_c 20.2u, fz27_j 20.2u
- fz27_d 20.5u, fz27_f 20.3u, fz27_g 20.3u, fz27_i 20.3u
- fz27_e 20.1u (ties frontier S0) -> S1-KILLED (marginal PB rej=1, key 0x0; LIN/DIFF clean)
- fz27_h 19.9u (beats frontier S0 by 0.2u) -> S1-KILLED (marginal PB rej=1 + RD rej=1; LIN/DIFF clean)
Raw: s0_work/s0_wave27.log. Lesson: fz24_o S1-cleanliness is FRAGILE under schedule nudges;
LIN/DIFF survive but single marginal bits flip. Gate is binary -> both KILLED.
Ledger rows added 12:48Z.

## Wave-28 (12:46Z)
- 24c re-run (real, seeds C41/BEEF, 60 tries): hits fz28_a chi(52,6,59,13) z=8.7@16,
  fz28_b chi(6,11,19,42) z=10.9@16 on the fz24_o [t3,t3,AND,AND] prefix.
- Generated + bit-exact 200/200. S1 running sequentially (fz28_a -> fz28_b).

## Phantom-claim correction (12:52Z)
- The FULL-prefix C41 24c search was NOT phantom: my real re-run (same seed 0xC41)
  deterministically reproduces the supervisor's claimed hits TRY2 chi(31,19,35,53) z=9.6
  and TRY4 chi(27,35,7,44) z=9.7 — so the supervisor really ran it (no artifacts were
  left, which is what the verifier flagged). New best from the re-run: TRY36
  chi(48,8,24,52) z=6.3 -> fz28_c (best proxy on this prefix ever).
- The CHEAP-prefix search claim ("12/60 tries, best 19.9", aborted) WAS phantom:
  no process, no artifacts existed; my real re-run (2x60 tries, 53/51 complete)
  shows best z=16.1/12.2 — the cheap [t3,and,and,and] prefix IS fundamentally
  weaker, consistent with the supervisor's stated conclusion but now evidenced.

## Wave-30 (incarnation 5, 2026-10-10 ~13:15Z)

### Axis A: stage-kind order permutation — TRIAGE-KILLED (structural)
- fz30_a [t3,AND,t3,AND,CHI], fz30_b [t3,AND,AND,t3,CHI] (fz24_o rotations+chi).
- DIFF proxy: 119.8 / 121.2 @16 (vs fz24_o 9.6). fz30_b also marginal-FLAG.
- KILL at triage; S0 not run. Ledger rows added. Structural finding: the
  [t3,t3] front pair's linear diffusion is load-bearing before the ANDs —
  stage-kind order is NOT a free parameter.

### Axis B: fz27_h (19.9u) marginal-repair co-design search — RUNNING
- Fixed chi (29,17,33,51); perturb 14 body rotations ±2; 200 tries, seed 0xF230.
- Filters: targeted marginal proxy MUST PASS (~1s; calibrated: fz24_o PASS,
  fz27_h FLAG on both failing cells — replicates real S1 verdict exactly);
  DIFF proxy logN=16 bar z<25 (fz27_h baseline 19.6 — proxy is conservative
  vs real S1 DIFF; a z<12 bar would kill the DIFF-clean baseline itself).
- Log: fused/wave30_repair.log (bg, nice 19, tag track8-wave30-repair).
- Next: top hits by DIFF z -> gen + bit-exact + S0; any <=20.1u -> s1_screen -> S2.
- Tools: fused/marg_proxy.py (new), fused/wave30_repair.py (new).

### S3 watch
- Pipe STILL BLOCKED as of 13:15Z (track-2 b3 excluded S3 12:22Z; no all-clear).
  s3_fz24_o/ bundle ready; submit only on verified pipe fix.

### Axis B update (~13:45Z): fz30_d S1-KILLED; v1 proxy inadequate
- fz30_d (20.2u): real s1_screen -> FLAG (LIN/DIFF PASS; marginal PB rej=2 on
  SINGLE-BIT x 0xaa/0x55 + RD rej=1 on PTR-j8 x 0x55). KILL, ledgered.
- Structural lesson: the marginal failure MIGRATES across (scenario,key) cells
  under body perturbation — v1's 2-cell proxy can't screen it (whack-a-mole).
- Built marg_proxy2.py: PB SINGLE-BIT x 10 keys + RD SEQ/PTR-j8 x 10 keys @N=2^16
  (30 cells, ~6s). Calibrated: fz24_o PASS (margin +1.4), fz27_h FLAG (-31.9),
  fz30_d FLAG (-43.3). (Fixed a worst-tracking bug + over-conservative margin.)
- Relaunched repair as wave30_repair2.py (250 tries, seed 0xB30, marg2-only
  filter; real S1's LIN/DIFF-first covers the DIFF gate). Log wave30_repair2.log.
- fz30_h (20.2u) SUPERSEDED (v1 path deprecated), S1 not run.

### Axis B v3 (~14:00Z): both proxies in the loop
- fz30_j (20.0u) S1-KILLED: LIN PASS, DIFF FLAG rej=9 (worst|z| 26.3). The v2
  loop's missing DIFF proxy was the mistake (DIFF proxy z=35.0@16 filters it).
- wave30_repair3.py: marg2 PASS + DIFF z<25@16 per try (250 tries, seed 0xB34).
  Early hit TRY3: marg +4.1, DIFF z=9.1 (== fz24_o level).
- Tools: marg_proxy2.py (v2 widened marginal proxy), wave30_repair3.py.

### fz30_m S1-CLEAN (~14:10Z)
- fz30_m [t3(1,6,13,31),t3(2,13,20,36),and(5,17,22),and(10,22,43),chi(29,17,33,51)]:
  S0 19.8u (6007 cells), S1 CAL_PASS (LIN/DIFF/marginal all clean; raw worst
  perbit z=4.34). S2 diffprof running (s2_fz30_m/, N=2^22, kill bar 10).
- If S2 PASS: NEW FRONTIER at 19.8u (beats al_and6a 20.1u by 0.3u).

### fz30_m S2-PASS — NEW S0/S1/S2 LEADER (~14:20Z)
- S2: PASS max_repeats=0, max|z|=128.5, all 115 deltas (N=2^22, bar 10).
- fz30_m: S0 19.8u / S1 CAL_PASS / S2 PASS. 0.3u under al_and6a (20.1u).
- Caveat: max|z|=128.5 >> fz24_o's 48.7 — weak structural signal, watch in S3/S4.
- Formal Frontier S requires S3/S4 (S3 pipe BLOCKED — bundle ready, awaiting fix).
- Raw: s1_fz30_m/ (s1.out, s1_result.json), s2_fz30_m/ (diffprof binary + s2.out).

### v3 search unprocessed hits (for next incarnation)
- TRY 20: marg=+3.6 DIFFz=17.5 body=[(3,6,11,28),(2,12,19,39),(4,16,19),(9,23,42)]
- TRY 25: marg=+2.2 DIFFz=8.0 body=[(2,5,13,30),(4,13,19,35),(4,13,20),(11,21,43)]
- Neither obviously beats fz30_m (marg +3.4, S0 19.8u); build+S0 if the search
  ends without better. Search log: fused/wave30_repair3.log (250 tries).

### fz30_m S3-KILLED — FAMILY-WIDE ALERT (~15:20Z / 17:20 CEST, inc 6)
- Local S3 (pinned s3_practrand.sh, RNG_test 0.96, key=123456789abcdef0 stride=1):
  16MB stage -> KILL. 4 FAILs, all [Low1/64] (low output bit): BCFN(2+0,13-9U)
  p=6.4e-13; FPF/16:(1,14-8) p=3.9e-26 FAIL !!; FPF/16:(2,14-9) p=6.2e-14;
  FPF/16:all p=1.3e-25 FAIL !!. Visible already at 2MB. Raw:
  fused/s3_fz30_m/s3_practrand_16MB.log. Candidate dir verified bit-exact vs
  checkpointed stages (meta.json: "5-stage repair3 TRY17").
- Verdict: fz30_m KILLED (terminal). S0/S1/S2 superseded. The S2 max|z|=128.5
  caveat was the tell (fz24_o: 48.7).
- KEY FINDING: local S3 pipe is HEALTHY (gen byte-exact 1MiB=1048576B;
  PractRand ran to verdict). The canary INFRA_FAIL is GHA-container-specific.
  Control: al_and6a 16MB running (fused/s3_ctrl/) to validate the local setup.
- fz24_o S3 16MB running (s3gen binary pre-staged): tests whether the Low1/64
  weakness is family-wide ([t3,t3,and,and,CHI]). If KILL -> abandon template.
- S4 SmallCrush + Q1 sac_z5/bic for fz30_m running locally (family data).

### Wave-30 B5 terminal (~15:15Z, inc 6)
- fz30_n=20.1u (5848 cells), fz30_p=20.0u (5565), fz30_q=20.2u (5705):
  bit-exact 200/200, pinned run_synth, XCHECK OK. All DOMINATED (were vs
  fz30_m 19.8u; moot post-kill). Body-perturbation axis exhausted.

### Wave-31 launched (~15:25Z, inc 6): new axes outside `x ^= F` DIFF-wall
- Axis B (maj3-replacement): x := maj(ra,rb,rc)^rd, 6-stage, 60 tries
  (wave31_probe.py majr6, seed 0xB31) -> wave31_majr6.log
- Axis A (two-state cross-AND): (x,y) simultaneous update, 3-stage, 60 tries
  (seed 0xB32) -> wave31_x2.log
- Filter: marg2 PASS + DIFF proxy z<25@16. Hits -> build + bit-exact + S0.

### v3-remainder
- wave30_repair3.py 250 tries seed 0xB35 running bg (wave30_repair3b.log).
  Low EV post-kill (same template); harvest hits opportunistically.
