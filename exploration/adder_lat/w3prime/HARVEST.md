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

## Battery (pending S0)
- Survivors → `run_fast_battery.sh` START=1, S1→S2→S3→S4→Q1 per b33 playbook.
