# Round 20 — notr family probes

**Date:** 2026-10-03. **Frontier after round:** TBD
{r19_feist6_alt_notr_chioff13_nw: 37.4u, r18_feist6_alt_notr_nw: 37.9u} entering.

**Multiplier reference:** 103.5u (pinned Yosys-0.69 flow; S0 bar ≤ 93.15u).

## Families (all 6r Feistel, no whitening, affine r7/r8/r9 key schedule)

Baseline (entering frontier): odd rounds F_S1 = lin(3,11)(S1(R))^rk, even
rounds 2,4 F_chi = lin(3,11)(chi32(R))^rk, round 6 F = chi32(R)^rk (truncated).

- **notr_s1final**: r18 notr but round 6 F = S1(R)^rk (no linear) — does an
  S1 final avoid the chi BIC blemish?
- **notr_chioff13all**: chioff13 with chi(1,3) also on round 6 (truncated).
- **chioff13_517**: chioff13 with (5,17) rotmix on the 5 surviving linears.
- **notr_keyin**: round 6 F = chi32(R ^ rk32) (key inside chi input).
- **notr_drop4**: round 4's (chi) linear ALSO dropped (S1-gated probe;
  expect harm — F_4 feeds F_5's input).
- **notr_713**: (7,13) rotmix on the 5 surviving linears.
- **notr_fm16**: F_6 = (chi32(R)^rk) ^ rotl32(chi32(R)^rk, 16) — BIC-fix probe.
- **notr_chioff31**: chi variant b_i = a_i ^ (~a_{i+3} & a_{i+1}) on rounds 2,4.
- **alt_chioff13**: r13-full alt (WITH round-6 linear) + chi(1,3) on rounds
  2,4,6 — S1+S2 only unless near-frontier.

Generator: `round20/gen_r20.py`; reference: `round20/models/r20.py`.

## Bit-exactness

C↔model 10,000/10,000 and RTL↔model 300/300 — results in `round20/xcheck/`,
`round20/rtlcheck/`. Round-key indexing: (i+2) convention (round-11 lesson);
all 9 first try.

## S0 ([run_synth.py](../run_synth.py), authorized path)

| Candidate | Delay | Ratio | Cells | Area | vs frontier |
|---|---:|---:|---:|---:|---|
| r20_feist6_alt_notr_s1final_nw | 39.4u | 0.381× | 4,091 | 11,700 | dominated by notr (37.9u) |
| r20_feist6_alt_notr_chioff13all_nw | **37.0u** | 0.357× | 4,357 | 12,511 | **faster than chioff13 (37.4u)** — full battery |
| r20_feist6_alt_notr_chioff13_517_nw | 38.4u | 0.371× | 4,100 | 11,734 | dominated by notr |
| r20_feist6_alt_notr_keyin_nw | **37.2u** | 0.359× | 4,382 | 12,497 | **faster than chioff13 (37.4u)** — full battery (near-duplicate of chioff13all) |
| r20_feist6_alt_notr_drop4_nw | **34.3u** | 0.331× | 4,198 | 11,787 | tempting — S1/S2-gated probe |
| r20_feist6_alt_notr_713_nw | 38.6u | 0.373× | 4,058 | 11,729 | dominated by notr |
| r20_feist6_alt_notr_fm16_nw | 40.5u | 0.391× | 4,717 | 13,401 | dominated (BIC-fix probe; worse than fm03's 39.8u) |
| r20_feist6_alt_notr_chioff31_nw | **37.5u** | 0.362× | **3,863** | **11,199** | **smaller than chioff13** on cells+area — full battery |
| r20_feist6_alt_chioff13_nw | 40.0u | 0.386× | 4,407 | 12,743 | dominated (S1+S2 only per brief) |

All 9 pass the S0 bar (≤ 93.15u). Multiplier ref: 103.5u.
Note: keyin's first S0 (38.0u) was measured on a buggy RTL (tail double-XORed
rk32 — caught by check_rtl 300/300 before synthesis numbers were trusted, per
process). Fixed, re-ran: 37.2u. The bug is documented in Process notes §1.

## S1

| Candidate | S1 verdict | Detail |
|---|---|---|
| r20_feist6_alt_notr_s1final_nw | **CAL_PASS** | rej=0 all four families |
| r20_feist6_alt_notr_chioff13all_nw | **CAL_PASS** | rej=0 all four families |
| r20_feist6_alt_notr_chioff13_517_nw | **CAL_PASS** | rej=0 all four families |
| r20_feist6_alt_notr_keyin_nw | **CAL_PASS** | rej=0 all four families |
| r20_feist6_alt_notr_drop4_nw | **CAL_PASS** | rej=0 — S1 blind to truncation breakage (r19 notr5 class); S2-gated |
| r20_feist6_alt_notr_713_nw | **CAL_PASS** | rej=0 all four families |
| r20_feist6_alt_notr_fm16_nw | **CAL_PASS** | rej=0 all four families |
| r20_feist6_alt_notr_chioff31_nw | **CAL_PASS** | rej=0 all four families |
| r20_feist6_alt_chioff13_nw | **CAL_PASS** | rej=0 all four families |

9/9 pass S1 with zero rejections — including drop4 (34.3u), which S1 cannot
see as broken (same class as r19's notr5: the marginal screen misses the
differential breakage from dropping an S-box round's linear).

## S2 (N=2^22, 115 deltas, kill threshold 10 — verified `10` at ref file)

| Candidate | S2 verdict | max\|z\| | repeats |
|---|---|---:|---:|
| r20_feist6_alt_notr_chioff13all_nw | **PASS** | 11.2 | 0 |
| r20_feist6_alt_notr_keyin_nw | **PASS** | 10.7 | 0 |
| r20_feist6_alt_notr_chioff31_nw | **PASS** | 12.5 | 0 |
| r20_feist6_alt_notr_drop4_nw | **PASS (formal) / BROKEN (structural)** | **743.5** | 2 |
| r20_feist6_alt_chioff13_nw | **PASS** | 11.2 | 0 |

S2 run only for the 5 S1-passing non-dominated-or-probe candidates (the four
S0-dominated S1-passing candidates carry no frontier information).

drop4: formal PASS (repeats=2 < 10) but 46/115 deltas show systematic
single-bit differential spikes |z| = 100–743 (e.g. 0x0000000800000000:
712.1, 0x0000001000000000: 676.0). Dropping round 4's chi linear is
differentially fatal — F_4's output feeds F_5's input, unlike the final
round's output which goes straight to the ciphertext. **drop4 is dead.**
Same "fast number, broken design" class as r19's notr5 (|z|=477); ledger
O15's scope note (truncation safe only on the final chi round) is confirmed
a second time.

alt_chioff13 reproduces chioff13all's 11.2 — the round-6 linear (even with
chi(1,3)) changes nothing differentially; dominated on S0, no further battery.

## Q1 (SAC/BIC, N=2^18, fixed key, same script/procedure as r13/r18/r19)

| Candidate | sac_z5 | sac_maxdev | bic_maxcorr | avalanche_mean |
|---|---|---:|---:|---:|
| r20_feist6_alt_notr_chioff13all_nw | 0 ✓ | 0.00359 | 0.14149 (blemish) | 32.0001 |
| r20_feist6_alt_notr_keyin_nw | 0 ✓ | 0.00446 | 0.17232 (blemish) | 32.0002 |
| r20_feist6_alt_notr_chioff31_nw | 0 ✓ | 0.00378 | 0.14092 (blemish) | 32.0015 |

All three carry the documented BIC blemish class (unmixed final chi output):
chioff13all/chioff31 match chioff13's 0.142, keyin matches notr's 0.172.
BIC is reported, not gated — per Carlo's open decision (two-frontier
structure); blemish-free variants would feed Frontier Q.
sac_z5=0 (mandatory) holds for all three.

## S3 / S4

| Candidate | S3 (2 PractRand configs, 1GB) | S4 SmallCrush | Battery |
|---|---|---|---|
| r20_feist6_alt_notr_chioff13all_nw | PASS ×2 | "All tests were passed" | **BATTERY-PASS** |
| r20_feist6_alt_notr_keyin_nw | PASS ×2 | "All tests were passed" | **BATTERY-PASS** |
| r20_feist6_alt_notr_chioff31_nw | PASS ×2 | "All tests were passed" | **BATTERY-PASS** |
| r19_feist6_alt_notr_fm07_nw | PASS ×2 | "All tests were passed" | **BATTERY-PASS** (backfill) |
| r19_feist6_alt_notr_fm11_nw | PASS ×2 | "All tests were passed" | **BATTERY-PASS** (backfill) |
| r19_feist6_alt_notr_fm311_nw | PASS ×2 | "All tests were passed" | **BATTERY-PASS** (backfill) |

Batteries launched with `[run_fast_battery.sh](../fast_battery/run_fast_battery.sh) <cand> 3` (start at S3) since
S0/S1/S2/Q1 evidence is already recorded; logs in
`fast_battery/results/<cand>/battery.log` + `round20/battery_<cand>.log`.
The three fm backfills clear their provisional markers — Frontier Q is now
fully confirmed.

## Findings

1. **chioff13all (37.0u) — new speed point.** Putting chi(1,3) on the
   truncated round 6 is pure speed: −0.4u vs chioff13, S2-neutral (|z|=11.2
   reproduces), BIC-neutral (0.14149 vs 0.142). The round-6 linear is dead
   weight in every sense tested — dropping it AND upgrading the chi offset
   both pay. New Frontier S speed point, full battery clean.
2. **chioff31 (37.5u) — new size point, dominates r18 notr on all axes.**
   The (3,1) chi variant b_i = a_i ^ (~a_{i+3} & a_{i+1}) synthesizes
   ~250 cells / ~620 area smaller than both (1,2) and (1,3) variants at
   essentially the same delay. Construction-specific: in alt (r18) the
   (1,3) variant bought nothing; in notr the offset choice is a genuine
   area lever. New Frontier S size point, full battery clean.
3. **keyin (37.2u) — verified, excluded.** Key inside chi vs XORed after
   is near-neutral (+0.2u/+25 cells/−14 area); statistically identical
   (S2 |z|=10.7 reproduces notr's exactly). A near-duplicate of
   chioff13all, kept out of the frontier as effectively dominated.
4. **drop4 — truncation kill confirmed a second time.** Formal S2 PASS
   (repeats=2 < 10) but 46/115 deltas with |z|=114–743: dropping round 4's
   chi linear is differentially fatal (F_4's output feeds F_5's input,
   unlike the final round's output which goes straight to ciphertext).
   Same "fast number, broken design" class as r19's notr5. Ledger O15
   closed at LOW.
5. **S1-final is a dead end in notr** (+2.0u vs chi-final, dominated before
   Q1) — the BIC question it was meant to answer is moot: you don't pay
   2.0u to maybe fix a blemish when fm07 fixes it for 1.4u with bic=0.008.
6. **fm16: rotl-16 is not cheaper in synthesis** (+1.0u/+860 cells vs
   fm03) — the rotation amount doesn't move the XOR-tree cost; the fm
   family's cost is the extra 32-bit XOR layer, not the rotation.
7. **(5,17)/(7,13) on notr: (3,11) stands** — both dominated (38.4u/38.6u),
   re-confirming r14's alt verdict in a second construction.
8. **r13-full-alt+chi(1,3): the offset's value is construction-specific**
   — (1,3) wins in notr (−0.4–0.5u) but buys nothing in the non-truncated
   alt (40.0u, dominated).
9. **BIC blemish is invariant across all r20 notr variants** (0.141–0.172)
   — the unmixed final chi is the sole carrier; no variant accidentally
   fixes it, and the fm cure (r19) remains the only known fix.

## Evidence locations

- Candidates: `exploration/fast_battery/candidates/r20_*/` (impl.c, rtl.v, model.py, meta.json)
- Generator: `round20/gen_r20.py`; models: `round20/models/r20.py`
- S0: `round20/s0/*.log`; S1: `round20/s1/*.log`
- S2 logs: `round20/s2_r20_*.log`; progress: `round20/progress.log`
- Q1: `round20/q1/q1_*.json`
- S3/S4: `fast_battery/results/<cand>/{s3.out,s4.out,battery.log}`; queue log: `round20/battery_progress.log`
- fm backfill script: `round20/run_fm_backfill.sh`

## Process notes

- **keyin RTL tail bug (escape protocol):** `check_rtl` caught a double-XOR
  of the round key in round 6's tail for tag `chi_keyin_notr` (t already
  mixed the key in; the tail XORed it again). Fixed by extending the
  "bakes rk into t" condition to `tag.startswith("chi_fm") or tag ==
  "chi_keyin_notr"`. Class hunt: any tag whose `t` already incorporates rk
  needs the tail skip — currently exactly `chi_fm*` and `chi_keyin_notr`.
  All 9 candidates regenerated; the other 8 were byte-identical in
  behavior (verified 300/300 again); keyin's stale S0 (38.0u) was discarded
  and re-measured (37.2u). No synthesis numbers were trusted before the
  RTL fix.
- Batteries for frontier candidates were launched with
  `[run_fast_battery.sh](../fast_battery/run_fast_battery.sh) <cand> 3` (start at S3) to avoid re-running
  recorded S0/S1/S2 stages; max 2 concurrent heavy pipelines throughout.
- A mid-round service restart killed the [run_q1.sh](run_q1.sh) queue after 2/3
  candidates; chioff31's Q1 was re-run standalone (resume marks in
  [progress.log](progress.log) made this safe).

## Process notes

TBD.
