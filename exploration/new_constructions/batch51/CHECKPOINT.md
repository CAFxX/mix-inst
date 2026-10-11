# Batch-51 checkpoint (track-6 supervisor incarnation XXI, 2026-10-11)

## Co-design (done)
- Axis audit of batches 19–50 (DESIGN.md):
  - **fz24_g/h: DEAD, not opened.** b45/b49/b50 "NEVER SCREENED, stay
    OPEN" notes are STALE — they missed the LEADS_LEDGER candidate
    table: track-8 STRUCT-KILLED fz24_g 2026-10-10 11:35Z (proxy
    max|z|=256.0, constant-dead output bit) and PROXY-KILLED fz24_i/j/k/l
    (max|z|=256.0, "dead-bit fix and diffusion irreconcilable").
    Dead-bit mechanism independently re-derived from the chi_4
    definition (single-bit Δ at within-nibble j → Δq_{(j+1)%4} ≡ 0 ∀x).
    With b47 cut #1 (chi_4 CUT ON PROOF: 16→12), the nibble-chi axis is
    closed on proof + two measurements. Process gap noted: future
    de-dups must grep the ledger candidate rows, not just code dirs.
  - **Cubic S-box mining: DEFERRED (weak cost thesis).** 2 AND levels
    project ~7–8u/stage → 3st ~21–24u vs <6.43u/stage budget. Fallback
    if muxS4 dies.
  - **chi_5-lane: b45 trigger answered** (b47 chi5S-3 0/40 dead; 4st
    ~23u over budget). Moot.
  - **MUX-4st SELECTED:** never screened; cost thesis 4×3.86u ≈ 15.4u
    (3.9u margin, strongest open); mechanism = cheapest no-zero-corner
    gate (MUX fires ≥1 bit on single-bit input vs AND's 0 — the b45
    chi property at 3.86u/stage instead of 5.77u/stage).
- De-dup grep-verified: no 4-stage masked MUX cascade anywhere
  (track-5: MU5/MU6 only; b8: fused 6st only; adder_lat: mux axis
  planned never executed; directed_design: none).
- DESIGN.md written: 11 cuts with defensible reasons, pre-registered
  pre-pilot verdict rules, escalation path (bundle → S0 stratified
  <19.3u → S1 fail-fast → staged battery).

## Screen + wrapper (written, calibration in flight)
- `t6_b51_screen.py`: MUX stage `x ^= mux(ra,rb,rc) ^ rd`,
  mux=(s&a)|(~s&b); draws s,a,b distinct (degeneracy proof), d free;
  exact-DIFF triage 10 keys N=2^18 bar max|z|<10; keeps → JSONL
  per-try; draw-loop cap 10000; dup stage-tuples re-drawn.
- Calibration (two fail-loud gates): (i) and1/b33c z=3.3;
  (ii) MU5-324 schedule through the MUX stage must KEEP (z<10;
  track-5 measured 2.34).
- `run_b51_prepilot.sh`: backoff-poll ≤12h → calibration fail-loud →
  muxS4 6 draws (0xB511) → muxS3 6 draws (0xB512) → keeps to
  `prepilot_keeps.jsonl`.

## Launch log
- 2026-10-11T17:20:54Z: calibration PASS (CALIB-1 and1/b33c z=3.3 exact;
  CALIB-2 mux/MU5-324 z=3.24 KEEP; track-5 measured 2.34 — same
  ballpark, harness variation only).
- 2026-10-11T17:20:54Z: PRE-PILOT LAUNCHED via
  `setsid agentwork-launch.sh --nice 19 --tag track6/b51-prepilot`
  (wrapper `run_b51_prepilot.sh`: backoff-poll ≤12h → calibration
  fail-loud → muxS4 6 draws seed 0xB511 → muxS3 6 draws seed 0xB512 →
  keeps to `prepilot_keeps.jsonl`; logs `prepilot.log`,
  `prepilot_calibrate.log`, `wrapper-launch.log`). At launch backoff
  ENGAGED → wrapper correctly backoff-polling (poll 1 logged
  17:20:59Z). Proceeds autonomously when clear; next report run
  adjudicates per the pre-registered rules.
