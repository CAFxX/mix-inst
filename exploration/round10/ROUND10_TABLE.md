# Round 10 — Attacking the (3,11) winner and the 5-round phase transition (2026-10-02)

Target: beat/extend { r9_feist6_rot311_nw: 41.0u/4265/11996, r8_feist6_s1_1sbox_nw: 42.9u/4133/11670 }.
Multiplier reference re-measured fresh in this round's pinned flow: **103.5u**
(cells 12,645, area 35,323). S0 bar: ≤ 0.9 × 103.5 = 93.15u.

S0 numbers from [`run_synth.py`](../run_synth.py) (authorized path, Yosys 0.69 pinned,
dual-analyzer agreement, 13/13 agreement lines present). Battery via
[`run_fast_battery.sh`](../fast_battery/run_fast_battery.sh) (2 lanes, S2 kill threshold verified = 10 at the call
site). Bit-exactness verified independently before synthesis: C↔Python
10,000/10,000 PASS (13/13), RTL↔Python 300/300 PASS (13/13)
(`round10/run_xcheck.sh`). Dedupe: all 13 pairwise-distinct by model output,
novel vs all round-9 candidates.

## S0 pre-screen (13/13 pass the 0.9× bar)

| Candidate | Structure | S0 delay | Ratio | Cells | Area |
|---|---|---:|---:|---:|---:|
| r10_feist5_rot311 | 5r, F=S1+lin(3,11), white | 35.7u | 0.345× | 3,743 | 10,605 |
| r10_feist6_rot0307_nw | 6r, F=S1+lin(3,7), no white | 41.4u | 0.400× | 4,410 | 12,349 |
| r10_feist6_rot0313_nw | 6r, F=S1+lin(3,13), no white | 41.4u | 0.400× | 4,645 | 12,855 |
| r10_feist6_rot311_ksalt_nw | 6r, F=S1+lin(3,11) alt-key-halves, no white | 41.4u | 0.400× | 4,365 | 12,212 |
| r10_feist6_rot311_ksrot_nw | 6r, F=S1+lin(3,11) rk=rotl64(k,8i), no white | 41.4u | 0.400× | 4,554 | 12,685 |
| r10_feist6_rot0317_nw | 6r, F=S1+lin(3,17), no white | 41.5u | 0.401× | 4,602 | 12,779 |
| r10_feist6_rot0211_nw | 6r, F=S1+lin(2,11), no white | 41.7u | 0.403× | 4,609 | 12,854 |
| r10_feist6_altrot311_713_nw | 6r, F=S1+lin alt (3,11)/(7,13), no white | 41.9u | 0.405× | 4,480 | 12,598 |
| r10_feist6_rot0511_nw | 6r, F=S1+lin(5,11), no white | 41.9u | 0.405× | 4,629 | 13,002 |
| r10_feist6_rot311 | 6r, F=S1+lin(3,11), white | 42.5u | 0.411× | 4,675 | 13,154 |
| r10_feist6_rot0411_nw | 6r, F=S1+lin(4,11), no white | 42.8u | 0.414× | 4,150 | 11,847 |
| r10_feist5_s1_lin2_nw | 5r, F=S1+lin713x2, no white | 49.2u | 0.475× | 5,325 | 14,885 |
| r10_feist5_s1_2sbox_nw | 5r, F=S1+lin(3,11)+S1, no white | 52.9u | 0.511× | 4,801 | 13,338 |

Bit-exactness: C↔Python 10,000/10,000 PASS (13/13); RTL↔Python 300/300 PASS (13/13).

## Q1 spot checks (SAC/BIC, N=2^18; required for any Pareto claim)

| Candidate | sac_z5 | sac_maxdev | bic_maxcorr | Verdict |
|---|---|---:|---:|---|
| r10_feist6_rot0313_nw | 0 | 0.0035 | 0.0087 | clean |
| r10_feist6_altrot311_713_nw | 0 | 0.0036 | 0.0094 | clean |
| r10_feist6_rot0411_nw | 0 | 0.0036 | 0.0088 | clean |
| r10_feist5_s1_2sbox_nw | 118 | 0.0269 | 0.0867 | **FAIL — excluded** (same 5r phase-transition verdict as round 9) |

## Battery results

| Candidate | S0 | S1 | S2 (115 deltas, thr 10) | S3 | S4 | Full |
|---|---|---|---|---|---|---|
| r10_feist6_rot0313_nw | 41.4u | CAL_PASS | 0 repeats, max\|z\|=4.1 | PASS | PASS | **YES** |
| r10_feist6_rot0307_nw | 41.4u | CAL_PASS | 1 repeat, max\|z\|=1079.9 | PASS | PASS | YES |
| r10_feist6_rot311_ksalt_nw | 41.4u | CAL_PASS | 0 repeats, max\|z\|=17.4 | PASS | PASS | YES |
| r10_feist6_rot311_ksrot_nw | 41.4u | CAL_PASS | 0 repeats, max\|z\|=16.9 | PASS | PASS | YES |
| r10_feist6_rot0317_nw | 41.5u | CAL_PASS | 7 repeats, max\|z\|=330.0 | PASS | PASS | YES |
| r10_feist6_rot0211_nw | 41.7u | CAL_PASS | 1 repeat, max\|z\|=48.6 | PASS | PASS | YES |
| r10_feist6_altrot311_713_nw | 41.9u | CAL_PASS | 0 repeats, max\|z\|=3.6 | PASS | PASS | YES |
| r10_feist6_rot311 | 42.5u | CAL_PASS | 0 repeats, max\|z\|=15.8 | PASS | PASS | YES |
| r10_feist6_rot0411_nw | 42.8u | CAL_PASS | 0 repeats, max\|z\|=4.1 | PASS | PASS | YES |
| r10_feist5_s1_2sbox_nw | 52.9u | CAL_PASS | 0 repeats, max\|z\|=170.3 | PASS | PASS | YES |
| r10_feist5_rot311 | 35.7u | **FLAG** | — | — | — | no |
| r10_feist5_s1_lin2_nw | 49.2u | **FLAG** | — | — | — | no |
| r10_feist6_rot0511_nw | 41.9u | **FLAG** | — | — | — | no |

## Pareto verdict

**Frontier UNCHANGED:** { r9_feist6_rot311_nw: 41.0u/4265/11996, r8_feist6_s1_1sbox_nw: 42.9u/4133/11670 }.

- No 6r rotation pair beats (3,11) on delay. (3,13) and (3,7) tie at 41.4u but are
  larger (4645/4410 vs 4265 cells) — dominated.
- (3,13) and (4,11) are S2-clean at max\|z\|=4.1, i.e. (7,13)-level differential
  cleanliness at near-(3,11) speed, Q1 clean — but dominated on delay/cells, so
  no Pareto claim. They are the quality-preferred alternatives (see ranking below).
- r10_feist6_rot0411_nw (42.8u) is 0.1u faster than r8 on paper but +17 cells /
  +177 area; 0.23% is below the P&R noise floor — not a meaningful extension,
  not claimed.
- (3,11)+whitening: 42.5u S4 PASS, S2 \|z\|=15.8 — whitening costs 1.5u for (3,11)
  and does not clean S2. Confirms whitening is pure cost at 6r.
- Key-schedule × (3,11): ksalt/ksrot both 41.4u, S2 \|z\|~17, dominated. Schedule
  variants don't move the needle.
- 5-round phase transition HOLDS: r10_feist5_rot311 (35.7u) S1-FLAG;
  r10_feist5_s1_lin2_nw S1-FLAG; r10_feist5_s1_2sbox_nw passes formally at 52.9u
  but S2 max\|z\|=170.3 (strong differential signal). 5r is not rescuable by a
  stronger F at acceptable cost.
- Heterogeneous alternating (3,11)/(7,13): 41.9u, S2 \|z\|=3.6 fully clean, dominated.

## Quality-preferred ranking (for the record, not the 2-axis frontier)

| # | Candidate | Delay | S2 max\|z\| | Q1 | Note |
|---|---|---:|---:|---|---|
| 1 | r10_feist6_altrot311_713_nw | 41.9u | 3.6 | clean | cleanest differential of any 6r candidate |
| 2 | r10_feist6_rot0313_nw | 41.4u | 4.1 | clean | fastest clean pair — hits the round's (3,13) target |
| 3 | r9_feist6_rot311_nw | 41.0u | 16.5 | clean | fastest overall (frontier) |
| 4 | r8_feist6_s1_1sbox_nw | 42.9u | 4.0 | clean | smallest (frontier) |

## Family summaries

1. **Fine rotation sweep around (3,11):** 6 pairs tested. None beats 41.0u.
   (5,11) S1-FLAG. Speed ranking: (3,11) > (3,7)=(3,13) > (3,17) > (2,11).
   Cleanliness ranking: (3,13)=(4,11) [4.1] > (3,11) [16.5] > (2,11) [48.6] >
   (3,17) [330] > (3,7) [1079.9]. Speed and differential cleanliness trade off
   across rotation pairs — no pair dominates both axes.
2. **(3,11)+whitening:** works, costs 1.5u, dominated.
3. **5r phase transition:** confirmed un-crossed (3 attempts, 2 S1 kills + 1
   differential mess).
4. **Key-schedule × (3,11):** dominated, no effect beyond ±0.4u.
5. **Heterogeneous:** alternating rotations work and are clean, dominated.
