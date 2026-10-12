# W3' harvest — checkpoint 2026-10-11 ~21:45 CEST

## Screen (verified complete, NOT re-screened)
- `adder_lat/w3prime/w3prime_screen.jsonl`: 200/200 rows, 29 KEEPs (best z_seq=2.38), 169 REJECT (mostly REJECT-affine pre-check), 2 kills.
- Log `w3prime/screen_w3prime.log` ends `DONE keeps=29`.
- Pre-check strictness documented in `w3prime/PRE_CHECK_NOTE.md` (rank≥8 filter rejects d=±5 weak ANDs; accepted as documented).

## Selection (best z_seq per P-constant class; z_seq is the screen KEEP metric)
| bundle | screen idx | z_seq | z_rnd | full_rank | P | reason |
|---|---|---|---|---|---|---|
| al_w3p_a | 38 | 2.38 | 3.31 | 63 | 0x94d049bb133111eb | best z_seq overall; sole 94d0-class rep |
| al_w3p_b | 19 | 2.43 | 3.72 | 63 | 0x9e3779b97f4a7c15 | best of 9e37 class |
| al_w3p_c | 87 | 2.43 | 3.40 | 62 | 0xbf58476d1ce4e5b9 | best of bf58 class |
| al_w3p_d | 138 | 2.47 | 2.71 | 62 | 0xbf58476d1ce4e5b9 | 4th-best z_seq; distinct schedule from c |

## Bundle verification (gen_w3prime.py, fixed 2 predecessor bugs)
- Bug 1: `0xW3E4` invalid hex literal (SyntaxError) → `0x23E4`.
- Bug 2: C harness `printf("%%016llx\n")` double-escaped → printed literal `%016llx` → `"%016llx\n"`.
- All 4: model.py == screen w3_model on 2000 vec × 3 keys; compiled C == Python; goldens in meta.json. `ALL BUNDLES OK`.

## S0 (running)
- `adder_lat/w3prime/s0/run_s0.sh` launched ~21:46 CEST, sequential via run_synth.py's global yosys flock.
- Log: `adder_lat/w3prime/s0/s0.log`. Bar: < 123.4u (adder-like; wave-14 mission).

## Battery (al_w3p_a COMPLETE — full pass)
- al_w3p_a: S0 48.3u/18917/58806 (< 123.4u bar); S0a xcheck PASS; **S1 CAL_PASS**
  (wave-14's LIN kill fixed by the W3' full-rank probe); **S2 PASS** (0 repeats,
  max|z|=4.1, all 115 deltas); **S3 PASS** (PractRand 1GB, 227 tests, 0 anomalies);
  **S3b PASS** (strided 1GB); **S4 PASS** (SmallCrush); **Q1 sac_z5=0,
  bic_maxcorr=0.00839 (BIC-clean)**.
  Verdict: FULL BATTERY+Q1 PASS. Dominated on implementation axes
  (48.3u/18917/58806 vs r8 42.9u/4133/11670) — retained, not frontier.
  First adder-latency-track design through the full battery with BIC-clean.
- al_w3p_b: S0 50.6u/18322/57155 (< 123.4u bar); S0a xcheck PASS; **S1 CAL_PASS**;
  **S2 PASS** (0 repeats, max|z|=3.9, all 115 deltas); **S3 PASS** (PractRand 1GB);
  **S3b PASS** (strided 1GB); **S4 PASS** (SmallCrush). **BATTERY-PASS.**
  Q1 running. → Q1 DONE: sac_z5=0, bic_maxcorr=0.00858 (BIC-clean).
  **FULL BATTERY+Q1 PASS.** Dominated on implementation axes (50.6u) — retained.
- al_w3p_c: S0 49.0u/18119/56361 (< 123.4u bar); S0a xcheck PASS; **S1 KILL
  (LIN FLAG rej=1, DIFF PASS)**. Verdict: KILLED at S1. Note: c had the minimum
  screen full_rank=62; a/b (rank 63) passed S1 — the rank-62 probe is marginal,
  not a sufficient S1-LIN gate.
- al_w3p_d: S0 48.7u/18983/58731 (< 123.4u bar); S0a xcheck PASS; **S1 CAL_PASS**;
  **S2 PASS** (0 repeats, max|z|=3.9, all 115 deltas); **S3 PASS** (PractRand 1GB);
  **S3b PASS** (strided 1GB); **S4 PASS** (SmallCrush);
  **Q1 sac_z5=0, bic_maxcorr=0.00861 (BIC-clean)**.
  **FULL BATTERY+Q1 PASS.** Dominated on implementation axes (48.7u) — retained.

## Harvest verdict (2026-10-11 ~23:50 CEST)
3 of 4 selected KEEPs pass the full battery + Q1 with BIC-clean (a, b, d);
c killed at S1 (LIN FLAG rej=1). First adder-latency-track designs through the
full battery — the W3' full-rank probe fixed wave-14's S1-LIN kill for rank-63
schedules; rank-62 remains marginal (c). All three survivors dominated on
implementation axes (48–51u vs r8 42.9u) — retained in RETAINED.md, not frontier.

## Battery (pending S0)
- Survivors → `run_fast_battery.sh` START=1, S1→S2→S3→S4→Q1 per b33 playbook.
