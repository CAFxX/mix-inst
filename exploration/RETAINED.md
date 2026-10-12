# Retained candidates — full-battery survivors

**Policy (Carlo 2026-10-03):** every candidate that passes the full battery
(S0–S4 + Q1 `sac_z5=0`) is **retained indefinitely**, on disk, with its
evidence — because the future extended-PractRand breaking-point batteries
will differentiate candidates that look identical under the standard 1GB
battery. **"Retired" means off the Pareto frontier. It never means deleted.**
No track may delete [`fast_battery/candidates/<name>/`](fast_battery/candidates/) or its round logs.
The RTL package (`~/workspace/your_files/mix_rtl_pareto/`) tracks the live
frontiers only; it is not the archive — the archive is this list plus the
candidate directories.

## The retained set (47 candidates, 2026-10-12)

| # | Candidate | Delay | Cells | Area | bic_maxcorr | Frontier status | Round |
|---|---|---:|---:|---:|---:|---|---|
| 1 | [r6_feist8_spn](fast_battery/candidates/r6_feist8_spn/) | 86.5u | — | — | n/a (predates Q1) | retired | 6 |
| 2 | [r7_feist8_s1_1sbox](fast_battery/candidates/r7_feist8_s1_1sbox/) | 56.5u | — | — | n/a (predates Q1) | retired | 7 |
| 3 | [r8_feist6_s1_1sbox_nw](fast_battery/candidates/r8_feist6_s1_1sbox_nw/) | 42.9u | 4,133 | 11,670 | 0.00804 | **Frontier Q** | 8 |
| 4 | [r9_feist6_rot311_nw](fast_battery/candidates/r9_feist6_rot311_nw/) | 41.0u | 4,265 | 11,996 | 0.00850 | **Frontier Q** | 9 |
| 5 | [r13_feist6_alt_s1chi_nw](fast_battery/candidates/r13_feist6_alt_s1chi_nw/) | 40.1u | 4,563 | 13,041 | 0.008 | retired | 13 |
| 6 | [r15_feist6_parsplit_nw](fast_battery/candidates/r15_feist6_parsplit_nw/) | 40.7u | 4,318 | 12,356 | 0.00842 | **Frontier Q** | 15 |
| 7 | [r18_feist6_alt_notr_nw](fast_battery/candidates/r18_feist6_alt_notr_nw/) | 37.9u | 4,119 | 11,621 | 0.172 | retired | 18 |
| 8 | [r18_feist6_alt_palk_nw](fast_battery/candidates/r18_feist6_alt_palk_nw/) | 40.5u | 4,447 | 12,905 | 0.00890 | retired (never frontier) | 18 |
| 9 | [r19_feist6_alt_notr_chioff13_nw](fast_battery/candidates/r19_feist6_alt_notr_chioff13_nw/) | 37.4u | 4,149 | 11,820 | 0.142 | retired | 19 |
| 10 | [r19_feist6_alt_notr_fm07_nw](fast_battery/candidates/r19_feist6_alt_notr_fm07_nw/) | 38.8u | 5,053 | 14,320 | 0.00805 | retired | 19 |
| 11 | [r19_feist6_alt_notr_fm11_nw](fast_battery/candidates/r19_feist6_alt_notr_fm11_nw/) | 39.3u | 4,877 | 13,748 | 0.00976 | retired | 19 |
| 12 | [r19_feist6_alt_notr_fm311_nw](fast_battery/candidates/r19_feist6_alt_notr_fm311_nw/) | 39.5u | 4,467 | 12,769 | 0.00882 | **Frontier Q** | 19 |
| 13 | [r20_feist6_alt_notr_chioff13all_nw](fast_battery/candidates/r20_feist6_alt_notr_chioff13all_nw/) | 37.0u | 4,357 | 12,511 | 0.14149 | retired | 20 |
| 14 | [r20_feist6_alt_notr_chioff31_nw](fast_battery/candidates/r20_feist6_alt_notr_chioff31_nw/) | 37.5u | 3,863 | 11,199 | 0.14092 | retired | 20 |
| 15 | [r20_feist6_alt_notr_keyin_nw](fast_battery/candidates/r20_feist6_alt_notr_keyin_nw/) | 37.2u | 4,382 | 12,497 | 0.17232 | threshold-excluded | 20 |
| 16 | [r21_feist6_alt_notr_chioff31final_nw](fast_battery/candidates/r21_feist6_alt_notr_chioff31final_nw/) | 36.7u | 4,198 | 12,005 | 0.14029 | **Frontier S** | 21 |
| 17 | [r21_feist6_alt_notr_3rot_ns_nw](fast_battery/candidates/r21_feist6_alt_notr_3rot_ns_nw/) | 37.4u | 3,667 | 10,742 | 0.25384 | **Frontier S** | 21 |
| 18 | [r21_feist6_alt_notr_chioff13all_fm311_nw](fast_battery/candidates/r21_feist6_alt_notr_chioff13all_fm311_nw/) | 39.1u | 4,485 | 12,763 | 0.00860 | **Frontier Q** | 21 |
| 19 | [r21_feist6_alt_notr_chioff31_fm07_nw](fast_battery/candidates/r21_feist6_alt_notr_chioff31_fm07_nw/) | 39.2u | 4,661 | 13,159 | 0.00851 | retired | 21 |
| 20 | [r21_feist6_alt_notr_chioff13all_fm07_nw](fast_battery/candidates/r21_feist6_alt_notr_chioff13all_fm07_nw/) | 39.4u | 4,870 | 13,729 | 0.00892 | retired | 21 |
| 21 | [r21_feist6_alt_notr_keyin31_nw](fast_battery/candidates/r21_feist6_alt_notr_keyin31_nw/) | 36.9u | 4,191 | 11,986 | 0.14092 | threshold-excluded | 21 |
| 22 | [r22c_spn_mix4r_lp_nw](fast_battery/candidates/r22c_spn_mix4r_lp_nw/) | 28.3u | 4,656 | 12,949 | 0.00865 | **Frontier S + Q** | O44 |
| 23 | [r21b_3rot_ns_fm311_nw](fast_battery/candidates/r21b_3rot_ns_fm311_nw/) | 38.3u | 4,299 | 12,356 | 0.00883 | **Frontier Q** | r21b |
| 24 | [rtw_pb2_rev_inout](fast_battery/candidates/rtw_pb2_rev_inout/) | 36.9u | 4,284 | 12,210 | 0.14320 | retired (dominated by chioff31final 36.7u) | tweak |
| 25 | [r23_spn_mix4r_pba19b01_nw](fast_battery/candidates/r23_spn_mix4r_pba19b01_nw/) | 27.8u | 5,732 | 15,374 | 0.01092 | retired 2026-10-05 (strictly dominated by r25 rasC2_0 on all axes: 26.5/5,125/14,019); former Frontier S+Q speed point (round 23–25) | 23 |
| 26 | [r23_spn_mix4r_pba27b01_nw](fast_battery/candidates/r23_spn_mix4r_pba27b01_nw/) | 28.2u | 5,093 | 13,870 | 0.00853 | threshold-excluded (near-duplicate of r22c: 0.1u edge at +9% cells) | 23 |
| 27 | [wf2d_aff_a17_b17](fast_battery/candidates/wf2d_aff_a17_b17/) | 27.9u | 5,299 | 14,223 | 0.00901 | retired 2026-10-05 (strictly dominated by r25 rasC2_0 on all axes); former Frontier S+Q mid-SPN point | wf2d |
| 28 | [r25_spn_pba19_sb_rasC2_5_nw](fast_battery/candidates/r25_spn_pba19_sb_rasC2_5_nw/) | 28.1u | 5,778 | 15,764 | 0.01009 | **full-pass reference, threshold-excluded** (S0–S4 all PASS: S1 CAL_PASS, S2 max\|z\|=12.1, S3 1GB pass both streams, S4 SmallCrush pass; sac_z5=0, BIC 0.01009 ≤ 0.02 — parent-verified 2026-10-05) but dominated by r23 pba19b01 on all S0 axes (+0.3u, +46 cells, +390 area): stays off Frontier S+Q | 25 |
| 29 | [al_cascad](fast_battery/candidates/al_cascad/) | 25.5u | 7,891 | 26,566 | 0.00891 | **retired 2026-10-10** (former Frontier S+Q point): strictly dominated by [t6_b33c](fast_battery/candidates/t6_b33c/) (19.8/6,133/19,817) on all three axes. 8-stage cascaded AND-rotation, no S-box; full battery evidence in fast_battery/results/[al_cascad](fast_battery/candidates/al_cascad/)/ | AL |
| 30 | [al_and6a](fast_battery/candidates/al_and6a/) | 20.1u | 6,116 | 19,541 | 0.00868 | **retired 2026-10-10** (former Frontier S speed point): dominated by [t6_b33b](fast_battery/candidates/t6_b33b/) (20.1u tie on delay, 5,992<6,116 cells, 19,280<19,541 area). 6-stage AND-rotation cascade; full battery evidence in fast_battery/results/[al_and6a](fast_battery/candidates/al_and6a/)/ | AL |
| 31 | [t6_b33c](fast_battery/candidates/t6_b33c/) | 19.8u | 6,133 | 19,817 | 0.01002 | **retired 2026-10-12** (former Frontier S+Q speed point): strictly dominated by [t6_b62_9](fast_battery/candidates/t6_b62_9/) (19.2/5,847/19,631) on all three axes | batch-33 |
| 32 | [t6_b33b](fast_battery/candidates/t6_b33b/) | 20.1u | 5,992 | 19,280 | 0.00913 | **retired 2026-10-12** (former Frontier S+Q size point): strictly dominated by [t6_b62_3](fast_battery/candidates/t6_b62_3/) (19.6/5,765/16,849) on all three axes | batch-33 |
| 33 | [al_w3p_a](fast_battery/candidates/al_w3p_a/) | 48.3u | 18,917 | 58,806 | 0.00839 | retired (never frontier — dominated on all axes) — full battery+Q1 PASS | wave-14 W3' |
| 34 | [al_w3p_b](fast_battery/candidates/al_w3p_b/) | 50.6u | 18,322 | 57,155 | 0.00858 | retired (never frontier — dominated on all axes) — full battery+Q1 PASS | wave-14 W3' |
| 35 | [al_w3p_d](fast_battery/candidates/al_w3p_d/) | 48.7u | 18,983 | 58,731 | 0.00861 | retired (never frontier — dominated on all axes) — full battery+Q1 PASS | wave-14 W3' |
| 36 | [t6_b57_8](fast_battery/candidates/t6_b57_8/) | 19.2u | 6,503 | 20,494 | 0.00863 | retired (dominated on all axes by [hyb29_mu5_008](fast_battery/candidates/hyb29_mu5_008/) 2026-10-12) — full battery PASS (S0–S4 + sac_z5=0 + BIC-clean) | batch-57 |
| 37 | [t6_b59_0](fast_battery/candidates/t6_b59_0/) | 19.1u | 6,358 | 20,580 | 0.00897 | **retired 2026-10-12** (former Frontier S+Q speed point): strictly dominated by [t6_b62_26](fast_battery/candidates/t6_b62_26/) (19.1u delay tie, 6,272<6,358 cells, 20,327<20,580 area) — full battery PASS (S0–S4 + sac_z5=0 + BIC-clean); muxD5f-local m=1 perturbation of the [t6_b57_8](fast_battery/candidates/t6_b57_8/) winner schedule | batch-59 |
| 38 | [t6_b59_47](fast_battery/candidates/t6_b59_47/) | 18.6u | 6,656 | 21,830 | 0.00986 | **Frontier S + Q (speed point)** — full battery PASS (S0–S4 + sac_z5=0 + BIC-clean); muxD5f-local m=2 rotation perturbation of the [t6_b57_8](fast_battery/candidates/t6_b57_8/) winner schedule (stage2_d 41→57, stage4_b 49→44) | batch-59 |
| 39 | [r25_spn_pba19_sb_rasC2_0_nw](fast_battery/candidates/r25_spn_pba19_sb_rasC2_0_nw/) | 26.5u | 5,125 | 14,019 | 0.01012 | **Frontier S + Q (speed point)** — full battery PASS (S0–S4 + sac_z5=0 + BIC ≤ 0.02), parent-verified 2026-10-05; strictly dominates r23 pba19b01 and wf2d aff_a17_b17 | 25 |
| 40 | [r25_spn_pba19_sb_rasC1_2_nw](fast_battery/candidates/r25_spn_pba19_sb_rasC1_2_nw/) | 28.5u | 4,980 | 13,247 | 0.00847 | **full-pass reference, frontier-excluded** — full battery PASS (S0–S4 + sac_z5=0 + BIC ≤ 0.02), parent-verified 2026-10-05; strictly dominated by r22c (28.3/4,656/12,949) on all axes | 25 |
| 41 | [hyb29_mu5_008](fast_battery/candidates/hyb29_mu5_008/) | 19.2u | 6,151 | 20,256 | 0.00813 | **retired 2026-10-12** (former Frontier S+Q 19.2u slot): strictly dominated by [t6_b62_9](fast_battery/candidates/t6_b62_9/) (19.2u delay tie, 5,847<6,151 cells, 19,631<20,256 area) — full battery PASS (S0–S4 + sac_z5=0 + BIC-clean), parent-verified from raw logs 2026-10-12; batch-29 m~U{1,2,3} rotation perturbation of the [hyb28_mu5_324](fast_battery/candidates/hyb28_mu5_324/) winner schedule | batch-29 |
| 42 | [t6_b59_41](fast_battery/candidates/t6_b59_41/) | 19.0u | 6,393 | 20,812 | 0.00816 | **Frontier S + Q (19.0u delay point)** — full battery PASS (S0–S4 + sac_z5=0 + BIC-clean); batch-59 muxD5f-local rotation perturbation of the [t6_b57_8](fast_battery/candidates/t6_b57_8/) winner schedule | batch-59 |
| 43 | [t6_xorh5_15](fast_battery/candidates/t6_xorh5_15/) | 21.8u | 5,833 | 17,170 | 0.00923 | **retired 2026-10-12** (former Frontier S+Q cells/area point): strictly dominated by [t6_b62_3](fast_battery/candidates/t6_b62_3/) (19.6/5,765/16,849) on all three axes — full battery PASS (S0–S4 + sac_z5=0 + BIC-clean), parent-verified from raw logs 2026-10-12; track-6 xorh5 hetero wide-chain | xorh5 |
| 44 | [hyb28_mu5_324](fast_battery/candidates/hyb28_mu5_324/) | 19.3u | 6,146 | 20,001 | 0.00870 | **retired 2026-10-12** (former Frontier S+Q cells/area point): strictly dominated by [t6_b62_9](fast_battery/candidates/t6_b62_9/) (19.2/5,847/19,631) on all three axes — full battery PASS (S0–S4 + sac_z5=0 + BIC-clean); batch-28 5-stage MUX-rotation cascade, pre-whiten, final x^=rotl(k,13) | batch-28 |
| 45 | [t6_b62_26](fast_battery/candidates/t6_b62_26/) | 19.1u | 6,272 | 20,327 | 0.00873 | **Frontier S + Q (19.1u slot; dominates t6_b59_0)** — full battery PASS (S0–S4 + sac_z5=0 + BIC-clean), Q1-adjudication lane raw-adjudicated 2026-10-12 (O161); batch-62 muxD5f 5-stage size-axis keep, weakness-gated triage (z=3.32) | batch-62 |
| 46 | [t6_b62_9](fast_battery/candidates/t6_b62_9/) | 19.2u | 5,847 | 19,631 | 0.00960 | **Frontier S + Q (19.2u slot; dominates 008/324/b33c)** — full battery PASS (S0–S4 + sac_z5=0 + BIC-clean), Q1-adjudication lane raw-adjudicated 2026-10-12 (O162); batch-62 muxD5f 5-stage size-axis keep, weakness-gated triage (z=2.75) | batch-62 |
| 47 | [t6_b62_3](fast_battery/candidates/t6_b62_3/) | 19.6u | 5,765 | 16,849 | 0.00869 | **Frontier S + Q (size point; dominates b33b/xorh5_15)** — full battery PASS (S0–S4 + sac_z5=0 + BIC-clean), Q1-adjudication lane raw-adjudicated 2026-10-12 (O163); batch-62 muxD5f 5-stage size-axis keep, weakness-gated triage (z=2.44) | batch-62 |

## Evidence locations (per candidate)

- Implementation + model: [`fast_battery/candidates/<name>/{impl.c,rtl.v,model.py,meta.json}`](fast_battery/candidates/)
- Round table: `round<N>/ROUND<N>_TABLE.md` (O44: `round22/ROUND22_TABLE.md`)
- Battery log: `round<N>/battery_<name>.log` (S3/S4 verdicts)
- S0/S1/S2/Q1: `round<N>/{s0,s1,q1}/`, `round<N>/s2_<name>.log`

## Breaking-point battery (future work — not yet launched)

When Carlo calls for it: per retained candidate, extended PractRand runs
past the standard 1GB — 2GB, 4GB, 8GB, … — in both configs (standard +
strided), stopping at the first FAIL. The breaking size is the new
discriminator the standard battery cannot provide. Practical notes:

- Cost scales with candidate count × breaking size; run longest-first or
  frontier-first depending on the question being asked.
- The 1GB-clean evidence stays valid; breaking-point runs are *additional*,
  not replacements.
- Any candidate that breaks first at a given size does not invalidate its
  1GB result — record breaking sizes as a new column, keep the frontier
  logic unchanged unless Carlo redefines it.
- Checkpoint per completed size per candidate (these runs take hours).

## Retention rules for all tracks

1. Never delete `fast_battery/candidates/<name>/`.
2. Never delete round logs (`round<N>/`, [`round_hyb/`](round_hyb/), [`round_tweak/`](round_tweak/), [`ga/`](ga/)).
3. "Retired" in PARETO.md / VERDICT_SCOPE.md / round tables = frontier
   membership only. The candidate and its evidence stay.
4. The RTL package is a *view* over the live frontiers, not the archive.
